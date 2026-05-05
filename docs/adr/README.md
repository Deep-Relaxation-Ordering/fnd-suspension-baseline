# Architecture Decision Records (ADRs)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

This directory holds the Architecture Decision Records for
`fnd-suspension-baseline`. ADRs follow
[Michael Nygard's classic format](https://github.com/joelparkerhenderson/architecture-decision-record/blob/main/locales/en/templates/decision-record-template-by-michael-nygard/index.md):
Context, Options considered, Decision, Consequences. They are
numbered in the order they are *opened* (drafted), not in the order
they are accepted, so that `Proposed` stubs hold their final number.

## Index

| ADR | Title | Status | Date | Phase |
|---|---|---|---|---|
| [0001](0001-v0.2-spec-anchoring.md) | `pilot-v0.2` spec-anchoring | Accepted | 2026-04-28 | 10 |
| [0002](0002-v0.3-spec-anchoring.md) | `pilot-v0.3` spec-anchoring and first-slice selection | Accepted | 2026-04-30 | 17 |
| [0003](0003-v0.4-spec-anchoring.md) | `pilot-v0.4` spec-anchoring and first-slice selection | Accepted | 2026-05-06 | 26 |

## Conventions

- **Status field is load-bearing.** `Proposed` ADRs are deliberation
  records, not commitments. Promotion to `Accepted` is a deliberate
  act and should be recorded in a phase lab note plus a cross-linked
  work plan or ADR-side decision step.
- **One ADR per coherent decision (or coupled set).** ADR 0002 bundles
  the v0.3 spec anchor (D1) with the first-slice selection because
  the two are tightly coupled: Option 2 ("v0.3 = implementation
  tightenings under the v0.2 envelope") and "S2 first" are the same
  architectural choice viewed from two angles. D2 / D3 / D4 / D5 / D6
  of the v0.3 work plan remain in their own deliberation surfaces.
- **Filenames** are `NNNN-short-kebab-title.md`. The number is
  zero-padded to four digits and never reused.
- **Supersession.** When an ADR replaces an earlier one, both ADRs
  record the cross-reference: the new ADR's `Supersedes` field and
  the old ADR's `Superseded by` field.
- **No silent edits.** Once an ADR is `Accepted`, substantive content
  changes go through a new ADR that supersedes it. Typo fixes and
  cross-reference updates are fine.

## Cross-references

- Pattern 11 in [`../findings-process.md`](../findings-process.md#11-spec-pinning-at-commit-hash-precision)
  — spec pinning at commit-hash precision; the convention ADR 0001
  enforced.
- [`../work-plan-v0-2.md`](../work-plan-v0-2.md) §1 forward-compat
  contract — the pattern ADR 0001 unlocked.
- [`../work-plan-v0-3.md`](../work-plan-v0-3.md) §0 / §5 — the
  deliberation surface ADR 0002 scopes.
- [`../work-plan-v0-4.md`](../work-plan-v0-4.md) §0 / §5 — the
  deliberation surface ADR 0003 scopes.
