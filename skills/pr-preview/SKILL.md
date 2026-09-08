---
name: pr-preview
description: Use when a user wants an on-demand GitHub pull request or local worktree preview for human review, production-like UI verification, or reliable preview startup, logs, and teardown with Docker Compose.
---

# PR Preview

Create or operate an explicitly requested preview using the project's production build path. A successful preview identifies the exact source and owns its disposable resources. Installing this skill does not start a deployment.

## Establish the deployment contract

Inspect the selected repository's existing preview tooling, Dockerfile, initialization, asset build, and actual deployment Compose/host overrides. Identify the app's real readiness route and required services. Record meaningful differences: configuration, runtime versions, reverse proxy/TLS, data, background jobs, and external integrations. A file named `prod` alone does not establish parity.

Use a dedicated preview Docker daemon or host with preview-only credentials and disposable data. Container names and resource limits do not make a production daemon a sandbox. Inspect the Docker context and existing workload inventory before creating resources. Use an established preview target; if none is available, prepare the implementation and report the missing execution target. Keep migrations and preview workers away from production databases, queues, and delivery credentials.

## Start or implement the preview

Prefer an existing project preview script after checking its source and ownership behavior. If it needs to be created or repaired, follow [the implementation contract](references/implementation.md); adapt the project's existing build rather than introducing another build path.

- Start only on the user's preview request; preserve any existing authorization. Preview work does not imply enabling automatic PR deployments or merging a PR.
- For a PR, fetch `refs/pull/<number>/head`, resolve its full SHA, and verify the detached worktree matches it. Stop on Git failures or dirty managed worktrees. For a local path, preserve uncommitted changes and report SHA plus dirty status.
- Use a trusted controller and reviewed Compose configuration. PR-supplied services, host mounts, privileges, networks, and build entitlements require an isolated execution boundary; an override does not remove them automatically.
- Give each source a stable, distinct identity. Hash the full canonical path for local worktrees. Use loopback ports and preview-owned volumes/networks; refuse existing resources whose ownership cannot be established.
- Save private startup configuration and source metadata independently of the source tree. Serialize mutations of one preview. Track the last successfully started image separately from a failed update.

## Verify before handing over

Require successful build, required service health, and a bounded HTTP check against this preview. A timeout or HTTP 503 is failure, regardless of a script's success message. Check authentication when relevant, and verify served assets match the built version. Capture UI evidence when reviewing appearance. Associate results with source SHA, dirty status, image ID, and URL; disclose untested parity differences.

## Logs and teardown

Use the saved startup configuration and verified resource ownership. Logs and teardown work offline without fetching, checking out, or requiring the original source directory. Following logs must not block teardown. Remove only this preview's disposable containers, networks, and volumes; verify removal and preserve other workloads. Missing state requires ownership recovery, not guessing today's PR configuration.

Report the preview URL and version, verification results, and cleanup command or cleanup result.
