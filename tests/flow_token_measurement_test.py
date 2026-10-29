import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'measure-flow-tokens.py'


class FlowTokenMeasurementTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('flow_tokens', SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def result(self):
        return {
            'is_error': False,
            'result': '{"sync":false,"review_dispatches":0,"complete":false,"recovery_remaining":null}',
            'modelUsage': {
                'target': {'inputTokens': 2, 'outputTokens': 9,
                           'cacheCreationInputTokens': 100, 'cacheReadInputTokens': 200,
                           'thinkingTokens': 5, 'cacheCreationEphemeral1hInputTokens': 100},
                'helper': {'inputTokens': 10, 'outputTokens': 3,
                           'cacheCreationInputTokens': 0, 'cacheReadInputTokens': 20},
            },
        }

    def test_counts_all_models_and_cache_without_double_counting(self):
        sample = self.module.measurement(self.result(), 'target')
        self.assertEqual(sample['total'], {
            'uncached_input': 12, 'cache_creation': 100, 'cache_read': 220,
            'input': 332, 'output': 12,
        })
        self.assertEqual(sample['models']['target']['input'], 302)
        self.assertEqual(sample['models']['target']['output'], 9)
        self.assertEqual(sample['decision']['review_dispatches'], 0)

    def test_missing_usage_wrong_model_and_failed_calls_are_rejected(self):
        for mutate in (
            lambda result: result.pop('modelUsage'),
            lambda result: result['modelUsage'].pop('target'),
            lambda result: result.update(is_error=True),
            lambda result: result['modelUsage']['target'].pop('cacheReadInputTokens'),
            lambda result: result['modelUsage']['target'].update(outputTokens=-1),
        ):
            result = self.result()
            mutate(result)
            with self.subTest(result=result), self.assertRaises(ValueError):
                self.module.measurement(result, 'target')

    def test_invalid_or_unstructured_decisions_are_rejected(self):
        result = self.result()
        result.pop('result')
        with self.assertRaises(ValueError):
            self.module.measurement(result, 'target')
        for decision in ('not JSON', '[]', '{}',
                         '{"sync":false,"review_dispatches":true,"complete":false,"recovery_remaining":null}'):
            result = self.result()
            result['result'] = decision
            with self.subTest(decision=decision), self.assertRaises(ValueError):
                self.module.measurement(result, 'target')

    def test_failed_call_keeps_known_usage_and_phase_before_raising(self):
        result = self.result()
        result['is_error'] = True
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / 'usage.jsonl'
            response = subprocess.CompletedProcess([], 1, json.dumps(result), 'failure')
            with mock.patch.object(self.module.subprocess, 'run', return_value=response):
                with self.assertRaises(RuntimeError):
                    self.module.invoke([], 'prompt', directory, ledger, 'semantic_review', 'attempt-1', 'target')
            row = json.loads(ledger.read_text())
            self.assertEqual(row['status'], 'failed')
            self.assertEqual(row['phase'], 'semantic_review')
            self.assertEqual(row['usage']['total']['input'], 332)
            summary = self.module.usage_summary(ledger)
            self.assertEqual(summary['total_tokens'], 344)
            self.assertEqual(summary['phases']['semantic_review']['failed_attempts'], 1)
            self.assertEqual(summary['phases']['semantic_review']['known']['input'], 332)
            self.assertEqual(summary['phases']['semantic_review']['models']['target']['input'], 302)

    def test_timeout_and_bad_decision_remain_visible_without_fake_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / 'usage.jsonl'
            with mock.patch.object(self.module.subprocess, 'run', side_effect=subprocess.TimeoutExpired([], 180)):
                with self.assertRaises(RuntimeError):
                    self.module.invoke([], 'prompt', directory, ledger, 'material_recovery', 'timeout', 'target')
            summary = self.module.usage_summary(ledger)
            self.assertIsNone(summary['total_tokens'])
            self.assertEqual(summary['unknown_attempts'], 1)
            result = self.result()
            result['result'] = 'broken JSON'
            response = subprocess.CompletedProcess([], 0, json.dumps(result), '')
            with mock.patch.object(self.module.subprocess, 'run', return_value=response):
                with self.assertRaises(RuntimeError):
                    self.module.invoke([], 'prompt', directory, ledger, 'validation', 'bad-json', 'target')
            rows = [json.loads(line) for line in ledger.read_text().splitlines()]
            self.assertEqual(rows[-1]['status'], 'invalid_response')
            self.assertEqual(rows[-1]['usage']['total']['input'], 332)

    def test_summary_deduplicates_attempts_and_rejects_conflicting_reuse(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / 'usage.jsonl'
            response = subprocess.CompletedProcess([], 0, json.dumps(self.result()), '')
            with mock.patch.object(self.module.subprocess, 'run', return_value=response):
                self.module.invoke([], 'prompt', directory, ledger, 'synchronization', 'same-id', 'target')
            row = ledger.read_text()
            ledger.write_text(row + row)
            self.assertEqual(self.module.usage_summary(ledger)['attempts'], 1)
            changed = json.loads(row)
            changed['phase'] = 'validation'
            ledger.write_text(row + json.dumps(changed) + '\n')
            with self.assertRaises(ValueError):
                self.module.usage_summary(ledger)

    def test_review_context_uses_configured_command_and_recorded_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'package.json').write_text(json.dumps({'scripts': {'test': 'custom-test --pattern "*_test.py"'}}))
            (root / '.github/workflows').mkdir(parents=True)
            (root / '.github/workflows/tests.yml').write_text('run: npm test\n')
            evidence = {'command': 'npm test', 'exit_code': 0, 'candidate': 'tree-1'}
            context = self.module.review_context(root, evidence)
            self.assertEqual(context['test_commands']['test'], 'custom-test --pattern "*_test.py"')
            self.assertEqual(context['execution'], evidence)
            self.assertEqual(context['ci']['.github/workflows/tests.yml'], 'run: npm test\n')

    def test_unavailable_telemetry_does_not_block_valid_task_output(self):
        result = self.result()
        result.pop('modelUsage')
        response = subprocess.CompletedProcess([], 0, json.dumps(result), '')
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / 'usage.jsonl'
            with mock.patch.object(self.module.subprocess, 'run', return_value=response):
                value = self.module.invoke([], 'prompt', directory, ledger, 'synchronization', 'unknown', 'target')
            self.assertFalse(value['sync'])
            summary = self.module.usage_summary(ledger)
            self.assertEqual(summary['unknown_attempts'], 1)
            self.assertIsNone(summary['total_tokens'])

    def test_failed_experiment_exposes_ledger_and_usage_without_retrying(self):
        result = self.result()
        result['is_error'] = True
        response = subprocess.CompletedProcess([], 1, json.dumps(result), '')
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'experiment.json'
            with mock.patch.object(sys, 'argv', ['measure', '--output', str(output), '--model', 'target']), \
                 mock.patch.object(self.module, 'git', return_value='fixture-input'), \
                 mock.patch.object(self.module.subprocess, 'check_output', return_value='test-cli'), \
                 mock.patch.object(self.module.subprocess, 'run', return_value=response) as calls:
                with self.assertRaises(RuntimeError):
                    self.module.main()
            report = json.loads(output.read_text())
            self.assertFalse(report['complete'])
            self.assertTrue((output.parent / report['usage_ledger']).exists())
            self.assertEqual(report['usage']['total_tokens'], 344)
            self.assertEqual(calls.call_count, 1)
