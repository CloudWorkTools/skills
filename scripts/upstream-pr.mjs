import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const prefix = 'automation/teaching-upstreams-';
const reportPath = '.github/upstream-reviews/teaching-with-diagrams.md';

export function proposal(report) {
  if (!Array.isArray(report.results) || !report.results.length ||
      report.results.some(r => !['current', 'update-available'].includes(r.status))) {
    throw new Error('Incomplete upstream check; no PR changes made');
  }
  const updates = report.results.filter(r => r.status === 'update-available');
  if (!updates.length) return null;
  for (const r of updates) {
    if (!/^[\w-]+$/.test(r.name) ||
        ![r.reviewed_commit, r.latest_commit, r.latest_license_sha].every(v => /^[a-f0-9]{40}$/.test(v)) ||
        !/^[a-f0-9]{64}$/.test(r.latest_fingerprint) ||
        ![r.source, r.compare].every(v => /^https:\/\/github\.com\/[\w./-]+$/.test(v)) ||
        !Array.isArray(r.changes) || !r.changes.length ||
        r.changes.some(v => !['skill-directory', 'license'].includes(v))) throw new Error('Invalid update report');
  }
  updates.sort((a, b) => a.name.localeCompare(b.name));
  // Ignore timestamps and unrelated upstream commits when deduplicating notifications.
  const signature = createHash('sha256').update(JSON.stringify(updates.map(r =>
    [r.name, r.reviewed_commit, r.latest_fingerprint, r.latest_license_sha]))).digest('hex');
  const text = `<!-- upstream-batch:${signature} -->\n# 待審查的教學技能上游更新\n\n` +
    '這是更新通知，不是已完成的技能整合。請勿只合併報告就視為完成更新。\n\n' +
    updates.map(r => `## ${r.name}\n\n變更：${r.changes.join(', ')}\n\n` +
      `[來源快照](${r.source}) · [差異比較（整個上游 repo）](${r.compare})\n\n` +
      `- 已審查版本：\`${r.reviewed_commit}\`\n- 待審查版本：\`${r.latest_commit}\`\n` +
      `- 目錄 fingerprint：\`${r.latest_fingerprint}\`\n- 授權 SHA：\`${r.latest_license_sha}\`\n`).join('\n') +
    '\n## 人工整合清單\n\n- [ ] 閱讀相關目錄與授權差異，決定採用或略過，記錄理由。\n' +
    '- [ ] 適配本地教學技能，保留刻意設計的差異。\n- [ ] 驗證 Mermaid、文件連結及 npm test。\n' +
    '- [ ] 僅將確實審查過的版本更新到 lock、來源連結及授權聲明。\n' +
    '- [ ] 再檢查上游是否有新變更，完成後才將 PR 標為 Ready for review。\n';
  return { signature, text };
}

async function github(method, endpoint, data) {
  const args = ['api', '--method', method, endpoint];
  if (data) args.push('--input', '-');
  return JSON.parse(execFileSync('gh', args, {
    input: data ? JSON.stringify(data) : undefined, encoding: 'utf8', timeout: 30000,
  }) || 'null');
}

export async function publish(report, { repo, assignee }, api = github) {
  const item = proposal(report);
  if (!item) return 'No updates; no PR needed';
  if (!/^[\w.-]+\/[\w.-]+$/.test(repo) || !/^[\w-]+$/.test(assignee)) throw new Error('Invalid repository or assignee');
  const root = `repos/${repo}`;
  const metadata = await api('GET', root);
  let open;
  for (let page = 1; ; page++) {
    const prs = await api('GET', `${root}/pulls?state=open&per_page=100&page=${page}`);
    const matches = prs.filter(p => p.head.repo?.full_name === repo && p.head.ref.startsWith(prefix));
    if (matches.length > 1 || (open && matches.length)) throw new Error('Multiple upstream PRs; review manually');
    open ||= matches[0];
    if (prs.length < 100) break;
  }
  if (open && !open.draft) return `PR ${open.html_url} is under review; left untouched`;
  const branch = open?.head.ref || `${prefix}${item.signature.slice(0, 16)}`;
  const head = encodeURIComponent(`${repo.split('/')[0]}:${branch}`);
  if (!open) {
    const previous = await api('GET', `${root}/pulls?state=closed&head=${head}&per_page=1`);
    if (previous.length) return `Batch already closed: ${previous[0].html_url}; reopen manually to reconsider`;
    const branches = await api('GET', `${root}/git/matching-refs/heads/${branch}`);
    if (!branches.some(b => b.ref === `refs/heads/${branch}`)) {
      const base = await api('GET', `${root}/commits/${encodeURIComponent(metadata.default_branch)}`);
      await api('POST', `${root}/git/refs`, { ref: `refs/heads/${branch}`, sha: base.sha });
    }
  }
  // A recursive tree avoids treating API/auth failures as a missing report.
  const tree = await api('GET', `${root}/git/trees/${branch}?recursive=1`);
  if (tree.truncated) throw new Error('Truncated tree; refusing an uncertain write');
  const file = tree.tree.find(f => f.path === reportPath);
  let unchanged = false;
  if (file) {
    const blob = await api('GET', `${root}/git/blobs/${file.sha}`);
    unchanged = Buffer.from(blob.content, 'base64').toString('utf8').startsWith(`<!-- upstream-batch:${item.signature} -->`);
  }
  if (!unchanged) await api('PUT', `${root}/contents/${reportPath}`, {
    message: 'docs: report pending teaching skill upstream updates', branch,
    content: Buffer.from(item.text).toString('base64'), ...(file ? { sha: file.sha } : {}),
  });
  const pr = open || await api('POST', `${root}/pulls`, {
    title: '教學技能上游更新：待人工整合', head: branch, base: metadata.default_branch, draft: true,
    body: `@${assignee} 發現上游更新，是否要採用？\n\n` +
      `請查看本 PR 的 \`${reportPath}\`，內含差異連結與審查清單。\n\n` +
      '這個 Draft PR **只有更新報告**，尚未修改技能或已審查版本。請先完成內容整合與測試，再決定合併；不採用可直接關閉。\n\n' +
      '排程只更新報告，不覆蓋人工修改的其他檔案或此 PR 說明。標為 Ready for review 後停止自動更新。',
  });
  await api('POST', `${root}/issues/${pr.number}/assignees`, { assignees: [assignee] });
  return pr.html_url;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const report = JSON.parse(await readFile(process.argv[2], 'utf8'));
  console.log(await publish(report, { repo: process.env.GITHUB_REPOSITORY, assignee: process.env.UPSTREAM_ASSIGNEE }));
}
