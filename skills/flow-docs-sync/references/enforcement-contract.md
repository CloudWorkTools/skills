# Enforcement contract

Use this contract to design or audit a project's checker. These are requirements for project adoption, not a claim that a universal checker or CI gate is installed. Keep the existing schema when it can represent them; add only missing fields and checks.

## Authoritative records

| Record | Required meaning |
| --- | --- |
| Scope | Candidate Git tree, comparison base, included behavior-bearing inputs, explicit exclusions with reasons, special-file policy |
| Feature | Stable ID, name/search terms, implemented or planned status, entrypoints, canonical flow, shared-subflow/dependency links |
| Source | Explicit repository-relative path and MD5 of file bytes, stored once; symbols where applicable |
| Mapping | Feature ID, flow node ID, source path and qualified symbol; data/config nodes may identify a key or resource instead |
| Review | Feature ID, changed-flow explanation or evidenced unchanged-flow reason, reviewer identity, verification evidence and reviewed-content identity |
| Derived view | Inputs and reproducible generation command for overview and thumbnail; runtime viewer output may be derived without a committed image |

A thumbnail is a preview; searchable text and normal links remain available to agents. Declare the diagram format and rendering command. Diagram clicks alone are insufficient navigation because viewer support varies.

## Inventory and impact

- Enumerate the candidate's tracked inputs independently of its mapping manifest. Require every in-scope input to have an explicit mapping or a reviewed, narrow exclusion. A broad directory match cannot silently classify new code as documented.
- Compare base and candidate inventories and mappings. Affected features include both sides, removed entries, new entrypoints and documented dependents/shared subflows. Preserve review responsibility when a feature is removed or a file renamed.
- Use project-native routing, command and job registration to check entrypoint coverage. A new branch or capability inside an existing function still needs source-diff review; symbol enumeration alone cannot prove business-function completeness.
- Identify the snapshot actually tested. Local working files and staged contents do not imply committed-candidate validation. CI covers the candidate Git tree; untracked local inputs remain outside that evidence.
- Hash deterministic file bytes. Define checkout/line-ending handling and keep it consistent across platforms. For symlinks, submodules or generated execution inputs, define how their actual contents/version enter the inventory or fail on unsupported cases. Add special handling only when such inputs exist.
- Include behavior-bearing configuration, templates, dependency locks and deployment inputs. Keep secrets out of manifests and logs; represent private inputs by a safe version/reference and record their separate verification. Floating dependencies, external APIs and remote configuration require integration/runtime evidence beyond a Git diff.

## Content-bound review

MD5 is a file-change signal, not reviewer authentication or a proof of behavior. Preserve a project's stronger existing digest when it already serves the same role and no MD5 requirement applies. When MD5 is explicitly required, retain the required MD5 records.

The reviewer must inspect the same relevant source, mapping, entrypoint and diagram contents that validation checks. Two workable bindings are an externally recorded review/check tied to the candidate with stale-review dismissal, or a deterministic fingerprint of those inputs referenced by the review record. Include the comparison-base identity, scope/impact policy and affected feature IDs in the reviewed-content identity. Recompute impact and invalidate affected reviews when these change. The authenticated review binds each feature ID, its disposition and the reviewed-content identity.

Use an unambiguous ordered serialization and an established content digest for the fingerprint; exclude the review record itself to avoid a self-reference cycle. Verify reviewer identity through the project's review mechanism; a JSON field containing a name does not authenticate approval.

Keep check results external to the tested candidate, or exclude evidence-output records from the tested-input fingerprint. Changes to source, diagrams, mappings, test/checker code or validation policy still invalidate affected evidence. A content-fingerprint result reused for another commit must match all tested inputs and policy; final required checks still target the actual candidate.

A declaration of unchanged behavior includes the actual change and why existing branches/outcomes still match, supported by source inspection and relevant tests. The checker can require the record and reject stale input identities. An independent reviewer decides whether the explanation is sound. All related features must be accounted for after a shared input changes.

When no independent review mechanism is available, report semantic review incomplete. Agent delegation may assist review when available and authorized; it does not silently substitute for repository-required human approval.

