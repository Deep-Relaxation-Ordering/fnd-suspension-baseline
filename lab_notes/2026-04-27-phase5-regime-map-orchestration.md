# 2026-04-27 — Phase 5: regime-map orchestration

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 5 of the breakout-note timeline (§9): wire Methods A and C into
the §5.1 regime classifier and a 4-axis grid walker. With Methods A,
B, C all in place from earlier phases, this is the *orchestration*
layer that produces the inputs to deliverables 3 (regime map) and 5
(design table). Notebook generation of those figures is deferred to
the next session — this commit is just the orchestration core.

## What was done

### `src/scan_grid.py` — t_obs axis

Added the fourth scan-grid axis:

- `T_OBS_S = (60, 600, 3600, 14400, 86400, 604800)` s — six
  hand-picked experimental durations from 1 minute (fast microscopy)
  to 1 week (long observation). Not strictly log-spaced — ratios
  vary from 4× to 10× (see Phase 5.1 errata).
- `T_OBS_LABELS` and `N_T_OBS = 6` aligned with the values.
- Module docstring updated to drop the "t_obs deferred" caveat that
  Phase 2.5 left as a TODO.

The §5 spec table for t_obs values is the same audit-gap pattern as
the depth axis: the values committed here are physically motivated
defaults; cross-check against the breakout-note §5 table at the next
spec drift.

### `src/regime_map.py` — `classify_cell` + `walk_grid`

Implemented the §5.1 classifier as `classify_cell(r, T, h, t_obs) →
RegimeResult`. The result keeps the underlying ratio and bottom-mass
fraction so deliverable-5 design-table generation doesn't have to
re-run Method C.

Three execution paths, in order of cost:

1. **Homogeneous-corner short-circuit**: when the analytic equilibrium
   ratio `exp(-h/ℓ_g) ≥ 0.95`, the finite-time ratio (decreasing
   monotonically from 1 toward eq_ratio) stays in [0.95, 1] for any
   t_obs → always homogeneous. No Method C call.
2. **Equilibrated-corner short-circuit**: when
   `t_obs ≥ max(5·t_relax, 1.01·h/v_sed)`, the residual transient is
   ≲ 0.7 % from analytic equilibrium. Use Method A's
   `barometric_mean_height` and the closed-form bottom-mass
   integral. No Method C call.
3. **Method C**: any cell that misses both short-circuits. The
   `min_resolvable_dz_m` default for the regime map is bumped to
   10 nm (vs 1 nm in the production Method C default), routing the
   high-r corner of the grid (ℓ_g ≲ 50 nm with t_obs in the
   transient regime) through Method C's existing
   asymptotic-sedimentation fallback rather than a refined-mesh
   `expm_multiply` that would otherwise cost 10-20 s per cell.

`walk_grid(*, radii, temperatures, depths, t_obs, ...)` walks any
Cartesian product of the four axes (defaults to the full §5 grid).
Iteration order is radius → temperature → depth → t_obs; pinned in
`test_walk_grid_subset_iteration_order` so downstream reshape into a
4-D array is unambiguous.

`_equilibrium_bottom_mass_fraction(h, ℓ_g, layer_fraction=0.05)` is
the closed-form `(1 - exp(-f·h/ℓ_g)) / (1 - exp(-h/ℓ_g))` with a
700-threshold asymptotic branch for the deeply-sedimented corner
(matches the same expm1-overflow pattern from Phase 3.2).

### `tests/test_scan_grid.py`

Three new tests pin the t_obs axis: shape, strict monotonicity, and
the spec contract (1 minute → 1 week).

### `tests/test_regime_map.py` (new file)

12 tests covering:

- §5.1 threshold logic (homogeneous, sedimented requires both
  criteria, stratified default).
- Each of the three execution paths fires for the right cells.
- Round-4 second criterion: in-transit cells are stratified, NOT
  sedimented, even when the ratio threshold is met.
- Grid walker default cardinality matches scan_grid (6300 cells), the
  iteration order is radius → temperature → depth → t_obs, and a
  small radius-spanning slice covers all three regimes.

## Decisions

