# flow-docs-sync adoption implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the bootstrap and adoption guidance requirements of [issue #3](https://github.com/CloudWorkTools/skills/issues/3), retaining the requested colored change-filtering diagram.

**Architecture:** Keep shared rules in root `AGENTS.md` and compatibility entrypoints as imports. Expand the existing enforcement contract with adoption references; retain the current checker, parser, manifest and review formats.

**Tech stack:** Markdown, Mermaid, existing Node.js and Python tests.

**Spec:** [Adoption decision](../../decisions/2026-10-23-flow-docs-sync-adoption.md).

**Additional source review:** Research `cursor/plugins/pstack` at the user's request; retain a separate cited research note and adopt only small verification-evidence improvements that fit the existing runtime template.

## Global constraints

- Preserve existing instructions and local-only files; verify actual agent discovery.
- AST cosmetic changes refresh byte fingerprints without unnecessary redraw/review; file-mode inputs remain conservative.
- Stage adoption by end-to-end feature with its shared dependencies; report partial coverage explicitly.
- CI templates are separate follow-up work; hooks, automatic dependency discovery and richer diagram parsing remain evaluation items.
- No changes to checker/parser behavior, manifest schema or reviewer JSON; no new dependencies.

## Review focus

- Existing root, `.claude`, ancestor and local instructions must not hide the shared gate; inspect the entrypoint matrix against official documentation.
- Partial scope must retain shared dependencies; inspect the dependency checklist and staged-adoption example.
- Cosmetic filtering must preserve behavior-bearing literals/directives and file-mode limitations; retain the existing tests and visually inspect the colored graph.
- Completion reporting must distinguish rule adoption, actual read ordering, structure, semantics and remote controls; inspect the report template.
- Deferred capabilities must have explicit dispositions and reasons; inspect the follow-up table and PR response against all issue suggestions.

## Task 1: Complete adoption guidance

**Files:** Modify `skills/flow-docs-sync/SKILL.md`, `skills/flow-docs-sync/references/enforcement-contract.md`, `README.md`, `README.zh-TW.md`. Create `docs/research/2026-10-23-pstack-flow-docs-sync.md`. Preserve and commit the linked decision and this plan with the changes.

**Interfaces:** Consumes the existing manifest/CLI and official Claude Code discovery rules. Produces a packaged, linked adoption procedure without changing runtime interfaces.

- [ ] Replace ambiguous bootstrap linking with a shared-rule/import/discovery contract; add a compact Adopt workflow and report-state pointer.
- [ ] Add the entrypoint matrix, authority and dependency inventory, mixed-language selection, phased adoption example, runtime evidence and completion templates, and scoped follow-up dispositions.
- [ ] Update README summaries to route to the owning guidance; retain the colored diagram and its guarantee/token boundaries.
- [ ] Verify local links and anchors, `git diff --check`, Mermaid rendering and `npm test`. Expected: valid links/render, green Node tests and Python tests with any skips identified.
- [ ] Obtain an independent review of the full diff and issue acceptance criteria. Correct factual or completeness findings before delivery.
- [ ] Commit the task, push the branch and create a reviewable PR with the main suggestion plus all nine dispositions. Keep merge and actual project rollout separate from implementation completion.
