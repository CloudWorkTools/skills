# Skill delivery guardrails implementation plan

> **For agentic workers:** Execute the scoped tasks below, preserving other workers' edits. Validate each task before the final branch review.

**Goal:** Make skill delivery errors observable through required PR tests, installed-link checks, behavioral review cases and global installation provenance.

**Architecture:** Reuse `npm test` and the existing installation tests. Keep behavior evaluation in a reviewer fixture, provenance outside installed skill directories, and repository instructions as short navigation pointers.

**Tech stack:** Node.js built-in test runner, Python standard library, GitHub Actions and GitHub CLI.

**Spec:** The user accepted all five retrospective recommendations in this session. The flow timing rationale is recorded in `docs/research/2026-10-23-flow-sync-trigger-timing.md`.

## Global constraints

- Preserve the accepted PR-delivery timing change and the existing optional strict hook.
- Add no runtime dependency and no AI generation runner.
- Use unprivileged PR CI with pinned actions, read-only contents and no persisted credentials.
- Do not weaken existing required checks or approvals; configure the new check only after its exact name has run successfully.
- Keep receipts outside the skill package, with source identity and content hashes.

## Review focus

- Installed links must not escape into repository-only documents or silently omit reference-style Markdown links.
- Draft/WIP must defer generation while ready PR updates invalidate stale evidence.
- Receipts must detect modified, missing or extra installed files and distinguish uncommitted source from a committed release.
- Fork PR tests must not receive privileged tokens or secrets.
- Protection and receipt status must be verified remotely/on disk rather than inferred from configuration writes.

## Tasks

1. Add deterministic installed Markdown link/anchor validation to the existing installation test, with failing fixtures for missing targets and package escapes.
2. Add an external receipt record/verify CLI and tests for matching installs, drift and worktree/commit identity.
3. Add `.github/workflows/tests.yml` to run existing tests on PRs, main pushes and merge groups; install pinned optional parser dependencies so CI exercises them.
4. Add the five behavior scenarios and a reviewer rubric in `tests/scenarios/flow-docs-sync.md`; record an independent current-skill evaluation.
5. Add a short repository navigation instruction and a contributor reference for focused reads, review responsibilities and receipt commands.
6. Run tests and independent review, create the PR, verify CI, protect main with the observed check, and merge using the user's existing instruction. Update and verify the global receipt against the merged commit.

## Verification

- [x] Installed link fixtures fail before the checker and pass afterward.
- [x] Receipt tests cover source identity and installed-content drift.
- [x] `npm test` passes; optional language coverage runs in CI.
- [x] Scenario review covers all five cases with concrete decisions.
- [ ] PR CI passes on the current head; main requires that check.
- [ ] Merge observed; global skill bytes and receipt match the merged source.
