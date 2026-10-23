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

## Reviewer rubric

| Case | Required observable decisions |
| --- | --- |
| WIP | Read the baseline plus pending diff before edits; retain pending impact and defer flow generation/semantic review. Do not claim synchronized delivery. |
| Ready and later change | Prepare the actual delivery candidate without a separate Maintain request. Filter impact, synchronize necessary documents and review affected fingerprints. Revalidate subsequent candidates/base changes; validate generated output commits too. Never self-compare committed `HEAD`. |
| Comments | Refresh byte hashes at delivery, retain correct flows and existing semantic evidence, and run candidate checks. Recognize docstrings/directives/file-mode limits without starting new review for unchanged bound semantics. |
| Hook | Do not newly impose the strict hook under PR-delivery policy. Preserve existing requirements and explicitly resolve conflicts. A bundled validator has no WIP detection or AI generation. |
| Installation | Explain that installation copies resources. Agent preparation can perform synchronization; unattended events need configured and exercised workflow/runner. Report that automation incomplete. |

A pass records the candidate identity, concrete decisions for all cases, source locations and limitations. Keep evaluation results outside the installed skill package. These cases do not test a live AI runner; add event integration tests when one exists.
