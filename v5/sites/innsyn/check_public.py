"""Check the public export boundary using synthetic fixtures and the actual output."""
import importlib.util
import json
import tempfile
import shutil
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('innsyn_site', HERE / 'build.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


def main():
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        (root / 'content').mkdir()
        shutil.copytree(HERE / 'assets', root / 'assets')
        for name in ('worker.mjs','comments.mjs','comments.js','comments-copy.json','moderation.js'):
            shutil.copyfile(HERE / name, root / name)
        shutil.copyfile(HERE / 'stats.css', root / 'stats.css')
        shutil.copyfile(HERE / 'contents.js', root / 'contents.js')
        (root / 'style.css').write_text('body{}', encoding='utf-8')
        article = dict(slug='public-fixture', title='Public fixture', deck='Public fixture',
                       kind='Forklart', date='2026-11-04', status='published',
                       approved_by='Synthetic test editor', approved_at='2026-11-04',
                       summary=['First summary point.', 'Second summary point.'],
                       sections=[dict(heading='Example', paragraphs=['Example [1]'])],
                       sources=[dict(title='Example', url='https://example.org/')])
        (root / 'content' / 'published.json').write_text(json.dumps(article), encoding='utf-8')
        draft = {**article, 'slug': 'private-fixture', 'title': 'PRIVATE_DRAFT_SENTINEL', 'status': 'draft'}
        (root / 'content' / 'draft.json').write_text(json.dumps(draft), encoding='utf-8')
        (root / 'preview').mkdir()
        (root / 'preview' / 'activity.json').write_text('PRIVATE_ACTIVITY_SENTINEL', encoding='utf-8')
        (root / 'public').mkdir()
        (root / 'public' / 'redaksjonen.html').write_text('STALE_PRIVATE_SENTINEL', encoding='utf-8')
        (root / 'dist').mkdir()
        (root / 'dist' / 'preview-sentinel').write_text('Keep original preview', encoding='utf-8')
        site.HERE = root
        site.build(False, None, 'public')
        names = {p.name for p in (root / 'public').iterdir()}
        assert names == {'index.html', 'om.html', 'tips.html', 'public-fixture.html', '404.html', 'style.css', 'contents.js', 'comments.js', 'moderation.js', 'stats.css', '_worker.js', '_routes.json', 'robots.txt', 'sitemap.xml', '_headers', 'icon.svg', 'favicon.png', 'favicon.ico', 'apple-touch-icon.png', 'social.png'}, names
        worker_text = (root / 'public/_worker.js').read_text(encoding='utf-8')
        assert '__COMMENT_ARTICLES__' not in worker_text and '__COMMENTS_COPY__' not in worker_text
        assert 'private-fixture' not in worker_text
        assert 'data-comments="public-fixture"' in (root / 'public/public-fixture.html').read_text(encoding='utf-8')
        assert '__PUBLIC_PATHS__' not in (root / 'public/_worker.js').read_text(encoding='utf-8')
        content = '\n'.join(p.read_text(encoding='utf-8') for p in (root / 'public').iterdir() if p.suffix in {'.html', '.xml', '.css', '.js', '.txt'})
        assert all(marker not in content for marker in ('PRIVATE_DRAFT_SENTINEL', 'PRIVATE_ACTIVITY_SENTINEL', 'STALE_PRIVATE_SENTINEL'))
        assert (root / 'dist' / 'preview-sentinel').read_text(encoding='utf-8') == 'Keep original preview'
        try:
            site.build(True, None, 'public')
        except ValueError:
            pass
        else:
            raise AssertionError('Preview was allowed into public output')
        assert 'class="ai-summary"' in (root / 'public' / 'public-fixture.html').read_text(encoding='utf-8')
        no_summary = {k: v for k, v in article.items() if k != 'summary'}
        (root / 'content' / 'published.json').write_text(json.dumps(no_summary), encoding='utf-8')
        try:
            site.build(False, None, 'public')
        except ValueError:
            pass
        else:
            raise AssertionError('Published article without summary was accepted')
        article['approved_at'] = ''
        (root / 'content' / 'published.json').write_text(json.dumps(article), encoding='utf-8')
        try:
            site.build(False, None, 'public')
        except ValueError:
            pass
        else:
            raise AssertionError('Missing editorial decision was accepted')
    site.HERE = HERE
    published = [json.loads(p.read_text(encoding='utf-8')) for p in (HERE / 'content').glob('*.json')]
    published = [a for a in published if a['status'] == 'published']
    allowed = {'index.html', 'om.html', 'tips.html', '404.html', 'style.css', 'robots.txt', 'sitemap.xml', '_headers', 'icon.svg', 'favicon.png', 'favicon.ico', 'apple-touch-icon.png', 'social.png'} | {a['slug'] + '.html' for a in published}
    allowed |= {name for a in published for name in site.transcripts(a)}
    media = {f"media/{a['slug']}/{item['file']}" for a in published for item in a.get('gallery') or []}
    media |= {f"media/{a['slug']}/{name}" for a in published for name in site.film_files(a)}
    media |= {f"media/{a['slug']}/{name}" for a in published for name in site.document_files(a)}
    if media:
        allowed |= {'media'}
    allowed |= {'_worker.js', '_routes.json', 'stats.css', 'contents.js', 'comments.js', 'moderation.js'}
    assert (HERE / 'public/contents.js').read_bytes() == (HERE / 'contents.js').read_bytes()
    assert '/contents.js' in json.loads((HERE / 'public/_routes.json').read_text(encoding='utf-8'))['exclude']
    assert "script-src 'self';" in (HERE / 'public/_headers').read_text(encoding='utf-8')
    assert 'stats' not in (HERE / 'public/sitemap.xml').read_text(encoding='utf-8')
    actual = {p.name for p in (HERE / 'public').iterdir()}
    assert actual == allowed, {'unexpected': sorted(actual - allowed), 'missing': sorted(allowed - actual)}
    assert all(p.is_file() and not p.is_symlink() for p in (HERE / 'public').iterdir() if p.name != 'media')
    actual_media = {p.relative_to(HERE / 'public').as_posix() for p in (HERE / 'public').glob('media/**/*') if p.is_file()}
    assert actual_media == media, {'unexpected_media': sorted(actual_media - media), 'missing_media': sorted(media - actual_media)}
    descriptions = set()
    for path in (HERE / 'public').glob('*.html'):
        text = path.read_text(encoding='utf-8')
        scripts = re.findall(r'<script\b[^>]*\bsrc="([^"]+)"', text)
        expected_scripts = (['contents.js'] if 'class="contents"' in text else []) + (['comments.js'] if 'data-comments=' in text else [])
        assert scripts == expected_scripts, (path.name, scripts)
        if path.stem in {a['slug'] for a in published}:
            assert 'id="kommentarer"' in text, path.name
            assert text.index('id="kommentarer"') < text.index('id="kilder"') < text.index('id="endringer"'), path.name
        assert 'href="/favicon.png"' in text and 'href="/apple-touch-icon.png"' in text
        if path.name == '404.html':
            assert '<meta name="robots" content="noindex,follow">' in text
            continue
        canonical = 'https://ki-avisa.pages.dev/' + ('' if path.name == 'index.html' else path.stem)
        assert f'<link rel="canonical" href="{canonical}">' in text
        assert f'<meta property="og:url" content="{canonical}">' in text
        description = re.search(r'<meta name="description" content="([^"]+)"', text).group(1)
        assert description not in descriptions
        descriptions.add(description)
        schema = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S).group(1)
        assert json.loads(schema)['@context'] == 'https://schema.org'
    assert (HERE / 'public/favicon.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    print(json.dumps({'public_boundary': 'passed', 'published_articles': len(published), 'files': sorted(actual), 'fixture_checks': ['draft excluded', 'activity excluded', 'stale files removed', 'private preview preserved', 'preview-to-public rejected', 'missing summary rejected', 'missing decision rejected']}))


if __name__ == '__main__':
    main()
