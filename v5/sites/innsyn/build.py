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
from urllib.parse import quote, urlparse

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
    links = [('index.html', 'Forsiden'), ('index.html#saker', 'Saker'), ('om.html', 'Slik jobber vi'), ('tips.html', 'Tips oss')]
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
    if 'class="contents"' in body:
        script += '<script src="contents.js" defer></script>'
    if 'data-comments=' in body:
        script += '<script src="comments.js" defer></script>'
    description = article['deck'] if article else ('Slik arbeider KI-avisa med kilder, faktakontroll, KI og rettelser. Ansvarlig redaktør: Anders Lunde.' if current == 'om.html' else 'Tips KI-avisa om maktmisbruk, lovbrudd, habilitet eller bruk av offentlige penger. Les hva du bør sende, og hva vi ikke kan love.' if current == 'tips.html' else 'KI-avisa undersøker makt, følger offentlige penger og forklarer samfunnsdebatten, med synlige kilder og rettelser.')
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
    return f'''<!doctype html><html lang="nb"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><title>{esc(title)} · KI-avisa</title><meta name="description" content="{esc(description)}">{seo}<meta name="theme-color" content="#23312f"><link rel="icon" href="/icon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.png" type="image/png" sizes="48x48"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180"><link rel="stylesheet" href="style.css">{script}</head><body><a class="skip" href="#main">Hopp til innhold</a>{banner}<div class="wrap"><header class="site-header"><div class="masthead"><a class="brand" href="index.html" aria-label="KI-avisa, forsiden">ki-avisa<i>.</i></a><p>Vi undersøker makten,<br>følger pengene og forklarer.</p><span class="edition">Undersøkende<br>journalistikk</span></div><nav class="nav" aria-label="Hovedmeny"><div class="reader-nav">{navigation}</div>{owner}</nav></header><main id="main">{body}</main><footer class="footer"><a class="footer-brand" href="index.html">ki-avisa.</a><p>Ansvarlig redaktør og eier: Anders Lunde.<br><a href="mailto:lunde.anders@gmail.com">lunde.anders@gmail.com</a></p><div><a href="tips.html">Tips oss om en sak</a><a href="om.html#metode">Metode og ansvar</a><a href="om.html#rettelser">Kontakt og rettelser</a></div></footer></div></body></html>'''


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
    title = f'<span class="film-title">{esc(film["title"])}</span>' if film.get('title') else ''
    duration = f'<span class="film-duration">{esc(film["duration"])}</span>' if film.get('duration') else ''
    return (f'<figure class="film"><div class="film-head"><span class="film-label">Video</span>{title}{duration}</div>'
            f'<div class="film-frame"><video controls preload="metadata" playsinline{poster} src="{base}{film["file"]}">{track}'
            f'Nettleseren din kan ikke vise videoen.</video></div><figcaption>{esc(film["caption"])}'
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


def document_html(article: dict, doc: dict) -> str:
    """A cropped image of an archive page, linked to the original. Files live in media/<slug>/."""
    name = doc.get('file', '')
    if not SAFE_FILE.fullmatch(name) or not name.endswith(('.jpg', '.png', '.webp')):
        raise ValueError(f'Invalid document image name: {name!r}')
    if not all(doc.get(k) for k in ('alt', 'caption', 'credit', 'source_url')):
        raise ValueError(f'Document image lacks alt, caption, credit or source: {name}')
    return (f'<figure class="doc-image"><a href="{url(doc["source_url"])}" rel="noreferrer">'
            f'<img src="media/{article["slug"]}/{name}" alt="{esc(doc["alt"])}" loading="lazy" decoding="async"></a>'
            f'<figcaption>{esc(doc["caption"])}<span class="credit">{esc(doc["credit"])} · '
            f'<a href="{url(doc["source_url"])}" rel="noreferrer">Se originalsiden ↗</a></span></figcaption></figure>')


def document_files(article: dict) -> list[str]:
    return [s['document']['file'] for s in article['sections'] if s.get('document')]


SAFE_NAME = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
SAFE_PAGE_ID = re.compile(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*')
INTERNAL_HREF = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\.html(?:#[a-z0-9-]+)?')


def transcripts(article: dict) -> dict[str, dict]:
    """Prepared public OCR pages for a register article: content/avskrift/<slug>/<group>.json.
    Only files the editor has deliberately placed there are rendered; no files means no transcript links."""
    folder = HERE / 'content' / 'avskrift' / article['slug']
    found = {}
    for file in sorted(folder.glob('*.json')) if folder.is_dir() else []:
        if not SAFE_NAME.fullmatch(file.stem):
            raise ValueError(f'Invalid transcript group name: {file}')
        data = json.loads(file.read_text(encoding='utf-8'))
        for p in data['pages']:
            if not SAFE_PAGE_ID.fullmatch(p['id']):
                raise ValueError(f'Invalid transcript page id {p["id"]!r} in {file}')
            url(p['url'])
        found[f'{article["slug"]}-avskrift-{file.stem}.html'] = data
    return found


def transcript_html(article: dict, name: str, data: dict) -> str:
    pages = ''.join(f'<section class="ocr-page" id="s-{esc(p["id"])}"><div class="ocr-head"><h2>{esc(p["id"])}</h2><a href="{url(p["url"])}" rel="noreferrer">Originalside ↗</a></div><pre class="ocr">{esc(p["text"])}</pre></section>' for p in data['pages'])
    return (f'<article class="reading transcript"><header class="article-head"><a class="back" href="{article["slug"]}.html#register">← {esc(article["title"])}</a>'
            f'<p class="eyebrow">Maskinlaget avskrift</p><h1>{esc(data["title"])}</h1><p class="deck">{esc(data["deck"])}</p>'
            '<p class="ocr-note">Teksten er lest maskinelt av en KI-modell fra skannede arkivbilder. Den kan inneholde feil, særlig i håndskrift, tabeller og hebraisk eller arabisk tekst. Originalsiden er alltid kilden.</p></header>'
            f'<div class="ocr-pages">{pages}</div></article>')


def register_html(article: dict, transcript_pages: dict[str, dict]) -> str:
    register = article.get('register')
    if not register:
        return ''
    where = {p['id']: name for name, data in transcript_pages.items() for p in data['pages']}
    items = ''
    for item in register['items']:
        if not isinstance(item['nr'], int):
            raise ValueError('Register item number must be an integer')
        pages = item['pages']
        shown = pages[:8]
        originals = ' '.join(f'<a href="{url(p["url"])}" rel="noreferrer">{esc(p["id"])}</a>' for p in shown)
        more = f' <span class="reg-more">+{len(pages) - len(shown)} sider</span>' if len(pages) > len(shown) else ''
        ocr = ' '.join(f'<a href="{where[p["id"]]}#s-{esc(p["id"])}">{esc(p["id"])}</a>' for p in shown if p['id'] in where)
        ocr = f'<span class="reg-label">Avskrift</span> {ocr}' if ocr else ''
        top = ''
        if item.get('story'):
            if not INTERNAL_HREF.fullmatch(item['story']):
                raise ValueError(f'Invalid internal story link: {item["story"]!r}')
            top = f' <a class="reg-story" href="{item["story"]}">Les saken →</a>'
        tags = ''.join(f'<span class="reg-tag">{esc(t)}</span>' for t in item.get('tags') or [])
        items += (f'<li id="funn-{item["nr"]}" class="reg-item"><div class="reg-meta"><span class="reg-nr">{item["nr"]}</span>'
                  f'<span>{esc(item.get("date") or "Udatert")}</span><span>{esc(item["source"])}</span>{tags}</div>'
                  f'<h3>{esc(item["title"])}{top}</h3><p>{esc(item["text"])}</p>'
                  f'<p class="reg-links"><span class="reg-label">Original</span> {originals}{more}{" · " + ocr if ocr else ""}</p></li>')
    return f'<section id="register" class="register"><h2>{esc(register["heading"])}</h2><ol class="reg-list">{items}</ol></section>'


def comparison_html(data: dict, source_count: int, references: dict[int, int], prefix: str) -> str:
    """Render deliberately prepared plain-text rows; never accept case HTML."""
    labels, cell_labels, rows = data['labels'], data['cell_labels'], data['rows']
    if len(labels) != 4 or len(cell_labels) != 3 or not rows:
        raise ValueError('Comparison needs four headings, three cell labels and rows')
    head = '<div class="comparison-head" aria-hidden="true">' + ''.join(f'<span>{esc(t)}</span>' for t in labels) + '</div>'
    body = []
    for i, row in enumerate(rows, 1):
        if len(row['cells']) != 3:
            raise ValueError('Comparison row needs three cells')
        ident = f'{prefix}-person-{i}'
        description = ''.join(f'<p>{sourced_text(t, source_count, references)}</p>' for t in row['description'])
        cells = ''.join(f'<div class="comparison-cell comparison-cell-{j}"><dt>{esc(label)}</dt><dd>{sourced_text(text, source_count, references)}</dd></div>' for j, (label, text) in enumerate(zip(cell_labels, row['cells']), 1))
        body.append(f'<div class="comparison-row" role="group" aria-labelledby="{ident}"><div class="comparison-who"><h3 id="{ident}">{esc(row["name"])}</h3>{description}</div><dl>{cells}</dl></div>')
    return '<div class="comparison-matrix">' + head + ''.join(body) + '</div>'


def event_list_html(data: dict, source_count: int, references: dict[int, int]) -> str:
    rows = []
    for item in data['items']:
        links = ' · '.join(f'<a href="{url(link["url"])}" rel="noreferrer">{esc(link["title"])}</a>' for link in item['links'])
        rows.append(f'<li>{sourced_text(item["text"], source_count, references)}<span class="event-links">{links}</span></li>')
    return f'<details class="article-details"><summary>{esc(data["label"])}</summary><ol class="article-events">' + ''.join(rows) + '</ol></details>'


def section_html(article: dict, section: dict, index: int, references: dict[int, int]) -> str:
    count = len(article['sources'])
    body = ''.join(f'<p>{sourced_text(p, count, references)}</p>' for p in section['paragraphs'])
    if section.get('comparison'):
        body += comparison_html(section['comparison'], count, references, f'avsnitt-{index}')
    if section.get('document'):
        body += document_html(article, section['document'])
    if section.get('figure'):
        body += figure_html(section['figure'])
    if section.get('event_list'):
        body += event_list_html(section['event_list'], count, references)
    if section.get('collapsed'):
        return f'<details id="avsnitt-{index}" class="article-details"><summary>{esc(section["heading"])}</summary>{body}</details>'
    return f'<section id="avsnitt-{index}"><h2>{esc(section["heading"])}</h2>{body}</section>'


def comments_copy() -> dict:
    return json.loads((HERE / 'comments-copy.json').read_text(encoding='utf-8'))


def comments_html(article: dict, preview: bool) -> str:
    c = comments_copy()
    if article['status'] != 'published' or article.get('comments') is False:
        return f'<section id="kommentarer" class="comments"><h2>{esc(c["heading"])}</h2><p>{esc(c["preview"] if article["status"] != "published" else c["closed"])}</p></section>'
    return (f'<section id="kommentarer" class="comments" data-comments="{esc(article["slug"])}" data-preview="{str(preview).lower()}" aria-labelledby="comments-heading">'
            f'<h2 id="comments-heading">{esc(c["heading"])}</h2><p>{esc(c["intro"])}</p>'
            f'<details class="comment-rules"><summary>{esc(c["rules_title"])}</summary><p>{esc(c["rules"])}</p><p>{esc(c["limits"])}</p><p>{esc(c["rules_privacy"])}</p><a href="tips.html">Tips oss</a> · <a href="om.html#personvern-kommentarer">{esc(c["privacy_link"])}</a></details>'
            f'<p class="comment-status" role="status" aria-live="polite"></p><noscript><p>{esc(c["no_js"])}</p></noscript>'
            f'<form class="comment-form" hidden><p data-reply-status></p><button type="button" data-cancel-reply hidden>{esc(c["cancel_reply"])}</button>'
            f'<label for="comment-name">{esc(c["name_label"])}</label><input id="comment-name" name="name" required maxlength="80" autocomplete="nickname" aria-describedby="comment-pseudonym"><p id="comment-pseudonym" class="comment-help">{esc(c["pseudonym"])}</p>'
            f'<label for="comment-body">{esc(c["body_label"])}</label><textarea id="comment-body" name="body" required maxlength="6000" rows="6" aria-describedby="comment-limits"></textarea><p id="comment-limits" class="comment-help">{esc(c["limits"])}</p>'
            f'<div class="comment-honey" aria-hidden="true"><label for="comment-website">Website</label><input id="comment-website" name="website" tabindex="-1" autocomplete="off"></div>'
            f'<button type="submit" disabled>{esc(c["submit"])}</button></form><div data-comment-list></div>'
            f'<button type="button" data-comment-more hidden>{esc(c["more"])}</button><button type="button" data-comment-retry hidden>{esc(c["retry"])}</button></section>')


def article_html(article: dict, transcript_pages: dict[str, dict] | None = None, preview: bool = False) -> str:
    comments_label = esc(comments_copy()['heading'])
    references: dict[int, int] = {}
    content = ''.join(section_html(article, s, i, references) for i, s in enumerate(article['sections'], 1))
    sources = ''
    for number, source in enumerate(article['sources'], 1):
        backlinks = ''.join(f'<a href="#henvisning-{number}-{i}" aria-label="Tilbake til henvisning {i} til kilde {number}">↩ {i}</a>' for i in range(1, references.get(number, 0) + 1))
        backlinks = f'<span class="backlinks">Til teksten {backlinks}</span>' if backlinks else ''
        sources += f'<li id="kilde-{number}"><a href="{url(source["url"])}" rel="noreferrer">{esc(source["title"])}</a><span class="source-domain">{esc(urlparse(source["url"]).netloc.removeprefix("www."))}</span>{backlinks}</li>'
    updates = ''.join(f'<li>{esc(item)}</li>' for item in article.get('updates', []))
    updates = f'<ol class="updates">{updates}</ol>' if updates else '<p>Ingen endringer er registrert i denne teksten.</p>'
    contents = ''.join(f'<li><a href="#avsnitt-{i}">{esc(s["heading"])}</a></li>' for i, s in enumerate(article['sections'], 1))
    if article.get('register'):
        contents += f'<li><a href="#register">{esc(article["register"]["heading"])}</a></li>'
    notice = '<p class="draft-notice"><strong>Utkast til metodebeskrivelse.</strong> Viser redaksjonens arbeidsmåte; dette er ikke en publisert undersøkelse.</p>' if article['status'] == 'draft' and article['kind'] == 'Metode' else '<p class="draft-notice"><strong>Upublisert utkast.</strong> Innholdet er under arbeid.</p>' if article['status'] == 'draft' else ''
    video = ''
    if article.get('youtube_id'):
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}', article['youtube_id']):
            raise ValueError('Invalid verified YouTube video ID')
        video = f'<iframe src="https://www.youtube-nocookie.com/embed/{article["youtube_id"]}" title="Se filmen" loading="lazy" allowfullscreen></iframe>'
    return f'<article class="reading"><header class="article-head"><a class="back" href="index.html">← Forsiden</a><p class="eyebrow">{esc(article["kind"])}</p><h1>{esc(article["title"])}</h1><p class="deck">{esc(article["deck"])}</p><div class="byline"><span>Av KI-avisas KI-redaksjon</span><time datetime="{esc(article["date"])}">{esc(article["date"])}</time>{draft_badge(article)}</div>{notice}{summary_html(article)}<nav class="evidence-nav" aria-label="Dokumentasjon"><a href="#kilder">{len(article["sources"])} {"kilde" if len(article["sources"]) == 1 else "kilder"} ↓</a><a href="#endringer">Endringer og rettelser ↓</a><a href="#kommentarer">{comments_label} ↓</a><a href="om.html#ki">Om KI-redaksjonen ↗</a></nav></header><div class="reading-layout"><nav class="contents" aria-label="I denne teksten"><p>I denne teksten</p><ol>{contents}</ol><a href="#kommentarer">{comments_label}</a><a href="#kilder">Kilder</a><a href="#endringer">Endringer og rettelser</a></nav><div class="article-body">{video}{film_html(article)}{content}{register_html(article, transcript_pages or {})}{gallery_html(article)}{comments_html(article, preview)}<section id="kilder" class="sources"><p class="eyebrow">Dokumentasjon</p><h2>Kilder til teksten</h2><ol>{sources}</ol></section><section id="endringer" class="changes"><h2>Endringer og rettelser</h2>{updates}<a href="om.html#rettelser">Slik håndterer vi rettelser →</a></section><a class="back-to-top" href="#main">Til toppen ↑</a></div></div></article>'


def about_html() -> str:
    c = comments_copy()
    privacy = (f'<h3 id="personvern-kommentarer">{esc(c["privacy_heading"])}</h3>'
               + ''.join(f'<p>{esc(c[key])}</p>' for key in ('privacy_comments', 'privacy_security', 'privacy_rights')))
    return ABOUT.replace('sporingsskript, kontaktskjemaer eller', 'sporingsskript eller').replace('<h2>Et nettsted under utvikling</h2>', privacy + '<h2>Et nettsted under utvikling</h2>')


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
        f'<section class="pillars" aria-labelledby="dekker"><h2 id="dekker" class="visually-hidden">Dette dekker vi</h2>{pillar_html}</section>'
        '<section class="tip-strip"><div><p class="eyebrow">Tips oss</p><h2>Vet du om noe som bør undersøkes?</h2><p>Et vedtak som ikke henger på greip, penger som forsvant, eller noen som avgjorde en sak de ikke burde? Fortell oss hva det gjelder og hvor dokumentasjonen finnes.</p></div><a class="tip-button" href="tips.html">Tips oss om en sak <span aria-hidden="true">→</span></a></section>'
        f'{newsroom}'
        '<section class="bottom"><div><p class="eyebrow">Samme krav til alle</p><h2>Partipolitisk nøytral.<br>Ikke nøytral overfor fakta.</h2><p>Vi stiller de samme spørsmålene til alle partier og alle med makt. Hvor mye plass en sak får, avgjøres av hvor viktig den er og hva dokumentene viser, ikke av hvem den handler om.</p></div>'
        '<div class="notice"><p class="eyebrow">Metoden vår</p><h2>Også det som taler imot.</h2><p>En god undersøkelse leter etter mer enn støtte for den første mistanken. Vi viser kildene, prøver alternative forklaringer og retter feil synlig.</p><a class="read" href="om.html">Slik jobber vi <span aria-hidden="true">↗</span></a></div></section>'
    )


ABOUT = '<article class="article about"><p class="eyebrow">Slik jobber vi</p><h1>Spørsmål som fortjener ordentlige svar.</h1>\n<p class="deck">KI-avisa er et norsk journalistikkprosjekt. KI-redaksjonen undersøker sakene og lager journalistikken. Anders Lunde er ansvarlig redaktør og eier. Han eier også KI-partiet, et separat prosjekt for politikkutvikling. KI-avisa bruker samme journalistiske beviskrav overfor alle aktører, også KI-partiet.</p>\n<nav class="evidence-nav" aria-label="Om redaksjonen"><a href="#metode">Metode ↓</a><a href="#ki">KI og ansvar ↓</a><a href="#rettelser">Kontakt og rettelser ↓</a><a href="#personvern">Personvern ↓</a></nav>\n<h2>Hva vi dekker</h2><p>Gravende saker om korrupsjon, lovbrudd, habilitet og sløsing med offentlige penger. Saker om makt, politi og rettsvesen der dokumentene kan etterprøves. Og forklaringer av debattene som preger norsk politikk, som strømpris, oljepenger, formuesskatt, energi og innvandring.</p>\n<h2>Samme metode, uansett parti</h2><p>Alle partier og personer møter samme dokumentasjonskrav. Hvor mye plass en sak får, avgjøres av betydning og belegg. I forklaringssaker skiller vi mellom hva dataene viser, hvilke forklaringer som har støtte, og hvilke valg som fortsatt er politiske.</p>\n<h2 id="metode">En metode du kan etterprøve</h2><p>Vi kontrollerer originalkilder, prøver alternative forklaringer og skiller mellom det som er dokumentert, det som er påstått og det som er vår vurdering. Personer, virksomheter og offentlige organer som får sterke faktiske beskyldninger mot seg, får en reell mulighet til å svare før saken publiseres.</p><p>Ved sentrale påstander skal artiklene vise til den konkrete kilden, oppgi perioden tallene gjelder og forklare viktige beregninger og begrensninger. Vi krediterer andre mediers arbeid. Artiklene kan leses uten en film.</p>\n<h2 id="ki">KI-journalister. Åpent ansvar.</h2><p>KI-redaksjonen finner og avgrenser saker, undersøker dokumenter og data, sender innsynskrav, kontakter berørte og følger opp svar. Den skriver artiklene og utarbeider filmene. KI kan ta feil, også med kilder og tall. Derfor skal sentrale påstander kontrolleres mot originalen, og feil rettes synlig.</p><p>Anders Lunde er ansvarlig redaktør. KI-redaktøren utfører og dokumenterer redaksjonelt arbeid innenfor mandatet; den er ikke en fysisk person og erstatter ikke den ansvarlige redaktøren. Eieren har bekreftet redaktør og offentlig kontakt 4. november 2026.</p><p>Vi opplyser om KI-avsender i journalistiske henvendelser og bruker syntetisk fortellerstemme. Illustrasjoner merkes og er aldri dokumentasjon av hva noen faktisk har gjort. Private kildearkiver og korrespondanse publiseres ikke.</p>\n<h2 id="rettelser">Kontakt og synlige rettelser</h2><p>Ansvarlig redaktør og eier: <strong>Anders Lunde</strong>.<br>Offentlig kontakt: <a href="mailto:lunde.anders@gmail.com">lunde.anders@gmail.com</a>.</p><p>Oppgi hvilken side og opplysning en rettelse gjelder. Meningsbærende endringer skal stå i artikkelens endringshistorikk, med dato og forklaring. Vesentlige feil følges opp også i eventuelle filmer.</p><p>Har du et tips? Les <a href="tips.html">Tips oss</a> før du sender. Vanlig e-post er ikke en sikker tipskanal, og vi kan ikke love anonymitet.</p>\n<h2>Felles eier med KI-partiet</h2><p>Anders Lunde eier både KI-avisa og <a href="https://ki-partiet.pages.dev/">KI-partiet</a>. KI-partiet utvikler politikk; KI-avisa driver journalistikk etter eget mandat. Felles eierskap er en binding leserne skal kjenne til. Journalistiske konklusjoner skal ikke tilpasses det politiske prosjektets forslag. Private kilder og korrespondanse overføres ikke til KI-partiet.</p>\n<h2 id="personvern">Personvern på nettstedet</h2><p>KI-avisa bruker ikke informasjonskapsler, sporingsskript, kontaktskjemaer eller eksterne skrifttyper. For å se hvordan nettstedet brukes, teller serveren sidevisninger samlet per kalenderdag (norsk tid), per offentlig side og etter en fast kildekategori, for eksempel Google, Facebook, lenker fra KI-avisa selv, direkte/ukjent eller andre nettsteder. Statistikkdatabasen vår lagrer ikke IP-adresser, besøks-ID-er, fullstendige henvisningsadresser, domenenavn for andre henvisende nettsteder eller nettleserinformasjon (user agent), og oversikten er passordbeskyttet. Tallene viser sidevisninger, ikke antall unike besøkende. Nettstedet leveres via Cloudflare, som kan behandle tekniske tilkoblingsdata for drift og sikkerhet. E-postlenker åpner e-postprogrammet ditt. For innebygde YouTube-videoer gjelder egen merknad.</p><p>Dersom en artikkel senere inneholder en YouTube-film, kan avspilling gi YouTube opplysninger om tilkoblingen din.</p>\n<h2>Et nettsted under utvikling</h2><p>Bare ferdig publiserte artikler med dokumentert redaksjonell beslutning skal vises her. Utkast, stemmeprøver og interne arbeidsoversikter er ikke en del av det offentlige nettstedet.</p>\n<div class="sources"><h2>Redaksjonelt utgangspunkt</h2><p>Metoden bygger på <a href="https://www.presse.no/vaer-varsom-plakaten">Vær Varsom-plakaten hos Norsk Presseforbund</a>. Det innebærer ingen påstand om medlemskap, PFU-tilknytning eller presseakkreditering.</p></div></article>'


TIP_QUESTIONS = ['Hva gjelder saken?', 'Hvem tok beslutningen, eller hvilket organ eller selskap gjelder det?', 'Når skjedde det?',
                 'Hvor finnes dokumentasjonen (saksnummer, journal, vedtak, regnskap eller lenker)?', 'Hva har du selv sett, og hva har du hørt fra andre?']
TIP_MAIL = ('mailto:lunde.anders@gmail.com?subject=' + quote('Tips til KI-avisa')
            + '&body=' + quote('\r\n\r\n\r\n'.join(TIP_QUESTIONS) + '\r\n'))

# Matches REDAKSJON.md: no secure channel yet, so the page must not promise anonymity
# or invite sensitive personal data by e-mail.
TIPS = ('<article class="article tips"><p class="eyebrow">Tips oss</p><h1>Vet du om noe som bør undersøkes?</h1>'
        '<p class="deck">Vi tar imot tips om maktmisbruk, lovbrudd, habilitet og bruk av offentlige penger. Et tips er starten på en undersøkelse, ikke en konklusjon. Vi kontrollerer det mot dokumenter før noe blir publisert.</p>'
        f'<a class="tip-button" href="{esc(TIP_MAIL)}">Send tips på e-post <span aria-hidden="true">→</span></a>'
        '<p class="tip-address">Adresse: <a href="mailto:lunde.anders@gmail.com">lunde.anders@gmail.com</a>. Lenken åpner e-postprogrammet ditt med noen spørsmål ferdig utfylt.</p>'
        '<aside class="tip-warning" aria-labelledby="for-du-sender"><h2 id="for-du-sender">Før du sender: vi kan ikke love anonymitet</h2>'
        '<p>KI-avisa har ennå ingen sikker tipskanal. Tips kommer til en vanlig Gmail-konto og leses av KI-redaksjonen, som bruker KI-tjenester fra eksterne leverandører.</p>'
        '<ul><li>Ikke send helseopplysninger, personnumre, passord eller fortrolige dokumenter.</li>'
        '<li>Ikke send noe som kan sette deg eller andre i fare om det blir kjent.</li>'
        '<li>Har du sensitive opplysninger, skriv først kort og generelt hva saken gjelder.</li>'
        '<li>Er du ansatt og vil si fra om forhold på arbeidsplassen, gjør deg kjent med varslingsreglene i arbeidsmiljøloven først.</li></ul></aside>'
        '<h2>Dette hjelper oss</h2><ul class="tip-list">'
        '<li><strong>Hva skjedde, og når?</strong> Konkrete datoer, beløp og hendelser er lettere å kontrollere enn inntrykk.</li>'
        '<li><strong>Hvem tok beslutningen?</strong> Navnet på organet, kommunen, selskapet eller rollen er ofte nok.</li>'
        '<li><strong>Hvor finnes dokumentasjonen?</strong> Saksnummer, offentlig journal, vedtak, møtereferat, regnskap eller lenker. Offentlige dokumenter kan vi be om innsyn i selv.</li>'
        '<li><strong>Hva vet du selv?</strong> Skill mellom det du har sett og det du har hørt fra andre.</li></ul>'
        '<h2>Hva skjer med tipset</h2>'
        '<p>Vi vurderer tipsene vi får, men kan ikke undersøke alle eller svare på hvert enkelt. Et tips er en hypotese. Vi prøver det mot dokumenter og alternative forklaringer, og den som får kritikk, får mulighet til å svare før vi publiserer.</p>'
        '<p>Tips om alle partier og aktører vurderes etter samme krav, også tips om KI-partiet, som har samme eier som KI-avisa. Tips og korrespondanse deles ikke med KI-partiet.</p>'
        '<p>Gjelder det en feil i noe vi har publisert? Se <a href="om.html#rettelser">Kontakt og rettelser</a>.</p></article>')


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
        if article['slug'] in {'index', 'om', 'tips', 'stats', 'moderering', 'api', 'stemmer', 'redaksjonen', '404'}:
            raise ValueError(f'Reserved article slug in {file}')
        if article['status'] == 'published' and not (article.get('approved_by') and article.get('approved_at')):
            raise ValueError(f'Published article lacks recorded editorial decision: {file}')
        if article['status'] == 'published' and article['kind'] != 'Metode' and not valid_summary(article):
            raise ValueError(f'Published article needs a summary of 2-5 short points: {file}')
        if not article['sections'] or not article['sources']:
            raise ValueError(f'Article requires actual body and sources: {file}')
        if 'comments' in article and not isinstance(article['comments'], bool):
            raise ValueError(f'Article comments flag must be boolean: {file}')
        articles.append(article)
    if len({a['slug'] for a in articles}) != len(articles):
        raise ValueError('Duplicate article slug')
    voices = bool(audition_root)
    with tempfile.TemporaryDirectory(prefix='.build-', dir=HERE) as temporary:
        output = Path(temporary) / 'dist'
        output.mkdir()
        shutil.copyfile(HERE / 'style.css', output / 'style.css')
        shutil.copyfile(HERE / 'contents.js', output / 'contents.js')
        copy = comments_copy()
        copy_json = json.dumps(copy, ensure_ascii=False).replace('<', '\\u003c')
        (output / 'comments.js').write_text((HERE / 'comments.js').read_text(encoding='utf-8').replace('__COMMENTS_COPY__', copy_json), encoding='utf-8')
        for name in ['icon.svg', 'favicon.png', 'favicon.ico', 'apple-touch-icon.png', 'social.png']:
            shutil.copyfile(HERE / 'assets' / name, output / name)
        for article in articles:
            media_files = [item['file'] for item in article.get('gallery') or []] + film_files(article) + document_files(article)
            if media_files:
                (output / 'media' / article['slug']).mkdir(parents=True, exist_ok=True)
                for name in media_files:
                    shutil.copyfile(HERE / 'media' / article['slug'] / name, output / 'media' / article['slug'] / name)
            pages_ocr = transcripts(article)
            (output / f'{article["slug"]}.html').write_text(page(article['title'], article_html(article, pages_ocr, preview), preview, voices, article['slug'] + '.html', article), encoding='utf-8')
            for name, data in pages_ocr.items():
                meta = dict(title=data['title'], deck=data['deck'], kind='Metode', date=article['date'])
                (output / name).write_text(page(data['title'], transcript_html(article, name, data), preview, voices, name, meta), encoding='utf-8')
        (output / 'index.html').write_text(page('Norsk journalistikk', home_html(articles, preview), preview, voices, 'index.html'), encoding='utf-8')
        (output / 'om.html').write_text(page('Slik jobber vi', about_html(), preview, voices, 'om.html'), encoding='utf-8')
        (output / 'tips.html').write_text(page('Tips oss', TIPS, preview, voices, 'tips.html'), encoding='utf-8')
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
            public_paths = sorted('/' if p.name == 'index.html' else '/' + p.stem for p in output.glob('*.html') if p.name != '404.html')
            comment_articles = {a['slug']: {'title': a['title'], 'open': a.get('comments', True)} for a in articles}
            comments = (HERE / 'comments.mjs').read_text(encoding='utf-8').replace('__COMMENT_ARTICLES__', json.dumps(comment_articles, ensure_ascii=False)).replace('__COMMENTS_COPY__', copy_json)
            worker = (HERE / 'worker.mjs').read_text(encoding='utf-8').replace('__PUBLIC_PATHS__', json.dumps(public_paths)).replace('// __COMMENTS_MODULE__', comments)
            (output / '_worker.js').write_text(worker, encoding='utf-8')
            shutil.copyfile(HERE / 'stats.css', output / 'stats.css')
            shutil.copyfile(HERE / 'moderation.js', output / 'moderation.js')
            static_paths = ['/style.css', '/contents.js', '/comments.js', '/moderation.js', '/stats.css', '/icon.svg', '/favicon.png', '/favicon.ico', '/apple-touch-icon.png', '/social.png', '/robots.txt', '/sitemap.xml']
            (output / '_routes.json').write_text(json.dumps({'version': 1, 'include': ['/*'], 'exclude': static_paths}), encoding='utf-8')
            (output / '_headers').write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n  Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; connect-src 'self'; frame-src https://www.youtube-nocookie.com; base-uri 'none'; frame-ancestors 'none'; form-action 'none'\n", encoding='utf-8')
            pages = ['index.html', 'om.html', 'tips.html'] + [f'{a["slug"]}.html' for a in articles]
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
