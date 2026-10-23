---
name: flow-docs-sync
description: Use when establishing system or feature flowcharts with source-code navigation, requiring agents to read flow documents before code changes, enforcing documentation synchronization in CI, or adding, modifying, refactoring, moving or deleting code in an adopted project.
license: MIT
---

# Flow documentation synchronization

Keep system overview, feature flows and implementation references consistent in the same change. A source MD5 detects content changes; semantic accuracy requires source review and relevant behavioral evidence.

## Select the operation

- **Adopt:** establish the feature inventory, source scope, diagrams, mappings and validation baseline.
- **Maintain:** update an adopted project's affected flows alongside its source changes.
- **Audit:** report gaps and bypasses without modifying the system.

Use the project's existing documentation and diagram format. Read local instructions and terminology first. During structural exploration, use its required discovery tools and verify candidates against source. Installing this skill alone supplies neither repository enforcement nor guaranteed invocation by future agents.

Read [the enforcement contract](references/enforcement-contract.md) when establishing or auditing controls, changing mappings or checker policy, or interpreting a failed gate. It owns the data requirements and acceptance cases.

## Mandatory reading before source edits

On every task that adds, modifies, refactors, moves or deletes code or behavior-bearing inputs, first read the project's root `AGENTS.md`, flow overview and scope/source manifest. Resolve the affected features, then read their canonical flows, shared subflows and linked contracts before editing. Reading source to establish impact is allowed. Record the document paths/content identities and affected feature IDs in the task's existing evidence or handoff.

For a new capability, read related flows and document the proposed flow before implementation; distinguish it from existing behavior. When a required flow is absent or stale, establish its minimal source-verified baseline first. An unreadable required document blocks dependent source edits; continue only work that does not rely on it and report the gap. Re-read affected documents after a scope change or changed input. Each delegated agent must receive the applicable rule and resolve/read its own relevant documents. After resuming from a handoff or compaction, check that the read set is current before further edits.

During adoption, write the hard rule into root `AGENTS.md` using the contract's project-instruction template with verified project paths. Link the same policy from other agent instruction entrypoints actually used by the project. Skill installation alone does not perform this adoption. If instructions are local-only, preserve that boundary and report shared-workspace adoption incomplete until the bootstrap is configured.

## Required workflow

1. **Pin scope and snapshot.** Identify the reviewed base and exact candidate contents. Inventory user functions and their UI, API, CLI and background entrypoints. Include behavior-bearing templates, configuration, dependencies and build/deploy inputs. Record exclusions with reasons and unresolved coverage. Classify remote configuration and external behavior separately. Worktree, index and committed-tree verification are distinct; state which was checked.
2. **Establish navigation.** Provide a system overview with a thumbnail or feature link, one canonical flow per feature, stable feature/node IDs, and node-to-relative-path/qualified-symbol references. Shared subflows have one owner. Every formal feature needs an entry; a mapped file alone does not establish feature coverage. Capture success, decisions, error, cancellation and recovery paths where implemented. Mark proposals separately from current behavior.
3. **Compute impact before editing records.** Compare both trees, including added, deleted, modified and moved inputs. Derive affected features from the union of base and candidate mappings. Inspect new or changed entrypoints inside existing files as well as new files. Treat removed mappings, scope reductions and policy changes as reviewable changes, not exemptions. With no usable base, perform baseline inventory and report incremental validation incomplete.
4. **Synchronize in the same change.** Update affected flow sources, node mappings, feature entries and relevant evidence. Maintain source MD5s in one authoritative manifest. Every affected feature receives either a flow change or a specific, evidenced explanation that its behavior remains unchanged. A whole-file change requires revalidation of all mapped features. Identify indirect dependents; uncertain impact remains unresolved.
5. **Bind semantic review to contents.** A reviewer independent of the author checks the actual behavior and evidence. Bind the feature-specific decision to the base, scope/impact policy, affected features and relevant sources, flow sources, entrypoints and mappings. Any later change to a bound input invalidates affected review. Use an external review/check or the contract's content fingerprint; keep result records outside their own fingerprint. An author-written assertion is a declaration, not independent approval.
6. **Validate and report.** Check inventory closure, MD5s, paths/symbols, bidirectional node mappings, diagram syntax and generated overview/thumbnail consistency. Render and inspect diagrams; a successful parser alone does not prove legibility. Run relevant behavioral tests. For CI adoption or changes, exercise the contract's failing fixtures and the project's required image/deployment validations. Evidence belongs to the tested candidate; later changes require affected checks again.

## Enforcement and completion

When implementing adoption, install project-specific deterministic checks using existing tools and add the contributor rule alongside the mandatory project instructions. Preserve local files and do not commit private deployment data. Determine the repository's required-check and review settings through read-only inspection where available. Modify remote settings, publish, deploy or send messages only within existing authorization.

A merge gate must require a successful result for the actual candidate plus its required review. Missing, pending or skipped results are unverified. Preserve protections for untrusted fork code; use the project's safe manual path instead. Checker, manifest scope and workflow changes require independent review and fixed failing fixtures.

Report each state with evidence or an explicit incomplete reason:

| State | Evidence required |
| --- | --- |
| Skill created | Valid skill package and exercised usage scenarios |
| Agent reading rule adopted | Root `AGENTS.md` rule, valid document links and verified discovery in the project's actual agent entrypoints |
| Documentation adopted | Feature/input inventory, verified flows and mappings, named gaps |
| Checker verified | Positive and adversarial negative fixtures executed |
| CI executed | Candidate identity, command/run and result |
| Merge enforcement active | Repository rule and candidate check/review evidence |

Without a checker, label the project **manual verification only**. Without verified merge settings, report merge enforcement unconfirmed. Discovery gaps, unexecuted production checks and external behavior remain explicit limits; completeness claims cover only the stated scope and evidence.

## Common failures

| Temptation | Required response |
| --- | --- |
| Refresh hashes or whitespace to clear CI | Show the behavior difference or a substantiated unchanged-flow review |
| Delete a feature mapping to reduce impact | Preserve both-version impact and justify removal |
| Accept a new API because its file is registered | Register the entrypoint and its feature flow |
| Reuse approval after modifying code or a diagram | Invalidate the content-bound review |
| Declare hard enforcement after installing the skill | Report the actual adoption/checker/CI/merge-gate states |

## Example

`shared.py` belongs to features `download.batch` and `queue.resume`. A candidate removes the second mapping, changes the file, and adds a route in an already mapped API file. Both old features still require review; the new route needs a feature/flow mapping. Refreshing MD5s and adding an author's “no impact” note leaves semantic review incomplete. If the source changes after review, rerun affected checks and obtain review for the new contents.
