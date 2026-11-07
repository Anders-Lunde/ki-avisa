"""Build only explicitly supplied public article fields, never case directories."""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
BASE = 'https://ki-avisa.pages.dev/'
PROVIDERS = {'gemini': 'Google Gemini', 'speechify': 'Speechify'}
LISTENING = {'awaiting_human_listening': 'Ikke lyttevurdert ennå', 'selected_for_channel': 'Valgt som fast kanalstemme'}


def esc(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Expected text, got {type(value).__name__}")
    return html.escape(value, quote=True)


def url(value: str) -> str:
    if urlparse(value).scheme not in {"https", "http"} or not urlparse(value).netloc:
        raise ValueError(f"Invalid public source URL: {value!r}")
    return esc(value)


def page(title: str, body: str, preview: bool, voices: bool, current: str = '', article: dict | None = None) -> str:
    banner = '<div class="preview"><div class="wrap"><span>Privat prøveutgave</span><span>Arbeidstittel · Under utvikling</span></div></div>' if preview else ''
    links = [('index.html', 'Forsiden'), ('index.html#saker', 'Saker'), ('om.html', 'Slik jobber vi')]
    def nav_link(href: str, label: str) -> str:
        active = ' aria-current="page"' if current == href else ''
        return f'<a href="{href}"{active}>{label}</a>'
    navigation = ''.join(nav_link(href, label) for href, label in links)
    owner = ''
    if preview:
        owner = '<div class="owner-nav"><span>For eier</span>' + nav_link('redaksjonen.html', 'Redaksjonen')
        if voices:
            owner += nav_link('stemmer.html', 'Stemmeprøver')
        owner += '</div>'
    script = '<script src="voices.js" defer></script>' if current == 'stemmer.html' else ''
    description = article['deck'] if article else ('Slik arbeider KI-avisa med kilder, faktakontroll, KI og rettelser. Ansvarlig redaktør: Anders Lunde.' if current == 'om.html' else 'KI-avisa undersøker makt, følger offentlige penger og forklarer samfunnsdebatten, med synlige kilder og rettelser.')
    description = ' '.join(description.split())[:160]
    canonical = BASE + ('' if current in {'', 'index.html'} else current.removesuffix('.html'))
    schema = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'NewsMediaOrganization', '@id': BASE + '#organization', 'name': 'KI-avisa', 'url': BASE, 'logo': BASE + 'apple-touch-icon.png', 'email': 'lunde.anders@gmail.com'},
        {'@type': 'WebSite', '@id': BASE + '#website', 'name': 'KI-avisa', 'url': BASE, 'inLanguage': 'nb-NO', 'publisher': {'@id': BASE + '#organization'}},
        {'@type': 'WebPage', '@id': canonical, 'url': canonical, 'name': title + ' · KI-avisa', 'description': description, 'inLanguage': 'nb-NO', 'isPartOf': {'@id': BASE + '#website'}},
    ]}
    if article:
        schema['@graph'].append({'@type': 'NewsArticle' if article['kind'] != 'Metode' else 'Article', 'headline': article['title'], 'description': description, 'mainEntityOfPage': canonical, 'datePublished': article['date'], 'author': {'@type': 'Organization', 'name': 'KI-avisas KI-redaksjon', 'url': BASE + 'om#ki'}, 'publisher': {'@id': BASE + '#organization'}, 'inLanguage': 'nb-NO'})
    seo = '<meta name="robots" content="noindex,nofollow">' if preview else '<meta name="robots" content="noindex,follow">' if current == '404.html' else (
        f'<link rel="canonical" href="{canonical}"><meta property="og:type" content="{"article" if article else "website"}"><meta property="og:site_name" content="KI-avisa"><meta property="og:locale" content="nb_NO"><meta property="og:url" content="{canonical}"><meta property="og:title" content="{esc(title)} · KI-avisa"><meta property="og:description" content="{esc(description)}"><meta property="og:image" content="{BASE}social.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="KI-avisa. Makt. Penger. Dokumentasjon."><meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>')
    return f'''<!doctype html><html lang="nb"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><title>{esc(title)} · KI-avisa</title><meta name="description" content="{esc(description)}">{seo}<meta name="theme-color" content="#23312f"><link rel="icon" href="/icon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.png" type="image/png" sizes="48x48"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180"><link rel="stylesheet" href="style.css">{script}</head><body><a class="skip" href="#main">Hopp til innhold</a>{banner}<div class="wrap"><header class="site-header"><div class="masthead"><a class="brand" href="index.html" aria-label="KI-avisa, forsiden">ki-avisa<i>.</i></a><p>Vi undersøker makten,<br>følger pengene og forklarer.</p><span class="edition">Undersøkende<br>journalistikk</span></div><nav class="nav" aria-label="Hovedmeny"><div class="reader-nav">{navigation}</div>{owner}</nav></header><main id="main">{body}</main><footer class="footer"><a class="footer-brand" href="index.html">ki-avisa.</a><p>Ansvarlig redaktør og eier: Anders Lunde.<br><a href="mailto:lunde.anders@gmail.com">lunde.anders@gmail.com</a></p><div><a href="om.html#metode">Metode og ansvar</a><a href="om.html#rettelser">Kontakt og rettelser</a></div></footer></div></body></html>'''


def draft_badge(article: dict) -> str:
    return ' <span class="draft">Utkast</span>' if article['status'] == 'draft' else ''


