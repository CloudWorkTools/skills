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


def usage_counts(result):
    usage = result.get('modelUsage', {})
    if not isinstance(usage, dict) or not usage:
        raise ValueError('Model usage is unavailable')
    models = {}
    for name, values in usage.items():
        if not isinstance(values, dict):
            raise ValueError('Invalid model counters')
        counts = {key: values.get(field) for key, field in FIELDS.items()}
        if any(type(value) is not int or value < 0 for value in counts.values()):
            raise ValueError('Missing or invalid model token counters')
        counts['input'] = sum(counts[key] for key in ('uncached_input', 'cache_creation', 'cache_read'))
        models[name] = counts
    return {'models': models, 'total': {key: sum(row[key] for row in models.values())
                                      for key in next(iter(models.values()))}}


def response_json(result):
    if not isinstance(result.get('result'), str):
        raise ValueError('Missing decision text')
    text = result['result'].strip()
    if text.startswith('```json\n') and text.endswith('\n```'):
        text = text[8:-4]
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError('Expected a JSON object')
    return value


def measurement(result, model):
    counts = usage_counts(result)
    if result.get('is_error') or model not in counts['models']:
        raise ValueError('Successful result with usage for the requested model is required')
    decision = response_json(result)
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
    return {**counts, 'decision': decision}


def model_command(claude, model, system):
    return [claude, '--print', '--output-format', 'json', '--model', model,
            '--effort', 'low', '--safe-mode', '--setting-sources', '',
            '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
            '--tools', '', '--no-session-persistence', '--max-budget-usd', '1',
            '--system-prompt', system]


def invoke(command, prompt, directory, ledger, phase, attempt, model, parse=response_json):
    row = {'attempt': attempt, 'phase': phase, 'status': 'failed', 'usage': None,
           'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest()}
    payload, error, value = {}, None, None
    try:
        response = subprocess.run(command, input=prompt, cwd=directory,
                                  capture_output=True, text=True, timeout=180, check=False)
        raw = response.stdout
        if response.returncode:
            error = f'CLI exit {response.returncode}'
    except subprocess.TimeoutExpired as failure:
        raw, error = failure.stdout or '', 'timeout'
    except OSError:
        raw, error = '', 'CLI unavailable'
    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError('Expected result object')
    except (ValueError, TypeError):
        payload = {}
        error = error or 'invalid CLI JSON'
    row['reported_usage'] = payload.get('modelUsage', {})
    row['response'] = payload.get('result')
    try:
        row['usage'] = usage_counts(payload)
    except (ValueError, AttributeError, TypeError):
        pass
    if not error:
        reported = payload.get('modelUsage')
        if payload.get('is_error') or (isinstance(reported, dict) and reported and model not in reported):
            error = 'failed call or requested model absent'
        else:
            try:
                value = parse(payload)
                row['status'] = 'success'
            except Exception as failure:
                row['status'], error = 'invalid_response', f'response validation: {type(failure).__name__}'
    row['error'] = error
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open('a') as handle:
        handle.write(json.dumps(row) + '\n')
    if error:
        raise RuntimeError(error)
    return value


def usage_summary(ledger):
    attempts, phases = {}, {}
    known = dict.fromkeys((*FIELDS, 'input'), 0)
    for line in ledger.read_text().splitlines() if ledger.exists() else []:
        row = json.loads(line)
        previous = attempts.get(row['attempt'])
        if previous is not None:
            if row != previous:
                raise ValueError('Conflicting attempt identity')
            continue
        attempts[row['attempt']] = row
        phase = phases.setdefault(row['phase'], {'attempts': 0, 'failed_attempts': 0,
                                                'unknown_attempts': 0, 'known_tokens': 0,
                                                'known': dict.fromkeys(known, 0), 'models': {}})
        phase['attempts'] += 1
        phase['failed_attempts'] += row['status'] != 'success'
        if row['usage'] is None:
            phase['unknown_attempts'] += 1
        else:
            total = row['usage']['total']
            phase['known_tokens'] += total['input'] + total['output']
            for key in known:
                known[key] += total[key]
                phase['known'][key] += total[key]
            for model, counters in row['usage']['models'].items():
                accumulated = phase['models'].setdefault(model, dict.fromkeys(known, 0))
                for key in known:
                    accumulated[key] += counters[key]
    unknown = sum(phase['unknown_attempts'] for phase in phases.values())
    subtotal = known['input'] + known['output']
    return {'scope': 'recorded calls only', 'attempts': len(attempts), 'phases': phases,
            'known': known, 'known_tokens': subtotal, 'unknown_attempts': unknown,
            'total_tokens': None if unknown else subtotal}


def review_context(root, execution):
    package = root / 'package.json'
    return {'test_commands': json.loads(package.read_text()).get('scripts', {}) if package.exists() else {},
            'configuration_files': {'package.json': package.read_text()} if package.exists() else {},
            'ci': {str(path.relative_to(root)): path.read_text()
                   for path in sorted((root / '.github/workflows').glob('*'))
                   if path.suffix in ('.yml', '.yaml')}, 'execution': execution,
            'missing_configuration': [] if package.exists() else ['project test configuration not supplied']}


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
    parser.add_argument('--phase', default='decision')
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error('--repetitions must be positive')
    revisions = {name: git('rev-parse', f'{ref}^{{commit}}')
                 for name, ref in (('before', args.before), ('after', args.after))}
    report = {'schema': 2, 'kind': 'decision-only', 'revisions': revisions,
              'model': args.model, 'effort': 'low', 'repetitions': args.repetitions,
              'cli_version': subprocess.check_output([args.claude, '--version'], text=True).strip(),
              'cases': CASES, 'complete': False, 'samples': []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as handle:
        json.dump(report, handle, indent=2)
    ledger = args.output.with_suffix('.usage.jsonl')
    with ledger.open('x'):
        pass
    report['usage_ledger'] = ledger.name
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    command = model_command(args.claude, args.model, SYSTEM)
    with tempfile.TemporaryDirectory(prefix='flow-tokens-') as directory:
        for case, definition in CASES.items():
            for repetition in range(args.repetitions):
                order = ['before', 'after'] if repetition % 2 == 0 else ['after', 'before']
                for variant in order:
                    documents = {path: git('show', f'{revisions[variant]}:skills/flow-docs-sync/{path}')
                                 for path in definition['files']}
                    prompt = '\n\n'.join(f'FILE {path}\n{text}' for path, text in documents.items())
                    prompt += '\n\nCASE\n' + definition['state']
                    try:
                        sample = invoke(command, prompt, directory, ledger, args.phase,
                                        f'{case}/{variant}/{repetition}', args.model,
                                        parse=lambda result: measurement(result, args.model))
                    except Exception as failure:
                        report.update(error=str(failure), usage=usage_summary(ledger))
                        args.output.write_text(json.dumps(report, indent=2) + '\n')
                        raise
                    sample.update(case=case, variant=variant, repetition=repetition,
                                  prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest())
                    report['samples'].append(sample)
                    report['usage'] = usage_summary(ledger)
                    args.output.write_text(json.dumps(report, indent=2) + '\n')
                    print(json.dumps({'case': case, 'variant': variant, 'repetition': repetition,
                                      **sample['total']}), flush=True)
    report['complete'] = True
    report['usage'] = usage_summary(ledger)
    args.output.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
