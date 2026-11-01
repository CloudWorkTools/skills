# Flow synchronization resource scope

Implement the approved retrospective: retain verifiable source, contract and
candidate checks while reducing repeated context and unrelated review work.
The existing real-session incomplete reviews provide the behavioral baseline;
new checker regressions must fail before implementation.

## Scope

- Shorten `skills/flow-docs-sync/SKILL.md` into an operation router and shared
  delivery rules; keep schema, adoption and integration detail in references.
- Preserve existing project gates. Installing this revision does not approve
  failed reviews, alter adopted scopes, replace hooks or migrate project copies.
- Bind local test/config inputs to their feature and transitive dependents.
  Preserve fingerprints for manifests that do not declare feature-local inputs.
- Add read-only `explain` and per-feature `packet` commands. Packets distinguish
  changed direct inputs, dependency boundaries and global policy changes;
  full raw sources remain available on demand.
- Keep only current passing pointers in the active manifest; preserve raw
  historical results outside mandatory reading and fingerprint inputs.
- Make review scope finite and explicit. Preserve existing authorization and
  stricter limits; otherwise use one initial batch review and one bounded
  follow-up for demonstrated findings or repaired material gaps. Track a shared
  delivery budget without resetting it for fingerprints, authors or pushes.
- Generate no mandatory extra baseline report or runtime scenario for ordinary
  maintenance when existing contracts and execution evidence already suffice.

## Execution

- [x] Add failing real-Git regressions for local input impact, complete missing
  review reporting and packet isolation; preserve rejection/inventory tests.
- [x] Implement the checker additions; keep parser and fingerprint invariants.
- [x] Rewrite instructions/references, update package navigation and raw behavior
  scenarios without replacing judgment tests with wording assertions.
- [x] Run `npm test`; obtain one independent raw-case behavior review required by
  `docs/contributing.md`, then address concrete findings.
- [x] Back up the existing local installation; update only flow-docs-sync,
  record/verify full-file provenance with `scripts/skill-receipt.py`.

## Verification boundaries

Use current source hashes and actual test output. Cached input is a subset of
input, and unknown telemetry does not justify another model call. No claimed
Token-saving percentage without a measured comparison. No remote push/merge,
project gate migration, deployment or installation of unrelated skills.