def sourced_text(value: str, source_count: int, references: dict[int, int] | None = None) -> str:
    """Link plain-text [1] references to the article's existing source list."""
    def reference(match: re.Match) -> str:
        number = int(match.group(1))
        if not 1 <= number <= source_count:
            raise ValueError(f'Source reference [{number}] has no source in this article')
        anchor = ''
        if references is not None:
            references[number] = references.get(number, 0) + 1
            anchor = f' id="henvisning-{number}-{references[number]}"'
        return f'<a class="source-ref"{anchor} href="#kilde-{number}" aria-label="Kilde {number}">[{number}]</a>'
    return re.sub(r'\[(\d+)\]', reference, esc(value))


def valid_summary(article: dict) -> bool:
    """A published article needs 2–5 short summary points (owner's requirement, 6.11.2026)."""
    points = article.get('summary')
    return (isinstance(points, list) and 2 <= len(points) <= 5
            and all(isinstance(p, str) and 0 < len(p.strip()) <= 260 for p in points))


def summary_html(article: dict) -> str:
    points = article.get('summary')
    if not isinstance(points, list) or not points:
        return ''
    items = ''.join(f'<li>{esc(p)}</li>' for p in points)
    return (f'<aside class="ai-summary" aria-label="Kort oppsummert"><p class="ai-summary-label">Kort oppsummert</p>'
            f'<ul>{items}</ul><p class="ai-summary-note">Sammendraget er laget med KI og kontrollert mot artikkelen.</p></aside>')


SAFE_FILE = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\.(?:svg|jpg|jpeg|png|webp|mp4|vtt)')


def film_files(article: dict) -> list[str]:
    film = article.get('film') or {}
    return [f for f in (film.get('file'), film.get('captions'), film.get('poster')) if f]


def film_html(article: dict) -> str:
    """Self-hosted film (CSP media-src 'self'), with captions and visible credits."""
    film = article.get('film')
    if not film:
        return ''
    for name in film_files(article):
        if not SAFE_FILE.fullmatch(name):
            raise ValueError(f'Invalid film file name: {name!r}')
    if not (film.get('file', '').endswith('.mp4') and film.get('caption') and film.get('credit')):
        raise ValueError('Film needs an .mp4 file, caption and credit')
    base = f'media/{article["slug"]}/'
    poster = f' poster="{base}{film["poster"]}"' if film.get('poster') else ''
    track = f'<track kind="captions" srclang="nb" label="Norsk" src="{base}{film["captions"]}" default>' if film.get('captions') else ''
    return (f'<figure class="film"><video controls preload="metadata" playsinline{poster} src="{base}{film["file"]}">{track}'
            f'Nettleseren din kan ikke vise videoen.</video><figcaption>{esc(film["caption"])}'
            f'<span class="credit">{esc(film["credit"])}</span></figcaption></figure>')


def figure_html(figure: dict) -> str:
    """Inline one of our own SVG graphics. The site CSP forbids inline styles and scripts."""
    name = figure.get('file', '')
    if not SAFE_FILE.fullmatch(name) or not name.endswith('.svg'):
        raise ValueError(f'Invalid graphic file name: {name!r}')
    svg = (HERE / 'graphics' / name).read_text(encoding='utf-8')
    if re.search(r'<script|<style|\sstyle=|\son[a-z]+=|<foreignObject|(?:xlink:)?href=|<image', svg, re.I):
        raise ValueError(f'Graphic contains scripts, styles, links or images: {name}')
    svg = re.sub(r'^\s*<\?xml[^>]*\?>', '', svg).strip()
    if not (figure.get('alt') and figure.get('caption')):
        raise ValueError(f'Graphic needs alt text and caption: {name}')
    return (f'<figure class="graphic"><div class="graphic-svg" role="img" aria-label="{esc(figure["alt"])}">{svg}</div>'
            f'<figcaption>{esc(figure["caption"])}</figcaption></figure>')


def gallery_html(article: dict) -> str:
    items = article.get('gallery') or []
    if not items:
        return ''
    cells = ''
    for item in items:
        name = item.get('file', '')
        if not SAFE_FILE.fullmatch(name) or name.endswith('.svg'):
            raise ValueError(f'Invalid gallery file name: {name!r}')
        if not all(item.get(k) for k in ('alt', 'caption', 'credit', 'license', 'source_url')):
            raise ValueError(f'Gallery image lacks alt, caption, credit, license or source: {name}')
        licence = esc(item['license'])
        if item.get('license_url'):
            licence = f'<a href="{url(item["license_url"])}" rel="noreferrer license">{licence}</a>'
        cells += (f'<figure><img src="media/{article["slug"]}/{name}" alt="{esc(item["alt"])}" loading="lazy" decoding="async">'
                  f'<figcaption>{esc(item["caption"])}<span class="credit">Foto: {esc(item["credit"])} · {licence} · '
                  f'<a href="{url(item["source_url"])}" rel="noreferrer">kilde</a></span></figcaption></figure>')
    return f'<section id="bilder" class="gallery"><p class="eyebrow">Bilder</p><h2>{esc(article.get('gallery_heading') or 'Bilder til saken')}</h2><div class="gallery-grid">{cells}</div></section>'


