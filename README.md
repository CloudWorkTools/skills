# CloudWorkTools Skills

Reusable agent skills. The first skill, **pr-preview**, helps an agent create or operate an on-demand PR/worktree preview using a project's production build path.

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

```bash
npm test
```

Node.js 22+ and npm are required for the install test. It packs the repository, installs the tarball into a temporary project, installs the skill through the real npm CLI, and verifies every skill resource is copied intact and discoverable. It leaves your user-level skills and Docker workloads untouched. Network access is needed to obtain the pinned CLI if it is not cached.

The portable guidance was developed from the PR preview work in [MUAMS PR #71](https://github.com/ROCMCSpace/MUAMS/pull/71); MUAMS-specific service names, credentials, and deployment settings are not bundled.
