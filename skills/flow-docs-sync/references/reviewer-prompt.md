# Independent agent review

Use a fresh subagent with no inherited conversation when the runtime supports it. Supply the raw artifacts below; omit the author's proposed verdict and justifications. A human reviewer is the fallback when available. Repository-required human approval remains separate.

## Review preparation

The coordinator binds one authoritative comparison base and a stable candidate snapshot, including isolated staged/worktree content when applicable. Other bases serve navigation only. Provide versioned source paths and required ranges, including module context and dependencies. Make raw artifacts accessible for bounded reads instead of dumping a large diff or source into one tool response.

Divide independent work along manifest feature boundaries. Within one feature, the same reviewer reads the complete required scope in bounded pieces and checks cross-boundary contracts. Partial outputs are reading aids; the final feature verdict belongs to an independent reviewer covering that full scope. Use existing task evidence for read gaps and attempts, without a separate preparation agent or per-chunk reviewer fan-out.

## Dispatch template

```text
Review flow-documentation consistency for the supplied candidate.
Read-only: do not modify files, execute target application code, publish,
approve a repository review, or spawn additional reviewers.

Inputs:
- Authoritative comparison base, stable candidate snapshot, scope/impact policy and feature ID.
- The checker-generated fingerprint for that feature.
- The manifest's exact flow path, relevant document paths and recorded layout overrides.
- Versioned paths/ranges for raw diff and base/candidate source, module context and dependencies.
- Base/candidate flow sources, mappings and relevant contracts.
- Behavioral test code and execution evidence, with unverified items marked.

Verify the feature's actual branches, interactions, errors, cancellation,
recovery and side effects against its flow. Check hidden impact from removed
mappings, changed globals/imports and new entrypoints. Read additional relevant
source in bounded reads when artifacts are insufficient; request missing access.
Track unread or truncated required ranges and finish them in this attempt
when access is available. Cite source versions and covered ranges in evidence.
A hash or passing checker is not semantic proof. State any unchanged-flow
reason precisely, supported by the artifacts, rather than accepting an
assertion from the author.

Return JSON only:
{"feature":"<ID>","fingerprint":"<provided fingerprint>",
 "reviewer":"<actual agent/task identity>","verdict":"pass|fail|incomplete",
 "findings":[],"evidence":["<source/test references>"],
 "limitations":["<unverified matters>"]}

Use fail for demonstrated inconsistencies, even if other evidence is missing.
Use incomplete when required evidence is missing and no inconsistency is demonstrated.
Name missing paths/ranges or artifacts in limitations. Use pass only when the
entire required scope is covered and has no unresolved consistency findings.
Required omissions cannot be recorded only as limitations alongside pass.
Each finding names location, consequence and smallest correction.
```

The coordinator preserves every raw result in task evidence. Accept a passing result only after checking its feature/fingerprint, required coverage evidence and limitations for required omissions. Store only a complete passing result at the review-evidence path in the [project-file layout](../SKILL.md#project-files-and-responsibilities) and reference that path in the manifest. Reject partial or missing coverage without rewriting the reviewer's JSON. Review outputs are excluded from their own fingerprints. Subsequent input changes invalidate the affected result.

This file format is an auditable agent declaration. It neither authenticates a remote reviewer nor supplies a cryptographic signature. A CI integration must use its own trusted review/control path when reviewer authenticity is required. The checker validates record consistency and rejection conditions; it cannot determine whether an author impersonated a reviewer.

## Correction and material recovery

The coordinator allows an initial review and at most two finding-correction/re-review cycles per feature per user delivery request. A cycle corrects demonstrated findings, then obtains a fresh independent review. Preserve findings even when an attempt also lacks evidence; the coordinator cannot relabel them as material-only failure.

An `incomplete` result with no demonstrated findings uses a separate material-recovery budget. Continue bounded reading with the current reviewer when possible. After an ended attempt, allow at most two recovery redispatches per feature in that delivery request. Each must supply the named missing artifacts or repair access to the named ranges. Unrelated additions and identical failed reading methods do not justify redispatch.

For an unusable or stale attempt without named gaps, record and address its concrete failure cause before recovery redispatch, such as a timeout or candidate change. Pin replacement material to a stable snapshot; the same recovery limit applies.

Every redispatch after a non-passing or unusable attempt consumes the applicable budget, including attempts invalidated by candidate changes. Demonstrated findings use the correction budget; otherwise missing, partial or stale inputs use material recovery. Address the named findings or gaps before redispatch.

Neither budget resets when a fingerprint, commit, base or reviewer changes within the request. Preserve each raw result, attempt count, named gap and supplied evidence in existing task evidence. Do not overwrite the attempt history with the final passing record. Recompute the candidate fingerprint before accepting a result; changed bound inputs invalidate it rather than allowing its fingerprint to be rewritten.

When a budget is exhausted or a required gap cannot be addressed, stop automatic reviewer calls for that feature. Keep its semantic gate failed or incomplete, finish unrelated safe work and report remaining findings or missing access. Never substitute self-approval or claim synchronized delivery with a missing gate.
