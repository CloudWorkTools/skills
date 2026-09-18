---
name: readme-value
description: Create or refocus repository READMEs so first-time visitors, including readers without a technical background, understand the problem, value, current results and next step. Use for unclear or overlong project introductions and evidence-based future-work proposals; also supports checking this skill's upstream sources.
license: MIT
---

# README value

Help a first-time visitor decide whether a project matters to them and where to go next. Show professional judgment through concrete contributions, evidence and honest scope. This skill works independently of `teaching-with-diagrams`.

## Establish what the project offers

Read the existing README and relevant implementation, examples, tests and project documents. Follow the environment's source-discovery rules. Verify claims at their source; distinguish a documented intention from implemented behavior and observed results.

Use the user's chosen audience and language. By default, assume a visitor with partial or no domain knowledge. Infer what can be learned from the repository; ask only for missing decisions that would materially change the document.

Before drafting, identify the beneficiary, their concrete problem, the project's contribution and the evidence supporting it. Distinguish local work from upstream components. A useful integration or reproducible experiment can be valuable without inventing a new algorithm.

## Write a short entrance

Open with one or two plain-language sentences connecting a recognizable situation to what this project lets someone do or understand. Introduce necessary technical terms beside their everyday meaning. Put internal class names, protocol details and equations in deeper documentation.

Give the visitor one concrete example or existing result early: a screenshot, sample output, short scenario or measured observation. Label inputs, mockups and proposed results accurately. If no demonstrable result exists, state the project's current stage and what can be inspected today.

Arrange the remaining material around the visitor's decisions:

- What is useful here, and who benefits? Select the few capabilities that explain the value.
- What exists today? Show supporting evidence and limitations that affect the decision to try or trust it.
- How can I start? Offer the shortest supported trial or a direct setup link, with prerequisites and an expected result. For unfinished projects, point to the available prototype or design.
- Where can I learn more? Link to existing operation, architecture, research or teaching documents.

Adapt headings and length to the project. Prefer a short main page a visitor can scan in about two minutes; this is an editorial target, not a measured usability claim or a fixed word quota. Every section must help a visitor understand, assess or try the project.

Preserve useful details when shortening: move them into an appropriate existing document, or create a focused document only when needed, then repair links. Keep material usage restrictions visible and retain license and attribution links. Keep the editing agent's test logs and handoff history out of the README.

Use a diagram only when it clarifies an important relationship more quickly than prose. Choose labels the intended reader understands, keep each diagram focused on one question, and retain a text explanation. Check destination rendering support and validate diagrams when tooling is available. Tutorials and exercises belong behind a learning link unless the requested deliverable is itself a tutorial.

## Separate value from ambition

Support a value claim with a concrete result or mechanism and its scope. Connect technical choices to a consequence for the user. Avoid unsupported claims about novelty, speed, reliability or production readiness. A test passing establishes only what that test exercises.

Consider whichever value directions fit the evidence: research can answer a specific question or enable reproduction; practical work can solve a concrete task; production work can establish operation under stated conditions. These are lenses for choosing content, not mandatory README sections.

When current value is unproven, include future work with one to three relevant proposals. When useful value already exists, include future work only if it adds a meaningful next step or the user requests it. Each proposal names:

- Who would benefit and the unresolved need or question.
- The next experiment or deliverable, including a comparison baseline when relevant.
- An observable completion criterion and material prerequisites or constraints.

Label agent-generated directions as proposals for exploration, separately from an accepted roadmap. Use reader-facing status labels such as "Proposed exploration"; keep the drafting history in the handoff. Distinguish research, practical and production goals when that helps the reader; select only supported directions. Never turn a proposal into a claim of present capability, a maintainer commitment or permission to implement features. If the evidence supports no credible direction, state the gap and propose a bounded investigation.

## Review as a newcomer

Read the opening without relying on source-code knowledge: can a visitor explain what this is, why someone would use it and what is available today? Check that the contribution is specific enough to distinguish this repository from a generic project description.

Trace material claims, follow local links, inspect image labels and check quick-start commands against the project. Run proportionate checks when feasible; report any unexecuted commands or unverified rendering in the handoff. Preserve consequential limitations in the document without repeating the full evidence audit beside every benefit.

Deliver the requested README and any necessary linked documents. A review-only request returns findings. A writing request completes the authorized edits without adding an outline-approval step.

## Maintain upstream sources

This skill adapts selected practices from three sources recorded in [upstream.lock.json](upstream.lock.json). Read [composition and maintenance](references/composition.md) when reviewing sources, checking updates or changing the skill itself. Attribution is in [THIRD-PARTY-NOTICES](THIRD-PARTY-NOTICES).

For an explicit update check, run:

```bash
node <skill-directory>/scripts/check-upstreams.mjs
```

The checker requires Node.js 22+ and GitHub access. It returns `0` for unchanged sources, `2` for available updates and `1` for errors. It leaves files unchanged. Ordinary README work uses the installed guidance; upstream adoption follows the review procedure rather than silently fetching new instructions.
