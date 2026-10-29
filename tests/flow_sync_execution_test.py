import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/exercise-flow-sync.py'


class FlowSyncExecutionTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('flow_execution', SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_real_checker_gates_draft_reuse_and_ast_cosmetic_work(self):
        calls = []

        def model(phase, inputs):
            calls.append((phase, inputs))
            if phase == 'synchronization':
                return {'flow': 'flowchart TD\nA["return 3"]\n'}
            return {'feature': inputs['feature'], 'fingerprint': inputs['fingerprint'],
                    'reviewer': inputs['reviewer'], 'verdict': 'pass', 'findings': [],
                    'evidence': ['app.py#first', 'docs/flows/one.mmd'], 'limitations': []}

        with tempfile.TemporaryDirectory() as directory:
            report = self.module.exercise(Path(directory), model)
        self.assertTrue(report['complete'])
        self.assertEqual([phase for phase, _ in calls], ['synchronization', 'semantic_review'])
        self.assertEqual([event['model_calls'] for event in report['events']], [0, 2, 0, 0])
        self.assertEqual(report['events'][1]['affected'], ['one'])
        self.assertEqual(report['events'][2]['checker_exit'], 0)
        self.assertEqual(report['events'][3]['checker_exit'], 0)
        review_inputs = calls[1][1]
        self.assertEqual(review_inputs['validation']['execution']['exit_code'], 0)
        self.assertIn('test', review_inputs['validation']['test_commands'])
        self.assertIn('return 3', report['flows']['one'])
        self.assertIn('return 2', report['flows']['two'])

    def test_failed_review_cannot_become_a_passing_record(self):
        def model(phase, inputs):
            if phase == 'synchronization':
                return {'flow': 'flowchart TD\nA["wrong behavior"]\n'}
            return {'feature': inputs['feature'], 'fingerprint': inputs['fingerprint'],
                    'reviewer': inputs['reviewer'], 'verdict': 'fail',
                    'findings': ['flow disagrees with source']}

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                self.module.exercise(Path(directory), model)
            manifest = json.loads((Path(directory) / 'docs/flow-manifest.json').read_text())
            self.assertEqual(manifest['reviews'], [])

    def test_bad_flow_blocks_paid_review_at_structural_preflight(self):
        calls = []

        def model(phase, inputs):
            calls.append(phase)
            return {'flow': 'flowchart TD\nB["unmapped node"]\n'}

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                self.module.exercise(Path(directory), model)
        self.assertEqual(calls, ['synchronization'])

    def test_recovery_reuses_matching_generated_flow_but_never_review_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def fail_review(phase, inputs):
                if phase == 'synchronization':
                    return {'flow': 'flowchart TD\nA["return 3"]\n'}
                return {'feature': inputs['feature'], 'fingerprint': inputs['fingerprint'],
                        'reviewer': inputs['reviewer'], 'verdict': 'incomplete', 'findings': []}
            with self.assertRaises(ValueError):
                self.module.exercise(root, fail_review)
            names = ['app.py', 'package.json', 'docs/flow-manifest.json', 'docs/flows/one.mmd', 'docs/flows/two.mmd']
            reuse = {'failure_artifacts': {name: (root / name).read_text() for name in names}}
        calls = []
        def review(phase, inputs):
            calls.append(phase)
            self.assertIn('diff --git', inputs['raw_diff'])
            self.assertTrue(inputs['candidate_snapshot'])
            return {'feature': inputs['feature'], 'fingerprint': inputs['fingerprint'],
                    'reviewer': inputs['reviewer'], 'verdict': 'pass', 'findings': [],
                    'evidence': ['app.py#first'], 'limitations': []}
        with tempfile.TemporaryDirectory() as directory:
            report = self.module.exercise(Path(directory), review, reuse)
        self.assertEqual(calls, ['semantic_review'])
        self.assertEqual(report['events'][1]['model_calls'], 1)
