---
name: flow-docs-sync
description: Use when creating project overview and source-linked flow diagrams for humans and AI agents, maintaining their correspondence to code, or auditing documentation drift.
license: MIT
---

# Flow documentation synchronization

Help humans understand what the project does and help AI agents locate entrypoints,
control decisions and implementation. Maintain a project overview plus focused,
source-linked feature flows. Detect version drift with deterministic inventory,
mapping and fingerprint checks; interpret affected behavior from source.
Independent review is a separate, policy-driven assurance step.

## Select the operation

| Operation | Read when needed | Result |
| --- | --- | --- |
| Adopt | [Project setup](references/enforcement-contract.md#project-file-layout) and [bounded inventory](references/enforcement-contract.md#adoption-inventory-and-staged-rollout) | Core end-to-end coverage, explicit gaps and actual project controls |
| Maintain | The workflow below; [checker contract](references/enforcement-contract.md#cli-and-staged-hook) for command details | A synchronized delivery candidate |
| Audit | Existing project rules, flows and evidence | Concrete drift/coverage findings; no edits unless requested |

Existing project gates and explicit user authorization take precedence. Updating
this skill does not migrate a project's checker, hook, scope, budgets or failed
review records. Plan such a migration separately; never label a bypass as reuse.

## Maintain

1. **Read the affected boundary.** Read project instructions, the flow index,
   relevant manifest feature/dependency records, flows and owning contracts
   before edits. Report affected feature IDs. Machine hashes and historical
   review indexes need validation, not repeated human-style reading. Respect
   stricter existing read rules until explicitly migrated. Verify an unknown
   baseline from source; name genuine missing access.
2. **Develop in the existing context.** During Draft/WIP work retain pending
   impact; generate maintained flows when intended content settles. Preserve
   requirements when implementation disagrees: record the defect rather than
   rewriting intent to claim completion. Keep old-system adoption separate from
   unrelated feature delivery.
3. **Pin and filter at delivery.** Select the trusted base and exact candidate.
   Run `python3 tools/flow-docs/flow_checker.py explain --base <sha> --staged`
   for an intended index (omit `--staged` for worktree delivery). Resolve source,
   mapping and syntax errors locally before requesting review. Use one candidate
   per repo; unchanged evidence stays valid only while its bound inputs match.
4. **Synchronize only affected documents.** Update actual behavior, mappings and
   necessary input registrations. Use feature-local `policy_inputs` for local
   tests/configuration; global inputs are reserved for genuinely shared policy.
   Run `snapshot` only to refresh registered source hashes; it neither registers
   unknown code nor approves it. Keep current passing pointers in the manifest;
   preserve historical raw results in existing task evidence, Git or artifacts.
5. **Select review by risk and policy.** For new adoption, explicitly set each
   feature's `requires_review`. Require independent review for initial adoption,
   important cross-module contracts, security/data-loss risk and project-mandated
   cases. Ordinary maintenance may use `false` after source-based verification.
   Record the decision and rationale in existing task evidence. Existing strict
   policy needs an explicit migration, including the checker and hooks.
   **When review is required, review a bounded packet.** Use `packet --base <sha> --feature <id>` with the
   same candidate mode. Supply changed relevant diff, direct module context,
   named dependency contracts and actual test command/input/result evidence.
   Read [review scope and budget](references/reviewer-prompt.md) before dispatch.
   Related features may share an independent reviewer with separate verdicts;
   partial source shards cannot be combined into approval. Keep complete raw
   sources accessible for justified expansion, not mandatory blanket rereads.
6. **Validate and report.** When independent review is required, import only an unchanged, complete passing review
   that matches the current feature fingerprint. Run `check` against the actual
   candidate and trusted base, plus existing project checks. Reuse tests only
   for unchanged recorded code/config/dependency/environment inputs. Report
   source verification, mechanical checks, required/optional independent review,
   runtime, visual and human approvals separately. A mechanical pass does not
   prove that documentation describes behavior correctly. Record known
   synchronization/review/recovery usage; unknown telemetry is not a new gate.

No separate preparation agent is needed for routine maintenance. Use the
existing PR/task evidence instead of creating another baseline, adoption report
or runtime document for every edit. Installation alone provides no AI runner or
remote merge protection; verify configured controls before claiming them.

## Navigation and synchronization outcome

The overview explains project purpose, primary entrypoints, core data/control flow,
module responsibilities and external systems. Link each overview stage to its
feature flow. Feature flows show meaningful branch conditions, errors,
cancellation/recovery and side effects. Map each node to a real source path and
qualified symbol where supported; line numbers are optional navigation hints.
A reader must be able to follow a use case from entry to outcome and an AI agent
must be able to locate the code controlling each important decision.

Track source correspondence separately from assurance. Report unchanged inputs,
changed inputs pending interpretation, or source-verified documentation, together
with the compared base/candidate and affected fingerprints. Report independent
review as required-passed, required-incomplete, or optional-not-run. Keep these
records in existing task/CI evidence, outside fingerprint inputs. `snapshot`
updates integrity hashes only; it cannot establish source verification.

At task completion, configured pre-commit checks and PR updates, run local impact
checks first and record affected features as pending when behavior changes.
During WIP, stale hashes indicate pending work; refresh once intended inputs
settle. Generate only necessary diagrams before delivery. No affected inputs
means no new AI call. Project hooks/events must actually be configured and tested;
installing the skill alone starts no background watcher or model runner.

## Project files and responsibilities

During project setup after installation, add or update a short reading guide in
root `AGENTS.md`, using the actual overview, flow and mapping paths. Preserve
existing instructions and avoid duplicate sections. Setup is incomplete without
this guide; resource installation alone does not write it.

Keep one authoritative contract and concise source-navigation index. For new
adoption use the [project layout and root rule](references/enforcement-contract.md#project-file-layout).
Detailed schema, AST adapters, entrypoint compatibility and runtime templates
are references for those operations, not a default reading list.

## Change filtering and synchronization gate

AST-normalized cosmetic source edits refresh raw integrity without a new semantic
review. File-mode inputs remain byte-sensitive; behavior, flow, mapping, base or
policy changes can invalidate affected evidence. See the [impact rules](references/enforcement-contract.md#change-filtering-and-review-cost).
A passing checker validates declarations and structure, not semantic correctness,
reviewer authenticity, physical behavior or permission to publish.
