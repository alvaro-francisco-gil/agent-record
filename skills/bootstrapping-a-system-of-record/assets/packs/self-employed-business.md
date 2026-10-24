# Pack: self-employed business

A sole trader's or small business's paperwork: what the business is, who it works for,
what it invoices and spends, and what it owes the authorities and when. Empty structure
only. Every row is a suggestion the interview keeps, renames or drops.

**No jurisdiction is assumed.** Tax forms, social-contribution schemes and filing
calendars differ by country and change with the law. Ask where the business is
registered, write the answer into the entry file, and route the specifics. Never fill
them in from general knowledge: a wrong filing date is worse than an `[unknown: ...]`.

**Ask what already does the regulated work.** Invoicing software or an accountant that
issues compliant invoices and files the returns is the authority for those, and many
jurisdictions now require certified invoicing software. The record then routes to it.
It holds what was filed and the acknowledgement, the adviser's advice and the dates, but
never hand-made invoices that compete with the system that issues them.

## Typical renderings

Invoices and quotes, proposals, the documents assembled for an accountant or a tax
filing, statements for a bank or a grant. Received: registration certificates,
contracts, supplier invoices and receipts, letters from the authorities.

## Routing rows to offer

| Fact | Suggested destination |
|---|---|
| What the business is, where it is registered, legal form, activity codes | `business/PROFILE.md` (the entry point) |
| Registrations, licences, bank and payment accounts (described, not their numbers) | `business/admin/` |
| Each client: who, terms, history | `clients/<client>.md` |
| Invoices issued | `invoices/<year>/` |
| Expenses and receipts | `expenses/<year>/` |
| Tax filings and social contributions, with their acknowledgements | `filings/<year>/` |
| Suppliers and subscriptions | `suppliers/<supplier>.md` |
| Signed contracts as received | `contracts/` |
| Dated obligations: filings, renewals, payment deadlines | `obligations.md` (the register) |

## Questions this domain needs

- Where is the business registered, and since when? What legal form does it have?
- Who does the filings: you, an accountant, a mix? What do they need from you, and when?
- Which deadlines have penalties: tax returns, social contributions, licence renewals?
- How do invoices get made today, and where do receipts end up?

## Sensitive categories to raise in question 3

Bank account and card numbers, tax and national identity numbers, login credentials
for tax portals and banks, digital certificates and their passwords, clients' personal
data.

## Skills that often help

The obligations register almost always: this is the domain where a missed date costs
money. `plans-lifecycle`, when a registration, a grant or a dispute runs over weeks.