## Mechanical checks and fail behavior

1. Validate schema, unique feature/node IDs and referential integrity. Reject duplicate/conflicting source hashes, unsafe/out-of-root paths and unsupported inputs.
2. Compare source inventories and MD5s. Detect missing/new/deleted/moved files, dangling references and unreviewed exclusions.
3. Resolve symbols/entrypoints using the project's tools. Compare graph nodes and mappings in both directions, including legitimate start/end/decision nodes under an explicit mapping convention. No mapping is invented solely to satisfy coverage.
4. Derive affected features from both snapshots and require current content-bound dispositions/review for every one. Check actual evidence identities rather than only whether a documentation filename changed.
5. Parse/render diagram sources and regenerate derived outputs; fail stale outputs, missing navigation and unresolved references. Inspect the resulting diagrams for readability.
6. Run the relevant behavior tests, including failure/recovery branches that the diagram promises. A passing unit test cannot stand in for required production validation.
7. Emit a nonzero result with affected feature IDs, file/flow references and the missing action. Incomplete scope, unavailable base, unsupported inputs or missing tools must not silently become success. A new-baseline operation can be reported separately from incremental verification.

Keep the checker deterministic and based on project-owned tools. Source graphs and AI suggestions assist discovery; validate their candidate relationships against implementation. Implement the smallest checker for the target languages rather than claiming a universal parser.

## Gate integrity

Compare the base and candidate checker, workflow and scope policy. Changes to enforcement need independent review and the fixed negative tests below. A change proposing to weaken the checker cannot use its own success result as its sole authorization; use the project's protected review/control path.

Require the actual candidate's checks and reviews before merge, verify stale approvals are dismissed when relevant contents change, and include merge-queue candidates when used. Preserve the repository's safe treatment of untrusted forks. If required work must be manually dispatched, document the dispatch path and match its resulting evidence to the exact candidate. Missing or skipped runs are not proof of successful verification.

Read repository CI rules before implementation. Where image integration or deployed production evidence is required, perform it within authorization or report adoption incomplete. Do not relax the rule or deploy without authorization merely to report completion.

## Acceptance fixtures

Run these as isolated temporary Git fixtures using the real project checker, not mocked “success” values. The semantic cases require both mechanical results and independent review evidence; test those distinct responsibilities. Every negative fixture names its expected rejection.

| Candidate change | Expected result |
| --- | --- |
| Valid baseline, then correct flow/source update with current review | Pass within declared scope |
| Source changes with no updated source digest | Reject stale MD5 |
| Rehash plus whitespace edit or unsupported “no impact” claim | Mechanical integrity may pass; semantic gate rejects missing adequate independent review |
| Remove an old mapping or narrow scope while changing its source | Preserve old affected features; reject missing removal/scope review |
| Add a file without explicit mapping | Reject uncovered input |
| Add a public route/command/job in an already mapped file | Reject missing entrypoint/feature mapping |
| Change a shared file but review only one of its features | Reject missing affected-feature review |
| Modify content after review or test execution | Reject stale review/check evidence |
| Keep head but change base, scope or impact policy | Recompute impact and reject stale review identities |
| Append only evidence-output records outside the tested-input fingerprint | Preserve content-level evidence without claiming the new commit's required gate ran |
| Delete/rename a source or symbol but keep old references | Reject dangling references |
| Update diagram source but retain stale thumbnail/overview | Reject stale derived view |
| Change a behavior-bearing config/lock/template/deploy input | Require mapped affected features and their review |
| Weaken checker/workflow to suppress a negative fixture | Reject through protected enforcement-change review/tests |
| Required result absent, skipped or for another candidate | Block merge verification |
| Pure formatting/refactor with current, substantiated unchanged-flow review | Pass without inventing a behavioral diagram change |

## Delivery evidence

Record commands, candidate identities, results and unverified scope in the project's existing evidence location. Keep semantic review, deterministic checks, runtime validation and remote merge-rule confirmation distinguishable. Report manual-only operation honestly until each relevant gate is deployed and verified.
