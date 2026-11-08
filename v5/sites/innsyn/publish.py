"""Publish an explicitly reviewed export once; never decide whether a draft is ready."""
from pathlib import Path
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
SITE = 'ki-avisa'
OUTPUT = HERE / 'public'
STATE = PROJECT / 'v5/workspace/hosting'


@contextmanager
def locked():
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE / 'publisher.lock').open('a+b') as handle:
        handle.seek(0)
        if not handle.read(1):
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            if os.name == 'nt':
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


MEDIA_SUFFIXES = {'.jpg', '.jpeg', '.png', '.webp', '.mp4', '.vtt'}


def fingerprint(folder):
    """Hash every exported file. Only top-level files and gallery images under media/ are allowed."""
    files = {}
    for path in sorted(folder.rglob('*')):
        relative = path.relative_to(folder).as_posix()
        if path.is_symlink():
            raise ValueError(f'Unexpected symlink in public export: {relative}')
        if path.is_dir():
            if relative != 'media' and not (relative.startswith('media/') and relative.count('/') == 1):
                raise ValueError(f'Unexpected directory in public export: {relative}')
            continue
        if '/' in relative and not (relative.startswith('media/') and relative.count('/') == 2 and path.suffix.lower() in MEDIA_SUFFIXES):
            raise ValueError(f'Unexpected nested file in public export: {relative}')
        files[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return digest, files


def save(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2), encoding='utf-8')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'run'])
    parser.add_argument('--reviewed-by')
    args = parser.parse_args()
    if args.command == 'prepare' and not (args.reviewed_by and args.reviewed_by.strip()):
        parser.error('prepare requires --reviewed-by after an actual publication review')
    with locked():
        for script in [['v5/sites/innsyn/build.py', '--output', 'public'], ['v5/sites/innsyn/check_public.py']]:
            result = subprocess.run([sys.executable, *script], cwd=PROJECT, capture_output=True, text=True, encoding='utf-8')
            if result.returncode:
                raise RuntimeError(result.stderr or result.stdout or 'Build or public export check failed')
        export_digest, files = fingerprint(OUTPUT)
        config = HERE / 'wrangler.toml'
        config_bytes = config.read_bytes()
        config_digest = hashlib.sha256(config_bytes).hexdigest()
        digest = hashlib.sha256((export_digest + config_digest).encode()).hexdigest()
        ready_path = STATE / 'publication-ready.json'
        deployed_path = STATE / 'publication-deployed.json'
        if args.command == 'prepare':
            save(ready_path, dict(site=SITE, sha256=digest, config_sha256=config_digest, files=files, reviewed_by=args.reviewed_by.strip(), reviewed_at=datetime.now(timezone.utc).isoformat()))
            print(json.dumps(dict(status='ready', site=SITE, sha256=digest, files=len(files))))
            return
        ready = json.loads(ready_path.read_text(encoding='utf-8')) if ready_path.exists() else {}
        if ready.get('site') != SITE or ready.get('sha256') != digest or not ready.get('reviewed_by') or not ready.get('reviewed_at'):
            print(json.dumps(dict(status='not_ready', site=SITE, reason='No reviewed release matches the current export')))
            return
        deployed = json.loads(deployed_path.read_text(encoding='utf-8')) if deployed_path.exists() else {}
        if deployed.get('sha256') == digest:
            print(json.dumps(dict(status='unchanged', site=SITE)))
            return
        npx = shutil.which('npx.cmd' if os.name == 'nt' else 'npx')
        if not npx:
            raise RuntimeError('npx is unavailable; retain the existing deployment')
        with tempfile.TemporaryDirectory(prefix='public-release-', dir=STATE) as temporary:
            stage = Path(temporary) / 'site'
            shutil.copytree(OUTPUT, stage)
            (Path(temporary) / 'wrangler.toml').write_bytes(config_bytes)
            if fingerprint(stage)[0] != export_digest:
                raise RuntimeError('Export changed during packaging; publication review must be repeated')
            result = subprocess.run([npx, '--yes', 'wrangler@4.157.0', 'pages', 'deploy', str(stage), '--project-name', SITE, '--branch', 'main', '--commit-dirty=true'], cwd=temporary, capture_output=True, text=True, encoding='utf-8', errors='replace')
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        (STATE / f'publication-{stamp}.log').write_text(result.stdout + result.stderr, encoding='utf-8')
        if result.returncode:
            raise RuntimeError('Cloudflare deployment failed; previous success state is unchanged. See the private publication log.')
        save(deployed_path, dict(site=SITE, sha256=digest, config_sha256=config_digest, files=files, reviewed_by=ready['reviewed_by'], reviewed_at=ready['reviewed_at'], deployed_at=datetime.now(timezone.utc).isoformat()))
        print(json.dumps(dict(status='deployed', site=SITE, url=f'https://{SITE}.pages.dev/', sha256=digest)))


if __name__ == '__main__':
    main()
