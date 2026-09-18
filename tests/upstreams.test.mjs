import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { checkSource, exitCode, fingerprint } from '../skills/teaching-with-diagrams/scripts/check-upstreams.mjs';

test('independently installed skills carry the same tested upstream checker', () => {
  assert.deepEqual(
    readFileSync(new URL('../skills/readme-value/scripts/check-upstreams.mjs', import.meta.url)),
    readFileSync(new URL('../skills/teaching-with-diagrams/scripts/check-upstreams.mjs', import.meta.url)),
  );
});

const sha = value => value.repeat(40);
const entries = [
  { name: 'SKILL.md', type: 'file', sha: sha('a') },
  { name: 'references', type: 'dir', sha: sha('b') },
];
const source = { name: 'example', repo: 'owner/repo', path: 'skills/example',
  commit: sha('c'), fingerprint: fingerprint(entries), license_sha: sha('d') };

function api(files = entries, license = sha('d')) {
  return async endpoint => {
    if (endpoint.endsWith('/commits/HEAD')) return { sha: sha('e') };
    assert.ok(endpoint.endsWith(`?ref=${sha('e')}`), 'reads must use the resolved revision');
    if (endpoint.includes('/contents/')) return files;
    if (endpoint.includes('/license?')) return { sha: license };
    throw new Error(`Unexpected endpoint ${endpoint}`);
  };
}

test('unrelated commits and directory listing order do not report updates', async () => {
  const result = await checkSource(source, api([...entries].reverse()));
  assert.equal(result.status, 'current');
  assert.equal(result.latest_commit, sha('e'));
  assert.equal(exitCode([result]), 0);
});

test('nested reference changes, additions and deletions report updates', async () => {
  for (const files of [
    [entries[0], { ...entries[1], sha: sha('f') }],
    [...entries, { name: 'notes.md', type: 'file', sha: sha('f') }],
    [entries[0]],
  ]) {
    const result = await checkSource(source, api(files));
    assert.deepEqual(result.changes, ['skill-directory']);
    assert.equal(exitCode([result]), 2);
  }
});

test('license-only changes count and checking never advances the baseline', async () => {
  const before = JSON.stringify(source);
  const result = await checkSource(source, api(entries, sha('f')));
  assert.deepEqual(result.changes, ['license']);
  assert.equal(JSON.stringify(source), before);
});

test('missing skill and unavailable source are errors; partial successes survive', async () => {
  const results = await Promise.all([
    checkSource(source, api()),
    checkSource(source, async () => { throw new Error('GitHub HTTP 403'); }),
    checkSource(source, api([entries[1]])),
  ]);
  assert.deepEqual(results.map(r => r.status), ['current', 'error', 'error']);
  assert.match(results[1].error, /403/);
  assert.equal(exitCode(results), 1);
});

test('invalid baseline is rejected before network access', async () => {
  const result = await checkSource({ ...source, path: '../other' }, () => {
    assert.fail('invalid path must not be requested');
  });
  assert.equal(result.status, 'error');
  assert.match(result.error, /baseline/);
});
