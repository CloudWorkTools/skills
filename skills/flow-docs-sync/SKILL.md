---
name: flow-docs-sync
description: Use when establishing system or feature flowcharts with source-code navigation, requiring agents to read flow documents before code changes, enforcing documentation synchronization in CI, or adding, modifying, refactoring, moving or deleting code in an adopted project.
license: MIT
---

# Flow documentation synchronization

Keep system overview, feature flows and implementation references consistent in the same change. The bundled checker verifies structural/content consistency; source review and behavioral evidence establish semantic confidence.

## Select the operation

- **Adopt:** inventory features/inputs, establish flows and mappings, install the project reading rule and checker/hook.
- **Maintain:** read affected flows before editing, synchronize changes and run checks/review.
- **Audit:** report coverage gaps and bypasses without changing the system.

Read local instructions and terminology first; reuse the project's documentation and discovery tools. Installing this skill does not configure a project or its CI. Whole-project adoption requires all first-party behavior-bearing logic accounted for; excluded logic remains an explicit coverage gap.

## Mandatory bootstrap, available in this file

During adoption, write this block into root `AGENTS.md` and link it from the other agent entrypoints actually used, including `CLAUDE.md` when applicable. Replace the paths and checker command with verified project locations. Preserve existing instructions and local-only files. Establish missing document baselines before enabling their pointers.

```markdown
## [MANDATORY] Flow Documentation Sync Gate
1. Pre-Edit Read: before adding, modifying, refactoring, moving or deleting
   code or behavior-bearing inputs, read docs/flows/README.md,
   docs/flow-manifest.json and all affected feature/shared flows and contracts.
   Before the first edit, report: Affected Feature IDs: <resolved IDs>.
   Missing/stale flows require a source-verified baseline first;
   unreadable required documents block dependent edits.
2. Post-Edit Sync: run flow-docs-sync Maintain, update affected flows,
   mappings and source fingerprints in the same change, then run:
   python3 tools/flow-docs/flow_checker.py check --base HEAD
   Use the project's actual comparison base; HEAD is the local default.
   Obtain independent agent review where required; preserve repository human
   approval requirements. Hash refreshes alone are not semantic review.
3. Delegation/resume: each executing agent reads its own affected documents.
   Recheck the read set after scope/input changes or a handoff.
   Missing required checks or unresolved coverage prevent completion claims.
```

This block is usable without a reference file or installed skill. For new capabilities, read related flows and document intended behavior as proposed before implementation. Record read document identities and affected IDs in existing task evidence. Reading source to discover impact is allowed before editing. A read declaration cannot prove comprehension.

If an optional packaged resource is missing, retain this rule, verify the installed package and recover the matching resource from the skill's managed source. Report tooling incomplete; missing tooling does not authorize bypassing it or require stopping unrelated work.

## Maintain workflow

1. **Read and pin.** Read root instructions, overview, manifest, affected flows and shared contracts. Identify the comparison base and exact worktree, staged or committed candidate. Re-read after expanding scope.
2. **Compute impact.** Use the union of base/candidate mappings, including removed records, new files and new symbols in existing files. Follow explicit dependent-feature links. Review scope reductions and policy/checker changes separately. Uncertain dependencies use conservative file-level coverage.
3. **Synchronize.** Update flow sources, mappings and evidence. Run `snapshot` to refresh explicitly registered inputs; it does not register unknown code or approve behavior. Native Python and optional multi-language Tree-sitter adapters normalize syntax while retaining semantic tokens/directives. Module context changes affect all features mapped to that file; symbol-body changes affect mapped features and declared dependents. Keep raw MD5 for file-byte integrity. Unsupported syntax or uncertain dynamic dependencies use explicit file-level coverage rather than an invented symbol match.
4. **Review automatically.** When affected behavior changes, obtain each feature's fingerprint, then dispatch a fresh reviewer with no conversation history using [the reviewer prompt](references/reviewer-prompt.md). Supply raw base/candidate sources, diff, flows, mappings, policy and tests, including relevant dependencies. The reviewer may request more source. Save its structured result as an evidence file and add the matching manifest review entry. This is an independent agent review record, not a cryptographic signature or repository human approval. Use at most two fix/review rounds per review request, then report unresolved findings. When subagents are unavailable, independent review is incomplete; continue safe work and report the missing gate rather than inventing approval.
5. **Check.** Run the bundled checker on the actual candidate, relevant behavioral tests and applicable project integration/deployment checks. For staged hooks use `--staged`; testing worktree bytes does not validate the index. Reject stale reviews when reviewed sources, flows, mappings, dependencies, base or policy change. Keep result records outside their own fingerprints.
6. **Report states.** Distinguish skill installed, reading rule adopted, documentation coverage, structural checker passed, agent semantic review, human/merge requirements and visual inspection. Missing/skipped candidate checks remain unverified.

## Bundled tools

Python 3.10+ and Git run the checker; its implementation language does not restrict the project's languages. File-level and native-Python checks need no third-party packages. Install `scripts/requirements-ast.txt` in a dedicated environment for optional Tree-sitter symbol checks across supported languages. Read [the enforcement contract](references/enforcement-contract.md) for the tested grammar/symbol boundaries and first adoption.

```bash
python3 <skill-dir>/scripts/flow_checker.py snapshot --root .
python3 <skill-dir>/scripts/flow_checker.py fingerprint --root . --base HEAD --feature feature.id
python3 <skill-dir>/scripts/flow_checker.py check --root . --base HEAD
```

The checker supports an explicit, bounded Mermaid flowchart/PlantUML named-state subset, not either language's full grammar. Unsupported constructs fail visibly. Its headless checks cover node/symbol mappings, inventory, fingerprints, diff obligations and configurable complexity limits. They do not establish visual readability or semantic correctness. Render and inspect when available; otherwise record `visual verification: pending` without blocking headless structural verification. Regenerate committed derived images through project tooling or report them stale.

Copy the complete `scripts/` directory to a project-owned path when installing CI/hooks. Include the checker, parser adapter and dependency pins in `policy_inputs`. Adapt [the pre-commit template](assets/pre-commit) to the project's hook path; compose with existing hooks rather than overwriting them. A local hook is bypassable. Required CI results and protected review settings provide the merge gate, including a safe manual path for untrusted forks. Verify those settings rather than assuming them.

## Completion boundaries

A semantic review may leave a flow unchanged with a concrete, evidenced explanation. Normalized comment/layout changes need refreshed byte fingerprints but do not invalidate unchanged semantic reviews. A whole-file fallback or module-level context change conservatively affects every mapped feature. Git function-context hunks assist impact investigation but are not a semantic-hash backend.

All first-party logical inputs, public entrypoints and shared dependencies must be accounted for before claiming whole-project coverage. External APIs, remote configuration and floating dependencies require separate runtime evidence. Preserve repository validation requirements and existing authorization for publishing, deployment or remote settings.

A complete install includes this file, the checker, hook and referenced resources. Missing resources mean an incomplete installation, not permission to skip the gate. A project with no checker remains manual-only; unconfirmed remote merge settings mean merge enforcement is unconfirmed.
