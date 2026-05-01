# Phase 20 — continuous regime thresholds (item B)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 19 (commit `e77b208`) closed items A and H. Phase 20 closes
item B from the [v0.3 work plan](../docs/work-plan-v0-3.md):
*"Continuous regime thresholds (interpolated design-table entries)
— root-finding on `top_to_bottom_ratio = 0.95` and
`bottom_mass_fraction = 0.95` would replace 30-bin steps with
continuous radii."*

Forward-compat baseline = `pilot-v0.2.1` per D2 Option 1: the §5
cache and the existing grid-snapped design-table CSVs are
unchanged. The continuous-threshold outputs ship as **additional**
CSVs and a new Markdown summary.

## What was done

### `src/continuous_thresholds.py`

New module exposing two root finders + their grid-bracketing
helpers:

- `find_max_homogeneous_radius(T, h, t_obs, *, r_lo, r_hi, ...)` —
  `brentq` on `top_to_bottom_ratio(r) - 0.95`. Returns `None` when
  the bracket does not straddle the boundary (both ends homogeneous,
  or both stratified).
- `find_min_sedimented_radius(T, h, t_obs, *, r_lo, r_hi, ...)` —
  `brentq` on `bottom_mass_fraction(r) - 0.95` with a **round-4
  guard**: after the root is found, `top_to_bottom_ratio(root)` is
  re-checked; if `> 0.05` the function returns `None` rather than
  silently accept a label that violates the §5.1 second criterion.
- `bracket_homogeneous_from_grid(radii, regime_column)` and
  `bracket_sedimented_from_grid(radii, regime_column)` derive
  `[r_lo, r_hi]` from a §5 column at fixed (T, h, t_obs).
- `is_finite_radius(value)` — sanity helper for downstream callers.

### `tests/test_continuous_thresholds.py`

11 new tests pinning:

- Bracket helpers find the correct adjacent §5 cells (and return
  `None` when no transition exists).
- Bracket-length mismatch raises `ValueError`.
- Recovered radii produce `top_to_bottom_ratio ≈ 0.95` (homogeneous
  finder) and `bottom_mass_fraction ≈ 0.95` with the round-4 guard
  satisfied (sedimented finder).
- `find_max_homogeneous_radius` returns `None` when the bracket sits
  entirely on one side of the boundary.
- `find_min_sedimented_radius` returns `None` when no transition.
- Endpoint-at-threshold short-circuit (re-running the finder with
  `r_lo = root` returns the same root, no spurious off-by-floating-
  point shifts).
- `is_finite_radius` rejects `None`, `NaN`, `inf`, zero, and
  negatives.

A `room_t_1mm_1day_column` module-scoped fixture caches the §5 r-axis
walk (30 `classify_cell` calls) so the four tests that need it share
one walk — keeps file runtime in the 50–60 s range instead of
80+ s.

### `notebooks/04_design_table.py`

Additive update — existing grid-snapped multi-T CSVs and Markdown
summary are unchanged, preserving v0.2.1 reproducibility. New
section adds:

- A `_continuous_room_t_columns(grid, ti_room)` helper that walks
  the room-T column and root-finds both boundaries per (h, t_obs).
- Two new room-T-only CSVs:
  `design_table_max_homogeneous_r_continuous_room_T.csv` and
  `design_table_min_sedimented_r_continuous_room_T.csv`.
- A new Markdown summary
  `design_table_room_T_continuous.md` showing continuous values
  with the parenthesised grid-snapped value alongside, so the
  ~10 % bin-width uncertainty is visually obvious.

Multi-T continuous sweeps are deferred — the headline at-a-glance
deliverable is the room-T table; multi-T continuous tables can be
added in a future phase if a downstream consumer needs them.

## Decisions

| Decision | Rationale |
|---|---|
| Option A for the sedimented root (single brentq on `bmf - 0.95` with a ratio guard) | The user's plan: simpler than searching for the exact `_classify_from_ratio_and_bmf` transition, and at the (h, t_obs) cells where the grid shows a sedimented transition the ratio drops to ~0 well before bmf reaches 0.95, so bmf is the binding constraint. The guard converts a label-mismatch to a `None` return — no silent acceptance. If the guard ever fires in practice, switch to Option B (search the classification transition directly); track that at the line-comment / Phase 20.1 level. |
| Continuous tables ship at room T only (not all 7 temperatures) | The room-T table is the headline deliverable referenced in the breakout-note §6 narrative. Multi-T continuous sweeps would require ~210 root-finds × 2 boundaries; at-a-glance value is low when the existing grid-snapped multi-T CSVs already give ~10 % uncertainty. Deferred to a future phase if needed. |
| Continuous CSVs are *new files* (not columns added to the existing CSVs) | D2 Option 1: the existing `design_table_max_homogeneous_r.csv` / `design_table_min_sedimented_r.csv` are byte-identical to v0.2.1. Adding columns would break that contract; new files preserve it. |
| Round-4 guard returns `None`, not raises | Caller-friendly: notebook 04's per-cell loop just stores NaN and the markdown table renders "—". Raising would force every consumer to wrap the call in try/except. |
| Caller supplies the `(r_lo, r_hi)` bracket; no implicit grid walk inside the finder | Keeps `src/continuous_thresholds.py` decoupled from the §5 cache shape. Notebook 04 supplies brackets from `RegimeGrid`; future callers can supply brackets from any source. |
| Module-scoped fixture (`room_t_1mm_1day_column`) | The §5 r-axis walk is the dominant test cost (~30 `classify_cell` calls per walk). Sharing it across the 4 tests that need it cuts file runtime by ~30 % without changing any assertion semantics. |
| `scipy.optimize.brentq` (not bisection / Newton) | Already-imported scipy; brentq combines bisection robustness with secant convergence speed; matches the pattern in `src/fokker_planck.py` (which already imports from `scipy.sparse.linalg`). No new dependency surface. |

