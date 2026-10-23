import importlib.util
import json
import os
import pathlib
import runpy
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

CHECKER = pathlib.Path(__file__).resolve().parents[1] / 'skills/flow-docs-sync/scripts/flow_checker.py'


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'fixture@example.test')
        self.git('config', 'user.name', 'Fixture')
        self.write('app.py', 'VALUE = 1\ndef first():\n    return VALUE\ndef second():\n    return 2\n')
        self.manifest = {'version': 1, 'scope': {'include': ['*.py'], 'exclude': {}},
                         'sources': [{'path': 'app.py', 'kind': 'python', 'md5': ''}],
                         'features': [], 'reviews': []}
        for feature, symbol in [('one', 'first'), ('two', 'second')]:
            flow = 'docs/' + feature + '.mmd'
            self.write(flow, 'flowchart TD\nA["work"]\n')
            self.manifest['features'].append({'id': feature, 'flow': flow,
                'mappings': [{'node': 'A', 'path': 'app.py', 'symbol': symbol}]})
        self.save()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.STDOUT)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def save(self):
        self.write('docs/flow-manifest.json', json.dumps(self.manifest))

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(CHECKER), *args, '--root', str(self.root)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0 if ok else 1, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def baseline(self):
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.git('add', '.')
        self.git('commit', '-qm', 'baseline')

    def review(self, feature):
        fingerprint = self.cli('fingerprint', '--feature', feature, '--base', 'HEAD').strip()
        evidence = 'reviews/' + feature + '.json'
        record = {'feature': feature, 'fingerprint': fingerprint, 'reviewer': 'independent', 'verdict': 'pass'}
        self.write(evidence, json.dumps({**record, 'findings': []}))
        self.manifest['reviews'] = [r for r in self.manifest['reviews'] if r['feature'] != feature]
        self.manifest['reviews'].append({**record, 'evidence': evidence})
        self.save()

    def test_valid_and_feature_local_review(self):
        self.baseline()
        self.cli('check', '--base', 'HEAD')
        self.write('app.py', 'VALUE = 1\ndef first():\n    return 42\ndef second():\n    return 2\n')
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.assertIn('one', self.cli('check', '--base', 'HEAD', ok=False))
        self.review('one')
        self.cli('check', '--base', 'HEAD')
        self.write('app.py', 'VALUE = 1\ndef first():\n    return 43\ndef second():\n    return 2\n')
        self.cli('snapshot')
        self.cli('check', '--base', 'HEAD', ok=False)

    def test_cosmetic_requires_md5_refresh_but_no_review(self):
        self.baseline()
        with (self.root / 'app.py').open('a') as stream:
            stream.write('\n# cosmetic\n')
        self.write('app.py', (self.root / 'app.py').read_text().replace('return 2', 'return    2'))
        self.assertIn('md5', self.cli('check', '--base', 'HEAD', ok=False).lower())
        self.cli('snapshot')
        self.cli('check', '--base', 'HEAD')

    def test_context_change_requires_both_reviews(self):
        self.baseline()
        self.write('app.py', 'import os\nVALUE = 2\ndef first():\n    return VALUE\ndef second():\n    return 2\n')
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.review('one')
        self.assertIn('two', self.cli('check', '--base', 'HEAD', ok=False))
        self.review('two')
        self.cli('check', '--base', 'HEAD')

    def test_inventory_and_mapping_gaps(self):
        self.baseline()
        for name, content in [('new.py', 'def added(): pass\n'), ('app.py', 'def first(): pass\ndef second(): pass\ndef added(): pass\n')]:
            with self.subTest(name=name):
                old = (self.root / 'app.py').read_text()
                self.write(name, content)
                self.cli('snapshot')
                self.cli('check', '--base', 'HEAD', ok=False)
                if name == 'new.py':
                    (self.root / name).unlink()
                else:
                    self.write(name, old)
        self.manifest['features'][0]['mappings'] = []
        self.save()
        self.cli('check', '--base', 'HEAD', ok=False)

    def test_deleted_feature_and_scope_reduction_need_review(self):
        self.baseline()
        self.manifest['features'].pop()
        self.save()
        self.cli('check', '--base', 'HEAD', ok=False)
        self.manifest['features'].append({'id':'two', 'flow':'docs/two.mmd', 'mappings':[{'node':'A','path':'app.py','symbol':'second'}]})
        self.manifest['scope']['include'] = []
        self.save()
        self.cli('check', '--base', 'HEAD', ok=False)

    def test_fake_evidence_rejected(self):
        self.baseline()
        self.write('docs/one.mmd', 'flowchart LR\nA["changed"]\n')
        self.review('one')
        self.write('reviews/one.json', '{}')
        self.cli('check', '--base', 'HEAD', ok=False)

    def test_bad_diagrams(self):
        self.baseline()
        for content in ['flowchart TD\nsubgraph x\nend\n', 'flowchart TD\nA --> B\n', 'junk', 'flowchart TD\nA["a"]\nA["duplicate"]\n']:
            with self.subTest(content=content):
                self.write('docs/one.mmd', content)
                self.cli('check', '--base', 'HEAD', ok=False)
        (self.root / 'docs/one.mmd').unlink()
        self.cli('check', '--base', 'HEAD', ok=False)

    def test_plantuml_and_branch_cycle(self):
        self.baseline()
        self.write('docs/one.mmd', '@startuml\nstate "work" as A\nA --> A : again\n@enduml\n')
        self.review('one')
        self.cli('check', '--base', 'HEAD')

    def test_complexity_limits(self):
        self.baseline()
        self.manifest['limits'] = {'nodes': 1, 'branch_depth': 0}
        self.manifest['features'][0]['mappings'].append({'node':'B','path':'app.py','symbol':'first'})
        self.write('docs/one.mmd', 'flowchart TD\nA["a"]\nB["b"]\nA --> A\nA --> B\n')
        self.save()
        self.cli('check', '--base', 'HEAD', ok=False)
        self.manifest['limits']['nodes'] = 25
        self.save()
        self.cli('check', '--base', 'HEAD', ok=False)

    def test_unsafe_and_symlink_paths(self):
        self.baseline()
        self.manifest['features'][0]['flow'] = '../outside'
        self.save()
        self.cli('check', '--base', 'HEAD', ok=False)
        self.manifest['features'][0]['flow'] = 'docs/one.mmd'
        self.save()
        (self.root / 'app.py').unlink()
        (self.root / 'app.py').symlink_to('/etc/passwd')
        self.cli('snapshot', ok=False)

    def test_staged_reads_and_snapshot_never_stages(self):
        self.baseline()
        self.write('app.py', 'broken python source !')
        self.cli('check', '--base', 'HEAD', '--staged')
        self.cli('check', '--base', 'HEAD', ok=False)
        self.cli('snapshot', '--staged', ok=False)
        self.git('checkout', '--', 'app.py')
        self.write('docs/one.mmd', 'invalid graph')
        self.cli('check', '--base', 'HEAD', '--staged')
        self.git('add', 'docs/one.mmd')
        self.git('restore', '--source=HEAD', '--worktree', '--', 'docs/one.mmd')
        self.cli('check', '--base', 'HEAD', '--staged', ok=False)

    def test_missing_base_and_dependency_cycle(self):
        self.baseline()
        self.cli('check', '--base', 'nonexistent-ref', ok=False)
        self.manifest['features'][0]['depends_on'] = ['two']
        self.manifest['features'][1]['depends_on'] = ['one']
        self.save()
        self.cli('check', '--base', 'HEAD', ok=False)

    def test_retirement_requires_review_and_retains_old_identity(self):
        self.baseline()
        self.write('app.py', 'VALUE = 1\ndef second():\n    return 2\n')
        self.manifest['features'][0]['retired'] = True
        self.manifest['features'][0]['mappings'] = []
        self.save()
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.cli('check', '--base', 'HEAD', ok=False)
        self.review('one')
        self.review('two')  # Module definition header changed too.
        self.cli('check', '--base', 'HEAD')

    def test_nonpython_file_removal_with_retirement(self):
        self.write('settings.json', '{"enabled":true}')
        self.manifest['scope']['include'].append('settings.json')
        self.manifest['sources'].append({'path':'settings.json','kind':'file'})
        self.manifest['features'].append({'id':'settings','flow':'docs/settings.mmd',
            'mappings':[{'node':'A','path':'settings.json'}]})
        self.write('docs/settings.mmd', 'flowchart TD\nA["settings"]\n')
        self.save()
        self.baseline()
        (self.root / 'settings.json').unlink()
        self.manifest['sources'].pop()
        self.manifest['features'][-1].update(retired=True, mappings=[])
        self.save()
        self.cli('check', '--base', 'HEAD', ok=False)
        self.review('settings')
        self.cli('check', '--base', 'HEAD')

    def test_dependents_inherit_source_changes(self):
        self.manifest['features'][1]['depends_on'] = ['one']
        self.save()
        self.baseline()
        self.write('app.py', 'VALUE = 1\ndef first():\n    return 42\ndef second():\n    return 2\n')
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.review('one')
        self.assertIn('two', self.cli('check', '--base', 'HEAD', ok=False))
        self.review('two')
        self.cli('check', '--base', 'HEAD')

    def test_policy_and_base_bind_reviews(self):
        self.write('policy.txt', 'initial')
        self.manifest['policy_inputs'] = ['policy.txt']
        self.save()
        self.baseline()
        self.write('policy.txt', 'changed')
        self.review('one')
        self.review('two')
        self.cli('check', '--base', 'HEAD')
        self.git('add', '.')
        self.git('commit', '-qm', 'policy')
        self.write('docs/one.mmd', 'flowchart TD\nA["new"]\n')
        self.cli('check', '--base', 'HEAD', ok=False)

    def test_weird_filename_is_nul_safe(self):
        self.write('odd\nname.py', 'def odd(): return 1\n')
        self.manifest['sources'].append({'path':'odd\nname.py','kind':'python'})
        self.manifest['features'][0]['mappings'].append({'node':'A','path':'odd\nname.py','symbol':'odd'})
        self.save()
        self.baseline()
        self.cli('check', '--base', 'HEAD', '--staged')

    def test_missing_source_and_deleted_symbol_fail(self):
        self.baseline()
        (self.root / 'app.py').unlink()
        self.cli('snapshot', ok=False)
        self.cli('check', '--base', 'HEAD', ok=False)
        self.write('app.py', 'def first(): pass\n')
        self.cli('snapshot')
        self.assertIn('symbol', self.cli('check', '--base', 'HEAD', ok=False))

    def test_initial_baseline_requires_all_reviews(self):
        self.git('add', 'app.py')
        self.git('commit', '-qm', 'before adoption')
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.assertIn('baseline', self.cli('check', '--base', 'HEAD', ok=False))
        self.review('one')
        self.review('two')
        self.cli('check', '--base', 'HEAD')

    def test_large_graph_and_deep_branches_rejected(self):
        self.baseline()
        self.write('docs/one.mmd', 'flowchart TD\n' + ''.join('N%d["node"]\n' % n for n in range(26)))
        self.assertIn('node limit', self.cli('check', '--base', 'HEAD', ok=False))
        nodes = ['N%d' % n for n in range(10)]
        diagram = 'flowchart TD\n' + ''.join(n + '["node"]\n' for n in nodes)
        diagram += ''.join('N%d --> N%d\nN%d --> N9\n' % (n,n+1,n) for n in range(9))
        self.write('docs/one.mmd', diagram)
        self.manifest['limits'] = {'branch_depth': 7}
        self.save()
        self.assertIn('depth limit', self.cli('check', '--base', 'HEAD', ok=False))

    def test_signature_context_docstrings_and_nested_methods(self):
        self.write('app.py', 'def first(default=1):\n    """meaningful"""\n    return default\nclass Example:\n    flag = 1\n    def second(self):\n        def nested(): return 2\n        return nested()\n')
        self.manifest['features'][1]['mappings'][0]['symbol'] = 'Example.second'
        self.save()
        self.baseline()
        self.write('app.py', (self.root / 'app.py').read_text().replace('default=1', 'default=2'))
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.review('one')
        self.assertIn('two', self.cli('check', '--base', 'HEAD', ok=False))
        self.review('two')
        self.cli('check', '--base', 'HEAD')
        self.write('app.py', (self.root / 'app.py').read_text().replace('meaningful', 'new docstring'))
        self.cli('snapshot')
        self.assertIn('one', self.cli('check', '--base', 'HEAD', ok=False))

    def test_subdirectory_root_rejected(self):
        self.baseline()
        result = subprocess.run([sys.executable, str(CHECKER), 'check', '--base', 'HEAD',
            '--root', str(self.root / 'docs')], text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Git root', result.stderr)

    def test_huge_complexity_budget_rejected(self):
        self.baseline()
        self.manifest['limits'] = {'nodes': 1000000}
        self.save()
        self.assertIn('1000', self.cli('check', '--base', 'HEAD', ok=False))

    def test_module_docstring_is_semantic_context(self):
        self.write('app.py', '"""module documentation"""\n' + (self.root / 'app.py').read_text())
        self.baseline()
        self.write('app.py', (self.root / 'app.py').read_text().replace('module documentation', 'changed documentation'))
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.review('one')
        self.assertIn('two', self.cli('check', '--base', 'HEAD', ok=False))

    def test_real_precommit_rejects_stale_index_then_accepts_review(self):
        self.manifest['scope']['include'] = ['app.py']
        self.save()
        self.baseline()
        self.write('tools/flow-docs/flow_checker.py', CHECKER.read_text())
        hook = CHECKER.parent.parent / 'assets/pre-commit'
        self.write('.git/hooks/pre-commit', hook.read_text())
        (self.root / '.git/hooks/pre-commit').chmod(0o755)
        self.write('app.py', 'VALUE = 1\ndef first():\n    return 42\ndef second():\n    return 2\n')
        self.git('add', 'app.py')
        failed = subprocess.run(['git', '-C', str(self.root), 'commit', '-qm', 'stale'], capture_output=True, text=True)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn('md5', failed.stderr)
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.review('one')
        self.git('add', '.')
        self.git('commit', '-qm', 'reviewed')
        self.assertEqual(self.git('log', '-1', '--format=%s').strip(), b'reviewed')

    def test_optional_parser_missing_fails_explicitly_without_fallback(self):
        self.baseline()
        self.write('client.ts', 'function render() { return 1; }\n')
        self.manifest['sources'].append({'path': 'client.ts', 'kind': 'tree-sitter', 'language': 'typescript'})
        self.save()
        result = subprocess.run([sys.executable, '-S', str(CHECKER), 'snapshot', '--root', str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('optional', result.stderr.lower())
        self.assertIn('tree-sitter', result.stderr.lower())
        self.assertNotIn('unsupported source kind', result.stderr)
        manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.assertNotIn('md5', manifest['sources'][-1])
        # Unavailable optional packages must leave existing stdlib modes usable.
        self.manifest['sources'].pop()
        self.save()
        result = subprocess.run([sys.executable, '-S', str(CHECKER), 'check', '--base', 'HEAD',
                                 '--root', str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(importlib.util.find_spec('tree_sitter_language_pack'), 'optional tree-sitter parser not installed')
    def test_mixed_typescript_python_sql_ast_and_review_isolation(self):
        self.write('client.ts', 'export function render() { return 1; }\nexport function other() { return 2; }\n')
        self.write('schema.sql', 'CREATE TABLE users (id INT);\n')
        self.manifest['scope']['include'] += ['*.ts', '*.sql']
        self.manifest['sources'] += [
            {'path':'client.ts','kind':'tree-sitter','language':'typescript'},
            {'path':'schema.sql','kind':'tree-sitter','language':'sql'}]
        backend_mappings = [self.manifest['features'][0]['mappings'][0], self.manifest['features'][1]['mappings'][0]]
        self.manifest['features'][0]['mappings'] = [{'node':'A','path':'client.ts','symbol':'render'}]
        self.manifest['features'][1]['mappings'] = [{'node':'A','path':'client.ts','symbol':'other'}]
        self.manifest['features'][0]['depends_on'] = ['backend', 'schema']
        self.manifest['features'].append({'id':'backend', 'flow':'docs/backend.mmd', 'mappings': backend_mappings})
        self.write('docs/backend.mmd', 'flowchart TD\nA["backend"]\n')
        self.manifest['features'].append({'id':'schema','flow':'docs/schema.mmd',
            'mappings':[{'node':'A','path':'schema.sql','symbol':'table.users'}]})
        self.write('docs/schema.mmd', 'flowchart TD\nA["users"]\n')
        self.save()
        self.baseline()
        self.assertEqual(self.manifest['sources'][1]['language'], 'typescript')
        self.assertEqual(set(self.manifest['sources'][1]['symbols']), {'render', 'other'})
        self.cli('check', '--base', 'HEAD')
        self.write('client.ts', 'export function render() { return 42; }\nexport function other() { return 2; }\n')
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.review('one')
        self.cli('check', '--base', 'HEAD')
        # A SQL table change reaches the dependent frontend/backend feature.
        self.write('schema.sql', 'CREATE TABLE users (id INT, name TEXT);\n')
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.review('schema')
        self.assertIn('one', self.cli('check', '--base', 'HEAD', ok=False))
        self.review('one')
        self.cli('check', '--base', 'HEAD')
        # Backend behavior reaches its declared frontend dependent only.
        self.write('app.py', 'VALUE = 1\ndef first():\n    return 42\ndef second():\n    return 2\n')
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.review('backend')
        self.assertIn('one', self.cli('check', '--base', 'HEAD', ok=False))
        self.review('one')
        self.cli('check', '--base', 'HEAD')
        # Cosmetic TypeScript layout/comments still refresh MD5, without a review.
        self.write('client.ts', '// cosmetic\nexport function render() {\n return 42;\n}\nexport function other() { return 2; }\n')
        self.cli('snapshot')
        self.cli('check', '--base', 'HEAD')
        # Added functions cannot disappear behind a source-level snapshot.
        self.write('client.ts', (self.root / 'client.ts').read_text() + 'export function added() { return 3; }\n')
        self.cli('snapshot')
        self.assertIn('unmapped', self.cli('check', '--base', 'HEAD', ok=False))

    @unittest.skipUnless(importlib.util.find_spec('tree_sitter_language_pack'), 'optional tree-sitter parser not installed')
    def test_parser_mode_and_language_are_bound_to_review(self):
        self.write('client.ts', 'function render() { return 1; }\n')
        self.manifest['sources'].append({'path':'client.ts','kind':'file'})
        self.manifest['features'][0]['mappings'].append({'node':'A','path':'client.ts','symbol':'render'})
        self.save()
        self.baseline()
        before = self.cli('fingerprint', '--feature', 'one', '--base', 'HEAD')
        self.manifest['sources'][-1].update(kind='tree-sitter', language='typescript')
        self.save()
        self.cli('snapshot')
        self.manifest = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        typed = self.cli('fingerprint', '--feature', 'one', '--base', 'HEAD')
        self.assertNotEqual(before, typed)
        self.manifest['sources'][-1]['language'] = 'javascript'
        self.save()
        self.cli('snapshot')
        scripted = self.cli('fingerprint', '--feature', 'one', '--base', 'HEAD')
        self.assertNotEqual(typed, scripted)
        self.cli('check', '--base', 'HEAD', ok=False)

    @unittest.skipUnless(os.environ.get('FLOW_TEST_OLD_PYTHON'), 'FLOW_TEST_OLD_PYTHON not configured')
    def test_python_snapshot_portable_across_minor_versions(self):
        self.write('app.py', '"""runtime documentation"""\ndef first(default=None):\n    """function documentation"""\n    return (True, 1, 1.0, b"bytes", 1j, ..., None)\nclass Example:\n    def second(self):\n        return 2\n')
        self.manifest['features'][1]['mappings'][0]['symbol'] = 'Example.second'
        self.save()
        old_python = os.environ['FLOW_TEST_OLD_PYTHON']
        result = subprocess.run([old_python, str(CHECKER), 'snapshot', '--root', str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.git('add', '.')
        self.git('commit', '-qm', 'older-runtime snapshot')
        self.cli('check', '--base', 'HEAD')
        command = [str(CHECKER), 'fingerprint', '--root', str(self.root), '--base', 'HEAD', '--feature', 'one']
        old = subprocess.run([old_python, *command], capture_output=True, text=True)
        self.assertEqual(old.returncode, 0, old.stdout + old.stderr)
        self.assertEqual(old.stdout, self.cli('fingerprint', '--base', 'HEAD', '--feature', 'one'))

    def test_python_literal_types_remain_distinct(self):
        hashes = []
        for literal in ('True', '1', '1.0', 'b"text"', '"text"', '1j', 'None', '...'):
            self.write('app.py', 'def first():\n    return ' + literal + '\ndef second(): return 2\n')
            self.cli('snapshot')
            record = json.loads((self.root / 'docs/flow-manifest.json').read_text())['sources'][0]
            hashes.append(record['symbols']['first'])
        self.assertEqual(len(set(hashes)), len(hashes))

    def test_snapshot_atomic_replace_failure_preserves_manifest(self):
        manifest = self.root / 'docs/flow-manifest.json'
        original = manifest.read_bytes()
        namespace = runpy.run_path(str(CHECKER))
        args = types.SimpleNamespace(root=str(self.root), staged=False,
            manifest='docs/flow-manifest.json', command='snapshot')
        with mock.patch('os.replace', side_effect=OSError('simulated replacement failure')):
            with self.assertRaises(OSError):
                namespace['run'](args)
        self.assertEqual(manifest.read_bytes(), original)
        self.assertEqual(sorted(p.name for p in manifest.parent.iterdir()),
            ['flow-manifest.json', 'one.mmd', 'two.mmd'])

    def test_snapshot_preserves_manifest_mode(self):
        manifest = self.root / 'docs/flow-manifest.json'
        manifest.chmod(0o640)
        self.cli('snapshot')
        self.assertEqual(manifest.stat().st_mode & 0o777, 0o640)

    def test_snapshot_only_updates_registered_sources(self):
        self.baseline()
        old_features = self.manifest['features']
        self.write('new.py', 'print(42)\n')
        self.cli('snapshot')
        current = json.loads((self.root / 'docs/flow-manifest.json').read_text())
        self.assertEqual(current['features'], old_features)
        self.assertEqual([s['path'] for s in current['sources']], ['app.py'])
        self.cli('check', '--base', 'HEAD', ok=False)


if __name__ == '__main__':
    unittest.main()