def article_html(article: dict) -> str:
    references: dict[int, int] = {}
    content = ''.join(f'<section id="avsnitt-{i}"><h2>{esc(s["heading"])}</h2>' + ''.join(f'<p>{sourced_text(p, len(article["sources"]), references)}</p>' for p in s['paragraphs']) + (figure_html(s['figure']) if s.get('figure') else '') + '</section>' for i, s in enumerate(article['sections'], 1))
    sources = ''
    for number, source in enumerate(article['sources'], 1):
        backlinks = ''.join(f'<a href="#henvisning-{number}-{i}" aria-label="Tilbake til henvisning {i} til kilde {number}">↩ {i}</a>' for i in range(1, references.get(number, 0) + 1))
        backlinks = f'<span class="backlinks">Til teksten {backlinks}</span>' if backlinks else ''
        sources += f'<li id="kilde-{number}"><a href="{url(source["url"])}" rel="noreferrer">{esc(source["title"])}</a><span class="source-domain">{esc(urlparse(source["url"]).netloc.removeprefix("www."))}</span>{backlinks}</li>'
    updates = ''.join(f'<li>{esc(item)}</li>' for item in article.get('updates', []))
    updates = f'<ol class="updates">{updates}</ol>' if updates else '<p>Ingen endringer er registrert i denne teksten.</p>'
    contents = ''.join(f'<li><a href="#avsnitt-{i}">{esc(s["heading"])}</a></li>' for i, s in enumerate(article['sections'], 1))
    notice = '<p class="draft-notice"><strong>Utkast til metodebeskrivelse.</strong> Viser redaksjonens arbeidsmåte; dette er ikke en publisert undersøkelse.</p>' if article['status'] == 'draft' and article['kind'] == 'Metode' else '<p class="draft-notice"><strong>Upublisert utkast.</strong> Innholdet er under arbeid.</p>' if article['status'] == 'draft' else ''
    video = ''
    if article.get('youtube_id'):
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}', article['youtube_id']):
            raise ValueError('Invalid verified YouTube video ID')
        video = f'<iframe src="https://www.youtube-nocookie.com/embed/{article["youtube_id"]}" title="Se filmen" loading="lazy" allowfullscreen></iframe>'
    return f'<article class="reading"><header class="article-head"><a class="back" href="index.html">← Forsiden</a><p class="eyebrow">{esc(article["kind"])}</p><h1>{esc(article["title"])}</h1><p class="deck">{esc(article["deck"])}</p><div class="byline"><span>Av KI-avisas KI-redaksjon</span><time datetime="{esc(article["date"])}">{esc(article["date"])}</time>{draft_badge(article)}</div>{notice}{summary_html(article)}<nav class="evidence-nav" aria-label="Dokumentasjon"><a href="#kilder">{len(article["sources"])} {"kilde" if len(article["sources"]) == 1 else "kilder"} ↓</a><a href="#endringer">Endringer og rettelser ↓</a><a href="om.html#ki">Om KI-redaksjonen ↗</a></nav></header><div class="reading-layout"><nav class="contents" aria-label="I denne teksten"><p>I denne teksten</p><ol>{contents}</ol><a href="#kilder">Kilder</a><a href="#endringer">Endringer og rettelser</a></nav><div class="article-body">{video}{film_html(article)}{content}{gallery_html(article)}<section id="kilder" class="sources"><p class="eyebrow">Dokumentasjon</p><h2>Kilder til teksten</h2><ol>{sources}</ol></section><section id="endringer" class="changes"><h2>Endringer og rettelser</h2>{updates}<a href="om.html#rettelser">Slik håndterer vi rettelser →</a></section><a class="back-to-top" href="#main">Til toppen ↑</a></div></div></article>'


def story_rows(articles: list[dict]) -> str:
    return ''.join(f'<a class="story" href="{a["slug"]}.html"><div class="story-label"><span class="type">{esc(a["kind"])}</span>{draft_badge(a)}</div><div><h3>{esc(a["title"])}</h3><p>{esc(a["deck"])}</p><span class="story-meta">{esc(a["date"])} · {len(a["sources"])} {"kilde" if len(a["sources"]) == 1 else "kilder"}</span></div><span class="arrow" aria-hidden="true">↗</span></a>' for a in sorted(articles, key=lambda a: a['date'], reverse=True))