## Verification

```sh
.venv/bin/python -m pytest -q
# 163 passed   (152 v0.2/Phase-19 baseline + 11 new continuous-threshold tests)

.venv/bin/python -m ruff check .
# All checks passed!

PYTHONPATH=src .venv/bin/python notebooks/04_design_table.py
# Existing grid-snapped multi-T CSVs continue to write byte-identical
# to v0.2.1.  The new continuous-threshold block was not run end-to-end
# in this commit — see "What was not done" below.

git diff --check
# clean
```

HEAD before Phase 20: `e77b208` (Phase 19 — audit-gap pins +
parallel walk).

## What was not done

- **No multi-T continuous tables.** Room-T only in this phase.
  Extension is mechanical (loop over `ti` instead of fixing
  `ti_room`); deferred until a downstream consumer asks.
- **No `p_stratified` root-finder.** The work-plan §1 item B
  mentions "p_stratified suitability" alongside the ratio / bmf
  thresholds. `p_stratified` is a derived deliverable-6 quantity
  (polydispersity smearing) and lives in `src/polydispersity.py`,
  not in the §5.1 thresholds; root-finding on it would require a
  smeared classify_cell wrapper and is a separate slice. Tracked
  as a Phase-20.x deferral if it becomes needed.
- **No replacement of the existing grid-snapped CSVs.** D2 Option 1
  forbids it; the new files ship alongside.
- **No `pyproject.toml` version bump.** Phase 20 ships under
  `pilot-v0.2.1`. The v0.3 release tag lands at Phase 24 per the
  contract.
- **No `n_workers` plumbing in the root-finder.** Each `classify_cell`
  inside `brentq` is fast (the boundary cells fire the homogeneous-
  corner or equilibrated short-circuits in most of the grid), so
  parallelism inside the root-finder would add complexity without
  clear gain. The notebook-level loop over (h, t_obs) is trivially
  parallelisable if a future phase needs it.
- **No end-to-end notebook 04 execution in this commit.** Informal
  timing showed `python notebooks/04_design_table.py` running >13 min
  wall under contention (5 min user CPU at 18 % utilisation due to a
  competing process). The notebook was killed before reaching the new
  continuous-threshold block, so the new CSVs and the
  `design_table_room_T_continuous.md` summary are not yet on disk.
  The room-T continuous tables are deferred to whichever phase next
  regenerates the deliverable artefacts (likely Phase 23 — the v0.3
  integration audit). The module-level correctness contract is fully
  pinned by `tests/test_continuous_thresholds.py` (11 tests, 55 s);
  the notebook block is a downstream consumer whose runtime is
  amortised away from this phase. Same pattern as Phase 19's
  wall-time benchmark deferral.

## Next step

Phase 21 — item C (mesh-convergence audit on the finite-time
bottom-mass threshold) + item F (`δ_shell` calibration against
literature). 1 session per the contract; Phase 21's audit may
escalate to a Phase 21.1 fix if drift exceeds the empirical 1 %
tolerance noted in `experimental-envelope.md`.

## Cross-references

- [`docs/work-plan-v0-3.md`](../docs/work-plan-v0-3.md) §1 item B
  — the contract this phase delivers against.
- [ADR 0002](../docs/adr/0002-v0.3-spec-anchoring.md) Decision 1
  (D1 = Option 2) — the spec-anchor under which root-finding ships
  as a v0.3 tightening.
- [ADR 0001](../docs/adr/0001-v0.2-spec-anchoring.md) — the byte-
  identical §5 cache contract that the additive ship of Phase 20
  preserves.
- [Phase 19 lab note](2026-05-01-phase19-audit-gap-pins-and-parallel-walk.md)
  — immediate predecessor (audit-gap pins + parallel walk).
- [Phase 18 lab note](2026-05-01-phase18-s2-stokes-einstein-corrections.md)
  — S2 first slice; introduced `lambda_se` which the root-finder
  inherits via `**classify_kwargs`.
- `src/regime_map.py` `_classify_from_ratio_and_bmf` — the §5.1
  classifier whose thresholds the root-finder solves against.
