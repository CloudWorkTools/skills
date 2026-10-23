#!/usr/bin/env python3
"""Record and verify a skill's file content without modifying its installation."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile


def safe_path(value):
    path = Path(os.path.abspath(value))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f'symlinks are not supported: {part}')
    return path.resolve()


def snapshot(root):
    if not root.is_dir():
        raise ValueError(f'not a directory: {root}')
    files = {}
    for directory, dirs, names in os.walk(root):
        for name in dirs + names:
            path = Path(directory) / name
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise ValueError(f'symlinks are not supported: {path}')
            if stat.S_ISREG(mode):
                files[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
            elif not stat.S_ISDIR(mode):
                raise ValueError(f'not a regular file or directory: {path}')
    return dict(sorted(files.items()))


def tree_digest(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=True).encode()).hexdigest()


def compare(expected, actual):
    errors = []
    for name in sorted(expected.keys() | actual.keys()):
        if name not in actual:
            errors.append(f'missing: {name}')
        elif name not in expected:
            errors.append(f'extra: {name}')
        elif expected[name] != actual[name]:
            errors.append(f'changed: {name}')
    if errors:
        raise ValueError('\n'.join(errors))


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE)


def provenance(source, files):
    repo = Path(os.fsdecode(git(source, 'rev-parse', '--show-toplevel')).strip()).resolve()
    commit = git(repo, 'rev-parse', 'HEAD').decode().strip()
    relative = source.relative_to(repo).as_posix()
    # Compare actual bytes to HEAD, including untracked/ignored files, not just Git status.
    entries = git(repo, 'ls-tree', '-rz', '--full-tree', commit, '--', relative).split(b'\0')
    committed = {}
    regular_files_only = True
    for entry in filter(None, entries):
        metadata, filename = entry.split(b'\t', 1)
        mode, kind, object_id = metadata.split()
        if kind != b'blob' or mode not in (b'100644', b'100755'):
            regular_files_only = False
            continue
        name = Path(os.fsdecode(filename)).relative_to(relative).as_posix()
        committed[name] = hashlib.sha256(git(repo, 'cat-file', 'blob', object_id.decode())).hexdigest()
    identity = {'kind': 'worktree', 'tree_digest': tree_digest(files)}
    if regular_files_only and committed == files:
        identity = {'kind': 'committed', 'revision': commit}
    return {'path': str(source), 'repository': str(repo), 'base_commit': commit, 'identity': identity}


def outside(receipt, *roots):
    for root in roots:
        if receipt == root or root in receipt.parents:
            raise ValueError(f'receipt must be outside the skill directory: {root}')


def record(args):
    source, installed, receipt = map(safe_path, (args.source, args.installed, args.receipt))
    outside(receipt, source, installed)
    backup = safe_path(args.backup) if args.backup else None
    if backup is not None and not backup.exists():
        raise ValueError(f'backup does not exist: {backup}')
    files = snapshot(source)
    compare(files, snapshot(installed))
    data = {'version': 1, 'recorded_at': datetime.now(timezone.utc).isoformat(),
            'source': provenance(source, files), 'installed_path': str(installed),
            'backup_path': str(backup) if backup else None,
            'files': files, 'tree_digest': tree_digest(files)}
    receipt.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=receipt.parent,
                                         prefix=f'.{receipt.name}.', delete=False) as output:
            temporary = Path(output.name)
            json.dump(data, output, indent=2, ensure_ascii=True)
            output.write('\n')
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, receipt)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f'Recorded {len(files)} files: {receipt}')


def verify(args):
    receipt = safe_path(args.receipt)
    data = json.loads(receipt.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('version') != 1:
        raise ValueError('unsupported receipt version')
    files = data.get('files')
    if not isinstance(files, dict) or any(
        not isinstance(name, str) or not name or Path(name).is_absolute()
        or '..' in Path(name).parts or not isinstance(digest, str)
        or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest)
        for name, digest in files.items()
    ):
        raise ValueError('invalid receipt file hashes')
    if tree_digest(files) != data.get('tree_digest'):
        raise ValueError('receipt tree digest does not match file hashes')
    installed_value = data.get('installed_path')
    if not isinstance(installed_value, str) or not Path(installed_value).is_absolute():
        raise ValueError('invalid installed path')
    installed = safe_path(installed_value)
    outside(receipt, installed)
    compare(files, snapshot(installed))
    print(f'Verified {len(files)} files: {installed}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    record_parser = commands.add_parser('record', help='record an existing matching installation')
    record_parser.add_argument('--source', required=True)
    record_parser.add_argument('--installed', required=True)
    record_parser.add_argument('--receipt', required=True)
    record_parser.add_argument('--backup')
    verify_parser = commands.add_parser('verify', help='verify installed files against a receipt')
    verify_parser.add_argument('--receipt', required=True)
    args = parser.parse_args()
    try:
        record(args) if args.command == 'record' else verify(args)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
