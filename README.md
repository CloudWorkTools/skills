# CloudWorkTools Skills

[繁體中文](README.zh-TW.md)

Reusable agent skills for previews, technical teaching, project documentation and client quotations.

| Skill | Purpose |
| --- | --- |
| [pr-preview](skills/pr-preview/SKILL.md) | Create or operate an on-demand PR/worktree preview using a project's production build path. |
| [teaching-with-diagrams](skills/teaching-with-diagrams/SKILL.md) | Teach technical concepts through grounded explanations, practice and Mermaid diagrams. Combines reviewed practices from three upstream skills with update tracking. |
| [readme-value](skills/readme-value/SKILL.md) | Help first-time visitors understand a project's use, evidence and next step, with concrete proposals when its value is still unproven. |
| [client-quotation](skills/client-quotation/SKILL.md) | Prepare a service quotation and matching plain-language scope attachment; includes blank editable ODT templates. |

## Client quotations

Install with `npx --yes skills@1.5.24 add CloudWorkTools/skills --skill client-quotation --agent codex --yes`. Use `$client-quotation` to draft or revise a quotation and scope attachment that share one identifier, show payment milestones clearly, and describe UI review and agreed adjustments. The bundled ODT templates contain field prompts only; replace them with authorized project details before delivery.

## README value

Install from this checkout with `npx --yes skills@1.5.24 add . --skill readme-value --agent codex --yes`, then ask:

> 用 $readme-value 改善這個 repo 的 README，讓第一次來、沒有專業背景的人看懂用途、目前成果與如何開始。把深入技術內容放到延伸文件；價值還未驗證的部分，提出具體且標示為建議的未來工作。

The skill adapts audience guidance from `crafting-effective-readmes`, benefit analysis from `value-proposition` and document organization from `documentation-writer`. It is independent of the teaching skill and includes its own upstream checker. See [sources, adaptations and maintenance](skills/readme-value/references/composition.md).

Run `npm run skills:check-readme-updates` in this repository, or `node <skill-directory>/scripts/check-upstreams.mjs` after installation. The weekly workflow checks both skills independently. README updates use a separate Draft PR and `.github/upstream-reviews/readme-value.md`; source adoption requires review before advancing the baseline.

## Teaching with diagrams

Install the composite skill in your project:

```bash
npx --yes skills@1.5.24 add CloudWorkTools/skills --skill teaching-with-diagrams --agent codex --yes
```

Then ask:

> 用 $teaching-with-diagrams，把這個模型的 README 整理成繁體中文初學者教材，加入 Mermaid 流程圖、數值例子與有解答的小練習，保留操作指南的入口。

The skill combines **teach** (learning outcomes and practice), **documentation-writer** (Diátaxis structure) and **mermaid-diagrams** (visual explanation) into a self-contained adaptation. It supports one-off Markdown documents as well as an explicitly requested ongoing course. The three original skills do not need to be installed separately. See [composition, source links and maintenance decisions](skills/teaching-with-diagrams/references/composition.md).

### Track upstream changes

In this repository:

```bash
npm run skills:check-updates
```

After installing the skill, ask the agent to check its upstream updates, or run:

```bash
node .agents/skills/teaching-with-diagrams/scripts/check-upstreams.mjs
```

Node.js 22+ and GitHub network access are required. The checker compares each complete skill directory and root license with the reviewed baseline. It prints changes and compare links without modifying files. Exit codes are `0` unchanged, `2` updates available, and `1` check failure. `GH_TOKEN` or `GITHUB_TOKEN` is optional for authenticated API rate limits.

