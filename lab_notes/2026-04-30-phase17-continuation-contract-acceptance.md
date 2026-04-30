# Phase 17 (continuation) — v0.3 work-plan contract acceptance

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 17 (opening, commit `197ce24`) promoted [ADR 0002](../docs/adr/0002-v0.3-spec-anchoring.md)
to `Accepted` and opened [`docs/work-plan-v0-3.md`](../docs/work-plan-v0-3.md)
as a SCAFFOLD against it. That commit resolved D1 (spec anchoring = Option 2)
and D9 (first slice = S2), but left D2–D7 open and §1–§7 partially empty.

This continuation commit finishes the acceptance ceremony.

## What was done

- **§1 reshape.** Items A–J evaluated against D1 = Option 2 (stay anchored to
  breakout-note v0.2 commit `3b7b18af`).
  - **In-scope:** A, B, C, F, H, J (tightenings under the v0.2 envelope).
  - **Out-of-scope:** D (parallel breakout — S1 aggregation), E (defer to v0.4 —
    wall hydrodynamics), G (defer to v0.4 — convection refinement), I (wait on
    breakout-note authors — σ_geom promotion).
  - **Already fixed:** K (S2 — Stokes-Einstein corrections at sub-150-nm radii),
    first slice per ADR 0002 Decision 2.

- **D2–D7 resolved in §5.**
  - **D2 = Option 1** (anchor to `pilot-v0.2.1`) for all in-scope items.
  - **D3 = parallel breakout** (S1 aggregation deferred upstream).
  - **D4 = defer to v0.4** (wall hydrodynamics exceed v0.2 envelope).
  - **D5 = defer to v0.4** (even κ(T) alone changes §5 cache numerics).
  - **D6 = wait** (ADR 0001 delegation stands).
  - **D7 = keep `3 - Alpha`** (promotion to `4 - Beta` gated on v1.0 per
    program-context §4.1).

- **§4 phase plan filled.** Phases 17–24 mapped to items with effort estimates
  and deliverables. Total: ~9–12 sessions, ~7–10 working days.

- **§6 risk register expanded.** Risks for all in-scope items (A, B, C, F, H,
  J, K) documented with mitigations. Out-of-scope residual risk acknowledged
  in `docs/experimental-envelope.md`.

- **§7 schedule filled.** Calendar span ~2 weeks (2026-04-30 through
  2026-05-14), allowing for session gaps.

- **§9 acceptance steps marked complete.** SCAFFOLD qualifier removed from
  title and status field.

## Decisions recorded

| Decision | Resolution | Gating document |
|---|---|---|
| D1 | Option 2 (stay on `3b7b18af`) | ADR 0002 §Decision 1 |
| D2 | Option 1 (anchor to `pilot-v0.2.1`) | work-plan-v0-3 §3 |
| D3 | Parallel breakout | work-plan-v0-3 §5 |
| D4 | Defer to v0.4 | work-plan-v0-3 §5 |
| D5 | Defer to v0.4 | work-plan-v0-3 §5 |
| D6 | Wait on breakout-note authors | work-plan-v0-3 §5 |
| D7 | Keep `3 - Alpha` | work-plan-v0-3 §5 |
| D8 | Hold DOI to v1.0 | Phase 16.1 lab note |
| D9 | S2 (item K) first slice | ADR 0002 §Decision 2 |

## In-scope summary for v0.3

| Item | Description | Phase |
|---|---|---|
| K (S2) | Stokes-Einstein corrections at sub-150-nm radii | 18 |
| A | Resolve audit-gap pins `T_OBS_S` / `DEPTHS_M` | 19 |
| H | Parallel §5 walk | 19 |
| B | Continuous regime thresholds | 20 |
| C | Mesh-convergence audit on bmf threshold | 21 |
| F | δ_shell calibration against literature | 21 |
| J | Continuous time-evolution channel | 22 |

## Out-of-scope (deferred or parallel)

| Item | Disposition | Tracking |
|---|---|---|
| D (S1) | Parallel breakout | `Deep-Relaxation-Ordering/diamonds_in_water` owes breakout note |
| E (S6) | Defer to v0.4 | program-context §3.1 S6 |
| G (S7) | Defer to v0.4 | program-context §3.1 S7 |
| I | Wait on authors | ADR 0001 delegation |

## Next step

Phase 18 opens: S2 — Stokes-Einstein corrections at sub-150-nm radii.
Forward-compat: `λ = 1.0` reproduces `pilot-v0.2.1` to machine precision.
API contract: `provisional=True` until S1 lands.
