# Phase 17 (opening) — ADR 0002 promoted; work-plan-v0-3 opened against it

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 16.3 landed [`docs/program-context.md`](../docs/program-context.md)
v0.1 (commit `1e602da`), which articulates the long-horizon goal and
records D-PC-2 as resolved (S2 ships first). With program-context.md
in place as upstream rationale, the v0.3 cycle's opening ceremony can
finally promote [ADR 0002](../docs/adr/0002-v0.3-spec-anchoring.md)
from `Proposed (stub)` to `Accepted` and open
[`docs/work-plan-v0-3.md`](../docs/work-plan-v0-3.md) against it.

Phase 17 has two parts:

- **Opening (this commit).** ADR 0002 promotion + work-plan-v0-3 D1 /
  D9 resolution + adding item K (S2) to §1.
- **Continuation (later).** §1 in-scope vs out-of-scope reshape against
  D1 = Option 2; D2 / D3 / D4 / D5 / D6 / D7 deliberation; §4 / §6 /
  §7 fill; promote work-plan-v0-3 from SCAFFOLD to contract.

Splitting Phase 17 lets the implementation phase (Phase 18, S2)
start as soon as the slice is unambiguously fixed, rather than
gating it behind every D-decision in the cycle.

## What was done

- **Promoted [`docs/adr/0002-v0.3-spec-anchoring.md`](../docs/adr/0002-v0.3-spec-anchoring.md)
  from `Proposed (stub)` to `Accepted`.** The ADR now records two
  coupled decisions:
  - **Decision 1 — D1 = Option 2.** v0.3 anchors to breakout-note
    v0.2 commit `3b7b18af` (same pin as v0.2 / v0.2.1).
  - **Decision 2 — first slice = S2.** Stokes-Einstein corrections at
    sub-150-nm radii ship first, while S1's upstream breakout note
    is being drafted at `Deep-Relaxation-Ordering/diamonds_in_water`.
  - Pins the `provisional=True` API contract for S2-refined
    diffusivities — the design-tool entry points refuse provisional
    outputs without an explicit `accept_provisional=True` override.
- **Updated [`docs/adr/README.md`](../docs/adr/README.md).** ADR 0002
  status flipped to `Accepted` with the new title "spec-anchoring and
  first-slice selection". The "ADR 0002 explicitly scopes itself to
  D1 only" line was reworded — ADR 0002 now bundles D1 and the
  first-slice selection because the two are tightly coupled.
- **Opened [`docs/work-plan-v0-3.md`](../docs/work-plan-v0-3.md)
  against ADR 0002.** Specifically:
  - Status field flipped from "SCAFFOLD — decisions [OPEN], not
    accepted" to "OPENED against ADR 0002 (Phase 17 opening)".
  - §0 spec anchoring marked RESOLVED with Option 2.
  - §1 added new candidate **K** (Stokes-Einstein corrections at
    sub-150-nm radii) flagged as **FIRST SLICE**, with the full
    spec content, forward-compat note, blast radius, and the
    `provisional=True` API contract recorded inline.
  - §3 forward-compat: item K covered (Option 1, `λ = 1.0` reproduces
    v0.2.1 to machine precision); D2 remains [OPEN] for other slices.
  - §4 phase plan upgraded from [TBD] to [PARTIAL] with Phase 17
    (opening, continuation), Phase 18 (S2 implementation), Phase Z
    (release).
  - §5 D-list: D1 Resolved (Option 2); D9 added and Resolved (S2
    first slice); other rows annotated with the implication of
    D1 = Option 2 but kept [OPEN].
  - §6 risk register: in-scope rows for item K (R-K1 cache drift,
    R-K2 provisional misuse, R-K3 calibration data fallback).
  - §9 acceptance / next step: marks ADR-drafting and D1-resolution
    done; lists remaining steps.
  - §10 cross-references: program-context.md added; ADR 0002 added
    as Accepted.
- **Updated [`README.md`](../README.md) phase table** to add the v0.3
  cycle section header and the Phase 17 (opening) row.
- **Updated [`lab_notes/README.md`](README.md)** to prepend the
  Phase 17 row.

## Decisions

