"""Check notification decisions with synthetic local state; no Gmail or D1 calls."""
import importlib.util
import json
from pathlib import Path
import tempfile
from datetime import datetime, timezone, timedelta

spec = importlib.util.spec_from_file_location('comment_notifications', Path(__file__).with_name('comment_notifications.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main():
    with tempfile.TemporaryDirectory() as folder:
        module.STATE = Path(folder)
        now = datetime(2026, 11, 9, 8, tzinfo=timezone.utc)
        calls = []
        def query(after):
            calls.append(after)
            return {'through': 5, 'new_count': 0}
        module.remote_window = query
        try:
            module.check(now)
        except OSError:
            pass
        else:
            raise AssertionError('Missing owner approval was accepted')
        assert calls == []
        message = {'to': module.RECIPIENT, 'subject': 'Synthetic owner notification',
                   'payload': {'mime_type': 'text/html', 'body': {'content': '<p>Local test.</p>'}}}
        approval = {'status': 'approved', 'approved_at': now.isoformat(), 'owner_instruction': 'Synthetic test only',
                    'recurring_exception': True, 'message': message, 'message_sha256': module.message_hash(message)}
        module.save(module.STATE / 'approval.json', approval)
        assert module.check(now)['status'] == 'no_new_comments'
        assert module.read_state()['cursor'] == 5
        def new_comments(after):
            assert after == 5
            return {'through': 8, 'new_count': 3}
        module.remote_window = new_comments
        result = module.check(now)
        assert result['status'] == 'ready_for_approved_send'
        assert result['gmail_args'] == message
        assert module.check(now)['status'] == 'delivery_uncertain'
        assert module.read_state()['cursor'] == 5
        receipt = module.STATE / 'test-provider.json'
        module.save(receipt, {'id': 'test-only'})
        try:
            module.record(result['pending_id'], receipt, now)
        except ValueError:
            pass
        else:
            raise AssertionError('Incomplete provider receipt was accepted')
        assert module.read_state()['cursor'] == 5
        approval['message']['subject'] = 'Changed without fresh approval'
        module.save(module.STATE / 'approval.json', approval)
        try:
            module.record(result['pending_id'], receipt, now)
        except ValueError:
            pass
        else:
            raise AssertionError('Changed message was accepted')
        approval['message']['subject'] = message['subject'] = 'Synthetic owner notification'
        module.save(module.STATE / 'approval.json', approval)
        module.save(receipt, {'structuredContent': {'id': 'synthetic-message-id', 'thread_id': 'synthetic-thread-id'}})
        assert module.record(result['pending_id'], receipt, now)['status'] == 'sent_recorded'
        assert module.read_state()['cursor'] == 8
        assert module.check(now)['status'] == 'already_sent_today'
        saved = json.loads((module.STATE / (result['pending_id'] + '-sent.json')).read_text())
        assert saved['message'] == message and saved['provider_receipt']['structuredContent']['id'] == 'synthetic-message-id'
        module.remote_window = lambda after: {'through': after, 'new_count': 0}
        assert module.check(now + timedelta(days=1))['status'] == 'no_new_comments'
        # Date cap follows Oslo, including UTC-day boundaries and daylight saving.
        module.save(module.STATE / 'state.json', {'cursor': 8, 'last_sent_on': '2026-11-10'})
        assert module.check(datetime(2026, 11, 9, 23, 5, tzinfo=timezone.utc))['status'] == 'already_sent_today'
        assert module.OSLO.utcoffset(datetime(2027, 7, 1)).total_seconds() == 7200
    print('Notification checks passed: approval gate, no mail on zero, exact payload, pending/retry guard, real-receipt requirement, one per Oslo date, cursor commit and private receipts. No email or production query performed.')


if __name__ == '__main__':
    main()
