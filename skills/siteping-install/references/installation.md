# Execute the project installation

Use these steps to change the target project. Select versions against the current registry and the project's runtime; commands below use npm notation, adapt to the existing package manager. Keep the lockfile and use exact resolved versions rather than copying historical pins.

## 1. Choose the stack and install dependencies

| Component | Package | Install when |
| --- | --- | --- |
| Browser annotations | `@siteping/widget` | Core installation |
| API with Prisma store | `@siteping/adapter-prisma` | Project uses Prisma, or a new Prisma service is the smallest fit |
| API over another store | `@siteping/server` | Project already has a supported store integration |
| Drizzle store | `@siteping/adapter-drizzle` | Project uses a supported Drizzle database |
| React administration inbox | `@siteping/dashboard` | Requested |
| External screenshots | `@siteping/screenshot-storage` | Selected storage policy needs it |
| GitHub/GitLab bridge | `@siteping/integration-issues` | Requested, after reviewing hook behavior |

Check each selected package's `npm view <package> version engines peerDependencies dependencies` output. Install only the needed packages with exact compatible versions, e.g. `npm install --save-exact @siteping/widget@<widget-version> @siteping/adapter-prisma@<adapter-version>`. Angle-bracket versions are values to resolve, not literal runnable arguments. See the [component overview](https://siteping.dev/docs).

For Django, Rails, static HTML or another non-Node host, keep the existing application: bundle the framework-independent widget and mount a small Node service behind the host's same-origin proxy if no compatible server runtime exists. Reuse the host's authorization boundary: strip browser-supplied identity headers at ingress and forward a server-verified principal through a short-lived signed assertion or an equivalent authenticated private channel; validate it in Node before granting access. Test that forged identity headers fail and that the service cannot bypass the gateway through a public port or alternate route. Do not rewrite the host or use browser-only storage as shared team persistence. For an explicitly requested browser-only prototype, use the documented localStorage adapter and disclose its device-local data limit. See [framework recipes](https://siteping.dev/docs/frameworks).

## 2. Wire persistent API and schema

For existing Prisma projects, inspect the selected CLI's help, then use a pinned `@siteping/cli` version. Its `sync --schema <actual-schema>` modifies schema files; review the diff, generate a migration using the project's normal workflow and regenerate its Prisma client. Avoid `db push` against existing/production data. `init` is interactive and scaffolds only Next.js App Router; in noninteractive sessions use schema sync and write the route yourself. The CLI installs no dependencies. See [CLI behavior and caveats](https://siteping.dev/docs/cli).

Mount `createSitepingHandler` from the selected adapter at one endpoint, forwarding GET, POST, PATCH, DELETE and OPTIONS; return 405 for unsupported methods. Use the official mounting recipe for the host server. Supply the real store/client, server-only secrets and the selected access policy. Keep screenshot-capable body limits aligned through the proxy and app. A Next.js import-time handler may require secrets during build; construct it lazily if secrets arrive only at runtime. See [server mounting and access options](https://siteping.dev/docs/server) and [Prisma integration](https://siteping.dev/docs/adapters/prisma).

For a new Prisma database, include complete feedback, annotation and comment models from the selected adapter's schema rather than hand-trimming fields. For an existing Drizzle project, follow its adapter's schema/migrations instead. Start the API on the configured development port and confirm a real API response, not a fallback HTML page.

## 3. Mount the widget in the real page

Bundle `initSiteping` from `@siteping/widget` in the browser entrypoint, passing the actual API `endpoint` and environment-specific `projectName`. In React use the documented `useSiteping` hook from `@siteping/widget/react`. Mount once; ensure client-side navigation does not create duplicate widgets. Use the selected version's cleanup API when the component lifecycle requires teardown.

The widget's normal visibility differs between development and production builds. Set `forceShow` deliberately for an authorized review environment; do not enable it for all public production visitors accidentally. Server API keys must stay off the client. With the default keyed API policy, submission can work while listing is forbidden: choose authenticated reads or explicitly public reads to match the requested pins/thread visibility. See the [quickstart](https://siteping.dev/docs/quickstart).

## 4. Prove this installation works

Run the project build, start its real development server, and complete the core browser journey in SKILL.md. Save feedback, restart the backend, and confirm the same feedback, annotation and any screenshot reopen. Confirm permitted reads and denied owner actions under the chosen policy. CLI `status` and `doctor` are supporting diagnostics: their exit codes alone do not prove schema equality or a real SitePing endpoint.

Leave concrete project changes: dependency lock, mounted API, schema/migration, widget entrypoint, private configuration example without secrets, and start/disable instructions. Record which optional integrations were installed. If credentials or target authorization are missing, finish all independent local work and name the specific remaining action; do not report an installed working integration without the browser/persistence evidence.