def home_html(articles: list[dict], preview: bool) -> str:
    published = [a for a in articles if a['status'] == 'published' and a['kind'] != 'Metode']
    featured = max(published, key=lambda a: a['date']) if published else None
    if featured:
        lead = f'<p class="eyebrow">{esc(featured["kind"])}</p><h1>{esc(featured["title"])}</h1><p class="deck">{esc(featured["deck"])}</p><a class="read" href="{featured["slug"]}.html">Les saken <span aria-hidden="true">↗</span></a>'
    else:
        # Before a story is actually published, the lead states the promise
        # instead of promoting a draft or a how-to as the top story.
        lead = '<p class="eyebrow">Makt. Penger. Dokumentasjon.</p><h1>Hvem bestemmer, og hvor går <em>pengene?</em></h1><p class="deck">Vi undersøker maktmisbruk, følger offentlige penger og forklarer debattene som angår deg. Hva skjedde, hvem tok beslutningen, og hvilke forklaringer holder?</p><p class="lead-format">Journalistikk i film og selvstendige artikler. Med kildene, svarene og det som fortsatt er uavklart.</p><a class="read" href="om.html">Slik jobber KI-redaksjonen <span aria-hidden="true">↗</span></a>'
    illustration = '<div class="art" role="img" aria-label="Illustrasjon: dokumenter med et funn markert med rød sirkel. Ikke et faktisk kildedokument."><span class="art-label">Illustrasjon · Se etter. Spør videre.</span><div class="sheet back"><div class="rule dark"></div><div class="rule"></div><div class="rule"></div></div><div class="sheet front"><span class="doc-label">DOKUMENTASJON</span><div class="rule short"></div><div class="rule dark"></div><div class="rule"></div><div class="rule"></div><div class="rule short"></div><div class="circle"></div></div><span class="art-caption">Det som holder, skal frem.</span></div>'
    rows = story_rows(published)
    other = [a for a in articles if a not in published]
    newsroom = f'<section class="method-stories"><div class="section-head"><h2>Fra redaksjonen</h2><span>{"Metode og utkast · Upubliserte tekster er merket" if preview else "Arbeidsmåte og metode"}</span></div>{story_rows(other)}</section>' if other else ''
    status = '<p class="site-state"><span class="status-dot" aria-hidden="true"></span><strong>Prøveutgave.</strong> Ingen undersøkelser er publisert ennå.' if not published else '<p class="site-state"><strong>Dokumentasjonen følger saken.</strong>'
    status += ' <a href="redaksjonen.html">Se redaksjonens status →</a></p>' if preview else '</p>'
    empty = '<div class="empty-state"><span class="empty-symbol" aria-hidden="true">—</span><div><h3>Ingen ferdige saker å lese ennå.</h3><p>KI-avisa er under utvikling. Her vil du finne undersøkelsene og forklaringene, med dokumentasjon og synlige rettelser.</p></div></div>'
    pillars = (
        ('Gravende', 'Korrupsjon, lovbrudd og maktmisbruk', 'Hvem tok beslutningen, hvilke interesser møttes, og hva ble konsekvensene? Vi følger dokumentene og prøver forklaringene før vi konkluderer.'),
        ('Følg pengene', 'Sløsing og offentlige penger', 'Hva ble vedtatt, hva ble brukt, og hvem har ansvaret når regningen vokser? Store avvik kan ha gode forklaringer. Vi undersøker begge deler.'),
        ('Forklart', 'Debattene som angår deg', 'Strømpris, oljepenger, formuesskatt, energi og innvandring: hva vet vi, hva er usikkert, og hvilke valg står igjen? Forklaringer som gjør det lettere å vurdere påstandene selv.'),
    )
    pillar_html = ''.join(f'<div class="pillar"><p class="eyebrow">{label}</p><h3>{title}</h3><p>{text}</p></div>' for label, title, text in pillars)
    return (
        f'<section class="lead"><div>{lead}</div>{illustration}</section>{status}'
        f'<section id="saker"><div class="section-head"><h2>Saker</h2><span>Undersøkelser og forklaringer</span></div>{rows or empty}</section>'
        f'<section class="pillars" aria-labelledby="dekker"><h2 id="dekker" class="visually-hidden">Dette dekker vi</h2>{pillar_html}</section>{newsroom}'
        '<section class="bottom"><div><p class="eyebrow">Samme krav til alle</p><h2>Partipolitisk nøytral.<br>Ikke nøytral overfor fakta.</h2><p>Vi stiller de samme spørsmålene til alle partier og alle med makt. Hvor mye plass en sak får, avgjøres av hvor viktig den er og hva dokumentene viser, ikke av hvem den handler om.</p></div>'
        '<div class="notice"><p class="eyebrow">Metoden vår</p><h2>Også det som taler imot.</h2><p>En god undersøkelse leter etter mer enn støtte for den første mistanken. Vi viser kildene, prøver alternative forklaringer og retter feil synlig.</p><a class="read" href="om.html">Slik jobber vi <span aria-hidden="true">↗</span></a></div></section>'
    )


