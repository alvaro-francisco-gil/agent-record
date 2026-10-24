# Pack: vehicle or asset

One physical thing someone owns and has to keep legal, insured and working: a vehicle,
a van being converted, a boat, a property. Empty structure only. Every row is a
suggestion the interview keeps, renames or drops.

This record has renderings, even if its owner doesn't call them that: the bundle
assembled for an inspection, an insurance claim, a sale or a regulatory approval of a
modification. That is what makes it a record, not a notebook.

## Typical renderings

Inspection bundles, insurance claims, a sale listing with its history, the file for
approving a modification, a cost summary. Received: registration and ownership papers,
inspection reports, insurance policies, workshop invoices, approval certificates.

## Routing rows to offer

| Fact | Suggested destination |
|---|---|
| What it is, identifiers, current state, what is planned | `PROFILE.md` (the entry point) |
| Ownership and registration papers (described; scans by policy) | `papers/` |
| Each inspection and its result | `inspections/<date>.md` |
| Insurance: policy, cover, renewals, claims | `insurance/` |
| Maintenance and repairs: what, when, by whom, cost | `maintenance/<date>-<what>.md` |
| Modifications, their parts and approvals | `modifications/<what>.md` |
| Running costs | `costs/<year>.md` |
| Dated obligations: inspection due, insurance renewal, service interval | `obligations.md` (the register) |

## Questions this domain needs

- What is it, when was it acquired, and what state was it in?
- What is it for, and what changes are planned (a conversion, a repair, a sale)?
- Which dates matter: next inspection, insurance renewal, service interval, tax?
- Who works on it, and where do their invoices end up?

## Sensitive categories to raise in question 3

Scans of identity and ownership documents, policy and account numbers, the owner's
address, where the asset is kept (for a vehicle or a property, a security matter).

## Skills that often help

The obligations register almost always: inspections and renewals are the dates people
miss. `plans-lifecycle`, when a modification or repair runs as a project over weeks.
