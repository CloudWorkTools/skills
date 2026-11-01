import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'agent-ops.py'


class AgentOpsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def cli(self, *args, data='', ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                                input=data, text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, ok, result.stderr)
        return json.loads(result.stdout)

    def snapshot(self):
        return {'schema_version': 1, 'source': {'repository': 'repo', 'revision': 'abc', 'version': '1.0'},
                'phase': 'published', 'status': 'unknown', 'components': {
                    'viewer': {'status': 'published', 'phase': 'verification', 'liveness': 'unknown',
                               'taskId': 'task1', 'dispatchId': 'dispatch1',
                               'evidencepath': '/private/evidence'}}}

    def current(self, data, *extra, ok=True):
        return self.cli('current', '--path', self.root / 'CURRENT.json',
                        '--repository', 'repo', '--revision', 'abc', '--version', '1.0',
                        *extra, data=json.dumps(data), ok=ok)

    def test_summary_bounds_nested_json_without_text_truncation(self):
        value = {'hashes': {str(i): 'x' * 500 for i in range(10000)},
                 'result': {'phase': 'failed', 'status': 'unknown', 'error': {'code': 'denied'},
                            'token': 'DO_NOT_PRINT', 'nested': [{'dispatchId': str(i)} for i in range(100)]}}
        result = self.cli('summary', data=json.dumps(value))
        self.assertLess(len(json.dumps(result)), 8192)
        self.assertGreater(result['omitted_fields'], 0)
        self.assertNotIn('DO_NOT_PRINT', json.dumps(result))
        self.assertNotIn('truncated', json.dumps(result))
        self.assertIn('failed', json.dumps(result))
        self.assertIn('unknown', json.dumps(result))

    def test_all_mail_types_accounted_and_no_silent_discard(self):
        messages = [{'type': 'worker_done', 'outcome': 'unknown'}, {'type': 'heartbeat', 'body': ''}, {'type': 'heartbeat', 'body': 'important'},
                    {'type': 'worker_done', 'body': 'failed', 'outcome': 'failed', 'dispatchId': 'old'}]
        result = self.cli('summary', data=json.dumps({'result': {'deliveryId': 'd1', 'count': 4, 'messages': messages}}))
        self.assertEqual(result['message_counts'], {'heartbeat': 2, 'worker_done': 2})
        self.assertEqual(result['nonempty_bodies'], 2)
        self.assertTrue(result['handling_required'])
        self.assertIn('old', json.dumps(result))

    def test_malformed_and_excessively_nested_input_fail_safely(self):
        for value in ('not-json SECRET', '[' * 1100 + '0' + ']' * 1100, '{"a":NaN}'):
            result = self.cli('summary', data=value, ok=False)
            self.assertEqual(result['error'], 'invalid_input')
            self.assertNotIn('SECRET', json.dumps(result))

    def test_oversize_rejected(self):
        self.cli('summary', data=' ' * (8 * 1024 * 1024 + 1), ok=False)

    def test_private_immutable_raw_archive(self):
        raw = self.root / 'attempt.json'
        result = self.cli('summary', '--raw', raw, data='{"status":"unknown","token":"private"}')
        self.assertEqual(raw.stat().st_mode & 0o777, 0o600)
        self.assertEqual(result['evidencepath'], str(raw))
        self.cli('summary', '--raw', raw, data='{}', ok=False)
        self.assertIn('private', raw.read_text())

    def test_snapshot_transition_requires_cas_and_identity(self):
        before = self.current(self.snapshot())
        changed = self.snapshot()
        changed['components']['viewer']['status'] = 'failed'
        self.current(changed, ok=False)
        self.current(changed, '--expected-digest', 'stale', ok=False)
        result = self.current(changed, '--expected-digest', before['digest'])
        self.assertNotEqual(before['digest'], result['digest'])
        self.assertEqual(json.loads((self.root / 'CURRENT.json').read_text()), changed)
        changed['source']['revision'] = 'old'
        self.current(changed, '--expected-digest', result['digest'], ok=False)

    def test_invalid_snapshot_preserves_previous(self):
        before = self.current(self.snapshot())
        original = (self.root / 'CURRENT.json').read_bytes()
        for key, value in [('components', []), ('status', 'invented'), ('source', {})]:
            changed = self.snapshot()
            changed[key] = value
            self.current(changed, '--expected-digest', before['digest'], ok=False)
            self.assertEqual((self.root / 'CURRENT.json').read_bytes(), original)

    def load(self):
        spec = importlib.util.spec_from_file_location('agent_ops', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_failed_atomic_replace_retains_current(self):
        module = self.load()
        path = self.root / 'CURRENT.json'
        path.write_text('previous')
        with patch.object(module.os, 'replace', side_effect=OSError('failure')):
            with self.assertRaises(OSError):
                module.atomic_write(path, b'new')
        self.assertEqual(path.read_text(), 'previous')
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['CURRENT.json'])

    def test_wait_contract_has_no_ack_or_lifecycle_mutation(self):
        module = self.load()
        calls = []
        def run(argv, **kwargs):
            calls.append(argv)
            if '--help' in argv:
                return subprocess.CompletedProcess(argv, 0, '--wait --types --timeout-ms --json --terminal', '')
            return subprocess.CompletedProcess(argv, 0, '{"result":{"count":0,"messages":[],"timedOut":true}}', '_keepalive')
        with patch.object(module.subprocess, 'run', side_effect=run):
            result = module.wait('/orca', 'terminal', 55000)
        self.assertEqual(result['result']['count'], 0)
        self.assertIn('worker_done,escalation,question', calls[-1])
        self.assertNotIn('--ack', calls[-1])
        with self.assertRaises(ValueError):
            module.wait('/orca', 'terminal', 55001)

    def test_wait_failure_preserves_structured_error(self):
        module = self.load()
        def run(argv, **kwargs):
            if '--help' in argv:
                return subprocess.CompletedProcess(argv, 0, '--wait --types --timeout-ms --json --terminal', '')
            return subprocess.CompletedProcess(argv, 1, '{"ok":false,"error":{"code":"stale_dispatch"}}', '')
        with patch.object(module.subprocess, 'run', side_effect=run):
            result = module.wait('/orca', 'terminal', 1)
        self.assertEqual(result['command_exit_code'], 1)
        self.assertEqual(result['error']['error']['code'], 'stale_dispatch')

    def test_empty_heartbeat_still_needs_handling_and_long_fields_are_bounded(self):
        result = self.cli('summary', data=json.dumps({'messages': [{'type': 'heartbeat', 'body': ''}],
                                                     'phase': 'x' * 100000}))
        self.assertTrue(result['handling_required'])
        self.assertLess(len(json.dumps(result)), 2000)
        self.cli('summary', data='{"status":"active","status":"failed"}', ok=False)

    def test_raw_cannot_be_current_and_raw_is_retained_for_parse_failure(self):
        path = self.root / 'CURRENT.json'
        self.current(self.snapshot(), '--raw', path, ok=False)
        self.assertFalse(path.exists())
        raw = self.root / 'malformed.json'
        self.cli('summary', '--raw', raw, data='malformed', ok=False)
        self.assertEqual(raw.read_text(), 'malformed')

    def test_known_credential_patterns_are_not_summary_metadata(self):
        marker = 'github_pat_FAKE_ONLY_FOR_TEST'
        result = self.cli('summary', data=json.dumps({'status': marker,
            'nested': {marker: {'dispatchId': 'ctx_test'}},
            'repository': 'https://private-credential@example.invalid/repo'}))
        self.assertNotIn(marker, json.dumps(result))
        self.assertNotIn('private-credential', json.dumps(result))

    def test_review_and_publication_states_preserve_failure_and_pending_signals(self):
        result = self.cli('summary', data=json.dumps({'verdict': 'fail',
            'state': 'published-but-verification-pending', 'findings': [{'severity': 'high'}]}))
        self.assertEqual(result['signals']['failure'], 1)
        self.assertEqual(result['signals']['unknown'], 1)
        self.assertIn('fail', json.dumps(result))
        self.assertIn('published-but-verification-pending', json.dumps(result))

    def test_coordinator_wait_selects_run_without_terminal_or_ack(self):
        module = self.load()
        calls = []
        def run(argv, **kwargs):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0,
                '--wait --types --timeout-ms --json --run' if '--help' in argv else
                '{"result":{"count":0}}', '')
        with patch.object(module.subprocess, 'run', side_effect=run):
            module.wait('/orca', None, 1, 'run_test')
        self.assertIn('--run', calls[-1])
        self.assertNotIn('--terminal', calls[-1])
        self.assertNotIn('--ack', calls[-1])

    def test_help(self):
        result = subprocess.run([sys.executable, str(SCRIPT), '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('current', result.stdout)


if __name__ == '__main__':
    unittest.main()