[Check skill upstreams](https://github.com/CloudWorkTools/skills/actions/workflows/skill-upstreams.yml) runs every Monday at 03:17 UTC (11:17 Asia/Taipei) and can be run manually from Actions. When updates are found, it opens or updates one **Draft PR**, assigned to `jhihweijhan`, containing a report, comparison links and a review checklist. Find it in [Pull requests](https://github.com/CloudWorkTools/skills/pulls) or [GitHub notifications](https://github.com/notifications); email delivery depends on your GitHub notification settings. No AI key is needed: the workflow uses its built-in `GITHUB_TOKEN`.

The PR is a notification, **not a completed adaptation**. Ask your agent to review and adapt the upstream changes on that PR branch, test them, and update the reviewed baseline before marking it ready. The automation only writes `.github/upstream-reviews/teaching-with-diagrams.md`; it preserves other files and your PR description. Identical batches cause no report commit, closed batches are not reopened automatically, and non-draft PRs are left untouched. Reopen a dismissed PR manually to reconsider it. If updates disappear, close the stale PR manually. Check failures stop PR writes and remain visible in Actions.

Organization and repository settings must allow Actions to create pull requests. The workflow grants only `contents: write` and `pull-requests: write` to its notification job, runs on the default branch, and never automatically merges or advances the lock. Follow the [review and adoption procedure](skills/teaching-with-diagrams/references/composition.md#review-and-adopt-an-update). Schedule timing depends on GitHub Actions availability.

## Install with npm

Run this in the project where you want to use the skill:

```bash
npm exec --yes --package=skills@1.5.24 -- skills add CloudWorkTools/skills --skill pr-preview --agent codex --yes
```

Equivalent `npx` command:

```bash
npx --yes skills@1.5.24 add CloudWorkTools/skills --skill pr-preview --agent codex --yes
```

For Claude Code, replace `--agent codex` with `--agent claude-code`. Add `--global` for user-level installation. These options use the standard [skills npm CLI](https://github.com/vercel-labs/skills), which installs the skill and its references into the agent's skill directory.

You can also install this repository as an npm dependency from GitHub, then register the skill:

```bash
npm install --save-dev github:CloudWorkTools/skills
npm exec --yes --package=skills@1.5.24 -- skills add ./node_modules/@cloudworktools/skills --skill pr-preview --agent codex --yes
```

The package is distributed through GitHub; it is not published under `@cloudworktools/skills` on the npm registry. Installation copies agent guidance; it does not start containers or modify deployment configuration.

## Use

Ask your agent:

> Use $pr-preview to preview PR #42 for manual review, using this project's production build path. Verify the source revision, login and assets, and give me the cleanup command.

Or:

> 用 $pr-preview 預覽目前 worktree（含未 commit 修改），確認與生產建置路徑一致。檢視完後清理這一站，保留其他環境。

The agent inspects and reuses the target project's preview script, or creates/adapts one using the included implementation contract. It covers exact PR revisions, distinct worktree identities, readiness failures, private state, offline logs/teardown, and cleanup verification.

Preview execution needs Git, Docker Compose, and a dedicated preview host/daemon. Use trusted code and preview-only credentials/data. Production parity depends on the project's actual deployment overlays, data, and external services; container naming alone is not a security boundary.

## Contents and validation

- [pr-preview skill](skills/pr-preview/SKILL.md)
- [Implementation contract](skills/pr-preview/references/implementation.md)
- [Teaching with diagrams skill](skills/teaching-with-diagrams/SKILL.md)
- [Teaching composition and update tracking](skills/teaching-with-diagrams/references/composition.md)

```bash
npm test
```

Node.js 22+ and npm are required for the install tests. They pack the repository, install the tarball into temporary projects, install each skill through the real npm CLI, and verify every resource is copied intact and discoverable. Update-check tests cover reference changes, additions/deletions, license changes, unrelated commits and failed API calls. The tests leave user-level skills and Docker workloads untouched. Network access is needed to obtain the pinned CLI if it is not cached.

The portable guidance was developed from the PR preview work in [MUAMS PR #71](https://github.com/ROCMCSpace/MUAMS/pull/71); MUAMS-specific service names, credentials, and deployment settings are not bundled.
