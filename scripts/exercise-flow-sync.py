"""Execute a bounded flow-sync fixture and measure its actual model calls."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('flow_tokens', ROOT / 'scripts/measure-flow-tokens.py')
tokens = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tokens)
CHECKER = ROOT / 'skills/flow-docs-sync/scripts/flow_checker.py'
VALIDATION = ('import json,os,app; assert app.first()==int(os.environ["FLOW_EXPECTED_FIRST"]); assert app.second()==2; '
              'print(json.dumps({"first":app.first(),"second":app.second()}))')
REVIEW_TEMPLATE = (ROOT / 'skills/flow-docs-sync/references/reviewer-prompt.md').read_text().split('```text\n', 1)[1].split('```', 1)[0]


def exercise(root, model, reuse=None):
    expected_first = 1

    def run(*command):
        result = subprocess.run(command, cwd=root, capture_output=True, text=True,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
                                     'FLOW_EXPECTED_FIRST': str(expected_first)})
        if result.returncode:
            raise ValueError(result.stdout + result.stderr)
        return result.stdout.strip()

    def write(path, text):
        destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text)

    def checker(*args):
        return run(sys.executable, '-B', str(CHECKER), *args, '--root', str(root))

    def manifest():
        return json.loads((root / 'docs/flow-manifest.json').read_text())

    def fingerprint(feature):
        return checker('fingerprint', '--feature', feature, '--base', base)

    run('git', 'init', '-q')
    run('git', 'config', 'user.name', 'Flow fixture')
    run('git', 'config', 'user.email', 'fixture@example.test')
    source = 'def first():\n    return 1\n\ndef second():\n    return 2\n'
    write('app.py', source)
    write('package.json', json.dumps({'scripts': {'test': 'python3 -c ' + json.dumps(VALIDATION)}}))
    data = {'version': 1, 'scope': {'include': ['app.py'], 'exclude': {}},
            'sources': [{'path': 'app.py', 'kind': 'python'}], 'features': [],
            'reviews': [], 'policy_inputs': ['package.json']}
    for feature, symbol, value in [('one', 'first', 1), ('two', 'second', 2)]:
        flow = f'docs/flows/{feature}.mmd'
        write(flow, f'flowchart TD\nA["return {value}"]\n')
        data['features'].append({'id': feature, 'flow': flow,
                                 'mappings': [{'node': 'A', 'path': 'app.py', 'symbol': symbol}]})
    write('docs/flow-manifest.json', json.dumps(data))
    checker('snapshot')
    run(sys.executable, '-c', VALIDATION)
    run('git', 'add', '.')
    run('git', 'commit', '-qm', 'trusted fixture baseline')
    base = run('git', 'rev-parse', 'HEAD')
    checker('check', '--base', base)
    fingerprints = {feature: fingerprint(feature) for feature in ('one', 'two')}
    baseline_flows = {feature: (root / f'docs/flows/{feature}.mmd').read_text() for feature in fingerprints}
    report = {'kind': 'executed-fixture', 'base': base, 'complete': False, 'events': [],
              'scope': 'Two fixture functions; no product deployment or unattended GitHub runner.'}
    write('app.py', source.replace('return 1', 'return 3'))
    expected_first = 3
    report['events'].append({'state': 'draft', 'model_calls': 0, 'status': 'pending'})
    for state in ('ready', 'repeated_ready', 'cosmetic'):
        if state == 'cosmetic':
            write('app.py', (root / 'app.py').read_text() + '\n# layout-only task\n')
        checker('snapshot')
        affected = [feature for feature in fingerprints if fingerprint(feature) != fingerprints[feature]]
        calls = 0
        for feature in affected:
            current_source = (root / 'app.py').read_text()
            flow_path = f'docs/flows/{feature}.mmd'
            inputs = {'feature': feature, 'base': base, 'base_source': source,
                      'candidate_source': current_source, 'base_flow': baseline_flows[feature],
                      'flow': (root / flow_path).read_text(), 'mapping': manifest()['features'],
                      'requirement': 'Change first() from return 1 to return 3; keep second() returning 2. Synchronize feature one.',
                      'manifest_path': 'docs/flow-manifest.json', 'layout_overrides': {}}
            if reuse is not None:
                artifacts = reuse['failure_artifacts']
                if artifacts['app.py'] != current_source or artifacts['package.json'] != (root / 'package.json').read_text() or json.loads(artifacts['docs/flow-manifest.json'])['features'] != manifest()['features']:
                    raise ValueError('Cached generation inputs do not match')
                generated = {'flow': artifacts[flow_path]}
            else:
                generated = model('synchronization', inputs)
                calls += 1
            if not isinstance(generated.get('flow'), str):
                raise ValueError('Generator must return flow text')
            write(flow_path, generated['flow'])
            checker('snapshot')
            current_fingerprint = fingerprint(feature)
            preflight = subprocess.run([sys.executable, '-B', str(CHECKER), 'check',
                                        '--root', str(root), '--base', base],
                                       capture_output=True, text=True)
            expected = f'flow checker: missing current review: {feature}; fingerprint {current_fingerprint}'
            if preflight.returncode != 1 or (preflight.stdout + preflight.stderr).strip() != expected:
                raise ValueError('Unexpected structural preflight result: ' + preflight.stdout + preflight.stderr)
            output = run(sys.executable, '-c', VALIDATION)
            if json.loads(output) != {'first': 3, 'second': 2}:
                raise ValueError('Unexpected executed behavior')
            execution = {'command': [sys.executable, '-c', VALIDATION], 'exit_code': 0,
                         'stdout': output, 'python': sys.version,
                         'environment': {'FLOW_EXPECTED_FIRST': str(expected_first)},
                         'candidate_source_sha256': hashlib.sha256(current_source.encode()).hexdigest()}
            inputs.update(flow=(root / flow_path).read_text(), fingerprint=current_fingerprint,
                          reviewer='fixture-review-' + str(uuid.uuid4()),
                          validation=tokens.review_context(root, execution),
                          base_manifest=run('git', 'show', base + ':docs/flow-manifest.json'),
                          candidate_manifest=(root / 'docs/flow-manifest.json').read_text(),
                          raw_diff=run('git', 'diff', '--no-ext-diff', '--no-textconv', base,
                                       '--', 'app.py', 'package.json', 'docs'))
            run('git', 'add', 'app.py', 'package.json', 'docs')
            inputs['candidate_snapshot'] = run('git', 'write-tree')
            inputs['scope_note'] = 'All fixture source and policy inputs are supplied in full. No external dependencies, contracts or CI runner exist in this fixture; rendering/deployment/CI integration are outside semantic-review scope.'
            review = model('semantic_review', inputs)
            calls += 1
            for key in ('feature', 'fingerprint', 'reviewer'):
                if review.get(key) != inputs[key]:
                    raise ValueError('Review identity mismatch')
            if review.get('verdict') != 'pass' or review.get('findings') != []:
                raise ValueError('Independent review did not pass')
            if not isinstance(review.get('evidence'), list) or not review['evidence'] or not isinstance(review.get('limitations'), list):
                raise ValueError('Fixture review lacks complete evidence')
            if fingerprint(feature) != current_fingerprint:
                raise ValueError('Candidate changed during review')
            evidence = f'docs/flow-evidence/reviews/{feature}/{current_fingerprint}.json'
            write(evidence, json.dumps(review))
            data = manifest()
            data['reviews'] = [row for row in data['reviews'] if row['feature'] != feature]
            data['reviews'].append({**{key: review[key] for key in ('feature', 'fingerprint', 'reviewer', 'verdict')},
                                    'evidence': evidence})
            write('docs/flow-manifest.json', json.dumps(data))
            fingerprints[feature] = current_fingerprint
            report['review'] = review
            report['validation'] = inputs['validation']
        checked = checker('check', '--base', base)
        report['events'].append({'state': state, 'affected': affected, 'model_calls': calls,
                                 'generation_reused': reuse is not None and bool(affected),
                                 'checker_exit': 0, 'checker_output': checked})
    report.update(complete=True, flows={feature: (root / f'docs/flows/{feature}.mmd').read_text()
                                       for feature in fingerprints}, fingerprints=fingerprints,
                  candidate_source=(root / 'app.py').read_text())
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--claude', default='claude')
    parser.add_argument('--model', default='claude-opus-5-5')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reuse-generated-from', type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x'):
        pass
    ledger = args.output.with_suffix('.usage.jsonl')
    with ledger.open('x'):
        pass
    report = {'kind': 'executed-fixture', 'complete': False, 'usage_ledger': ledger.name,
              'model': args.model, 'cli_version': subprocess.check_output([args.claude, '--version'], text=True).strip()}
    instructions = {
        'synchronization': 'Update the supplied Mermaid flow to match candidate_source for the assigned feature. Preserve node A and return JSON only: {"flow":"complete Mermaid source"}.',
        'semantic_review': REVIEW_TEMPLATE + '\nYour task identity is the supplied reviewer ID. Assess the declared source-to-flow scope from the supplied raw snapshots and execution records; their external authentication is not asserted. Rendering, deployment and CI integration are outside scope.',
    }
    with tempfile.TemporaryDirectory(prefix='flow-sync-') as directory:
        def model(phase, inputs):
            command = tokens.model_command(args.claude, args.model, instructions[phase])
            return tokens.invoke(command, json.dumps(inputs), directory, ledger,
                                 phase, phase + '/' + str(uuid.uuid4()), args.model)
        try:
            reuse = json.loads(args.reuse_generated_from.read_text()) if args.reuse_generated_from else None
            report.update(exercise(Path(directory), model, reuse))
            if args.reuse_generated_from:
                report['generation_reuse'] = {'source_report': args.reuse_generated_from.name,
                                             'sha256': hashlib.sha256(args.reuse_generated_from.read_bytes()).hexdigest()}
        except Exception as failure:
            report['error'] = str(failure)
            paths = ['app.py', 'package.json', 'docs/flow-manifest.json',
                     'docs/flows/one.mmd', 'docs/flows/two.mmd']
            report['failure_artifacts'] = {path: (Path(directory) / path).read_text()
                                           for path in paths if (Path(directory) / path).exists()}
            raise
        finally:
            report['usage'] = tokens.usage_summary(ledger)
            args.output.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
