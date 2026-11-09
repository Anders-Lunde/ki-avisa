// The builder replaces this array with the exact public HTML route allowlist.
const PUBLIC_PATHS = __PUBLIC_PATHS__;
const HOST = 'ki-avisa.pages.dev';
// __COMMENTS_MODULE__
const BOT = /bot|crawler|spider|slurp|headless|lighthouse|preview|facebookexternalhit|curl|wget|python|httpx|uptime|monitor/i;
const SOURCES = {
  'google.com': 'Google', 'google.no': 'Google', 'bing.com': 'Bing',
  'duckduckgo.com': 'DuckDuckGo', 'facebook.com': 'Facebook',
  'instagram.com': 'Instagram', 'linkedin.com': 'LinkedIn',
  'youtube.com': 'YouTube', 't.co': 'X', 'x.com': 'X', 'reddit.com': 'Reddit',
};
const PRIVATE_HEADERS = {
  'Cache-Control': 'private, no-store',
  'X-Robots-Tag': 'noindex, nofollow, noarchive',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'no-referrer',
  'Vary': 'Authorization',
  'Content-Security-Policy': "default-src 'none'; style-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
};
const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number = value => new Intl.NumberFormat('nb-NO').format(value);
const dayAt = date => new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Oslo' }).format(date);

async function authorized(request, expected) {
  const header = request.headers.get('Authorization') || '';
  if (!/^Basic [A-Za-z0-9+/]+=*$/i.test(header) || header.length > 1024) return false;
  let credentials;
  try { credentials = atob(header.slice(6)); } catch { return false; }
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(credentials));
  const actual = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
  let difference = actual.length ^ expected.length;
  for (let i = 0; i < actual.length; i++) difference |= actual.charCodeAt(i) ^ expected.charCodeAt(i);
  return difference === 0;
}

function sourceFor(request) {
  let hostname;
  try { hostname = new URL(request.headers.get('Referer')).hostname.toLowerCase(); }
  catch { return 'Direkte / ukjent'; }
  if (hostname === HOST) return 'Internt';
  for (const [domain, label] of Object.entries(SOURCES)) {
    if (hostname === domain || hostname.endsWith('.' + domain)) return label;
  }
  return 'Andre nettsteder'; // Never retain arbitrary hostnames or referral URLs.
}

function canonicalPath(path) {
  if (path === '/index' || path === '/index.html') return '/';
  return path.replace(/\.html$/, '');
}

function shouldCount(request, response, url) {
  return url.hostname === HOST && request.method === 'GET' &&
    !request.headers.has('Authorization') &&
    request.headers.get('Accept')?.includes('text/html') &&
    request.headers.get('User-Agent') && !BOT.test(request.headers.get('User-Agent')) &&
    !/prefetch|prerender/i.test((request.headers.get('Purpose') || '') + (request.headers.get('Sec-Purpose') || '')) &&
    PUBLIC_PATHS.includes(canonicalPath(url.pathname)) && response.status === 200 &&
    response.headers.get('Content-Type')?.includes('text/html');
}

async function recordView(request, env, path) {
  await env.STATS_DB.prepare(`INSERT INTO daily_views (day, path, source, views) VALUES (?, ?, ?, 1)
    ON CONFLICT (day, path, source) DO UPDATE SET views = views + 1`)
    .bind(dayAt(new Date()), path, sourceFor(request)).run();
}

function table(title, rows, name) {
  return `<section class="stats-panel"><h2>${title}</h2><table><thead><tr><th scope="col">${name}</th><th scope="col">Sidevisninger</th></tr></thead><tbody>${rows.length ? rows.map(row => `<tr><th scope="row">${esc(row.label)}</th><td>${number(row.views)}</td></tr>`).join('') : '<tr><td colspan="2">Ingen registrerte sidevisninger i perioden.</td></tr>'}</tbody></table></section>`;
}