ABOUT = '<article class="article about"><p class="eyebrow">Slik jobber vi</p><h1>Spørsmål som fortjener ordentlige svar.</h1>\n<p class="deck">KI-avisa er et norsk journalistikkprosjekt. KI-redaksjonen undersøker sakene og lager journalistikken. Anders Lunde er ansvarlig redaktør og eier. Han eier også KI-partiet, et separat prosjekt for politikkutvikling. KI-avisa bruker samme journalistiske beviskrav overfor alle aktører, også KI-partiet.</p>\n<nav class="evidence-nav" aria-label="Om redaksjonen"><a href="#metode">Metode ↓</a><a href="#ki">KI og ansvar ↓</a><a href="#rettelser">Kontakt og rettelser ↓</a><a href="#personvern">Personvern ↓</a></nav>\n<h2>Hva vi dekker</h2><p>Gravende saker om korrupsjon, lovbrudd, habilitet og sløsing med offentlige penger. Saker om makt, politi og rettsvesen der dokumentene kan etterprøves. Og forklaringer av debattene som preger norsk politikk, som strømpris, oljepenger, formuesskatt, energi og innvandring.</p>\n<h2>Samme metode, uansett parti</h2><p>Alle partier og personer møter samme dokumentasjonskrav. Hvor mye plass en sak får, avgjøres av betydning og belegg. I forklaringssaker skiller vi mellom hva dataene viser, hvilke forklaringer som har støtte, og hvilke valg som fortsatt er politiske.</p>\n<h2 id="metode">En metode du kan etterprøve</h2><p>Vi kontrollerer originalkilder, prøver alternative forklaringer og skiller mellom det som er dokumentert, det som er påstått og det som er vår vurdering. Personer, virksomheter og offentlige organer som får sterke faktiske beskyldninger mot seg, får en reell mulighet til å svare før saken publiseres.</p><p>Ved sentrale påstander skal artiklene vise til den konkrete kilden, oppgi perioden tallene gjelder og forklare viktige beregninger og begrensninger. Vi krediterer andre mediers arbeid. Artiklene kan leses uten en film.</p>\n<h2 id="ki">KI-journalister. Åpent ansvar.</h2><p>KI-redaksjonen finner og avgrenser saker, undersøker dokumenter og data, sender innsynskrav, kontakter berørte og følger opp svar. Den skriver artiklene og utarbeider filmene. KI kan ta feil, også med kilder og tall. Derfor skal sentrale påstander kontrolleres mot originalen, og feil rettes synlig.</p><p>Anders Lunde er ansvarlig redaktør. KI-redaktøren utfører og dokumenterer redaksjonelt arbeid innenfor mandatet; den er ikke en fysisk person og erstatter ikke den ansvarlige redaktøren. Eieren har bekreftet redaktør og offentlig kontakt 4. november 2026.</p><p>Vi opplyser om KI-avsender i journalistiske henvendelser og bruker syntetisk fortellerstemme. Illustrasjoner merkes og er aldri dokumentasjon av hva noen faktisk har gjort. Private kildearkiver og korrespondanse publiseres ikke.</p>\n<h2 id="rettelser">Kontakt og synlige rettelser</h2><p>Ansvarlig redaktør og eier: <strong>Anders Lunde</strong>.<br>Offentlig kontakt: <a href="mailto:lunde.anders@gmail.com">lunde.anders@gmail.com</a>.</p><p>Oppgi hvilken side og opplysning en rettelse gjelder. Meningsbærende endringer skal stå i artikkelens endringshistorikk, med dato og forklaring. Vesentlige feil følges opp også i eventuelle filmer.</p><p>Vanlig e-post er ikke en sikker tipskanal. Avtal en egnet kontaktmåte før du sender fortrolige eller sensitive opplysninger.</p>\n<h2>Felles eier med KI-partiet</h2><p>Anders Lunde eier både KI-avisa og <a href="https://ki-partiet.pages.dev/">KI-partiet</a>. KI-partiet utvikler politikk; KI-avisa driver journalistikk etter eget mandat. Felles eierskap er en binding leserne skal kjenne til. Journalistiske konklusjoner skal ikke tilpasses det politiske prosjektets forslag. Private kilder og korrespondanse overføres ikke til KI-partiet.</p>\n<h2 id="personvern">Personvern på nettstedet</h2><p>Nettstedet bruker ingen analyseverktøy, sporingsskript, kontaktskjemaer eller eksterne skrifter. Cloudflare leverer sidene og kan behandle tekniske tilkoblingsopplysninger for drift og sikkerhet. E-postlenker åpner e-postprogrammet ditt. Dersom en artikkel senere inneholder en YouTube-film, kan avspilling gi YouTube opplysninger om tilkoblingen din.</p>\n<h2>Et nettsted under utvikling</h2><p>Bare ferdig publiserte artikler med dokumentert redaksjonell beslutning skal vises her. Utkast, stemmeprøver og interne arbeidsoversikter er ikke en del av det offentlige nettstedet.</p>\n<div class="sources"><h2>Redaksjonelt utgangspunkt</h2><p>Metoden bygger på <a href="https://www.presse.no/vaer-varsom-plakaten">Vær Varsom-plakaten hos Norsk Presseforbund</a>. Det innebærer ingen påstand om medlemskap, PFU-tilknytning eller presseakkreditering.</p></div></article>'


def seconds(value: float) -> str:
    return f'{value:.1f}'.replace('.', ',') + ' s'