| Decision | Rationale |
|---|---|
| t_obs values committed as defensible defaults with audit-gap doc | Same pattern as depth axis (Phase 2.5). The audit pin moves at the next breakout-note drift; the current implementation is consumable now. |
| Homogeneous-corner short-circuit using analytic eq_ratio | Saves Method C calls on ~50 % of grid cells (the small-r / high-T corner) at zero accuracy cost: the finite-time ratio is provably bounded by [eq_ratio, 1] from uniform IC. |
| Equilibrated short-circuit at `5 · t_relax` | e⁻⁵ ≈ 0.7 % residual is two orders of magnitude below the §5.1 threshold sharpness. Smaller multipliers tested (2, 3) have rel-err visible at 4 % near the threshold; 5 is the safety/cost balance. |
| `min_resolvable_dz_m = 10 nm` for the regime walk | The full-fidelity Method C default of 1 nm trades runtime for boundary-layer fidelity. Regime classification only needs the integrated quantities (top/bottom ratio, bottom-mass fraction), and Method C's asymptotic transient + equilibrium branches give them analytically — verified by hand-computation on r=1µm/h=1mm/t=60s where bmf=0.42 either way. |
| Grid walker returns `list[RegimeResult]` rather than a numpy array or pandas DataFrame | Avoids a pandas dependency; consumers (deliverable notebooks) can convert in one line. The dataclass keeps the provenance flags (which short-circuit fired, fallback used) attached to each cell. |
| Iteration order pinned in a test, not just a docstring | Reshape into 4-D array works only if order is stable; this is the kind of contract that gets accidentally swapped during refactors and bites silently. |
| Bumping `MAX_N_CELLS` or n_cells *did not* fix the slow corner | Confirmed empirically: spectral radius of the FV operator scales like D/(ℓ_g/5)², independent of total cell count. Bumping mesh fidelity makes the operator *smaller*-step but no faster. The fallback was the right architectural move. |

## Performance snapshot

Grid runtime estimates from a 5-radii × 1-T × 5-h × 6-t_obs (150-cell)
slice at 25 °C:

| Path | Cells | Avg time/cell |
|---|---|---|
| Homogeneous short-circuit | 30 / 150 | < 1 ms |
| Equilibrated short-circuit | 84 / 150 | < 1 ms |
| Method C asymptotic fallback | 6 / 150 | < 1 ms |
| Method C resolved mesh | 30 / 150 | ~0.9 s |
| **Slice total** | **150** | **27 s** |

Extrapolation to the full 6300-cell §5 grid: ~18 minutes at default
settings. Acceptable for a one-time deliverable run; the unit tests
walk a 16-cell slice.

## What was *not* done

- **Notebook 02-04 generation** — deferred to Phase 6. The orchestration
  surfaces (`classify_cell`, `walk_grid`, `RegimeResult`) are stable
  enough now to drive the figure generation in a separate commit.
- **Deliverable 5 design table** — same; the orchestration computes
  the underlying numbers, the table presentation is a notebook task.
- **Method-B cross-check inside the regime walk** — Method B's
  feasibility envelope can be queried via `langevin.is_feasible`, but
  the §5.1 classification doesn't require a B↔C agreement check on
  every cell. Spot checks live in `test_method_consistency.py` from
  Phase 3 / 4.1.
- **Caching of `walk_grid` results** — at 18 min for the full grid,
  a one-time run plus pickle is cheaper than a caching layer. Defer
  unless the deliverable notebooks need re-runs in the same session.

## Verification

```
HEAD before this pass:  da4387210480de20820945dee8dd5a34cbbb3f95
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
86 passed in 2.30s
$ ruff check src/ tests/ notebooks/
All checks passed!
```

The +14 passing tests over Phase 4.1 are 2 t_obs axis tests on
scan_grid and 12 classifier tests in `test_regime_map.py` (corrected
in Phase 5.1 — the original note conflated subsections of
`test_regime_map.py` and miscounted scan_grid additions). Skipped
count remains at 0.

## Cross-references

- breakout-note §5 — parameter scan; Phase 5 owns all four axes.
- breakout-note §5.1 — regime classification; the round-4 fix
  (sedimented requires both criteria) is pinned in
  `test_classify_thresholds_sedimented_requires_both_criteria`.
- breakout-note §6 — deliverables 3 (regime-map figure) and 5
  (design table); both are notebook outputs deferred to Phase 6.
- Phase 2.5 lab note — `scan_grid.py` centralisation; t_obs is the
  fourth axis it now owns.
- Phase 4.1 lab note — `top_to_bottom_ratio` log-linear extrapolation
  is what gives the regime classifier exact c(h)/c(0) values from
  Method C profiles.

## Next session

Phase 6 — deliverable notebooks. `notebooks/02_regime_map.py` to
produce the deliverable-3 figure (regime grid coloured by classification
across (r, h) at fixed (T, t_obs) slices). Subsequent notebooks
03/04 for the parameter-scan plots and the deliverable-5 design
table.

## Errata

Four wording / arithmetic corrections to this note's first revision
are addressed in
[`2026-04-27-phase5-1-review-driven-fixes.md`](2026-04-27-phase5-1-review-driven-fixes.md):
the "log-spaced" misnomer for the t_obs axis, an over-broad
"Methods A/B/C" claim that didn't match the code (the regime walker
composes A and C; B remains as a Phase-3 cross-validation harness),
the homogeneous short-circuit's reported bottom-mass fraction (now
the analytic equilibrium value rather than the 0.05 layer-fraction
constant), and the test-count breakdown above.
