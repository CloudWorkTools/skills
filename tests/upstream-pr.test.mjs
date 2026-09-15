import assert from 'node:assert/strict';
import test from 'node:test';
import { proposal, publish } from '../scripts/upstream-pr.mjs';

const update = { name: 'teach', status: 'update-available', changes: ['skill-directory'],
  reviewed_commit: 'a'.repeat(40), latest_commit: 'b'.repeat(40),
  latest_fingerprint: 'c'.repeat(64), latest_license_sha: 'd'.repeat(40),
  source: 'https://github.com/owner/repo/tree/main/skills/teach',
  compare: 'https://github.com/owner/repo/compare/a...b' };
const report = { results: [update] };
const options = { repo: 'owner/repo', assignee: 'owner' };

test('deduplication ignores time and unrelated commits; malformed or failed checks cannot write', async () => {
  assert.equal(proposal(report).signature, proposal({ checked_at: 'later', results: [
    { ...update, latest_commit: 'e'.repeat(40) },
  ] }).signature);
  assert.notEqual(proposal(report).signature, proposal({ results: [
    { ...update, latest_license_sha: 'e'.repeat(40) },
  ] }).signature);
  for (const bad of [{ results: [{ status: 'error' }] }, { results: [{ ...update, source: 'https://evil.test/' }] }]) {
    await assert.rejects(publish(bad, options, () => assert.fail('no API call allowed')));
  }
  assert.match(await publish({ results: [{ status: 'current' }] }, options, () => assert.fail()), /No updates/);
});

test('creates a draft, updates only the report, reuses PR, and preserves closed/ready batches', async () => {
  let pr, content, closed = false, ready = false;
  const writes = [];
  const api = async (method, path, data) => {
    if (method !== 'GET') writes.push({ method, path, data });
    if (path === 'repos/owner/repo') return { default_branch: 'main' };
    if (path.includes('state=open')) return pr && !closed ? [{ ...pr, draft: !ready }] : [];
    if (path.includes('state=closed')) return closed ? [pr] : [];
    if (path.includes('/git/matching-refs/')) return [];
    if (path.endsWith('/commits/main')) return { sha: 'f'.repeat(40) };
    if (path.endsWith('/git/refs')) return {};
    if (path.includes('/git/trees/')) return { tree: content ? [{ path: '.github/upstream-reviews/teaching-with-diagrams.md', sha: '1'.repeat(40) }] : [] };
    if (path.includes('/git/blobs/')) return { content };
    if (path.includes('/contents/')) { content = data.content; return {}; }
    if (path.endsWith('/pulls')) {
      pr = { number: 1, html_url: 'https://github.com/owner/repo/pull/1', draft: data.draft,
        head: { ref: data.head, repo: { full_name: 'owner/repo' } } };
      return pr;
    }
    if (path.endsWith('/assignees')) return {};
    assert.fail(`Unexpected API: ${method} ${path}`);
  };
  await publish(report, options, api);
  assert.equal(pr.draft, true);
  assert.equal(writes.filter(w => w.path.endsWith('/pulls')).length, 1);
  writes.length = 0;
  await publish(report, options, api);
  assert.equal(writes.filter(w => w.method === 'PUT' || w.path.endsWith('/pulls')).length, 0);
  await publish({ results: [{ ...update, latest_fingerprint: 'f'.repeat(64) }] }, options, api);
  assert.equal(writes.filter(w => w.method === 'PUT').length, 1);
  assert.ok(writes.filter(w => w.method === 'PUT').every(w => w.path.endsWith('/contents/.github/upstream-reviews/teaching-with-diagrams.md') && w.data.sha));
  ready = true;
  writes.length = 0;
  assert.match(await publish(report, options, api), /under review/);
  assert.equal(writes.length, 0);
  closed = true;
  assert.match(await publish(report, options, api), /already closed/);
  assert.equal(writes.length, 0);
});
