# Flow sync execution and usage plan

**Goal:** Observe actual conditional generation/review calls and report docs-sync token usage, including failures and unknown coverage.

**Approved scope:** The four retrospective candidates and the per-sync usage field approved in the conversation.

**Design:** Reuse the existing checker and Claude Code counters. Keep per-attempt usage in an append-only ledger, separate decision experiments from actual fixture execution, and attach test configuration to review inputs. Skill delivery reports use measured totals or an explicit partial/unknown status.

## Implementation

1. Add failing offline tests for failed-call accounting, missing usage, phase totals and review configuration.
2. Extract usage normalization from decision parsing; persist every CLI attempt before raising or validating output.
3. Exercise a real two-feature temporary Git repository through Draft, ready, repeated-ready and cosmetic changes. Only invalidated features invoke generation and an independent reviewer; execute the existing checker on actual candidates.
4. Include exact test commands/configuration and execution evidence in review inputs.
5. Add per-request token accounting to Maintain, the completion report and raw behavioral cases. Keep usage evidence outside fingerprint inputs; unavailable telemetry does not block synchronization.
6. Run offline repository checks, one measured execution, and bounded independent review. Record execution and validation overhead separately.
7. Deliver through required CI and a normal PR merge, then update the global skill and its receipt.

## Verification

- Zero extra generation/review calls in Draft, unchanged and AST-cosmetic states.
- One changed feature generates and receives independent review; the unrelated feature remains untouched.
- Failed/malformed/timed-out calls remain recorded; missing counters remain unknown.
- Phase totals include all reported models and preserve cache categories without double-counting.
- Review packets contain actual configured commands and evidence rather than guessed defaults.
- Final reports distinguish measured fixture calls from broader task/provider coverage and decision-only samples.
