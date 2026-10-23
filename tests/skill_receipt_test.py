import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'skill-receipt.py'


class SkillReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.source = self.repo / 'skills' / 'example'
        self.source.mkdir(parents=True)
        (self.source / 'SKILL.md').write_text('example\n')
        (self.source / 'nested').mkdir()
        (self.source / 'nested' / 'data.txt').write_text('payload\n')
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.com', 'commit', '-qm', 'initial')
        self.commit = self.git('rev-parse', 'HEAD').strip()
        self.installed = self.root / 'installed'
        shutil.copytree(self.source, self.installed)
        self.receipt = self.root / 'receipts' / 'example.json'

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True)

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), *map(str, args)], capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def record(self, *extra, ok=True):
        return self.cli('record', '--source', self.source, '--installed', self.installed,
                        '--receipt', self.receipt, *extra, ok=ok)

    def test_committed_receipt_verifies_without_source_checkout(self):
        backup = self.root / 'backup'
        backup.mkdir()
        self.record('--backup', backup)
        receipt = json.loads(self.receipt.read_text())
        self.assertEqual(receipt['source']['repository'], str(self.repo))
        self.assertEqual(receipt['source']['base_commit'], self.commit)
        self.assertEqual(receipt['source']['identity']['kind'], 'committed')
        self.assertEqual(receipt['source']['identity']['revision'], self.commit)
        self.assertEqual(receipt['files']['SKILL.md'], hashlib.sha256(b'example\n').hexdigest())
        self.assertEqual(receipt['backup_path'], str(backup))
        shutil.rmtree(self.repo)
        self.cli('verify', '--receipt', self.receipt)

    def test_dirty_source_never_claims_committed_revision(self):
        for change in ('modified', 'extra', 'missing', 'staged'):
            with self.subTest(change=change):
                self.git('reset', '--hard', '-q', self.commit)
                self.git('clean', '-fdq')
                if change in ('modified', 'staged'):
                    (self.source / 'SKILL.md').write_text('changed\n')
                elif change == 'extra':
                    (self.repo / '.git' / 'info' / 'exclude').write_text('ignored.txt\n')
                    (self.source / 'ignored.txt').write_text('extra')
                else:
                    (self.source / 'nested' / 'data.txt').unlink()
                if change == 'staged':
                    self.git('add', '.')
                shutil.rmtree(self.installed)
                shutil.copytree(self.source, self.installed)
                self.record()
                identity = json.loads(self.receipt.read_text())['source']['identity']
                self.assertEqual(identity['kind'], 'worktree')
                self.assertNotIn('revision', identity)

    def test_missing_head_symlink_is_not_an_exact_committed_package(self):
        link = self.source / 'tracked-link'
        link.symlink_to('SKILL.md')
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.com', 'commit', '-qm', 'link')
        link.unlink()
        self.record()
        self.assertEqual(json.loads(self.receipt.read_text())['source']['identity']['kind'], 'worktree')

    def test_drift_reports_changed_missing_and_extra_files(self):
        self.record()
        (self.installed / 'SKILL.md').write_text('changed')
        (self.installed / 'nested' / 'data.txt').unlink()
        (self.installed / 'extra').write_text('extra')
        result = self.cli('verify', '--receipt', self.receipt, ok=False)
        for path in ('SKILL.md', 'nested/data.txt', 'extra'):
            self.assertIn(path, result.stderr)

    def test_record_mismatch_preserves_previous_receipt(self):
        self.record()
        before = self.receipt.read_bytes()
        for change in ('changed', 'missing', 'extra'):
            with self.subTest(change=change):
                shutil.rmtree(self.installed)
                shutil.copytree(self.source, self.installed)
                if change == 'changed':
                    (self.installed / 'SKILL.md').write_text('different')
                elif change == 'missing':
                    (self.installed / 'SKILL.md').unlink()
                else:
                    (self.installed / 'extra').write_text('extra')
                self.record(ok=False)
                self.assertEqual(self.receipt.read_bytes(), before)

    def test_verify_rejects_symlink_and_corrupt_receipt(self):
        self.record()
        data = self.receipt.read_bytes()
        (self.installed / 'SKILL.md').unlink()
        (self.installed / 'SKILL.md').symlink_to(self.source / 'SKILL.md')
        self.cli('verify', '--receipt', self.receipt, ok=False)
        (self.installed / 'SKILL.md').unlink()
        shutil.copy(self.source / 'SKILL.md', self.installed / 'SKILL.md')
        receipt = json.loads(data)
        receipt['files']['SKILL.md'] = '0' * 64
        self.receipt.write_text(json.dumps(receipt))
        self.cli('verify', '--receipt', self.receipt, ok=False)

    def test_receipt_cannot_be_inside_package(self):
        for root in (self.source, self.installed):
            with self.subTest(root=root):
                self.cli('record', '--source', self.source, '--installed', self.installed,
                         '--receipt', root / 'receipt.json', ok=False)
                self.assertFalse((root / 'receipt.json').exists())

    def test_rejects_symlinks_in_tree_and_paths(self):
        for root in (self.source, self.installed):
            link = root / 'link'
            link.symlink_to(self.root)
            self.record(ok=False)
            link.unlink()
        alias = self.root / 'alias'
        alias.symlink_to(self.source, target_is_directory=True)
        self.cli('record', '--source', alias, '--installed', self.installed,
                 '--receipt', self.receipt, ok=False)
        self.record()
        before = self.receipt.read_bytes()
        self.receipt.unlink()
        real = self.root / 'real.json'
        real.write_bytes(before)
        self.receipt.symlink_to(real)
        self.record(ok=False)
        self.assertEqual(real.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
