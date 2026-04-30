# 2026-04-30 — Phase 14: polydispersity smearing and deliverable 6

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 14 adds log-normal particle-size polydispersity as a
post-processing layer on the v0.2 §5 cache. The cache remains the sharp
material-radius reference; `src/polydispersity.py` integrates over the
§5 radius bins using exact CDF differences in log-radius space.

## Implementation

### `src/polydispersity.py`

Added:

- `SIGMA_GEOM_AXIS = (1.05, 1.10, 1.20, 1.40, 1.60)`.
- `lognormal_pdf(...)` and `lognormal_cdf(...)`.
- `SmearedGrid`, carrying probability channels over
  `(r_geom_mean, sigma_geom, T, h, t_obs)`.
- `lognormal_smear(...)`, which:
  - defaults `r_geom_mean_axis` to `grid.r_material`;
  - builds geometric bin edges from the §5 radius axis;
  - computes log-normal bin masses by CDF subtraction;
  - accumulates `p_homogeneous`, `p_stratified`, and `p_sedimented`;
  - renormalises by covered mass so accepted cells conserve
    probability to machine precision;
  - records `truncation_loss` and an `accepted` mask;
  - raises in strict mode when covered mass is below 95 %.

No σ axis was added to `scan_grid.py`; polydispersity remains
post-processing, not a §5 scan axis.

### Tests

Added `tests/test_polydispersity.py`, covering:

- CDF median sanity.
- The pinned `SIGMA_GEOM_AXIS`.
- Degenerate limit against a sharp §5 label vector.
- Probability conservation over every accepted cell.
- Strict truncation rejection and mask-mode diagnostics.
- Anchored regression values for homogeneous, stratified, and
  sedimented preparations as `sigma_geom` broadens.
- Rejection for geometric means outside the §5 support.

Also folded in two Phase-13 review polish items:

- `test_committed_regime_map_cache_uses_v02_zero_shell_schema` now
  reads the header with `csv.reader`, matching production parsing.
- The notebook-02 convection hatch helper no longer carries an unused
  radius-axis argument.

## Notebook 05

Added `notebooks/05_polydispersity_smearing.py`.

Generated figures:

- `notebooks/figures/05_polydispersity/probabilistic_regime_rgb_room_T_1mm_1h.png`
- `notebooks/figures/05_polydispersity/sigma_sensitivity_100nm_room_T_1mm_1h.png`
- `notebooks/figures/05_polydispersity/p_stratified_suitability_room_T_1mm_1h.png`

The notebook writes deliverable 6:

- `notebooks/data/design_table_polydispersity_room_T.csv`
- `notebooks/data/design_table_polydispersity_room_T.md`

The table summarises, at 25 °C and `t_obs = 1 h`, the geometric-mean
radius interval satisfying `p_stratified >= 0.8` for each
`(h, sigma_geom)` row. Rows with radius samples rejected by the 5 %
truncation gate are marked `partial_rejected_truncation` and include
`max_truncation_loss` plus a rejected-count diagnostic.

## Verification

```text
$ .venv/bin/python -m pytest tests/test_polydispersity.py tests/test_regime_map.py
36 passed

$ MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python notebooks/05_polydispersity_smearing.py
loaded grid (30, 7, 5, 6) from .../notebooks/data/regime_map_grid.csv
smeared shape: (30, 5, 7, 5, 6) (r_geom_mean, sigma_geom, T, h, t_obs)
sigma_geom axis: (1.05, 1.1, 1.2, 1.4, 1.6)
wrote .../notebooks/data/design_table_polydispersity_room_T.csv
wrote .../notebooks/data/design_table_polydispersity_room_T.md
notebook 05 complete; figures written to .../notebooks/figures/05_polydispersity

$ .venv/bin/python -m pytest
133 passed

$ .venv/bin/python -m ruff check .
All checks passed!

$ git diff --check
(no output)
```

## Decision

Phase 14 is complete. The §5 cache now supports probabilistic
classification for log-normal preparations, deliverable 6 is committed,
and Phase 15 release closeout can start.

## Cross-references

- [`docs/work-plan-v0-2.md`](../docs/work-plan-v0-2.md)
- [`2026-04-30-phase13-cache-regeneration.md`](2026-04-30-phase13-cache-regeneration.md)
