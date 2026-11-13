# Independent review

Use a reviewer independent of the author when required by project policy. A
fresh context receives raw artifacts and scope, not the author's desired verdict.
A reviewer may cover related features in one repo, recording one verdict per
feature. Repository human approvals remain separate.

## Review preparation

Pin the authoritative base and candidate. Run the checker locally first; inventory,
syntax, stale source hashes and missing mappings do not need a model to diagnose.
Generate `packet` for affected features and supply:

- Direct changed input paths and bounded raw diff, including removed mappings.
- Full direct module context needed to understand those changes, the affected
  flows and owning contracts; exact source versions and available ranges.
- Named dependency contracts, versions and changed boundaries. Inspect additional
  implementation where a contract is absent, contradicted or cannot establish
  the interaction. A transitive fingerprint invalidation is not by itself a
  requirement to reread every dependency implementation or license bundle.
- Relevant global policy changes, actual configured test/CI commands, recorded
  execution and tested input/environment identity. Keep full raw sources and
  historical evidence available on demand; no whole-repository diff dump.

Before paid review, verify that the finite required read set, exact source
versions, bounded ranges, flows and actual test evidence are available. Repair
known material gaps and local checker errors before dispatch. State remaining
unknowns; do not pay a reviewer merely to rediscover a missing file.
Split oversized work at behavior/contract boundaries; source chunks are reading
aids, not independent approvals. Reuse verified unchanged context and evidence.
Read generated hashes and archival history through tool summaries rather than
printing them into every context. Complete available required reads within the
current attempt; clipped output names a next range, not a reason to end early.

## Dispatch template

```text
Independently review consistency for the supplied feature(s) and exact candidate.
Read-only repository; write only the review result in the assigned evidence path.
Inputs: packet, required read set, bounded raw diff, source/flow/contract versions,
relevant dependency boundaries, actual test command and execution/input evidence,
review allowance and prior unresolved findings if this is a follow-up.

Check branches, interactions, failure/cancellation/recovery and side effects.
Verify hidden impact from removed mappings, new entrypoints and changed globals.
Start with required direct context and named dependency contracts. Expand to
additional source when the interaction is uncertain; cite the reason and ranges.
Complete available unread/truncated required ranges before returning a verdict.
Request genuinely missing access by named path; keep unrelated work moving.
A hash, summary, old review or passing checker alone is not semantic proof.

Return one JSON object per feature:
{"feature":"<id>","fingerprint":"<provided>","reviewer":"<actual identity>",
 "verdict":"pass|fail|incomplete","findings":[],"evidence":[],"limitations":[]}
Each finding names location, consequence and smallest correction. Evidence names
versions, covered ranges and relevant tests/input identity. Demonstrated mismatch
is fail even if other material is missing. Required gaps with no findings are
incomplete and name exact missing ranges. Pass requires all required feature
scope and no unresolved inconsistency; required omissions cannot hide in limits.
```

Store only complete passing objects at
`docs/flow-evidence/reviews/<feature>/<fingerprint>.json`, referenced by the
manifest. Check the fingerprint again before import; retain the object unchanged.
Keep failed/incomplete raw attempts in existing task evidence. Historical raw
records may stay in Git/artifacts while the active manifest contains only current
passing pointers. Review results are excluded from source/policy fingerprints.
The checker verifies declarations, not actual reading or reviewer authenticity;
protected review/CI must establish those where required.

## Correction and material recovery

There is no universal two-round limit. Before dispatch, record any explicit
shared delivery-batch cap with its unit, value and spent amount: model calls,
elapsed time or tokens. Preserve user/runtime budgets and stricter project limits.
If none is configured, state that no numeric cap is configured; never invent a
provider quota or treat missing telemetry as unlimited credit.

Within a live attempt, complete bounded reads in the same reviewer context.
After an ended attempt, dispatch again only with recorded concrete progress:
a demonstrated finding was corrected or specifically named missing material is
now accessible in a repaired packet. Both consume actual configured cost, but
record finding correction and material recovery separately. Stop automatic
redispatch when the same blocker recurs without new evidence or correction;
changing a fingerprint, reviewer, base or unrelated file is not progress.
A completed initial review and follow-up do not themselves forbid further
review when the next attempt has concrete progress and fits explicit limits.

Preserve unresolved findings, raw attempts and one request identity across
features, retries and task-owned pushes. Splitting work, changing credentials or
reviewers does not reset spent cost. Enforce a cap before dispatch; if a hard cap
cannot be measured/enforced, stop paid automation and report that limitation.

When a configured cap is exhausted or progress stops, stop automatic dispatch
and give one consolidated report of blockers, evidence, spent cost and remaining
work. Continue independent safe work. Report source/document synchronization,
mechanical validation and independent review separately. Optional review does
not block ordinary synchronized delivery. Required review stays incomplete and
keeps the project's merge gate closed. Never substitute author self-approval or
rewrite a fingerprint to manufacture approval.

Record native usage for each observed attempt, including failures, in existing
task evidence. Label missing counters and shared-session attribution unknown;
cache/thinking subcounts are not additive to their parent totals. Telemetry gaps
neither justify another model call nor invalidate otherwise complete review.
