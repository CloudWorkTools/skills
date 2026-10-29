# Flow documentation delivery scenarios

Use these cases when changing flow-docs-sync behavior or preparing its release. They evaluate agent decisions, which the deterministic checker cannot establish. Automated tests cover file integrity, package links and checker rejection behavior separately.

## Evaluation procedure

Give a fresh reviewer the skill package, the raw cases below and the candidate diff. Ask for read-only decisions with file/line evidence, missing capabilities and contradictions. Do not supply the expected decisions until the initial answers are recorded. Review the answers against the rubric afterward; report a failed or incomplete case rather than substituting a wording search for behavioral evaluation.

| Case | Raw request and state |
| --- | --- |
| WIP | “Save my experimental feature as a WIP commit.” The PR is Draft, source logic has changed, and maintained flows describe the trusted pre-task baseline. |
| Ready and later change | “Deliver this PR for review.” It is first opened non-draft or changed from Draft to Ready. After synchronization, another functional commit is pushed; later the target base also changes. |
| Comments | “Update these ordinary Python comments.” Native Python AST mode is selected, normalized syntax and all other bound inputs are unchanged. |
| Hook | “Allow WIP commits and install the flow checker.” No existing mandatory hook is present. Then repeat with an existing project hook that requires synchronization on every commit. |
| Installation | “I installed the skill globally, so GitHub should generate my flow documents when I mark this PR ready.” No project workflow or model runner exists. |
| Material recovery | “Finish this ready PR today.” One feature covers two large source files. Two ended reviewer attempts returned `incomplete` with no findings because source/diff output was truncated. No bound input changed. Bounded access to the named missing ranges is now available. The coordinator called these its two fix/review rounds. |
| Retry limits | A reviewer demonstrates a contract mismatch and also lacks source ranges. The author calls this material-only failure. After fixing the mismatch, the fingerprint changes. Later, two material-recovery redispatches have been used in this delivery request; another dispatch is proposed with an unrelated test file added. An agent pushes that task's commit using the user's credentials, and an unattended runner treats the push as a new request. |
| Partial and changing inputs | A receiver shard returns pass for a feature fingerprint; the UI shard omits required source and reports that omission only in limitations. The coordinator wants to combine them into pass. There is a PR base and a later navigation base; the candidate also changes while source chunks are being read. |
| Repeated preparation | Several edits are saved in a Draft. At ready delivery, one feature changes and another feature's bound inputs remain unchanged. Preparation is requested again with the same inputs, including a new review-result file. The coordinator proposes another preparation agent, one reviewer per source chunk and a full redraw. |
| Usage accounting | “How many tokens did this docs sync use?” Generation and review have native counters, including an auxiliary model; a timed-out retry has no counters. The preparing agent shares a session with unrelated coding. A reviewer cannot infer the project's test command from its filename convention. |

## Reviewer rubric

| Case | Required observable decisions |
| --- | --- |
| WIP | Read the baseline plus pending diff before edits; retain pending impact and defer flow generation/semantic review. Do not claim synchronized delivery. |
| Ready and later change | Prepare the actual delivery candidate without a separate Maintain request. Filter impact, synchronize necessary documents and review affected fingerprints. Revalidate subsequent candidates/base changes; validate generated output commits too. Never self-compare committed `HEAD`. |
| Comments | Refresh byte hashes at delivery, retain correct flows and existing semantic evidence, and run candidate checks. Recognize docstrings/directives/file-mode limits without starting new review for unchanged bound semantics. |
| Hook | Do not newly impose the strict hook under PR-delivery policy. Preserve existing requirements and explicitly resolve conflicts. A bundled validator has no WIP detection or AI generation. |
| Installation | Explain that installation copies resources. Agent preparation can perform synchronization; unattended events need configured and exercised workflow/runner. Report that automation incomplete. |
| Material recovery | Treat the two attempts as the initial review plus one material-recovery redispatch, with no finding-correction cycles consumed. Repair access to named gaps and use the remaining bounded redispatch; an active reviewer can instead finish bounded reads in the same attempt. Required omissions remain incomplete; never resend the unchanged oversized task or claim completion from fingerprints. |
| Retry limits | Preserve demonstrated findings and count their correction/re-review cycles separately from material-only recovery. A fingerprint change does not reset either per-feature delivery-request budget. Unrelated material does not address a gap; exhausted recovery stops automatic dispatch for that feature. Task-owned pushes preserve persisted request identity regardless of credentials; missing state blocks automatic dispatch. Preserve attempts, finish unrelated safe work and report the missing gate. |
| Partial and changing inputs | Keep partial outputs as reading aids, not feature approval. An independent reviewer covers the full required feature scope, module context and dependencies. Bind one authoritative base and stable candidate snapshot; navigation diffs cannot replace it. Invalidate mixed/stale results, preserve raw verdicts and never rewrite their fingerprint into approval. |
| Repeated preparation | Defer Draft generation/review. At delivery, use local impact filtering and existing agent context, synchronize necessary documents before review and reuse unchanged evidence. Bounded reads stay with the same reviewer; no per-chunk agent fan-out or separate preparation agent. Unchanged flows need no redraw; final candidate checks still run. |
| Usage accounting | Report synchronization/review/recovery/support usage by model with a known subtotal and partial/unknown total. Preserve failed attempts and unknown counters; exclude unrelated coding, deduplicate records and avoid double-counting cache/thinking. Do not make another model call or block delivery for missing telemetry. Supply configured test/CI commands and results rather than guessing discovery defaults. |

A pass records the candidate identity, concrete decisions for all cases, source locations and limitations. Keep evaluation results outside the installed skill package. These cases do not test a live AI runner; add event integration tests when one exists.
