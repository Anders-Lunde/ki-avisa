"""Prepare a daily owner-only Gmail notification; never send mail from Python.

The scheduler uses the connected Gmail tool with the exact returned arguments,
then records its real receipt. Approval, cursors and correspondence stay ignored.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import uuid
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
STATE = PROJECT / 'v5/workspace/hosting/comments-notifications'
OSLO = ZoneInfo('Europe/Oslo')
RECIPIENT = 'lunde.anders@gmail.com'


def save(path: Path, data: dict):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def message_hash(message: dict) -> str:
    return hashlib.sha256(json.dumps(message, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


@contextmanager
def locked():
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE / 'notification.lock').open('a+b') as handle:
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
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == 'nt':
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def approved_message() -> dict:
    approval = json.loads((STATE / 'approval.json').read_text(encoding='utf-8'))
    message = approval['message']
    if (approval.get('status') != 'approved' or not approval.get('approved_at')
            or not approval.get('owner_instruction') or not approval.get('recurring_exception')
            or approval.get('message_sha256') != message_hash(message)
            or message.get('to') != RECIPIENT
            or any(message.get(key) for key in ('cc', 'bcc', 'attachments'))):
        raise ValueError('Missing or changed exact owner approval for the daily self-notification')
    # No sender override, recipient expansion, attachments or changed content.
    return {key: message[key] for key in ('to', 'subject', 'payload')}


def read_state() -> dict:
    path = STATE / 'state.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'cursor': 0}


def remote_window(after: int) -> dict:
    if type(after) is not int or not 0 <= after <= 9007199254740991:
        raise ValueError('Invalid private notification cursor')
    npx = shutil.which('npx.cmd' if os.name == 'nt' else 'npx')
    if not npx:
        raise RuntimeError('Wrangler/npx unavailable; no mail prepared')
    # Counts/IDs only. No reader text, names or IP pseudonyms are retrieved.
    query = ("SELECT COALESCE((SELECT seq FROM sqlite_sequence WHERE name='comments'),0) AS through, "
             f"(SELECT COUNT(*) FROM comments WHERE id>{after}) AS new_count")
    result = subprocess.run([npx, '--yes', 'wrangler@4.157.0', 'd1', 'execute', 'ki-avisa-stats',
                             '--remote', '--command', query, '--json'], cwd=HERE,
                            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    if result.returncode:
        raise RuntimeError('Comment count unavailable; no email prepared or cursor advanced')
    data = json.loads(result.stdout)
    if not data or not data[0].get('success'):
        raise RuntimeError('Invalid D1 receipt; no email prepared')
    window = data[0]['results'][0]
    if (type(window.get('through')) is not int or window['through'] < after
            or type(window.get('new_count')) is not int or window['new_count'] < 0):
        raise ValueError('Invalid comment count/cursor; retain previous state')
    return window


def check(now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    today = now.astimezone(OSLO).date().isoformat()
    message = approved_message()
    state = read_state()
    if state.get('pending'):
        return {'status': 'delivery_uncertain', 'pending': state['pending'],
                'action': 'Search Gmail Sent and verify exact recipient/content before recording delivery; never resend blindly.'}
    if state.get('last_sent_on') == today:
        return {'status': 'already_sent_today', 'date': today}
    window = remote_window(state['cursor'])
    if not window['new_count']:
        state.update(cursor=window['through'], checked_at=now.isoformat())
        save(STATE / 'state.json', state)
        return {'status': 'no_new_comments', 'date': today, 'email_sent': False}
    pending = {'id': str(uuid.uuid4()), 'after': state['cursor'], **window,
               'prepared_at': now.isoformat(), 'date': today,
               'message_sha256': message_hash(message), 'gmail_args': message}
    state['pending'] = pending
    save(STATE / 'state.json', state)
    save(STATE / (pending['id'] + '-prepared.json'), pending)
    return {'status': 'ready_for_approved_send', 'pending_id': pending['id'],
            'new_comments': window['new_count'], 'gmail_args': message}


def record(pending_id: str, receipt_path: Path, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    message = approved_message()
    state = read_state()
    pending = state.get('pending')
    if not pending or pending['id'] != pending_id or pending['message_sha256'] != message_hash(message):
        raise ValueError('No matching approved pending email; do not advance cursor')
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    actual = receipt.get('structuredContent') or receipt
    message_id = actual.get('id') or actual.get('message_id')
    thread_id = actual.get('thread_id') or actual.get('threadId')
    if receipt.get('isError') or not message_id or not thread_id:
        raise ValueError('Actual successful Gmail message and thread IDs are required')
    # Preserve exact sent payload and full provider receipt together, privately.
    save(STATE / (pending_id + '-sent.json'), {'message': message, 'provider_receipt': receipt,
         'message_id': message_id, 'thread_id': thread_id, 'recorded_at': now.isoformat(), 'window': pending})
    state.update(cursor=pending['through'], last_sent_on=now.astimezone(OSLO).date().isoformat(),
                 last_message_id=message_id, last_thread_id=thread_id)
    del state['pending']
    save(STATE / 'state.json', state)
    with (STATE / 'reporting.md').open('a', encoding='utf-8') as log:
        log.write(f'\n- {now.isoformat()}: exact approved daily notification sent to {RECIPIENT}; '
                  f'Gmail message {message_id}, thread {thread_id}; receipt `{pending_id}-sent.json`.\n')
    return {'status': 'sent_recorded', 'message_id': message_id, 'thread_id': thread_id}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'record'])
    parser.add_argument('--pending-id')
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    try:
        with locked():
            if args.command == 'record':
                if not args.pending_id or not args.receipt:
                    parser.error('record requires --pending-id and --receipt')
                result = record(args.pending_id, args.receipt)
            else:
                result = check()
        print(json.dumps(result, ensure_ascii=False))
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f'Comment notification stopped: {exc}\n')


if __name__ == '__main__':
    main()
