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

State the finite required read set and remaining unknowns before paid review.
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

Set a shared delivery-batch allowance before dispatch using authorized model calls,
time or tokens available in the runtime. Preserve existing stricter project limits
and explicit user budgets. Otherwise allow one initial independent batch review
and at most one bounded follow-up for demonstrated findings or repaired material
gaps. Split only for real independent boundaries, not to reset the allowance.

Within a live attempt, continue bounded reads in the same reviewer context.
Before an ended attempt is followed up, fix the named issue or supply the named
missing access/ranges in a smaller packet. Finding correction and material repair
are different causes, both visible in the shared allowance. Preserve demonstrated
findings even when a result also lacks evidence; unrelated additions do not fix
a read gap. Source/base/fingerprint/reviewer changes and task-owned pushes do not
reset the request identity or spent allowance.

When the allowance is exhausted, stop automatic dispatch, preserve the failed or
incomplete gate and finish independent safe work. Give one consolidated account
of remaining risks, scope and cost with options for a policy/budget decision;
repeated per-feature rerun approvals are not a default recovery strategy. Never
replace missing review with author self-approval or a rewritten fingerprint.

Record native usage for each observed attempt, including failures, in existing
task evidence. Label missing counters and shared-session attribution unknown;
cache/thinking subcounts are not additive to their parent totals. Telemetry gaps
neither justify another model call nor invalidate otherwise complete review.
