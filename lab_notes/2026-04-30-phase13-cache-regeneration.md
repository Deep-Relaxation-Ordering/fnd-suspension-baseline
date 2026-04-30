# 2026-04-30 — Phase 13: cache regeneration and convection overlays

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 12.1 proved that the current `notebooks/data/regime_map_grid.csv`
was byte-identical to the post-9.3 baseline cache at `94b102a`, and
that current `results_from_csv(...)` loads it as a zero-shell,
all-False-convection compatibility cache. Phase 13 therefore migrated
that proven cache through the current CSV writer instead of spending
~150 min recomputing identical cells.

## Cache migration

Command:

```text
$ PYTHONPATH=src .venv/bin/python - <<'PY'
from pathlib import Path
from regime_map import results_from_csv, results_to_csv
path = Path('notebooks/data/regime_map_grid.csv')
results = results_from_csv(path)
results_to_csv(results, path)
print(f'migrated {len(results)} rows to {path}')
PY
migrated 6300 rows to notebooks/data/regime_map_grid.csv
```

The cache now uses the Phase-12+ schema:

```text
r_material_m,r_hydro_m,delta_shell_m,temperature_kelvin,sample_depth_m,t_obs_s,regime,top_to_bottom_ratio,bottom_mass_fraction,used_homogeneous_short_circuit,used_equilibrated_short_circuit,used_method_c_fallback,convection_flag
```

Added
`tests/test_regime_map.py::test_committed_regime_map_cache_uses_v02_zero_shell_schema`
to pin:

- current cache header is the v0.2 schema;
- `radius_m` is no longer persisted;
- row count is 6300;
- `convection_flag` is all-False in compatibility mode;
- `delta_shell_m = 0.0`;
- `r_material_m == r_hydro_m == radius_m` via the compatibility
  property for every row.

## Diff audit

Compared the migrated cache to `94b102a` via `git show`:

```text
rows_compared=6300
label_and_numeric_channels_string_equal=True
zero_shell_columns_match_legacy_radius=True
cache_convection_flag_all_false=True
```

The label and numeric channels are string-equal to the post-9.3
baseline. The only intentional cache changes are the explicit radius
schema and the all-False `convection_flag` column.

## Notebook updates

Notebook 02 now renders a room-temperature regime-map overlay with
the experimental convection side channel at
`DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1 K`:

- `notebooks/figures/02_regime_map/regime_map_room_T_1h_convection_overlay.png`

Notebook 03 now renders the `(T, h)` convection mask at the same
experimental convention:

- `notebooks/figures/03_parameter_scans/convection_flag_vs_T_h.png`

Notebook 04 remains compatibility-mode and the design-table CSV /
Markdown outputs are unchanged.

## Notebook smoke

```text
$ MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python notebooks/01_baseline_validation.py
notebook 01 complete; figures written to .../notebooks/figures/01_baseline_validation

$ MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python notebooks/02_regime_map.py
loaded 6300 cells from cache: .../notebooks/data/regime_map_grid.csv
axes: r=30, T=7, h=5, t_obs=6  (total = 6300)
regime distribution: {'homogeneous': 1158, 'stratified': 2301, 'sedimented': 2841}
notebook 02 complete; figures written to .../notebooks/figures/02_regime_map

$ MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python notebooks/03_parameter_scans.py
loaded grid (30, 7, 5, 6) from .../notebooks/data/regime_map_grid.csv
notebook 03 complete; figures written to .../notebooks/figures/03_parameter_scans

$ MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python notebooks/04_design_table.py
loaded grid (30, 7, 5, 6) (6300 cells)
notebook 04 complete; tables written under .../notebooks/data
```

The Matplotlib `FigureCanvasAgg is non-interactive` warnings are
expected in headless smoke runs.

## Verification

```text
$ .venv/bin/python -m pytest tests/test_regime_map.py
26 passed

$ .venv/bin/python -m pytest
123 passed

$ .venv/bin/python -m ruff check .
All checks passed!

$ git diff --check
(no output)
```

## Decision

Phase 13 is complete. The cache is in v0.2 schema, compatibility-mode
columns are unchanged relative to `94b102a`, notebooks 02 / 03 expose
the experimental convection overlays, and notebook 04's design table is
unchanged. Phase 14 can start.

## Cross-references

- [`docs/work-plan-v0-2.md`](../docs/work-plan-v0-2.md)
- [`2026-04-30-phase12-1-regression-audit.md`](2026-04-30-phase12-1-regression-audit.md)
