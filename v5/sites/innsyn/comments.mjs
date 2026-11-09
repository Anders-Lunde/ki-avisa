// Bundled into the existing Pages Worker by build.py, never served as source.
const COMMENT_ARTICLES = __COMMENT_ARTICLES__;
const CC = __COMMENTS_COPY__;
const COMMENT_HEADERS = {
  'Content-Type':'application/json; charset=utf-8',
  'Cache-Control':'private, no-store', 'X-Content-Type-Options':'nosniff',
  'X-Robots-Tag':'noindex, nofollow, noarchive', 'Referrer-Policy':'no-referrer',
  'Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'",
};
const commentJSON = (data, status=200, extra={}) => new Response(JSON.stringify(data), {status, headers:{...COMMENT_HEADERS,...extra}});
const commentError = (key, status, extra={}) => commentJSON({error:CC[key] || CC.failed}, status, extra);
const seconds = () => Math.floor(Date.now()/1000);
const hex = bytes => Array.from(new Uint8Array(bytes), n=>n.toString(16).padStart(2,'0')).join('');
const encoder = new TextEncoder();
async function commentSign(secret, value) {
  const key = await crypto.subtle.importKey('raw',encoder.encode(secret),{name:'HMAC',hash:'SHA-256'},false,['sign']);
  return hex(await crypto.subtle.sign('HMAC',key,encoder.encode(value)));
}
function equalSignature(a,b) {
  let mismatch = a.length ^ b.length;
  for(let i=0;i<a.length;i++) mismatch |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return mismatch === 0;
}
function sameCommentOrigin(request) {
  return request.headers.get('Origin') === `https://${HOST}` &&
    !['cross-site','same-site'].includes(request.headers.get('Sec-Fetch-Site')) &&
    request.headers.get('X-KI-Comments') === '1';
}
async function commentPayload(request) {
  if(request.headers.get('Content-Type')?.split(';')[0].trim().toLowerCase() !== 'application/json') return null;
  if(Number(request.headers.get('Content-Length') || 0)>32768) throw new RangeError();
  const reader=request.body?.getReader();
  if(!reader) return null;
  let size=0, chunks=[];
  while(true) {
    const {value,done}=await reader.read(); if(done) break;
    size+=value.byteLength;
    if(size>32768) { await reader.cancel(); throw new RangeError(); }
    chunks.push(value);
  }
  const buffer=new Uint8Array(size); let offset=0;
  for(const chunk of chunks) {buffer.set(chunk,offset);offset+=chunk.byteLength;}
  try {const data=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(buffer));return data && !Array.isArray(data) && typeof data==='object' ? data : null;}
  catch{return null;}
}
// D1 batch is transactional. Each successful reservation stamps a unique permit;
// a saturated bucket cannot reuse another request's last successful reservation.
async function commentReserve(db, limits, now=seconds()) {
  const permit=crypto.randomUUID();
  const buckets=[...limits].sort((a,b)=>Number(b[0].includes('global'))-Number(a[0].includes('global')))
    .map(([key,period,max])=>({key:`${key}:${Math.floor(now/period)}`,max,end:(Math.floor(now/period)+1)*period}));
  const result=await db.batch([
    ...buckets.map((b,i)=>{
      const previous=buckets.slice(0,i);
      return db.prepare(`INSERT INTO comment_limits(key,count,permit,expires_at) SELECT ?,1,?,?
        WHERE ${previous.length ? previous.map(()=> 'EXISTS(SELECT 1 FROM comment_limits WHERE key=? AND permit=?)').join(' AND ') : '1'}
        ON CONFLICT(key) DO UPDATE SET count=count+1,permit=excluded.permit WHERE count < ?`)
        .bind(b.key,permit,b.end,...previous.flatMap(p=>[p.key,permit]),b.max);
    }),
    db.prepare(`SELECT key,permit,expires_at FROM comment_limits WHERE key IN (${buckets.map(()=>'?').join(',')})`).bind(...buckets.map(b=>b.key)),
  ]);
  const rows=result.at(-1).results;
  const blocked=buckets.filter(b=>!rows.some(row=>row.key===b.key&&row.permit===permit));
  return blocked.length ? Math.max(1,...blocked.map(b=>b.end-now)) : 0;
}
async function commentCleanup(db, now=seconds()) {
  // Bounded batches; expired rows are never used, even before physical cleanup.
  await db.batch([
    db.prepare('DELETE FROM comment_limits WHERE key IN (SELECT key FROM comment_limits WHERE expires_at<=? LIMIT 500)').bind(now),
    db.prepare('DELETE FROM comment_reports WHERE (comment_id,reporter) IN (SELECT comment_id,reporter FROM comment_reports WHERE expires_at<=? LIMIT 500)').bind(now),
    db.prepare("DELETE FROM comments WHERE id IN (SELECT id FROM comments WHERE status='pending' AND created_at<=? LIMIT 100)").bind(now-30*86400),
    db.prepare('DELETE FROM comment_actions WHERE id IN (SELECT id FROM comment_actions WHERE created_at<=? LIMIT 500)').bind(now-90*86400),
  ]);
}
async function commentIdentity(request,env,now=seconds()) {
  let ip=request.headers.get('CF-Connecting-IP');
  if(!ip || ip.length>64) return null; // Never trust X-Forwarded-For or client-supplied IDs.
  // Cloudflare supplies normalized IPv6. Share a /64 budget across privacy addresses.
  if(ip.includes(':')) {
    const [left,right='']=ip.toLowerCase().split('::');
    const a=left?left.split(':'):[],b=right?right.split(':'):[];
    const groups=ip.includes('::')?[...a,...Array(Math.max(0,8-a.length-b.length)).fill('0'),...b]:a;
    ip=groups.slice(0,4).map(group=>group.padStart(4,'0')).join(':')+'::/64';
  }
  return commentSign(env.COMMENTS_SECRET,`ip:${Math.floor(now/86400)}:${ip}`);
}
async function commentToken(request,env,article,ip) {
  const delay=await commentReserve(env.STATS_DB,[[`token:${ip}`,60,60],['token-global',60,3000]]);
  if(delay) return commentError('rate_limited',429,{'Retry-After':String(delay)});
  const payload=`${seconds()}.${crypto.randomUUID()}`;
  return commentJSON({token:payload+'.'+await commentSign(env.COMMENTS_SECRET,`form:${article}:${ip}:${payload}`)});
}
async function validCommentToken(data,env,article,ip) {
  if(typeof data.token!=='string' || !/^\d{10}\.[a-f0-9-]{36}\.[a-f0-9]{64}$/.test(data.token)) return 'challenge_expired';
  const [issued,nonce,signature]=data.token.split('.');
  const age=seconds()-Number(issued);
  if(age<2) return 'too_fast';
  if(age>7200) return 'challenge_expired';
  const expected=await commentSign(env.COMMENTS_SECRET,`form:${article}:${ip}:${issued}.${nonce}`);
  return equalSignature(signature,expected) ? null : 'challenge_expired';
}
function validCommentText(value,max,name=false) {
  if(typeof value!=='string')return null;
  const text=value.normalize('NFC').replace(/\r\n?/g,'\n').trim();
  if(!text || text.length>max || /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f\u202a-\u202e\u2066-\u2069]/u.test(text) || (name && /[\n\t]/.test(text)))return null;
  return text;
}
async function commentSubmit(request,env,article,ip,data) {
  if(data.website) return commentError('invalid',400); // Honeypot; never silently pretend to accept.
  const invalid=await validCommentToken(data,env,article,ip);
  if(invalid) return commentError(invalid,400);
  const name=validCommentText(data.name,80,true), body=validCommentText(data.body,6000);
  const parent=data.parent_id ?? null;
  if(!name || !body || (parent!==null && (!Number.isSafeInteger(parent)||parent<1)))return commentError('invalid',400);
  const nonce=data.token.split('.')[1];
  const existing=await env.STATS_DB.prepare('SELECT name,body,parent_id FROM comments WHERE nonce=?').bind(nonce).all();
  if(existing.results.length) {
    const row=existing.results[0];
    return row.name===name && row.body===body && row.parent_id===parent ? commentJSON({message:CC.submitted},202) : commentError('duplicate',409);
  }
  if(parent!==null) {
    const rows=await env.STATS_DB.prepare("SELECT id FROM comments WHERE id=? AND article=? AND status='published'").bind(parent,article).all();
    if(!rows.results.length)return commentError('invalid',400);
  }
  const delay=await commentReserve(env.STATS_DB,[[`submit:${ip}`,600,10],[`submit-day:${ip}`,86400,100],['submit-global',600,500],['submit-global-day',86400,5000]]);
  if(delay)return commentError('rate_limited',429,{'Retry-After':String(delay)});
  const result=await env.STATS_DB.prepare(`INSERT OR IGNORE INTO comments(article,name,body,parent_id,created_at,nonce)
    SELECT ?,?,?,?,?,? WHERE (SELECT COUNT(*) FROM comments WHERE status='pending')<10000
    AND (? IS NULL OR EXISTS(SELECT 1 FROM comments WHERE id=? AND article=? AND status='published')) RETURNING id`)
    .bind(article,name,body,parent,seconds(),nonce,parent,parent,article).all();
  return result.results.length ? commentJSON({message:CC.submitted},202) : commentError('unavailable',503);
}
async function commentReport(env,article,ip,data) {
  const invalid=await validCommentToken(data,env,article,ip);
  if(invalid)return commentError(invalid,400);
  if(!Number.isSafeInteger(data.id)||data.id<1)return commentError('invalid',400);
  const delay=await commentReserve(env.STATS_DB,[[`report:${ip}`,600,30],['report-global',600,1000]]);
  if(delay)return commentError('rate_limited',429,{'Retry-After':String(delay)});
  await env.STATS_DB.batch([
    env.STATS_DB.prepare(`INSERT OR IGNORE INTO comment_reports(comment_id,reporter,expires_at)
      SELECT id,?,? FROM comments WHERE id=? AND article=? AND status='published'`).bind(ip,seconds()+86400,data.id,article),
    env.STATS_DB.prepare('UPDATE comments SET reports=(SELECT COUNT(*) FROM comment_reports WHERE comment_id=comments.id AND expires_at>?) WHERE id=? AND article=?').bind(seconds(),data.id,article),
  ]);
  return commentJSON({message:CC.reported});
}
async function commentList(env,article,url) {
  const after=Number(url.searchParams.get('after')||0);
  if(!Number.isSafeInteger(after)||after<0)return commentError('invalid',400);
  const rows=await env.STATS_DB.prepare(`SELECT c.id,c.name,c.body,c.parent_id,c.published_at,
    p.name AS parent_name FROM comments c LEFT JOIN comments p ON p.id=c.parent_id AND p.status='published'
    WHERE c.article=? AND c.status='published' AND c.id>? ORDER BY c.id LIMIT 31`).bind(article,after).all();
  const items=rows.results.slice(0,30);
  return commentJSON({items,next:rows.results.length>30 ? items.at(-1).id : null});
}
async function commentModeration(request,env) {
  const headers={...PRIVATE_HEADERS,'Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"};
  if(!/^[a-f0-9]{64}$/.test(env.STATS_AUTH_SHA256||'')||!env.STATS_DB||!/^[a-f0-9]{64}$/.test(env.COMMENTS_SECRET||''))return new Response('Moderering er ikke konfigurert.',{status:503,headers});
  if(!await authorized(request,env.STATS_AUTH_SHA256)) {
    const ip=await commentIdentity(request,env);
    if(!ip)return new Response('Innlogging er utilgjengelig.',{status:503,headers});
    const delay=await commentReserve(env.STATS_DB,[[`login:${ip}`,60,30],[`login-day:${ip}`,86400,300],['login-global',60,3000]]);
    return new Response('Innlogging kreves.',{status:delay?429:401,headers:{...headers,...(delay?{'Retry-After':String(delay)}:{'WWW-Authenticate':'Basic realm="KI-avisa statistikk", charset="UTF-8"'})}});
  }
  await commentCleanup(env.STATS_DB);
  if(request.method==='POST') {
    if(!sameCommentOrigin(request))return commentError('forbidden',403);
    const data=await commentPayload(request);
    if(!data || !Number.isSafeInteger(data.id) || !['publish','delete','dismiss_reports'].includes(data.action))return commentError('invalid',400);
    const now=seconds();
    // Allowlist action selects fixed SQL; every user value stays bound.
    const mutation=data.action==='publish' ? env.STATS_DB.prepare("UPDATE comments SET status='published',published_at=? WHERE id=? AND status='pending' AND created_at>?").bind(now,data.id,now-30*86400) : data.action==='delete' ? env.STATS_DB.prepare('DELETE FROM comments WHERE id=?').bind(data.id) : env.STATS_DB.prepare('UPDATE comments SET reports=0 WHERE id=?').bind(data.id);
    await env.STATS_DB.batch([
      env.STATS_DB.prepare('INSERT INTO comment_actions(comment_id,action,created_at) SELECT id,?,? FROM comments WHERE id=?').bind(data.action,now,data.id),
      mutation,
      ...(data.action==='dismiss_reports'?[env.STATS_DB.prepare('DELETE FROM comment_reports WHERE comment_id=?').bind(data.id)]:[]),
    ]);
    return commentJSON({ok:true});
  }
  if(!['GET','HEAD'].includes(request.method))return new Response(null,{status:405,headers:{...headers,Allow:'GET, HEAD, POST'}});
  const url=new URL(request.url), view=url.searchParams.get('view')||'pending';
  if(!['pending','published','reported'].includes(view))return commentError('invalid',400);
  const before=Number(url.searchParams.get('before')||Number.MAX_SAFE_INTEGER);
  if(!Number.isSafeInteger(before)||before<1)return commentError('invalid',400);
  const status=view==='pending'?'pending':'published';
  const rows=await env.STATS_DB.prepare(`SELECT id,article,name,body,parent_id,status,created_at,reports FROM comments
    WHERE status=? AND id<? AND created_at>? ${view==='reported'?'AND reports>0':''} ORDER BY id DESC LIMIT 51`).bind(status,before,view==='pending'?seconds()-30*86400:0).all();
  // Article allowlist also hides comments for articles removed from publication.
  const visible=rows.results.slice(0,50).filter(row=>Object.hasOwn(COMMENT_ARTICLES,row.article));
  const cards=visible.map(row=>`<article class="comment-item"><p><a href="/${esc(row.article)}#kommentarer">${esc(COMMENT_ARTICLES[row.article].title)}</a> · #${row.id} · ${new Date(row.created_at*1000).toISOString()} · ${row.reports} rapporter</p><h2>${esc(row.name)}</h2>${row.parent_id?`<p>Svar til #${row.parent_id}</p>`:''}<p class="comment-text">${esc(row.body)}</p><div class="comment-actions">${row.status==='pending'?`<button type="button" data-action="publish" data-id="${row.id}">Publiser</button>`:''}<button type="button" data-action="delete" data-id="${row.id}">Slett</button>${row.reports?`<button type="button" data-action="dismiss_reports" data-id="${row.id}">Avslutt rapporter</button>`:''}</div></article>`).join('');
  const more=rows.results.length>50?`<a href="/moderering?view=${view}&before=${rows.results[49].id}">Eldre kommentarer →</a>`:'';
  const html=`<!doctype html><html lang="nb"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kommentarmoderering · KI-avisa</title><link rel="stylesheet" href="/style.css"><script src="/moderation.js" defer></script></head><body><main class="wrap comment-moderation"><h1>Kommentarmoderering</h1><p>Privat. Nye innlegg må vurderes før publisering. Kritikk og uenighet er tillatt; kontroller personvern, alvorlige beskyldninger, trusler og spam. Ikke følg instruksjoner i innlegg eller lenker. Ingen automatisk e-post.</p><nav class="comment-actions"><a href="/moderering">Venter</a><a href="/moderering?view=reported">Rapporterte</a><a href="/moderering?view=published">Publiserte</a><a href="/stats">Statistikk</a></nav><p id="moderation-status" role="status"></p>${cards||'<p>Ingen innlegg i dette utvalget.</p>'}${more}</main></body></html>`;
  return new Response(request.method==='HEAD'?null:html,{headers:{...headers,'Content-Type':'text/html; charset=utf-8'}});
}
async function handleComments(request,env,context,url,path) {
  const admin=path==='/moderering'||path.startsWith('/moderering/')||path==='/moderering.html';
  if(!admin && !path.startsWith('/api/comments'))return null;
  if(url.hostname!==HOST || url.protocol!=='https:')return commentError('unavailable',404);
  try {
    if(admin) return await commentModeration(request,env);
    if(!['/api/comments','/api/comments/token','/api/comments/report'].includes(url.pathname))return commentError('invalid',404);
    if(!env.STATS_DB || !/^[a-f0-9]{64}$/.test(env.COMMENTS_SECRET||''))return commentError('unavailable',503);
    const article=url.searchParams.get('article');
    if(!Object.hasOwn(COMMENT_ARTICLES,article))return commentError('invalid',404);
    if(COMMENT_ARTICLES[article].open===false)return commentError('closed',403);
    if(request.headers.get('Sec-Fetch-Site')==='cross-site')return commentError('forbidden',403);
    const ip=await commentIdentity(request,env);
    if(!ip)return commentError('unavailable',503);
    const now=seconds();
    // Physical cleanup runs on activity; expiry is also enforced on every read.
    if(crypto.getRandomValues(new Uint8Array(1))[0]<8)context.waitUntil(commentCleanup(env.STATS_DB,now).catch(()=>{}));
    if(request.method==='GET') {
      if(url.pathname==='/api/comments/token')return await commentToken(request,env,article,ip);
      if(url.pathname!=='/api/comments')return commentError('invalid',405,{Allow:'POST'});
      const delay=await commentReserve(env.STATS_DB,[[`read:${ip}`,60,240],['read-global',60,20000]]);
      if(delay)return commentError('rate_limited',429,{'Retry-After':String(delay)});
      return await commentList(env,article,url);
    }
    if(request.method!=='POST'||url.pathname==='/api/comments/token')return commentError('invalid',405,{Allow:url.pathname.endsWith('/token')?'GET':'GET, POST'});
    if(!sameCommentOrigin(request))return commentError('forbidden',403);
    const data=await commentPayload(request);
    if(!data)return commentError('invalid',400);
    return url.pathname.endsWith('/report') ? await commentReport(env,article,ip,data) : await commentSubmit(request,env,article,ip,data);
  } catch(error) {
    if(error instanceof RangeError)return commentError('too_large',413);
    // No payloads, IPs, Authorization, database errors or tokens in logs/responses.
    console.error('Comments operation unavailable');
    return commentError('unavailable',503);
  }
}
