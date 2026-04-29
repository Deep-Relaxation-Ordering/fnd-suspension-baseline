# 2026-04-29 — Phase 12: radius schema and CSV parser checkpoint

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

The Phase 11 review identified one design trap to fix before the
hydrodynamic-vs-material radius split spreads through Method A/B/C:
legacy regime-map CSV parsing must survive three cache schemas:

1. v0.1 rows with `radius_m` and no `convection_flag`;
2. Phase 11 rows with `radius_m` plus `convection_flag`;
3. Phase 12+ rows with explicit `r_material_m`, `r_hydro_m`,
   `delta_shell_m`, and `convection_flag`.

This checkpoint lands the data-model surface and parser before the
larger wrapper refactor. It intentionally leaves the physics call sites
in compatibility mode (`delta_shell_m = 0.0`) until the next Phase 12
slice.

## Changes

### `src/parameters.py`

Added frozen `ParticleGeometry`:

- `r_material_m` is the radius that sets buoyant mass and equilibrium
  quantities.
- `delta_shell_m` is non-negative and defaults to zero.
- `r_hydro_m = r_material_m + delta_shell_m` is the radius that will
  set Stokes drag and Stokes-Einstein diffusivity.
- `radius_m` and `from_radius(...)` provide v0.1-compatible aliases.

### `src/regime_map.py`

`RegimeResult` now persists explicit radius fields:

- `r_material_m`
- `r_hydro_m`
- `delta_shell_m`

The old Python `radius_m` attribute remains as a compatibility property
equal to `r_material_m`; it is no longer a persisted CSV field for new
rows.

CSV parsing now uses `_detect_csv_format(header)` with frozen legacy
headers:

- `_V01_CSV_FIELDS`
- `_PHASE11_CSV_FIELDS`
- `_CSV_FIELDS` for the current Phase 12+ schema

Legacy `radius_m` rows map to
`r_material_m = r_hydro_m = radius_m` and `delta_shell_m = 0.0`.
Missing v0.1 `convection_flag` values map to `False`.

`RegimeGrid.radii` remains the material-radius coordinate axis for
notebook compatibility. `RegimeGrid.r_material` aliases it, and
`RegimeGrid.r_hydro` is an aligned per-cell channel.

### Tests

Added `tests/test_hydrodynamic_split.py` for the initial
`ParticleGeometry` invariants and extended `tests/test_regime_map.py`
to pin:

- current CSV round-trip of explicit radii;
- v0.1 CSV back-compat;
- Phase 11 CSV back-compat;
- `_detect_csv_format(...)` for all three supported schemas;
- `RegimeGrid.radii` stability and aligned `r_hydro` values.

## Verification

```text
$ .venv/bin/python -m pytest tests/test_hydrodynamic_split.py tests/test_regime_map.py
29 passed

$ .venv/bin/python -m pytest
115 passed

$ .venv/bin/python -m ruff check .
All checks passed!

$ git diff --check
(no output)
```

## Cross-references

- [`docs/work-plan-v0-2.md`](../docs/work-plan-v0-2.md)
- [`2026-04-29-phase11-1-review-fixes.md`](2026-04-29-phase11-1-review-fixes.md)

## Next slice

Propagate `ParticleGeometry` through `parameters.py` primitives and the
Method-A `_geom` primaries, keeping the scalar-radius public wrappers
unchanged for v0.1 callers.
