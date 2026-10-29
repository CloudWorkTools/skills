# Flow review recovery implementation plan

> **For agentic workers:** Use `executing-plans` for inline execution. Keep the implementation and its independent decision review separate.

**Goal:** Complete flow synchronization at delivery without repeated generation or review calls for unchanged inputs.

**Spec:** The approved discussion requires bounded source reading, independent full-feature review, separate material-recovery and correction budgets, and local/GitHub synchronization.

**Architecture:** Preserve the checker, fingerprints, delivery boundaries and review JSON format. Keep review preparation and recovery rules in the reviewer reference, linked from Maintain and the enforcement contract.

**Tech stack:** Markdown instructions and scenarios; existing npm/Python package tests and Orca decision reviews.

## Constraints and review focus

- Draft/WIP work retains pending impact; unchanged bound inputs reuse evidence.
- Required source includes module context and dependencies from one pinned base/candidate pair.
- Partial passes cannot establish complete feature review; required omissions remain incomplete.
- Fingerprint changes cannot reset retry budgets; demonstrated findings cannot become material-only failures.
- Keep attempts in existing task evidence; no new checker schema, runner or dependency.
- The baseline reviewer interpreted pure material failures correctly but reported ambiguous counting and reviewer continuity. This is not evidence of a reproduced premature stop.

## Execution

- [x] Read existing instructions, prior adversarial feedback and installation receipt.
- [x] Run a fresh baseline decision against the unchanged instruction package.
- [x] Add raw recovery, retry, partial-review and repeated-preparation scenarios with separate rubrics.
- [x] Update Maintain, reviewer preparation/verdict/recovery rules and contract pointers.
- [ ] Run `npm test` and a fresh decision review without supplying the rubric initially.
- [ ] Create a PR with candidate identity, decisions and verification limits; satisfy required CI and merge normally.
- [ ] Update the local checkout and global installation, retain a backup and verify the installation receipt against the merged revision.
