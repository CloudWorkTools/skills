# Portable implementation contract

Read this when adding, adapting, or fixing a project's preview script. The service names, paths, routes, and initialization are project-specific. Reuse a suitable existing implementation; this reference specifies behavior, not a mandatory framework.

## Command surface

| Command | Source access | Result |
| --- | --- | --- |
| `up <PR-number>` | Fetch and verify PR head | Build the selected revision and start its preview |
| `up <path>` | Read canonical local source, including dirty files | Start a local preview without editing those files |
| `logs <selector>` | Saved state only | Follow the existing preview's logs |
| `down <selector>` | Saved state only | Delete only that preview's disposable resources |
| `list` | State and Docker labels | Show source/version, URL, and observed status |

Keep a stable slot across updates; record the changing SHA in state. Include repository identity in PR slots when multiple repositories share a daemon. Use a full canonical-path hash for local slots: `/alice/app` and `/bob/app` must differ. A short basename alone is not an identity. Let Docker allocate a loopback port, or check candidates and handle bind failure; a hash into a small port range cannot guarantee uniqueness. Save the assigned port.

## Source integrity

Treat PR numbers as bounded decimal input before shell arithmetic. Fetch an explicit PR ref; do not guess the branch name or silently substitute the merge commit or default branch.

In Bash, split dependent assignments:

```bash
local pr="$1" ref
ref="refs/pr-preview/pr-$pr"
```

Inside command substitution, use explicit failure propagation for fetch, status, checkout, worktree creation, and SHA resolution. `set -e` alone is insufficient. A checkout failure must never build the previous revision. Compare both repositories' `git rev-parse --path-format=absolute --git-common-dir`, since the controller can itself live in a linked worktree. Compare fetched SHA with worktree HEAD before building.

Preserve dirty local sources. Refuse changes in managed PR worktrees instead of resetting or deleting them. Record dirty status without calling a dirty image an exact committed revision. For mutable local sources, document the build snapshot and avoid claiming reproducibility from SHA alone.

## Production path and trust boundary

Use the selected source's established Dockerfile, asset build, startup command, and migration path. Inspect the effective deployment configuration, including host overlays; record deliberate preview differences. Use synthetic or sanitized data and isolated queues/delivery endpoints. An empty database only validates empty-state behavior.

Operate from a trusted controller checkout. One conservative policy is to compare the target production Compose file to the trusted version and reject differences, then use the trusted file with the selected build context. Infrastructure PRs need separate review and an isolated host; do not silently ignore their changes while claiming full parity.

An override preserves unspecified base configuration. Review all services, published ports, host mounts, external volumes/networks, privileged settings, and build entitlements. Isolate every required service, including workers. Compose project names do not override explicit `container_name`, external resources, or explicit volume/network names.

For Compose versions supporting `!override`, replace the full web port list rather than appending to the production mapping. Resolve build context to the selected absolute source path, not the saved-state directory. Verify the effective configuration with `docker compose ... config` before starting it. Avoid logging its secrets.

Use generated preview-only credentials, explicit environment handling (for example `--env-file /dev/null` when defaults are unwanted), runtime CPU/memory/PID limits, and loopback binding. Runtime limits do not constrain the image build or guarantee host isolation. Avoid production credentials in both build context and container environment.

## Durable state and lifecycle

Store state in a private controller-owned location outside the source tree. Persist:

- Selector, canonical source, repository identity, full SHA and dirty status.
- Docker context/daemon identity, project name, resource identities, and allocated URL.
- Startup configuration with resolved paths and environment, plus preview-only credentials.
- Last successful image ID and source metadata, distinct from a pending or failed update.

Keep directories/files private (for example modes 700/600). Use an atomic state update. Preserve the prior successful state until an update succeeds, and keep enough information to clean up failed creation. Plain structured data avoids executing a state file as shell code.

Serialize `up` and `down` per slot; acquire the lock before reading mutable state or changing the checkout. Keep lock files outside state directories deleted by `down`. Following logs must not retain the mutation lock. If resources exist without matching state, stop rather than adopting them with a new database password. Verify the saved Docker target before logs or deletion: matching names on another daemon are not proof of ownership.

`down` uses the saved configuration, not the current PR files. An explicitly disposable preview may use project-scoped `down --volumes --remove-orphans` after checking ownership and excluding shared/external resources. Do not use global prune commands. Keep user source changes. Document any retained worktrees, caches, and state-root requirements.

## Verification and regression cases

Use a finite readiness deadline and bounded HTTP requests. Require the actual required services to be healthy, not just running. Ensure the responding port belongs to this preview. Propagate build, migration, and readiness failures; do not print success after the retry loop unconditionally. HTTP 200 alone does not prove authentication, correct assets, or migration success.

Validate these scenarios through the real CLI, using disposable Git repositories and a dedicated Docker test target where necessary:

| Scenario | Required observation |
| --- | --- |
| Numeric PR, then a new head | Selected full SHA updates; no stale image is reported as current |
| Checkout blocked by `index.lock` | Nonzero exit; no build/start of the old revision |
| Controller in a linked worktree | Refresh succeeds for the same repository |
| Two same-basename paths | Distinct containers, ports, networks, and DB data |
| Dirty local source | Change appears in the image; source remains untouched |
| Occupied candidate port | Another port is chosen, or startup fails safely |
| HTTP 503, timeout, unhealthy service | Nonzero exit and useful diagnostics |
| Remote unavailable, source moved/deleted | Saved logs and teardown still work |
| Following logs while stopping | Teardown is not locked out |
| Missing state, existing resources | Refusal without recreating or deleting them |
| Changed PR Compose adds a host/socket mount | Rejection before executing that configuration |
| Failed rebuild after a successful start | Last successful revision remains distinguishable |

For a real smoke test, record baseline workload IDs and image IDs, launch the preview, check login and served-versus-built CSS where applicable, and clean up. Confirm that preview resources are gone and baseline workloads are unchanged. State precisely which behaviors were simulated versus tested with real containers.
