---
name: client-quotation
description: Create or revise a client-facing service quotation and its paired scope attachment, including editable ODT templates, payment milestones, UI review, and plain-language feature value.
license: MIT
---

# Client quotation

Create a quotation a client can approve and a scope attachment a nontechnical reader can understand. Start from the user's facts and existing documents. Use the editable [quotation template](assets/quotation-template.odt) and [scope attachment template](assets/scope-attachment-template.odt) when an ODT deliverable is useful; resolve every bracketed prompt to confirmed content or a deliberately blank field before sending a client copy.

## Keep the pair consistent

- Give the quotation and attachment one shared quotation/order identifier. Keep the client, project name, scope, dates, and exclusions consistent. The attachment explains the quoted work; it does not silently add deliverables.
- Distinguish the quoting entity, client, invoice issuer, and designated payee. Use only supplied names, tax IDs, bank details, prices, and stamps. Leave unknown fields visibly blank for the owner to complete.
- State whether the price is tax exclusive or inclusive. Recalculate subtotal, tax, total, and each payment milestone; if the user gives only a project total, avoid inventing prices for individual features. Specify each milestone's trigger and amount.
- For invoice timing or tax treatment, check current official rules for the relevant jurisdiction before advising. Record the agreed billing wording in the quotation, without treating a template as legal or accounting authority.

## Express revisions against the preceding version

- Mark each scope attachment with its version, date, shared quotation/order identifier, and whether it is the current scope or a historical baseline. Version 1 explicitly says it has no preceding version; keep its original scope available for comparison.
- From version 2 onward, include a prominent comparison with the *immediately preceding* version. For each material change, name the affected feature, label it added, changed, or removed, and state the previous and current client-visible behavior. Mention material items that carry forward when that prevents confusion.
- Make the current version a complete, standalone scope for approval. Highlight changed passages with bold or color while keeping the change type and old/new wording readable without color. Preserve earlier version files and use distinct versioned filenames; identify which version governs acceptance.
- Apply the same version wording to the editable ODT, review PDF, and any linked issue or quotation reference. The version comparison is explanatory; the full current scope is authoritative.

## Explain the scope in the client's language

Describe what visitors can see and do, what staff can change in the admin UI, and what system or data changes make those actions possible. Pair each behind-the-scenes change with a concrete benefit, such as fewer duplicate entries or preserving existing links. State who supplies copy and media, what counts as acceptance, and material exclusions.

When UI work is included, describe a development-stage demo as a review and communication point: the client sees representative pages and flows, discusses them with the provider, and the provider adjusts agreed visual and interaction details within the quoted scope. A demo alone is not the deliverable or acceptance criterion.

## Deliver clean documents

Use a restrained visual hierarchy: aligned columns, readable type, adequate whitespace, and distinct totals and payment terms. If an authorized stamp is supplied, embed it in the ODT beside the provider's signing area without pushing the two signature columns out of alignment. Fill the provider's date only when authorized and leave the client's signing date open until they sign.

Export both editable ODT and reviewable PDF when requested. Render every PDF page and inspect for clipped text, broken tables, orphan headings, signature alignment, and image placement. Check that embedded images remain inside the ODT and that both documents carry the same identifier. Before publishing a reusable skill or template, inspect its contents and metadata for real client names, account numbers, prices, signatures, stamps, and other private project data.
