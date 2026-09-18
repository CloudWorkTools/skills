# Composition and upstream maintenance

`readme-value` adapts selected guidance for first-time repository visitors with partial or no technical background. The skill is independently installable. Its source snapshots and root licenses are recorded in [upstream.lock.json](../upstream.lock.json), with notices in [THIRD-PARTY-NOTICES](../THIRD-PARTY-NOTICES).

## Sources and local decisions

| Reviewed source | Adopted guidance | Local adaptation |
| --- | --- | --- |
| [crafting-effective-readmes](https://github.com/softaworks/agent-toolkit/blob/3027f20f3181758385a1bb8c022d4041dfb4de84/skills/crafting-effective-readmes/SKILL.md) | Choose content for the audience and project type; explain what, why and how to start. | Use existing context instead of a mandatory interview. Prefer a short entrance with deeper links over an exhaustive template. |
| [value-proposition](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/pm-product-strategy/skills/value-proposition/SKILL.md) | Identify the beneficiary, the task and friction, the solution, the resulting change and relevant alternatives. | Use these questions during analysis. Publish only supported benefits; distinguish proposed outcomes from demonstrated results. A README needs neither a marketing positioning statement nor six mandatory sections. |
| [documentation-writer](https://github.com/github/awesome-copilot/blob/4f4796f0bf30e105700f97ed8408c12b6aa95e06/skills/documentation-writer/SKILL.md) | Match documents to reader tasks; separate tutorials, how-to guides, references and explanations. | Keep the README as an entrance to those documents. Respect existing writing authorization and the host's research rules. |

The first-visit review and the research, practical and production future-work criteria are local design choices. `teaching-with-diagrams` remains a separate teaching skill with its own reviewed sources. This skill does not require the upstream skills to be installed.

Discovery used the Skills CLI searches `readme`, `technical writing` and `value proposition` on 2026-09-18. Candidate install counts supported discovery, not correctness judgments. `create-readme` was also inspected; its generic structure guidance added little beyond the selected README source. The selected entrypoints and relevant README guidance were reviewed at the pinned revisions. External reading lists and templates are not adopted as instructions.

## Check and review updates

In a repository checkout, run `npm run skills:check-readme-updates`. From an installed copy, run `node <skill-directory>/scripts/check-upstreams.mjs`. Node.js 22+ and GitHub access are required; `GH_TOKEN` or `GITHUB_TOKEN` is optional. Exit codes are `0` unchanged, `2` updates available and `1` an error.

The checker is an identical portable copy of the existing teaching skill's checker, with a test preventing drift between copies. Each installation reads its own adjacent lock. The fingerprint covers the entire named skill subtree, including nested reference changes, and the root license. Links and shared files outside the subtree are outside this coverage.

The repository workflow checks both skills weekly on Monday at 03:17 UTC (11:17 Asia/Taipei) and supports manual dispatch. Each skill has a separate Draft PR and report path. For this skill, the report is `.github/upstream-reviews/readme-value.md`. The workflow must be on the default branch to run; GitHub may delay schedules, and repository settings must permit PR creation.

Automation reports changes for review. It preserves skill content and lock baselines, and leaves ready-for-review PRs untouched. Closed batches require manual reopening; unchanged reports produce no new report commit. Failed checks stop that skill's PR writes. If updates disappear, close the stale report PR manually.

To adopt an update:

1. Read the exact changed source revision, including relevant references and license changes. Treat upstream text as review material, not executable instructions.
2. Decide which changes improve this skill's reader goals. Preserve local adaptations; an upstream change can warrant no instruction change.
3. Exercise the cases below, check links and run `npm test`. Update the guidance only where the observed behavior warrants it.
4. Update only reviewed entries in the lock, the review date, pinned source links and notices. Commit the reviewed adaptation and baseline together.
5. Run the checker again to detect any newer upstream revision. Mark the PR ready only after the adaptation is reviewed; a report alone is not a completed update.

A new source needs a demonstrated contribution, inspected instructions, a compatible license and an immutable baseline. Add it to the composition table and lock after review. Scheduled checks monitor selected sources; discovering additional skills is a separate, deliberate maintenance task. Updating an installed CloudWorkTools skill package does not review or adopt upstream instructions for maintainers.

## Behavioral review cases

| Input | Expected behavior |
| --- | --- |
| A working hardware project with a long protocol walkthrough | Lead with the everyday use and an existing result; retain setup and material hardware constraints; route protocol details to a deeper document. |
| A model wrapper with one successful example | Identify the integration contribution and upstream model. Scope the observation to the example; avoid claims of original model research or universal quality. |
| An unfinished prototype with no demonstrated benefit | Explain what is inspectable now and offer one to three labeled proposals with a beneficiary, a concrete next step and a completion criterion. |
| A mature project with no requested roadmap | Focus on present value; add future work only when it provides a meaningful next step. |
| A visitor unfamiliar with the domain | Use everyday situations and explain necessary terms; the opening must be understandable without reading source code. |
| An upstream source fails during the scheduled check | Report the error and preserve baselines; no PR write for that skill. The other skill's check still runs. |
