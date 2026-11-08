// Exercise the Worker against real SQLite, including access checks and failure paths.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {DatabaseSync} from 'node:sqlite';
import {createHash} from 'node:crypto';

const code = readFileSync(new URL('./worker.mjs', import.meta.url), 'utf8')
  .replace('__PUBLIC_PATHS__', JSON.stringify(['/', '/om', '/example']));
const {default:worker} = await import('data:text/javascript;base64,' + Buffer.from(code).toString('base64'));
const db = new DatabaseSync(':memory:');
db.exec(readFileSync(new URL('./stats.sql', import.meta.url), 'utf8'));
const d1 = {
  prepare(sql) {
    let values = [];
    return {
      bind(...args) { values = args; return this; },
      async run() { return db.prepare(sql).run(...values); },
      async all() { return {results:db.prepare(sql).all(...values)}; },
    };
  },
  batch(statements) { return Promise.all(statements.map(statement => statement.all())); },
};
const password = 'admin:local-test-password';
const authorization = 'Basic ' + Buffer.from(password).toString('base64');
const env = {
  STATS_DB:d1,
  STATS_AUTH_SHA256:createHash('sha256').update(password).digest('hex'),
  ASSETS:{async fetch(request) {
    const path = new URL(request.url).pathname;
    if (path.endsWith('.mp4')) return new Response(new Uint8Array([0,1,2,3,4,5,6,7]), {headers:{'Content-Type':'video/mp4'}});
    return new Response('Public page', {status:path === '/missing' ? 404 : 200, headers:{'Content-Type':'text/html; charset=utf-8'}});
  }},
};
async function fetch(path, options = {}, bindings = env) {
  const pending = [];
  const response = await worker.fetch(new Request('https://ki-avisa.pages.dev' + path, options), bindings, {waitUntil(promise){pending.push(promise);}});
  await Promise.all(pending);
  return response;
}
const browser = {'Accept':'text/html', 'User-Agent':'Mozilla/5.0'};
const count = () => Number(db.prepare('SELECT COALESCE(SUM(views), 0) AS total FROM daily_views').get().total);

for (const path of ['/stats', '/stats/', '/stats.html', '/STATS', '/%73tats', '/stats/private?days=90']) {
  const denied = await fetch(path);
  assert.equal(denied.status,401,path);
  assert.match(denied.headers.get('WWW-Authenticate'),/^Basic /);
  assert.match(denied.headers.get('Cache-Control'),/no-store/);
  assert.match(denied.headers.get('X-Robots-Tag'),/noindex/);
  assert.doesNotMatch(await denied.text(),/Nettstedet i tall|Sidevisninger i dag/);
}
assert.equal((await fetch('/stats',{headers:{Authorization:'Basic !!!'}})).status,401);
assert.equal((await fetch('/stats',{headers:{Authorization:'Basic '+btoa('admin:wrong')}})).status,401);
assert.equal((await fetch('/stats',{}, {...env, STATS_AUTH_SHA256:undefined})).status,503);
assert.equal((await fetch('/stats',{}, {...env, STATS_DB:undefined})).status,503);
assert.equal((await fetch('/stats',{method:'POST',headers:{Authorization:authorization}})).status,405);
let page = await fetch('/stats',{headers:{Authorization:authorization}});
assert.equal(page.status,200);
assert.match(await page.text(),/Ingen sidevisninger ennå/);

await fetch('/?private=query-is-not-stored',{headers:{...browser,Referer:'https://www.google.com/search?q=private'}});
await fetch('/om.html',{headers:{...browser,Referer:'https://private-person.secret.example.org/private'}});
await fetch('/om',{headers:browser});
assert.equal(count(),3);
assert.deepEqual(db.prepare('SELECT source, SUM(views) AS views FROM daily_views GROUP BY source ORDER BY source').all().map(row=>({...row})),[
  {source:'Andre nettsteder',views:1},{source:'Direkte / ukjent',views:1},{source:'Google',views:1},
]);
assert.deepEqual(db.prepare('SELECT DISTINCT path FROM daily_views ORDER BY path').all().map(row=>row.path),['/','/om']);
for (const [path,options] of [
  ['/stats',{headers:{...browser,Authorization:authorization}}],
  ['/om',{method:'HEAD',headers:browser}],
  ['/om',{headers:{...browser,'User-Agent':'Googlebot'}}],
  ['/om',{headers:{...browser,Purpose:'prefetch'}}],
  ['/om',{headers:{...browser,'Sec-Purpose':'prerender'}}],
  ['/om',{headers:{...browser,Authorization:authorization}}],
  ['/missing',{headers:browser}], ['/style.css',{headers:browser}],
  ['/private-case',{headers:browser}], ['/om',{headers:{Accept:'application/json'}}],
]) await fetch(path,options);
assert.equal(count(),3,'Excluded requests must not inflate counts');
const pending = [];
await worker.fetch(new Request('https://preview.ki-avisa.pages.dev/',{headers:browser}),env,{waitUntil(p){pending.push(p);}});
await Promise.all(pending);
assert.equal(count(),3,'Preview traffic must not enter production counts');
page = await fetch('/stats?days=7',{headers:{Authorization:authorization}});
const html = await page.text();
assert.match(html,/href="\/stats\?days=7" aria-current="page"/);
assert.match(html,/Google/);
assert.doesNotMatch(html,/private-person|secret\.example|query-is-not-stored|<script|Set-Cookie/);
assert.equal((await fetch('/stats',{method:'HEAD',headers:{Authorization:authorization}})).body,null);
assert.equal((await fetch('/stats',{headers:{Authorization:authorization}}, {...env, STATS_DB:{batch(){throw Error('offline');}}})).status,503);
assert.equal((await fetch('/',{headers:browser}, {...env, STATS_DB:{prepare(){throw Error('offline');}}})).status,200,'Stats failure must not break public pages');

for (const [range,status,expected] of [['bytes=2-4',206,[2,3,4]],['bytes=-2',206,[6,7]],['bytes=20-',416,[]]]) {
  const response = await fetch('/media/example/video.mp4',{headers:{Range:range}});
  assert.equal(response.status,status);
  assert.deepEqual([...new Uint8Array(await response.arrayBuffer())],expected);
}
assert.equal((await fetch('/media/example/video.mp4',{method:'HEAD'})).body,null);
db.close();
console.log('Stats checks passed: authentication, fail-closed configuration, real SQL aggregation, exclusions, privacy, dashboard, database failures and video ranges.');
