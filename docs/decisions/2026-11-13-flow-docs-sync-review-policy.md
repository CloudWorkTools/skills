# Flow navigation and risk-based review

Status: Accepted.

## Decision

Make project understanding, source navigation and documentation correspondence
the primary flow-docs-sync outcomes. Keep a project overview linked to focused
feature flows, with source paths and qualified symbols for control decisions.
Track drift at configured task/commit/PR boundaries and synchronize before delivery.

Separate source verification, mechanical validation and independent assurance.
Use per-feature `requires_review` booleans. Omission preserves strict review;
ordinary low-risk maintenance can explicitly opt out after a reviewed policy
migration. Initial adoption and important contract/security/data-loss changes
require independent review. A strict comparison base keeps review mandatory
until the policy migration enters that trusted base.

Replace the universal initial-plus-one-follow-up allowance with explicit cost
caps and concrete-progress recovery. Corrected findings or repaired named material
gaps justify another attempt within configured limits. Repeated blockers without
new evidence stop automatic redispatch. Preserve cost and request identity across
fingerprint changes and task-owned pushes.

## Reason and trade-off

A fixed round count measures neither cost nor completion. Material repair can
make another review useful after two attempts. Separating optional review allows
ordinary documentation delivery without pretending independent approval exists.
The cost is reliance on an agent or project policy to classify risk and verify
semantics; the portable checker cannot establish either.

Keeping mandatory review for every change offers stronger default assurance but
adds model work to ordinary maintenance. Removing all limits avoids early stops
but permits repeated unproductive spending. Retain explicit limits and stop when
no progress is demonstrated.

## Scope and verification

This changes the skill package and its checker, not consuming-project hooks,
installed copies, remote merge controls or an unattended AI runner. Numeric cost
and progress enforcement remain agent/runner responsibilities. Existing strict
projects require an authorized migration.

Deterministic regression cases live in
[checker tests](../../tests/flow_checker_test.py). Agent decision cases live in
[delivery scenarios](../../tests/scenarios/flow-docs-sync.md).

## Validation evidence

`npm test` passed with 22 Node tests and 103 Python cases, including 13 skips
for optional parsers and an unconfigured alternate Python interpreter. Added
checker cases cover optional review, strict-base migration, enabling required
review, invalid policy types and integrity checks under optional review.
`git diff --check` passed.

A fresh read-only reviewer answered all 17 raw delivery scenarios without the
rubric. Its decisions matched the scenario rubric. It found ambiguous migration
wording, reproduced the strict-base behavior, then confirmed the wording fix and
ran the added strict-base regression successfully. It reported no remaining
confirmed issue. Baseline evaluation had demonstrated mandatory review for
ordinary maintenance, the two-attempt recovery stop and incomplete overview
acceptance guidance.

No provider usage reduction was measured. Installed-project migration, live
GitHub events, unattended generation and rendered diagram readability were not
exercised. These checks do not establish those capabilities.
