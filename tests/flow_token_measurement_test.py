import importlib.util
from pathlib import Path
import unittest


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