def newsroom_html(articles: list[dict], voice_count: int, voice_choice: dict | None = None) -> str:
    """Owner-only view: editorial export counts and an explicitly prepared snapshot."""
    published = len([a for a in articles if a['status'] == 'published' and a['kind'] != 'Metode'])
    drafts = len([a for a in articles if a['status'] == 'draft'])
    snapshot_path = HERE / 'preview' / 'activity.json'
    snapshot = '<p class="empty-note">Saksaktivitet er ikke koblet til denne visningen. Antall henvendelser, svar og saker under arbeid er derfor ikke oppgitt.</p>'
    priorities = ''
    schedule = ''
    snapshot_date = ''
    if snapshot_path.exists():
        data = json.loads(snapshot_path.read_text(encoding='utf-8'))
        stamp = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            raise ValueError('Newsroom snapshot updated_at must include its timezone')
        updated = stamp.astimezone(timezone.utc).strftime('%d.%m.%Y kl. %H:%M UTC')
        items = ''.join(f'<div class="activity-item"><dt>{esc(item["label"])}</dt><dd><strong>{esc(item["value"])}</strong><p>{esc(item["detail"])}</p></dd></div>' for item in data['items'])
        notes = ''.join(f'<li>{esc(note)}</li>' for note in data['notes'])
        snapshot_date = f'<p class="snapshot-date">Sammenstilt <time datetime="{esc(data["updated_at"])}">{updated}</time>. Datert øyeblikksbilde, ikke sanntid.</p>'
        if data.get('priorities'):
            cards = ''.join(f'<article class="priority"><p class="eyebrow">{esc(item["label"])}</p><h3>{esc(item["value"])}</h3><p>{esc(item["detail"])}</p></article>' for item in data['priorities'])
            priorities = f'<section aria-labelledby="neste-arbeid"><div class="section-head"><h2 id="neste-arbeid">Redaksjonens neste arbeid</h2><span>Planlagt · Ikke utført</span></div><div class="priority-grid">{cards}</div></section>'
        if data.get('schedule'):
            # Configured recurring work and its stated status; not evidence that a run succeeded.
            rows = ''.join(f'<div class="activity-item"><dt>{esc(item["label"])}</dt><dd><strong>{esc(item["value"])}</strong><p>{esc(item["detail"])}</p></dd></div>' for item in data['schedule'])
            schedule = f'<section aria-labelledby="drift"><div class="section-head"><h2 id="drift">Fast drift</h2><span>Konfigurert · Ikke bevis på vellykket kjøring</span></div><dl class="activity-grid">{rows}</dl></section>'
        snapshot = f'<dl class="activity-grid">{items}</dl><ul class="snapshot-notes">{notes}</ul>'
    voices = f'<a class="read" href="stemmer.html">Sammenlign {voice_count} stemmeprøver <span aria-hidden="true">→</span></a>' if voice_count else '<p>Ingen stemmeprøver er med i denne visningen.</p>'
    voice_summary = (f'<h3>{esc(voice_choice.get("display_name") or voice_choice["voice"])}</h3><p>Valgt som fast fortellerstemme av eieren. {esc(PROVIDERS[voice_choice["provider"]])} · <code>{esc(voice_choice["model"])}</code>. Den journalistiske retningen og batchmodus er lagret i kanaloppsettet.</p><a class="read" href="stemmer.html#{voice_choice["id"]}-name">Hør den valgte stemmen →</a>' if voice_choice else f'<h3>{voice_count} prøver å lytte til</h3><p>Ingen fast kanalstemme er registrert i denne visningen.</p>')
    return (
        '<section class="workspace-head"><p class="eyebrow">Privat · For eier</p><h1>Redaksjonen.</h1><p class="deck">Hva skal undersøkes, hva er faktisk gjort, og hvilke valg gjenstår før lansering?</p></section>'
        f'{snapshot_date}<nav class="desk-nav" aria-label="Redaksjonsoversikt">' + ('<a href="#neste-arbeid">Neste arbeid ↓</a>' if priorities else '') + '<a href="#aktivitet">Dokumentert aktivitet ↓</a>' + ('<a href="#drift">Fast drift ↓</a>' if schedule else '') + '<a href="#eiervalg">Valg før lansering ↓</a></nav>'
        f'{priorities}<section aria-labelledby="aktivitet"><div class="section-head"><h2 id="aktivitet">Dokumentert aktivitet</h2><span>Innhenting er ikke en ferdig sak</span></div>{snapshot}</section>{schedule}'
        f'<section class="site-inventory"><p><strong>{published} publiserte saker · {drafts} utkast på nettstedet.</strong> Metodebeskrivelser regnes ikke som publiserte undersøkelser.</p><a href="index.html#saker">Åpne forsiden →</a></section>'
        '<section aria-labelledby="eiervalg"><div class="section-head"><h2 id="eiervalg">Valg før lansering</h2><span>For eier · Research kan fortsette</span></div><p class="owner-intro">Eieren avklarer rammene for utgivelse. Redaksjonen utfører kildevalg, kontakt, undersøkelser og vurdering av hver sak.</p>'
        f'<div class="export-state"><div><p class="eyebrow">Navn, ansvar og kontakt</p><h3>Hvem er redaktør etter loven?</h3><p>Medieansvarsloven krever at en fysisk person er redaktør, med navn og kontaktopplysninger synlige for publikum, og redaktøren har et særlig straffe- og erstatningsansvar (<a href="https://www.stortinget.no/globalassets/pdf/lovvedtak/2019-2020/vedtak-201920-088.pdf" rel="noreferrer">lovteksten</a>). Eieren avgjør hvem det er og hvilken kontroll vedkommende beholder, i tillegg til endelig navn, kontaktvei og YouTube-identitet. Det er et ansvarsvalg før lansering, ikke godkjenning av enkeltsaker. Prøveutgaven er privat, og research fortsetter.</p><a class="read" href="om.html#rettelser">Se dagens kontaktstatus →</a></div><div><p class="eyebrow">Fortellerstemme</p>{voice_summary}{voices}</div></div></section>'
        '<section class="responsibility"><p class="eyebrow">Slik er ansvaret fordelt</p><div><h2>Redaksjonen gjør journalistarbeidet.</h2><p>KI-redaksjonen velger saker, innhenter dokumenter, sender henvendelser og følger opp svar. KI-redaktøren dokumenterer den redaksjonelle beslutningen. Eieren fastsetter mandatet og er ikke et obligatorisk godkjenningsledd i hver sak.</p><a href="om.html#ki">Les om KI og ansvar →</a></div></section>'
    )


