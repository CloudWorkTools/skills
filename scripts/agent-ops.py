#!/usr/bin/env python3
"""Bounded JSON observations and one CURRENT snapshot; never owns an Orca queue.

summary < input.json [--raw PRIVATE_NEW_FILE] projects metadata, not bodies.
current --path CURRENT.json --repository REPO --revision REV --version VERSION
    < snapshot.json creates a validated snapshot; replacement additionally needs
    --expected-digest from the previous result. Source identity is caller evidence,
    not a claim that this tool verified a repository or publication.
wait --orca /exact/orca --terminal HANDLE performs ONE check --wait (<=55s).
    --types controls waking only. All returned messages still require handling.

Raw archives are exclusive-create mode 0600 and may contain secrets. Parent
storage must be trusted/private. CURRENT uses atomic replacement and a writer
lock; its parent must already exist. No automatic ack, heartbeat handling,
settlement, worker release/stop, or completion inferred from empty results.
"""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

MAX_INPUT = 8 * 1024 * 1024
MAX_FIELDS = 40
STATUSES = {'unknown', 'pending', 'active', 'running', 'blocked', 'failed', 'succeeded',
            'published', 'published-but-verification-pending', 'verified', 'complete', 'completed',
            'cancelled', 'settled', 'unverifiable', 'exited', 'live', 'ready', 'skipped'}
