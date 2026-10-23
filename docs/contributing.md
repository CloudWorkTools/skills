# Skill delivery checks

Run `npm test` before delivering repository changes. The command owns installation, upstream tracking and Python checker tests. `.github/workflows/tests.yml` runs it for PRs, main pushes and merge-group candidates with pinned optional parsers and two Python versions. Required-check settings are remote configuration; inspect them before claiming merge enforcement.

The installation tests compare packaged resources and validate relative Markdown links in the installed skills. A repository-only document cannot satisfy an installed resource link. Supported Markdown syntax and limitations live beside the link checker.

## Behavior review

When changing flow-docs-sync instructions, give a fresh reviewer the raw cases from [the delivery scenarios](../tests/scenarios/flow-docs-sync.md). Keep the rubric out of the initial scenario prompt. The reviewer owns cross-file consistency and whether agent decisions match the intended delivery boundary; deterministic tests own file/path/anchor rules.

Record case decisions, source evidence, candidate identity and unverified behavior in the PR. A passing package test does not establish that a GitHub event invokes an AI model. Flow generation and the final candidate validator need separate integration evidence.

## Global installation provenance

Keep receipts outside installed skills so metadata does not affect package equality. After installation, record the exact source and installed bytes:

```bash
python3 -B scripts/skill-receipt.py record --source skills/flow-docs-sync --installed /home/karl/.agents/skills/flow-docs-sync --receipt /home/karl/.agents/skill-receipts/flow-docs-sync.json --backup /path/to/existing/backup
python3 -B scripts/skill-receipt.py verify --receipt /home/karl/.agents/skill-receipts/flow-docs-sync.json
```

Use the actual installation, receipt and backup paths; omit `--backup` when none exists. Recording compares the complete file set and SHA-256 content before writing. A worktree installation carries a content identity; only source bytes and inventory matching `HEAD` receive a committed revision. After merging, record again from the merged checkout and verify. The receipt records provenance; it does not install or replace skill files.