def auditions(root: Path, output: Path) -> tuple[str, dict | None]:
    """Render every registered audition sample; fail if any registered sample is incomplete."""
    registry = json.loads((root / 'samples.json').read_text(encoding='utf-8'))
    result = json.loads((root / 'results.json').read_text(encoding='utf-8'))
    if result.get('errors'):
        raise ValueError(f'Audition run reported errors; inspect {root / "results.json"}')
    ids = [s['id'] for s in registry]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate sample IDs in samples.json')
    done = {s['id']: s for s in result['samples']}
    if set(done) - set(ids):
        raise ValueError(f'results.json has unregistered samples: {sorted(set(done) - set(ids))}')
    missing = [i for i in ids if i not in done]
    if missing:
        raise ValueError(f'Registered samples without completed audio: {missing}; finish run.py or remove them from samples.json')
    groups: dict[str, list[dict]] = {}
    for registered in registry:
        sample = {**done[registered['id']], **registered}
        if not re.fullmatch(r'[a-z0-9_]+', sample['id']):
            raise ValueError(f'Invalid sample ID {sample["id"]!r}')
        provider = sample.get('provider') or ('gemini' if sample['model'].startswith('gemini') else '')
        if provider not in PROVIDERS:
            raise ValueError(f'Sample {sample["id"]} needs a known provider (got {provider!r})')
        source = (root / sample['audio']).resolve()
        source.relative_to(root.resolve())
        if not source.is_file():
            raise ValueError(f'Missing audio for {sample["id"]}: {source}')
        shutil.copyfile(source, output / 'audio' / f'{sample["id"]}.wav')
        groups.setdefault(provider, []).append(sample)
    choices = [s for samples in groups.values() for s in samples if s.get('listening_status') == 'selected_for_channel']
    if len(choices) > 1:
        raise ValueError('More than one permanent channel voice is selected')
    voice_choice = choices[0] if choices else None
    sections = ''
    for provider, samples in groups.items():
        cards = ''
        for s in samples:
            sid, name = s['id'], s.get('display_name') or s['voice']
            status = LISTENING.get(s.get('listening_status', ''), s.get('listening_status', ''))
            mode = ' · Batch' if s.get('execution_mode') == 'batch' else ''
            cards += (
                f'<li class="audition" id="{sid}" data-provider="{provider}" data-sample="{sid}" data-name="{esc(name)}"><div class="audition-heading"><h3 id="{sid}-name">{esc(name)}</h3><button type="button" class="compare-pick" data-enhance hidden data-compare="{sid}" aria-pressed="false" aria-label="Velg {esc(name)}, {esc(sid)}, til sammenligning">Sammenlign</button></div>'
                f'<p class="meta" id="{sid}-meta">{esc(PROVIDERS[provider])} · <code>{esc(s["model"])}</code> · {seconds(s["seconds"])}{mode}'
                f'{" · " + esc(status) if status else ""} · prøve-ID <code>{esc(sid)}</code></p>'
                f'<audio controls preload="none" src="audio/{sid}.wav" aria-labelledby="{sid}-name {sid}-meta">'
                f'<a href="audio/{sid}.wav">Last ned {esc(name)} (WAV)</a></audio><p class="audio-error" role="alert" hidden>Lydfilen kunne ikke spilles i nettleseren. Prøv nedlastingslenken.</p>'
                f'<a class="download" href="audio/{sid}.wav" download>Last ned WAV</a><a class="sample-link" href="#{sid}" aria-label="Direktelenke til prøve {esc(sid)}">Lenke til prøven ↗</a></li>'
            )
        sections += f'<section class="provider" id="{provider}" aria-labelledby="{provider}-head"><h2 id="{provider}-head">{esc(PROVIDERS[provider])} <span>{len(samples)} prøver</span></h2><ul class="auditions">{cards}</ul></section>'
    jump = ''.join(f'<a href="#{p}">{esc(PROVIDERS[p])} ({len(s)})</a>' for p, s in groups.items())
    text = ''.join(f'<p>{esc(p.strip())}</p>' for p in (root / 'text.txt').read_text(encoding='utf-8').strip().split('\n\n'))
    total = sum(len(s) for s in groups.values())
    choice_note = (f'<p class="deck">Fast kanalstemme: <a href="#{voice_choice["id"]}-name">{esc(voice_choice.get("display_name") or voice_choice["voice"])}</a>, valgt av eieren. {total} prøver fra {len(groups)} leverandører er beholdt for sammenligning, med samme oppdiktede tekst.</p>' if voice_choice else f'<p class="deck">{total} prøver. {len(groups)} leverandører. Samme oppdiktede tekst. Ingen fast kanalstemme er registrert.</p>')
    text_html = (
        '<article class="voice-page"><header class="workspace-head"><p class="eyebrow">Privat · Stemmeprøver</p><h1>Kanalens stemme.</h1>'
        f'{choice_note}</header>'
        f'<nav class="jump" aria-label="Gå til leverandør">{jump}</nav>'
        '<p class="listening-guide">Lytt etter norsk uttale og setningsmelodi, tydelige tall, naturlig betoning, tempo og om stemmen er behagelig å høre på i et kvarter. '
        'De nye kvinnelige Gemini-prøvene merket «journalistisk» er lest med høyere tempo, korte pauser og direkte levering. '
        'Leverandørene styres ulikt: Gemini får en norsk fortellerinstruks, Speechify leser teksten med enkle pausemarkeringer. '
        'Oppgi prøve-ID når du gir beskjed om hva du foretrekker.</p>'
        f'<details class="script"><summary>Les teksten som leses opp</summary>{text}</details>'
        '<div class="voice-controls" data-enhance hidden><div><label for="provider-filter">Vis leverandør</label><select id="provider-filter"><option value="all">Alle leverandører</option>'
        + ''.join(f'<option value="{p}">{esc(PROVIDERS[p])}</option>' for p in groups)
        + '</select></div><div class="comparison-actions"><p id="compare-status" role="status">Velg to prøver for å sammenligne.</p><button type="button" id="show-comparison" disabled>Vis de to valgte</button><button type="button" id="show-all" hidden>Tilbake til alle</button></div></div>'
        f'<div class="voice-list">{sections}</div><p class="small">Sammenligningen gjelder bare denne siden og lagres ikke som stemmevalg. Lyd spiller av én prøve om gangen.</p></article>'
    )
    return text_html, voice_choice