async function dashboard(request, env) {
  if (!/^[a-f0-9]{64}$/.test(env.STATS_AUTH_SHA256 || '') || !env.STATS_DB) {
    return new Response('Statistikk er ikke konfigurert.', {status:503, headers:PRIVATE_HEADERS});
  }
  if (!await authorized(request, env.STATS_AUTH_SHA256)) {
    return new Response('Logg inn for å se statistikken.', {status:401, headers:{...PRIVATE_HEADERS, 'WWW-Authenticate':'Basic realm="KI-avisa statistikk", charset="UTF-8"'}});
  }
  if (!['GET', 'HEAD'].includes(request.method)) {
    return new Response(null, {status:405, headers:{...PRIVATE_HEADERS, Allow:'GET, HEAD'}});
  }
  const url = new URL(request.url);
  const chosen = Number(url.searchParams.get('days') || 30);
  const days = [7, 30, 90].includes(chosen) ? chosen : 30;
  const today = dayAt(new Date());
  const start = new Date(today + 'T12:00:00Z');
  start.setUTCDate(start.getUTCDate() - days + 1);
  const since = dayAt(start);
  let results;
  try {
    results = await env.STATS_DB.batch([
      env.STATS_DB.prepare('SELECT day AS label, SUM(views) AS views FROM daily_views WHERE day BETWEEN ? AND ? GROUP BY day ORDER BY day').bind(since, today),
      env.STATS_DB.prepare('SELECT path AS label, SUM(views) AS views FROM daily_views WHERE day BETWEEN ? AND ? GROUP BY path ORDER BY views DESC, path LIMIT 20').bind(since, today),
      env.STATS_DB.prepare('SELECT source AS label, SUM(views) AS views FROM daily_views WHERE day BETWEEN ? AND ? GROUP BY source ORDER BY views DESC, source').bind(since, today),
      env.STATS_DB.prepare('SELECT MIN(day) AS first_day FROM daily_views'),
    ]);
  } catch {
    return new Response('Statistikken er midlertidig utilgjengelig. Prøv igjen senere.', {status:503, headers:PRIVATE_HEADERS});
  }
  const [daily, pages, sources, first] = results.map(result => result.results);
  const byDay = new Map(daily.map(row => [row.label, Number(row.views)]));
  const total = daily.reduce((sum, row) => sum + Number(row.views), 0);
  const firstDay = first[0]?.first_day;
  const peak = Math.max(1, ...byDay.values());
  const bars = Array.from({length:days}, (_, index) => {
    const date = new Date(since + 'T12:00:00Z'); date.setUTCDate(date.getUTCDate() + index);
    const label = dayAt(date), views = byDay.get(label) || 0;
    // SVG attributes avoid inline CSS and work with the strict policy.
    return `<g><title>${label}: ${views} sidevisninger</title><rect x="${index * 12 + 1}" y="${100 - views / peak * 96}" width="9" height="${Math.max(views ? 1 : 0, views / peak * 96)}"/></g>`;
  }).join('');
  const body = `<!doctype html><html lang="nb"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Besøksstatistikk · KI-avisa</title><link rel="icon" href="/icon.svg"><link rel="stylesheet" href="/stats.css"></head><body><main class="stats-wrap"><header class="stats-header"><a class="stats-brand" href="/">ki-avisa<span>.</span></a><span class="stats-private">Privat · Kun for eier</span></header><p class="stats-eyebrow">Nettstedet i tall</p><div class="stats-title"><div><h1>Besøksstatistikk</h1><p>${since} – ${today} · Norsk tid</p></div><nav aria-label="Velg periode">${[7,30,90].map(value => `<a href="/stats?days=${value}"${value === days ? ' aria-current="page"' : ''}>${value} dager</a>`).join('')}</nav></div><section class="stats-cards" aria-label="Nøkkeltall"><div><span>Sidevisninger i perioden</span><strong>${number(total)}</strong></div><div><span>Sidevisninger i dag</span><strong>${number(byDay.get(today) || 0)}</strong></div><div><span>Daglig gjennomsnitt</span><strong>${number(Math.round(total / days * 10) / 10)}</strong></div></section><section class="stats-panel"><div class="stats-section-head"><h2>Dag for dag</h2><a href="${esc('/stats?days=' + days)}">Oppdater ↻</a></div>${total ? `<svg class="stats-chart" role="img" aria-label="Sidevisninger per dag. Tallene står i tabellen nedenfor." viewBox="0 0 ${days * 12} 104" preserveAspectRatio="none">${bars}</svg><div class="stats-axis"><span>${since}</span><span>${today}</span></div>` : '<p class="stats-empty">Ingen sidevisninger ennå. Tallene vises når noen åpner en offentlig side.</p>'}</section><div class="stats-columns">${table('Mest leste sider', pages, 'Side')}${table('Hvor trafikken kommer fra', sources, 'Kilde')}</div><details class="stats-panel"><summary>Daglige tall</summary>${table('Sidevisninger per dato', [...daily].reverse(), 'Dato')}</details><footer class="stats-notes"><h2>Hva tallene betyr</h2><p>En sidevisning er en vellykket sideinnlasting. Samme person kan telles flere ganger. Dette er ikke antall unike personer. Kjente roboter og forhåndslasting filtreres, men filtreringen er ikke fullstendig. Statistikkbesøk og forespørsler med innlogging telles ikke.</p><p>Kun summer per dato, offentlig side og kildegruppe lagres. Ingen informasjonskapsler, IP-adresser, besøks-ID-er eller komplette henvisningsadresser lagres i statistikken. Internt betyr navigasjon mellom egne sider; direkte / ukjent kan også skyldes at nettleseren skjuler kilden.</p><p>${firstDay ? `Første registrerte sidevisning: ${esc(firstDay)}.` : 'Innsamlingen begynner ved første offentlige sidevisning etter aktivering.'} Eldre trafikk kan ikke hentes tilbake. Tall kan bruke noen sekunder på å oppdateres.</p></footer></main></body></html>`;
  return new Response(request.method === 'HEAD' ? null : body, {headers:{...PRIVATE_HEADERS, 'Content-Type':'text/html; charset=utf-8'}});
}

