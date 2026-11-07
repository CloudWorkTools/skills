# SitePing integration lessons

These lessons were extracted from a private host integration's research, clean builds, independent reviews and regression work in November 2026. They are historical constraints to recheck, not a portable copy of that application's implementation or a claim about current releases.

## Version and upstream sources

The researched upstream revision was [37deb7eb04df496e0958f2efa5b00a1a895d48c4](https://github.com/NeosiaNexus/SitePing/tree/37deb7eb04df496e0958f2efa5b00a1a895d48c4). Consult its [package sources](https://github.com/NeosiaNexus/SitePing/tree/37deb7eb04df496e0958f2efa5b00a1a895d48c4/packages) and the selected version's documentation when implementing. Historical registry availability and engine requirements must be checked again.

- A required core workspace dependency was unavailable from the registry. The host used verified source and bounded widget patches. Another site may use a complete released package set instead.
- The capture dependency required Node 24 even though a Node 22 bundle succeeded. Check the complete toolchain's engines, not just the top-level package.
- A patch invoked from the wrong working directory could be skipped. Clean isolated builds checked source hashes, unexpected/nonregular entries, patch identity and emitted behavior. The shipped bundles retained the upstream MIT notice.

## Data and publication

- The optional issue bridge's creation hook immediately creates an issue. Disabling status synchronization did not disable issue closure on feedback deletion. Inspect [the pinned bridge hooks](https://github.com/NeosiaNexus/SitePing/blob/37deb7eb04df496e0958f2efa5b00a1a895d48c4/packages/integration-issues/src/core/hooks.ts).
- A failed hook could leave feedback saved without an issue, while a deduplicated client retry did not rerun creation. Track storage and delivery separately; reconcile uncertain outcomes before resending.
- The generated issue omitted full annotation metadata and discussion. Retain the native persistent model. Verify lookup markers/labels and listing limits if using the bundled bridge.
- Widget normalization could change annotations after a preview hash was computed. Approval must bind the actual wire payload. Lost responses, deleted feedback, concurrent retries and redeployment all exposed lifecycle gaps in the host's custom delivery flow.
- Legacy offline entries lacked trustworthy actor binding and could lose screenshots under storage pressure. Preserve/quarantine unattributable entries; do not silently publish them under the next signed-in user. Explain any unrecovered drafts.

## Identity, capture and interaction

- Self-entered names and client-supplied team roles are not authenticated identities. The dashboard needed an author to expose its composer; server authorization still determined reply roles.
- Storage denial broke identity/consent paths despite ordinary browser success. Test denied localStorage and server-backed recovery if recovery is promised.
- A later composer focus problem remained under investigation. Delayed identity/render work around field focus could disrupt typing; a controlled scheduling reproduction was not proof of the historical incident's cause. Test initial and reopened forms, repeated focus switches and normal typing. Record failures without claiming a simulated race proves production causality.
- Pins may resolve approximately after DOM changes or disappear when elements are removed. Use stable unique anchors where useful and retain a panel route to feedback whose pin cannot resolve.
- Cross-origin iframe contents and DOM-based screenshot rendering have capture limits. Inspect representative images; preserve written context and allow real device screenshots when needed. iOS long-press is not a reliable substitute for annotation-mode tap/drag.
- Text redaction does not sanitize screenshot pixels. Verify masking, private asset access and any deliberately public image route separately.

## Operational boundary

The host used a same-origin authenticated gateway, persistent PostgreSQL and private media. These were host choices, not requirements to duplicate a Django gateway, container layout or ingress provider. Keep the underlying invariants: verified principal/project access, TLS at the actual boundary, durable storage, recoverable deployment and explicit public-image policy.

An installed widget, a passing build, a healthy endpoint, a visual review and customer acceptance each prove different things. Preserve unresolved findings and attach evidence to the outcome actually tested.