def build(preview: bool, audition_root: Path | None, output_name: str = 'dist') -> dict:
    if output_name not in {'dist', 'public'} or (preview and output_name == 'public'):
        raise ValueError('Public output requires public mode; output must be dist or public')
    if audition_root and not preview:
        raise ValueError('Voice auditions are internal: require --preview')
    articles = []
    for file in sorted((HERE / 'content').glob('*.json')):
        article = json.loads(file.read_text(encoding='utf-8'))
        if article['status'] not in {'draft', 'published'}:
            raise ValueError(f'Invalid article status in {file}')
        if not preview and article['status'] != 'published':
            continue
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', article['slug']):
            raise ValueError(f'Invalid article slug in {file}')
        if article['slug'] in {'index', 'om', 'stemmer', 'redaksjonen', '404'}:
            raise ValueError(f'Reserved article slug in {file}')
        if article['status'] == 'published' and not (article.get('approved_by') and article.get('approved_at')):
            raise ValueError(f'Published article lacks recorded editorial decision: {file}')
        if article['status'] == 'published' and article['kind'] != 'Metode' and not valid_summary(article):
            raise ValueError(f'Published article needs a summary of 2-5 short points: {file}')
        if not article['sections'] or not article['sources']:
            raise ValueError(f'Article requires actual body and sources: {file}')
        articles.append(article)
    if len({a['slug'] for a in articles}) != len(articles):
        raise ValueError('Duplicate article slug')
    voices = bool(audition_root)
    with tempfile.TemporaryDirectory(prefix='.build-', dir=HERE) as temporary:
        output = Path(temporary) / 'dist'
        output.mkdir()
        shutil.copyfile(HERE / 'style.css', output / 'style.css')
        for name in ['icon.svg', 'favicon.png', 'favicon.ico', 'apple-touch-icon.png', 'social.png']:
            shutil.copyfile(HERE / 'assets' / name, output / name)
        for article in articles:
            media_files = [item['file'] for item in article.get('gallery') or []] + film_files(article)
            if media_files:
                (output / 'media' / article['slug']).mkdir(parents=True, exist_ok=True)
                for name in media_files:
                    shutil.copyfile(HERE / 'media' / article['slug'] / name, output / 'media' / article['slug'] / name)
            (output / f'{article["slug"]}.html').write_text(page(article['title'], article_html(article), preview, voices, article['slug'] + '.html', article), encoding='utf-8')
        (output / 'index.html').write_text(page('Norsk journalistikk', home_html(articles, preview), preview, voices, 'index.html'), encoding='utf-8')
        (output / 'om.html').write_text(page('Slik jobber vi', ABOUT, preview, voices, 'om.html'), encoding='utf-8')
        voice_count = 0
        voice_choice = None
        if audition_root:
            (output / 'audio').mkdir()
            voice_page, voice_choice = auditions(audition_root, output)
            (output / 'stemmer.html').write_text(page('Norske stemmeprøver', voice_page, True, True, 'stemmer.html'), encoding='utf-8')
            shutil.copyfile(HERE / 'voices.js', output / 'voices.js')
            voice_count = len(list((output / 'audio').glob('*.wav')))
        if preview:
            (output / 'redaksjonen.html').write_text(page('Redaksjonen', newsroom_html(articles, voice_count, voice_choice), True, voices, 'redaksjonen.html'), encoding='utf-8')
        (output / 'robots.txt').write_text('User-agent: *\nDisallow: /\n' if preview else f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n', encoding='utf-8')
        if not preview:
            (output / '404.html').write_text(page('Siden finnes ikke', '<article class="article"><p class="eyebrow">404</p><h1>Siden finnes ikke.</h1><p>Adressen kan være feil, eller siden er flyttet.</p><a class="read" href="index.html">Til forsiden →</a></article>', False, False, '404.html'), encoding='utf-8')
            (output / '_headers').write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n  Content-Security-Policy: default-src 'none'; style-src 'self'; img-src 'self' data:; media-src 'self'; frame-src https://www.youtube-nocookie.com; base-uri 'none'; frame-ancestors 'none'; form-action 'none'\n", encoding='utf-8')
            pages = ['index.html', 'om.html'] + [f'{a["slug"]}.html' for a in articles]
            sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{BASE}{"" if name == "index.html" else name.removesuffix(".html")}</loc></url>' for name in pages) + '</urlset>'
            (output / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
        dist = HERE / output_name
        if dist.is_symlink() or dist.resolve() != HERE.resolve() / output_name:
            raise ValueError('Refusing unexpected build output target')
        if dist.exists():
            shutil.rmtree(dist)
        shutil.copytree(output, dist)
    return {'status':'built', 'directory':str(dist), 'preview':preview, 'articles':len(articles), 'voice_auditions':voices}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--auditions', type=Path)
    parser.add_argument('--output', choices=('dist', 'public'), default='dist')
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.preview, args.auditions.resolve() if args.auditions else None, args.output), ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f'innsyn site build: {exc}\n')
