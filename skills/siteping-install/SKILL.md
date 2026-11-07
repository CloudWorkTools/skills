---
name: siteping-install
description: Install and configure SitePing in a project when asked to add SitePing page annotations or a feedback widget, including its API, persistent storage and working browser flow.
---

# Install SitePing into a website

Execute the installation, configuration, build and browser verification in the target project; deliver changed project files and a working feedback flow, not only recommendations. Produce a working integration in the user's chosen site and deployment environment. Installing this skill copies guidance; it does not install or enable SitePing. Reuse the host's authentication, deployment path and database tooling where compatible. Keep project names, hosts, accounts and credentials as deployment inputs.

Follow [installation steps](references/installation.md) to implement the integration appropriate to the project stack. Read [integration lessons](references/integration-lessons.md) before choosing packages or designing delivery. The lessons describe a pinned historical integration; verify behavior against the actual version being installed.

## Establish the integration contract

Inspect the site's build, login, proxy, persistence and deployment configuration. Record the target revision and the intended users, accessible projects, environment/origin, data retention and screenshot visibility. Determine whether GitHub delivery is requested, its destination and posting identity, and whether submission publishes immediately or requires review. Ask only for missing decisions that affect implementation; existing authorization remains valid.

Choose the smallest supported integration: widget plus server and persistent adapter; add the React dashboard only when an administration inbox is needed. A dashboard component is not a standalone service. Retain annotation geometry, anchors, comments and screenshot associations in durable storage; a generated GitHub issue is not a replacement for that data.

## Resolve and build reproducibly

Verify registry availability, package engines and compatibility for the entire dependency graph in a clean environment. Pin the selected versions and lockfile. A workspace manifest does not prove a dependency is published. If source building is needed, pin and verify upstream source, retain its license, and document the bounded patch and why it is needed. Prefer supported released functionality when sufficient.

Check the generated widget and dashboard artifacts, including any patched behavior; a successful patch command or bundle exit code alone does not prove the patch landed. Keep a clean-build check for source/patch integrity when vendoring.

## Enforce access and storage on the server

Implement the selected anonymous or authenticated access policy on the server. For private reviews, reuse host sessions and server-verified identities and project authorization; protect owner actions in every mode. Do not add a login system to a project that requests public submissions. Treat widget identity fields, project names, Mine filters and readOnly controls as UI inputs. Test anonymous access, wrong project, forged owner role, expired login and CSRF as applicable to the host's authentication scheme. Keep administrative keys and GitHub tokens server-side.

Prefer same-origin routes for cookie sessions. If a separate origin is necessary, verify the selected version's credential support and explicit origin policy before promising login works. Protect feedback APIs and private screenshots, including direct URLs. Public image publication requires an explicit visibility decision and review of the image itself, not only its issue text.

Use durable database/media storage and least-privilege runtime access. Separate migration authority from runtime credentials where supported. For production or an installation with existing data, demonstrate backup and restore into an isolated empty target, preserving both records and image associations; for a fresh local installation, document the persistence and backup path. Define rollback before schema changes; rolling back an image does not roll back a database.

## Implement the chosen submission and delivery behavior

Only when GitHub delivery is requested, implement this section. Otherwise skip it. For GitHub delivery, inspect all enabled hooks, including deletion. Select lifecycle behavior deliberately; disabling status sync may leave creation/deletion hooks active. Preserve the original feedback independently of GitHub state and customer acceptance.

Only when publication review is required, preview the exact normalized outgoing text, destination and image visibility before approval. Bind approval to the authenticated actor, payload and captured revision. Sending, recovery and retry must use the approved bytes; destination or policy changes require reassessing stored approvals. Offer cancellation that sends nothing.

When GitHub delivery is enabled, make retries idempotent across reloads, concurrent workers and deletion. Distinguish saved feedback, attempted delivery, confirmed remote issue and unknown remote outcome. A timeout after issue creation requires reconciliation before another POST; never treat it as proof that creation failed. If recovery is promised, preserve actor/project-bound recovery server-side when browser storage is denied; otherwise show failures accurately and keep the form usable without claiming a successful submission. Add a durable staging/outbox only if the selected workflow needs it; inspect existing facilities first.

## Verify and deploy

Use the site's actual build and test commands. Cover the chosen integration's trust boundaries, persistence and failure paths, including interrupted/repeated submissions and unavailable GitHub when enabled. Keep targeted regression tests for custom logic.

Run the browser journey under the selected access policy: open annotation mode, mark an element/region, edit text, review if configured, cancel, submit, reload, reopen the pin and reply. Exercise owner actions, failed delivery and recovery when present. Test supported desktop/mobile layouts, page navigation and changed/missing anchors. Include denied localStorage and delayed identity initialization; type into and switch between all visible form fields after opening/reopening the composer. See the lessons for the focus-race warning.

Inspect actual screenshots and interaction recordings for capture accuracy, focus, overlays and clipping. DOM assertions and passing headless tests do not establish visual correctness. Follow the target project's evaluator requirements; mark images not actually inspected as `notviewed` and report untested devices and unresolved behaviors explicitly.

Finish local installation and verification within existing authorization. Use a sandbox repository for GitHub test writes. Before real external writes, production migrations or deployment, check that the specific action and target are already authorized; request only missing authorization with a concrete diff and verification results. Deploy only to the authorized target with TLS, secrets, migrations and persistence configured. Verify the public origin's access policy, including login when configured, permitted operations and forbidden anonymous operations, then repeat checks after an ordinary deployment update. An opt-in service must remain enabled across updates without exposing it in unrelated environments. Supply a disable/rollback procedure that preserves data.

Report the tested revision, package/source versions, target, commands/results, actual browser/image evidence, restore result, remaining limitations and whether real external writes occurred. Keep deployment readiness and customer acceptance as separately evidenced outcomes.