| Decision | Rationale |
|---|---|
| Promote ADR 0002 to `Accepted` (not keep as `Proposed`) | Program-context.md v0.1 (Phase 16.3) made the rationale for both Decision 1 and Decision 2 explicit; the deliberation context is now load-bearing rather than working notes. ADR 0001's precedent is "Accepted at the cycle-opening phase note", which Phase 17 is. |
| Bundle D1 (spec anchor) and first-slice selection in one ADR | Option 2 ("v0.3 = implementation tightenings under v0.2 envelope") and "S2 first" are the same architectural choice viewed from two angles. Splitting them into two ADRs would multiply bookkeeping without informational gain. The adr/README convention was reworded to allow "one ADR per coherent decision (or coupled set)". |
| Split Phase 17 into opening + continuation | Phase 18 (S2) is unambiguously fixed by ADR 0002, but the rest of §1 / §4 / §6 / §7 still requires deliberation on D2 / D3 / D4 / D5 / D6 / D7. Splitting lets implementation start while the rest of the cycle scope is being decided. Same pattern Phase 16 → 16.1 → 16.2 → 16.3 used for the v0.2.1 cycle. |
| Encode `provisional=True` at the API surface, not just in docs | Per ADR 0002 §"API surface — the `provisional=True` contract": documentation alone cannot prevent downstream users from treating S2-only outputs as L1-complete. Programmatic refusal at the design-tool entry points, with a loud override pathway, is the only enforcement that survives serialisation and copy-paste. |
| No `pyproject.toml` version bump for Phase 17 opening | Documentation-only change; ships under `pilot-v0.2.1`. Phase 18 (S2 implementation) will be the first phase that touches code and may bump the package version. |

## Verification

```sh
.venv/bin/python -m pytest -q
# 135 passed

.venv/bin/python -m ruff check .
# All checks passed!

.venv/bin/cffconvert --validate -i CITATION.cff
# Citation metadata are valid according to schema version 1.2.0.

git diff --check
# clean
```

HEAD before Phase 17 (opening): `1e602da` (Phase 16.3 — program-
context articulation).

## What was not done

- **No Phase 17 continuation.** §1 reshape (per-item in-scope vs
  out-of-scope under D1 = Option 2), D2 / D3 / D4 / D5 / D6 / D7
  deliberation, and §4 / §6 / §7 fill remain ahead.
- **No Phase 18 implementation.** S2 is the first slice but the slice
  itself is not implemented in this commit; that is the Phase 18
  task.
- **No `pyproject.toml` version bump.** Stays on `pilot-v0.2.1`.
- **No `docs/local-specs/` directory.** Created on first use under
  the program-context §5 supplier-failure clause; no local spec is
  owed yet for S2 (S2 has no upstream dependency).
- **No re-pin to a future breakout-note v0.3.** Per ADR 0002 §"Re-pin
  policy", any movement of the breakout-note pin during the v0.3
  cycle happens at the release phase only.

## Next step

1. **Phase 17 (continuation).** §1 reshape: tag each of items A–J as
   in-scope, parallel-breakout, or deferred under D1 = Option 2.
   Resolve D2 / D3 / D4 / D5 / D6 / D7 in their own deliberation
   surfaces or as work-plan §1 in-line tags. Fill §6 risk register
   for the resulting in-scope set. Promote work-plan-v0-3 from
   SCAFFOLD to contract.
2. **Phase 18.** Implement S2 — Stokes-Einstein corrections at
   sub-150-nm radii. λ-sweep over `{0.1, 0.5, 1.0}`; calibration
   against the gold-NP benchmark (Laloyaux z₂); `λ = 1.0`
   regression test against the v0.2.1 §5 cache;
   `provisional=True` flag on result objects;
   `accept_provisional=True` override on the design-tool entry
   points.

## Cross-references

- [`docs/adr/0002-v0.3-spec-anchoring.md`](../docs/adr/0002-v0.3-spec-anchoring.md)
  — Accepted in this phase.
- [`docs/work-plan-v0-3.md`](../docs/work-plan-v0-3.md) — opened
  against ADR 0002 in this phase.
- [`docs/program-context.md`](../docs/program-context.md) — the
  upstream rationale (Phase 16.3, commit `1e602da`).
- [Phase 16.3 lab note](2026-04-30-phase16-3-program-context.md) —
  immediate predecessor.
- [Phase 16.2 lab note](2026-04-30-phase16-2-v0-3-deliberation-surfaces.md)
  — the deliberation-surface commit whose stub ADR 0002 is now
  promoted.
- [`docs/adr/0001-v0.2-spec-anchoring.md`](../docs/adr/0001-v0.2-spec-anchoring.md)
  — precedent ADR for the cycle-opening promotion pattern.
- [`docs/adr/README.md`](../docs/adr/README.md) — ADR index updated
  to reflect ADR 0002's `Accepted` status.