FIELDS = {'phase', 'status', 'state', 'verdict', 'severity', 'id', 'runId', 'taskId', 'dispatchId', 'deliveryId',
          'messageId', 'terminalId', 'outcome', 'count', 'total', 'hasMore', 'nextCursor',
          'timedOut', 'cancelled', 'connectionLost', 'replayed', 'ok', 'code',
          'failedStage', 'liveness', 'reason', 'settlement', 'requiresAction',
          'revision', 'version', 'repository', 'evidencepath', 'type', 'command_exit_code'}


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    if len(raw) > MAX_INPUT:
        raise ValueError('input too large')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate key')
            result[key] = value
        return result
    value = json.loads(raw, object_pairs_hook=unique,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
    stack = [(value, 0)]
    while stack:
        item, depth = stack.pop()
        if depth > 64:
            raise ValueError('input depth')
        if isinstance(item, (dict, list)):
            stack.extend((child, depth + 1) for child in (item.values() if isinstance(item, dict) else item))
    return value


def secret_like(value):
    return bool(re.search(r'(?:github_pat_|gh[pousr]_)[A-Za-z0-9_]+|https?://[^/@\s]+@', value))


def summary(value, raw, evidence=None):
    fields, omitted, bodies, messages = [], 0, 0, Counter()
    signals = {'failure': 0, 'unknown': 0, 'errors': 0}
    stack = [('', value)]
    while stack:
        path, item = stack.pop()
        if isinstance(item, dict):
            # Message bodies remain private even when they look like JSON metadata.
            if isinstance(item.get('type'), str):
                kind = item['type']
                kind = kind if kind in {'heartbeat', 'worker_done', 'question', 'status', 'escalation'} else 'other'
                messages[kind] += 1
                bodies += int(bool(item.get('body')))
            for key, child in reversed(list(item.items())):
                if key in {'body', 'token', 'password', 'secret', 'authorization'}:
                    continue
                child_path = f'{path}.{key}' if path else key
                if key in {'error', 'errors'} and child:
                    signals['errors'] += 1
                if key in {'status', 'state', 'verdict', 'outcome', 'liveness'} and isinstance(child, str):
                    signals['failure'] += int(child in {'failed', 'failure', 'error', 'fail'})
                    signals['unknown'] += int(child in {'unknown', 'unverifiable', 'incomplete', 'published-but-verification-pending'})
                if key in FIELDS and isinstance(child, (str, int, float, bool, type(None))):
                    if len(fields) < MAX_FIELDS:
                        safe = child
                        if isinstance(child, str):
                            # Free-form diagnostics can contain credentials: emit only short metadata.
                            safe = child if key not in {'reason', 'settlement'} and len(child) <= 128 and not secret_like(child) and re.fullmatch(r'[\w .:/@+,-]*', child) else {'digest': digest(child.encode()), 'length': len(child)}
                        fields.append({'path': child_path if len(child_path) <= 160 and not secret_like(child_path) else 'nested', 'value': safe})
                    else:
                        omitted += 1
                if isinstance(child, (dict, list)):
                    stack.append((child_path, child))
        elif isinstance(item, list):
            stack.extend((f'{path}[{i}]', child) for i, child in reversed(list(enumerate(item))))
    result = {'digest': digest(raw), 'bytes': len(raw), 'fields': fields,
            'omitted_fields': omitted, 'message_counts': dict(sorted(messages.items())),
            'nonempty_bodies': bodies, 'handling_required': bool(messages),
            'signals': signals, 'evidencepath': str(evidence) if evidence else None}
    # Reduce whole rows; never cut JSON bytes or append textual truncation markers.
    while len(encode(result)) > 8192 and fields:
        fields.pop()
        result['omitted_fields'] += 1
    return result


def archive(path, raw):
    with open(path, 'xb', opener=lambda p, flags: os.open(p, flags, 0o600)) as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def atomic_write(path, raw):
    name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f'.{path.name}.', delete=False) as stream:
            name = stream.name
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def text(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 1024


def identity(value):
    return isinstance(value, dict) and set(value) == {'repository', 'revision', 'version'} and all(text(v) for v in value.values())


def validate_snapshot(value, expected):
    if not isinstance(value, dict) or set(value) != {'schema_version', 'source', 'phase', 'status', 'components'}:
        raise ValueError('snapshot shape')
    if type(value['schema_version']) is not int or value['schema_version'] != 1:
        raise ValueError('snapshot version')
    if not identity(value['source']) or value['source'] != expected:
        raise ValueError('stale source identity')
    if not text(value['phase']) or value['status'] not in STATUSES:
        raise ValueError('snapshot state')
    components = value['components']
    if not isinstance(components, dict) or not 1 <= len(components) <= 64:
        raise ValueError('components')
    allowed = {'status', 'phase', 'source', 'taskId', 'dispatchId', 'runId', 'liveness',
               'evidencepath', 'error', 'settlement'}
    for name, component in components.items():
        if not text(name) or not isinstance(component, dict) or not set(component) <= allowed:
            raise ValueError('component shape')
        if component.get('status') not in STATUSES:
            raise ValueError('component status')
        for key, item in component.items():
            if key == 'source':
                if not identity(item):
                    raise ValueError('component source')
            elif not text(item):
                raise ValueError('component field')
        if component.get('liveness', 'unknown') not in {'unknown', 'unverifiable', 'live', 'exited'}:
            raise ValueError('component liveness')
        if ('taskId' in component) != ('dispatchId' in component):
            raise ValueError('dispatch identity needs task and dispatch')


def current(path, value, expected, expected_digest):
    validate_snapshot(value, expected)
    raw = encode(value)
    # Exclusive lock prevents two cooperating writers from passing the same CAS.
    lock = path.with_name(path.name + '.lock')
    with open(lock, 'xb', opener=lambda p, flags: os.open(p, flags, 0o600)):
        try:
            if path.is_symlink():
                raise ValueError('symlink current')
            if path.exists():
                if expected_digest != digest(path.read_bytes()):
                    raise ValueError('stale current digest')
            elif expected_digest is not None:
                raise ValueError('missing prior current')
            atomic_write(path, raw)
        finally:
            lock.unlink()
    return raw


def wait(orca, terminal, timeout_ms, run=None):
    if not 1 <= timeout_ms <= 55000:
        raise ValueError('wait bound')
    base = [orca, 'orchestration', 'check']
    help_result = subprocess.run([*base, '--help'], capture_output=True, text=True, timeout=10)
    selector = '--run' if run else '--terminal'
    if help_result.returncode or not all(flag in help_result.stdout for flag in ('--wait', '--types', '--timeout-ms', '--json', selector)):
        raise ValueError('unsupported wait contract')
    result = subprocess.run([*base, selector, run or terminal, '--wait', '--types',
                             'worker_done,escalation,question', '--timeout-ms', str(timeout_ms), '--json'],
                            capture_output=True, text=True, timeout=timeout_ms / 1000 + 10)
    # stderr keepalive is transport activity, never a worker heartbeat.
    value = parse(result.stdout.encode())
    if result.returncode:
        return {'command_exit_code': result.returncode, 'status': 'failed', 'error': value}
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('summary', 'current', 'wait'):
        sub = commands.add_parser(command)
        sub.add_argument('--raw', type=Path, help='exclusive-create private raw evidence file')
        if command == 'current':
            sub.add_argument('--path', type=Path, required=True)
            for key in ('repository', 'revision', 'version'):
                sub.add_argument('--' + key, required=True)
            sub.add_argument('--expected-digest')
        elif command == 'wait':
            sub.add_argument('--orca', required=True, help='exact executable; no shell evaluation')
            owner = sub.add_mutually_exclusive_group(required=True)
            owner.add_argument('--terminal')
            owner.add_argument('--run', help='coordinator run; mutually exclusive with terminal')
            sub.add_argument('--timeout-ms', type=int, default=55000)
    args = parser.parse_args()
    try:
        if args.command == 'current' and args.raw and args.raw.resolve() == args.path.resolve():
            raise ValueError('raw archive cannot be CURRENT')
        if args.command == 'wait':
            value = wait(args.orca, args.terminal, args.timeout_ms, args.run)
            raw = encode(value)
            if args.raw:
                archive(args.raw, raw)
        else:
            raw = sys.stdin.buffer.read(MAX_INPUT + 1)
            if args.raw:
                archive(args.raw, raw)
            value = parse(raw)
        if args.command == 'current':
            expected = {key: getattr(args, key) for key in ('repository', 'revision', 'version')}
            raw = current(args.path, value, expected, args.expected_digest)
        sys.stdout.buffer.write(encode(summary(value, raw, args.raw)))
        return 1 if args.command == 'wait' and value.get('command_exit_code', 0) else 0
    except (ValueError, TypeError, OSError, RecursionError, subprocess.SubprocessError):
        print('{"error":"invalid_input","status":"unknown"}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
