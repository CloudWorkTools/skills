# Release retro followups implementation plan

> **For agentic workers:** Use executing-plans for assigned ownership; parallel authors have isolated task context. Root integrates and reviews. Existing review allowances remain unchanged.

**Goal:** Implement the seven retro improvements accepted by the user, preserving source protection and safe device recovery.

**Architecture:** Extend existing release/device/checker tools. Keep raw attempts immutable and one typed current snapshot. Use deterministic summaries and transition-driven waiting rather than new agent rules.

**Tech Stack:** Existing Python standard-library tools, unittest/pytest, Node installation checks, GitHub Actions and Orca CLI.

**Spec:** User accepted all seven findings in the 2026-11-01 release retrospective. Details and acceptance are below; no additional product-design approval is pending.

## Constraints

- Keep private source/Public compiled-only boundaries, exact source/version/hash gates, ABI-native checks and scoped publisher environments.
- Keep pidfd safety and existing eight-second observation budget. A currently healthy R36 is not permission for a restart or a fabricated successful transaction.
- Preserve original dirty Viewer workspace. Authors leave scoped changes uncommitted for root flow integration; do not overwrite another author's files.
- No fresh reviewer dispatch and no blanket hash-only approvals. Root reviews author changes; authors review root-owned policy deltas when requested.
- No token values in chat, files or broad owner credentials in CI. Manual human authentication is an external dependency.

## Tasks and ownership

- [x] Viewer author: package_install.py and recovery tests. Record expected/observed revision and observation time with bounded sanitized diagnostics; test unavailable, unmarked, wrong and ready observations. Diagnose before changing retry semantics. No live-device writes.
- [x] Sender author: existing release controller/backend, relevant tests and sender-release workflow. Add read-only exact-release verification/resume with explicit published-but-unverified state, API-403 fallback to anonymous public page/assets and no re-upload. Skip duplicate release checks when publisher preflight fails; private build-only still requires all source/flow/platform gates.
- [x] Operations author: minimal deterministic utilities in scripts/ and tests/ of CloudWorkTools/skills. Bounded projection, a single validated current checkpoint separate from immutable attempts, and transition-driven waiting. Preserve unknown/failure/liveness information and mailbox acknowledgment authority. Reuse available Orca CLI waiting rather than patching installed application binaries.
- [x] Root: align an explicit trusted flow base between local staged checks and candidate CI, including validation and branch/first-push tests; migrate both source copies and installed checker with receipts.
- [x] Root: Viewer preflight/check job ordering; finish scoped publisher credential setup where current authentication permits it, otherwise retain a concrete executable wizard and exact blocker.
- [x] Root: adopt the operations utility for the existing private publication snapshot, remove contradictory current-state descriptions while preserving raw attempts, and use bounded output for this run.
- [ ] Root: run appropriate complete checks, synchronize only affected flows/evidence, commit/push reviewable PRs and present any required exact-head landing decisions only after readiness.

## Verification

- Viewer fixed check runner, focused recovery regressions, actual-base flow gates.
- Sender make check, native/Windows and release workflow invariants, explicit post-publication transport-failure fixtures.
- Skills npm test, install equality/link tests and new operations/base tests.
- Read-only device checks may confirm current runtime; installed bytes remain the already published versions until a newly approved release.

## Delivery evidence

- Viewer: full50 local checks passed with pinned MQTT dependency; PR58 initial CI passed.
- Sender: full540 passed17skips and focused64 passed; PR30 initial CI passed.
- Skills: full20Node/97Python passed13optional-parser skips; independent13case/4boundary review passed after one bounded Windows UID correction. Native Windows execution and ACL validation remain unverified.
- Canonical private CURRENT replaces contradictory mutable state; raw histories and failed R36 attempts remain immutable.
- Dedicated publisher credentials remain absent. Browser access host unavailable; executable wizard delivered and user action pending. No broad owner credential installed in CI.
- Final corrected checker commits/CI and exact-head landing decisions remain the delivery boundary.