// Keep the existing media byte-range support, including seeking and captions.
async function video(request, env, url) {
  const asset = await env.ASSETS.fetch(new Request(url.toString(), {method:request.method === 'HEAD' ? 'HEAD' : 'GET'}));
  if (asset.status !== 200) return asset;
  const headers = new Headers(asset.headers);
  headers.set('Accept-Ranges', 'bytes');
  headers.set('X-Content-Type-Options', 'nosniff');
  headers.set('Referrer-Policy', 'no-referrer');
  headers.set('Cache-Control', 'public, max-age=3600');
  const range = request.headers.get('Range');
  const match = range ? /^bytes=(\d*)-(\d*)$/.exec(range.trim()) : null;
  if (request.method === 'HEAD' || !match || (match[1] === '' && match[2] === '')) {
    return new Response(request.method === 'HEAD' ? null : asset.body, {status:200, headers});
  }
  const body = await asset.arrayBuffer(), size = body.byteLength;
  let start, end;
  if (match[1] === '') { start = Math.max(0, size - Number(match[2])); end = size - 1; }
  else { start = Number(match[1]); end = match[2] === '' ? size - 1 : Math.min(Number(match[2]), size - 1); }
  if (start >= size || end < start) {
    headers.set('Content-Range', `bytes */${size}`);
    return new Response(null, {status:416, headers});
  }
  headers.set('Content-Range', `bytes ${start}-${end}/${size}`);
  headers.set('Content-Length', String(end - start + 1));
  return new Response(body.slice(start, end + 1), {status:206, headers});
}

export default {
  async fetch(request, env, context) {
    const url = new URL(request.url);
    let path;
    try { path = decodeURIComponent(url.pathname).toLowerCase(); }
    catch { return new Response('Ugyldig adresse.', {status:400}); }
    const comments = await handleComments(request, env, context, url, path);
    if (comments) return comments;
    if (path === '/stats' || path.startsWith('/stats/') || path === '/stats.html') {
      return dashboard(request, env);
    }
    if (url.pathname.startsWith('/media/') && url.pathname.endsWith('.mp4')) return video(request, env, url);
    const response = await env.ASSETS.fetch(request);
    if (env.STATS_DB && shouldCount(request, response, url)) {
      context.waitUntil(recordView(request, env, canonicalPath(url.pathname)).catch(() => {
        console.error('Aggregate page-view write failed'); // No request metadata or credentials.
      }));
    }
    return response;
  },
};
