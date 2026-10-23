import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { markdownLinkErrors } from './helpers/markdown-links.mjs';

function check(files) {
  const directory = mkdtempSync(join(tmpdir(), 'skill-links-'));
  try {
    for (const [name, content] of Object.entries(files)) {
      const path = join(directory, name);
      mkdirSync(join(path, '..'), { recursive: true });
      writeFileSync(path, content);
    }
    return markdownLinkErrors(directory);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
}

test('accepts local files, images, references, encoded paths and duplicate heading anchors', () => {
  assert.deepEqual(check({
    'SKILL.md': '# Start\n[local](#start) [guide](guide%20one.md#repeat-1)\n![image](assets/a.svg)\n[full][Guide] [Guide][] [Guide]\n[Guide]: <guide%20one.md#repeat> "Guide"\n',
    'guide one.md': '# Repeat\n# Repeat\n# 中文 `heading`!\n[unicode](#%E4%B8%AD%E6%96%87-heading)\n',
    'assets/a.svg': '<svg/>',
  }), []);
});

test('reports missing inline, image and reference targets with the source file', () => {
  const errors = check({ 'SKILL.md': '[inline](missing.md) ![image](missing.png)\n[ref][guide]\n[guide]: absent.md\n[undefined][no-definition]\n' });
  assert.equal(errors.length, 4);
  for (const target of ['missing.md', 'missing.png', 'absent.md', 'no-definition']) {
    assert.ok(errors.some(error => error.includes('SKILL.md') && error.includes(target)), target);
  }
});

test('reports missing anchors in local and linked documents', () => {
  const errors = check({ 'SKILL.md': '# Start\n[here](#absent) [there](guide.md#missing)\n', 'guide.md': '# Guide\n' });
  assert.equal(errors.length, 2);
  assert.ok(errors.some(error => error.includes('#absent')));
  assert.ok(errors.some(error => error.includes('#missing')));
});

test('ignores external schemes and links/headings inside fenced examples and inline code', () => {
  assert.deepEqual(check({ 'SKILL.md': '# Real\n[web](https://example.com) [email](mailto:hi@example.com) [plugin](plugin://example) [network](//example.com/x)\n```markdown\n[template](missing.md)\n[ref][missing]\n# Real\n```\n~~~~markdown\n![template](missing.png)\n~~~~\n`[example](missing.md)`\n[real](#real)\n' }), []);
});

test('rejects package escapes, including encoded and absolute paths', () => {
  const errors = check({ 'SKILL.md': '[parent](../outside.md) [encoded](%2e%2e/outside.md) [absolute](/tmp/outside.md)\n' });
  assert.equal(errors.length, 3);
  assert.ok(errors.every(error => error.includes('escapes installed skill')));
});

test('does not count fenced example headings as real anchors', () => {
  assert.equal(check({ 'SKILL.md': '[example](#example)\n```markdown\n# Example\n```\n' }).length, 1);
});


test('rejects an existing target reached through a symlink outside the skill', () => {
  const sandbox = mkdtempSync(join(tmpdir(), 'skill-link-escape-'));
  try {
    const skill = join(sandbox, 'skill');
    mkdirSync(skill);
    writeFileSync(join(sandbox, 'outside.txt'), 'outside');
    symlinkSync(join(sandbox, 'outside.txt'), join(skill, 'linked.txt'));
    writeFileSync(join(skill, 'SKILL.md'), '[escape](linked.txt)');
    assert.match(markdownLinkErrors(skill)[0], /escapes installed skill/);
  } finally {
    rmSync(sandbox, { recursive: true, force: true });
  }
});
