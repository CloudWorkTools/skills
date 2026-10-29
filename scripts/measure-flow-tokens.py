"""Measure Claude Code decision tokens for pinned flow-docs-sync instructions."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
FIELDS = {'uncached_input': 'inputTokens', 'cache_creation': 'cacheCreationInputTokens',
          'cache_read': 'cacheReadInputTokens', 'output': 'outputTokens'}
CASES = {
    'draft': {
        'files': ['SKILL.md'],
        'state': 'Save a WIP commit on a Draft PR. Logic changed; baseline flows remain trusted. No delivery was requested.',
    },
    'unchanged': {
        'files': ['SKILL.md'],
        'state': 'Prepare the same ready PR again. Every bound input and feature fingerprint still matches passing review evidence. Required candidate checks have passed. Only a review-result file was added outside fingerprints.',
    },
    'material_recovery': {
        'files': ['SKILL.md', 'references/reviewer-prompt.md'],
        'state': 'Finish ready delivery. Two ended reviewer attempts returned incomplete with no findings because source/diff output was truncated. No bound input changed. The existing flow is correct. Named missing ranges are now accessible in bounded reads. The coordinator called these two fix/review rounds.',
    },
}
SYSTEM = ('Apply the supplied instruction package to the case. This is a decision-only measurement, '
          'not execution. Return only JSON with exactly these fields: sync (boolean, whether to '
          'rewrite maintained flows now), review_dispatches (nonnegative integer, new semantic '
          'reviewer calls needed now), complete (boolean, whether delivery can be claimed now), '
          'recovery_remaining (nonnegative integer or null if the package does not define it). '
          'Return no explanation. Do not use tools.')


def measurement(result, model):
    usage = result.get('modelUsage', {})
    if result.get('is_error') or model not in usage:
        raise ValueError('Successful result with usage for the requested model is required')
    models = {}
    for name, values in usage.items():
        counts = {key: values.get(field) for key, field in FIELDS.items()}
        if any(type(value) is not int or value < 0 for value in counts.values()):
            raise ValueError('Missing or invalid model token counters')
        counts['input'] = sum(counts[key] for key in ('uncached_input', 'cache_creation', 'cache_read'))
        models[name] = counts
    if not isinstance(result.get('result'), str):
        raise ValueError('Missing decision text')
    decision = json.loads(result['result'])
    keys = {'sync', 'review_dispatches', 'complete', 'recovery_remaining'}
    if not isinstance(decision, dict) or set(decision) != keys:
        raise ValueError('Unexpected decision shape')
    if any(type(decision[key]) is not bool for key in ('sync', 'complete')):
        raise ValueError('Invalid decision booleans')
    for key in ('review_dispatches', 'recovery_remaining'):
        value = decision[key]
        if value is None and key == 'recovery_remaining':
            continue
        if type(value) is not int or value < 0:
            raise ValueError('Invalid decision counter')
    return {'models': models, 'total': {key: sum(row[key] for row in models.values())
                                      for key in models[model]}, 'decision': decision}


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', default='b17df8308b674704f9c0aab13cd4db434609e2c4')
    parser.add_argument('--after', default='d1cfa7cec2af1799455887cd30c0be1052ad4323')
    parser.add_argument('--model', default='claude-opus-5-5')
    parser.add_argument('--claude', default='claude')
    parser.add_argument('--repetitions', type=int, default=2)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error('--repetitions must be positive')
    revisions = {name: git('rev-parse', f'{ref}^{{commit}}')
                 for name, ref in (('before', args.before), ('after', args.after))}
    report = {'schema': 1, 'kind': 'decision-only', 'revisions': revisions,
              'model': args.model, 'effort': 'low', 'repetitions': args.repetitions,
              'cli_version': subprocess.check_output([args.claude, '--version'], text=True).strip(),
              'cases': CASES, 'complete': False, 'samples': []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as handle:
        json.dump(report, handle, indent=2)
    command = [args.claude, '--print', '--output-format', 'json', '--model', args.model,
               '--effort', 'low', '--safe-mode', '--setting-sources', '',
               '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
               '--tools', '', '--no-session-persistence', '--max-budget-usd', '1',
               '--system-prompt', SYSTEM]
    with tempfile.TemporaryDirectory(prefix='flow-tokens-') as directory:
        for case, definition in CASES.items():
            for repetition in range(args.repetitions):
                order = ['before', 'after'] if repetition % 2 == 0 else ['after', 'before']
                for variant in order:
                    documents = {path: git('show', f'{revisions[variant]}:skills/flow-docs-sync/{path}')
                                 for path in definition['files']}
                    prompt = '\n\n'.join(f'FILE {path}\n{text}' for path, text in documents.items())
                    prompt += '\n\nCASE\n' + definition['state']
                    response = subprocess.run(command, input=prompt, cwd=directory,
                                              capture_output=True, text=True, timeout=180, check=True)
                    sample = measurement(json.loads(response.stdout), args.model)
                    sample.update(case=case, variant=variant, repetition=repetition,
                                  prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest())
                    report['samples'].append(sample)
                    args.output.write_text(json.dumps(report, indent=2) + '\n')
                    print(json.dumps({'case': case, 'variant': variant, 'repetition': repetition,
                                      **sample['total']}), flush=True)
    report['complete'] = True
    args.output.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
