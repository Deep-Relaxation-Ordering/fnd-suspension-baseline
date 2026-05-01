# Phase 22 — Continuous time-evolution channel (item J)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 21 (commit `92d7ce6`) closed the mesh-convergence audit and
δ_shell calibration.  Phase 22 implements item J from the v0.3 work
plan: continuous time-evolution — treating ``t_obs`` as a continuous
variable rather than the six discrete points of the §5 cache.

## What was done

### 1. Core module — `src/time_evolution.py`

Two public functions:

- **`time_series(r, T, h, *, t_values)`** — evaluates a cell at an
  arbitrary sequence of observation times, returning ``(t, ratio,
  bmf, regime)`` tuples.  Default uses the §5 ``T_OBS_S`` axis; callers
  can supply any sequence.

- **`crossing_time(r, T, h, *, criterion, target, t_min, t_max,
  n_points)`** — finds the observation time at which a criterion
  (``"bmf"`` or ``"ratio"``) crosses a target value.

**Algorithm:** Two-stage bracket-and-refine.

1. **Trivial rejections** — check equilibrium value; return ``None``
   if target is unreachable, ``0.0`` if already met at ``t = 0``.
2. **Bracketing sweep** — evaluate ``solve_cell`` at ``n_points``
   log-spaced times (default 15).
3. **Root-find** — PCHIP interpolation + Brent's method on the
   bracketed interval.

**Accuracy:** Verified to within ~1 % relative / 0.005 absolute against
a direct ``solve_cell`` re-evaluation at the found crossing time.

**Performance:** ~10–30 s per crossing for resolved Method-C cells;
~0.1–1 s for short-circuit cells.  Tractable for design-table work
(~20 crossings = ~5–10 min).

### 2. Tests — `tests/test_time_evolution.py` (8 tests)

- `test_time_series_structure` — correct tuple shape and bounds
- `test_time_series_bmf_increases_monotonically` — physical sanity
- `test_time_series_ratio_decreases_monotonically` — physical sanity
- `test_crossing_time_hits_target[bmf-0.06]` — accuracy guard
- `test_crossing_time_hits_target[ratio-0.5]` — accuracy guard
- `test_crossing_time_none_for_unreachable_target` — equilibrium bound
- `test_crossing_time_zero_for_already_met` — t = 0 guard
- `test_crossing_time_none_for_homogeneous_cell` — homogeneous guard

Slow tests (2 × parametrized) marked with `@pytest.mark.slow`.
Registered in `pyproject.toml`.

### 3. Design-table script — `notebooks/08_time_evolution_design_table.py`

Generates `notebooks/data/design_table_crossing_times.csv` with
 crossing times for 5 representative cells × 4 thresholds:

| Threshold | Meaning |
|---|---|
| bmf = 0.10 | Early sedimentation signal |
| bmf = 0.50 | Mid-point of sedimentation |
| bmf = 0.90 | Near-complete sedimentation |
| ratio = 0.50 | Mid-point of stratification |

**Forward-compat:** No §5 cache schema change. The script runs
`crossing_time` on live `solve_cell` evaluations; it does not depend on
cached snapshots. A future optimisation could pre-compute a dense time
series once per cell and interpolate, but that is out of scope for v0.3.

## Files changed

| File | Change |
|---|---|
| `src/time_evolution.py` | New module: `time_series` + `crossing_time` |
| `tests/test_time_evolution.py` | 8 tests |
| `notebooks/08_time_evolution_design_table.py` | Design-table generator |
| `pyproject.toml` | Register `@pytest.mark.slow` |

## Decisions recorded

| Decision | Resolution | Rationale |
|---|---|---|
| Interpolator choice | **PCHIP** (monotonicity-preserving) | bmf(t) and ratio(t) are monotonic; cubic spline can overshoot |
| Root-finder | **Brent's method on PCHIP** | Robust, bracketed, no derivative needed |
| n_points default | **15** | Brackets crossing reliably for tested cells without excessive cost |
| t_max default | **10 × equilibration_time_geom** | Conservative upper bound; covers all tested cells |
| §5 cache impact | **None** | Live solve_cell calls; no cache read or write |

## Open questions

- **Q-22-1.** Dense-time-series caching: for a full design table with
  hundreds of cells, re-running `solve_cell` ~15× per cell is expensive.
  A future optimisation could store a dense `(t, ratio, bmf)` series
  per cell and interpolate crossings in O(1) per threshold.
- **Q-22-2.** Multiple thresholds per cell: the current API finds one
  crossing at a time. A batch API that finds all crossings for a cell
  in a single sweep would be more efficient for design-table generation.

## Next step

Phase 23: Integration / regression audit across all in-scope items
(A, B, C, F, H, J, K). Verify byte-identical baseline at λ = 1.0,
δ_shell = 0, and cache defaults. Prepare for v0.3 release.
