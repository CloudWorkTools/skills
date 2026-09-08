import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const env = { ...process.env, DISABLE_TELEMETRY: '1', DO_NOT_TRACK: '1' };
function npm(args, cwd) {
  return execFileSync('npm', args, { cwd, env, encoding: 'utf8', timeout: 180_000 });
}

test('npm package installs a complete, discoverable pr-preview skill', () => {
  const source = join(root, 'skills/pr-preview');
  assert.match(readFileSync(join(source, 'SKILL.md'), 'utf8'), /^---\nname: pr-preview\n/);
  const sandbox = mkdtempSync(join(tmpdir(), 'cloudworktools-skills-'));
  try {
    const project = join(sandbox, 'project');
    mkdirSync(project);
    const packed = JSON.parse(npm(['pack', '--json', '--pack-destination', sandbox], root));
    npm(['install', '--ignore-scripts', '--no-audit', '--no-fund', '--no-package-lock',
      join(sandbox, packed[0].filename)], project);
    const dependency = join(project, 'node_modules/@cloudworktools/skills');
    npm(['exec', '--yes', '--package=skills@1.5.24', '--', 'skills', 'add', dependency,
      '--skill', 'pr-preview', '--agent', 'codex', '--copy', '--yes'], project);
    const installed = join(project, '.agents/skills/pr-preview');
    function compare(directory, relative = '') {
      for (const entry of readdirSync(directory, { withFileTypes: true })) {
        const path = join(relative, entry.name);
        if (entry.isDirectory()) compare(join(directory, entry.name), path);
        else assert.deepEqual(readFileSync(join(installed, path)), readFileSync(join(source, path)), path);
      }
    }
    compare(source);
    const listed = npm(['exec', '--yes', '--package=skills@1.5.24', '--',
      'skills', 'list', '--agent', 'codex', '--json'], project);
    assert.match(listed, /pr-preview/);
  } finally {
    rmSync(sandbox, { recursive: true, force: true });
  }
});
