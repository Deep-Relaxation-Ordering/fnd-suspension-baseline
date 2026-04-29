# 2026-04-29 — Phase 12: radius-split physics propagation

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

The previous Phase 12 checkpoint landed the explicit radius schema and
the three-format CSV parser. This slice propagates `ParticleGeometry`
through the physics primitives and convenience wrappers while preserving
the v0.1 scalar call style.

## Changes

### `src/parameters.py`

Added explicit geometry-aware primitives:

- `gamma_stokes_geom(geom, T)` uses `geom.r_hydro_m`.
- `diffusivity_geom(geom, T)` uses `geom.r_hydro_m`.
- `buoyant_mass_geom(geom, T, rho_p)` uses `geom.r_material_m`.
- `as_particle_geometry(...)` coerces scalar radii to zero-shell
  geometry objects.

The existing `gamma_stokes(...)`, `diffusivity(...)`, and
`buoyant_mass(...)` names now accept either a scalar radius or
`ParticleGeometry`; scalar inputs remain v0.1-compatible.

### `src/analytical.py`

Added Method-A `_geom` primaries:

- `scale_height_geom`
- `settling_velocity_geom`
- `equilibration_time_geom`
- `settling_time_geom`
- `top_to_bottom_ratio_geom`
- `barometric_profile_geom`
- `cell_summary_geom`

The unsuffixed Method-A functions remain scalar-radius wrappers.
`cell_summary(...)` now includes `r_material_m`, `r_hydro_m`, and
`delta_shell_m`, while retaining `r_m == r_material_m` as the
compatibility alias.

### Method B/C and regime map

`langevin.simulate_cell(...)`, `fokker_planck.solve_cell(...)`,
`fokker_planck.equilibrium_cell(...)`, and
`regime_map.classify_cell(...)` now accept `float | ParticleGeometry`.
Each coerces once at the boundary and then uses the geometry-aware
physics functions. `classify_cell(...)` records the explicit geometry
fields in `RegimeResult`.

## Physics checks

The hydrodynamic split tests now pin the core invariants:

- doubling `r_hydro_m` at fixed `r_material_m` doubles Stokes drag;
- doubling `r_hydro_m` halves diffusivity and settling velocity;
- scale height and buoyant mass are unchanged by `delta_shell_m`;
- equilibrium barometric profiles are unchanged by `delta_shell_m`;
- relaxation time doubles when `r_hydro_m` doubles because the length
  scale is material-radius controlled while diffusivity halves;
- Method B/C wrappers and `classify_cell(...)` accept
  `ParticleGeometry` and use / record the hydrodynamic channel.

## Verification

```text
$ .venv/bin/python -m pytest tests/test_hydrodynamic_split.py tests/test_analytical.py tests/test_einstein_relation.py tests/test_langevin.py tests/test_method_consistency.py tests/test_regime_map.py
89 passed

$ .venv/bin/python -m pytest
121 passed

$ .venv/bin/python -m ruff check .
All checks passed!
```

## Cross-references

- [`docs/work-plan-v0-2.md`](../docs/work-plan-v0-2.md)
- [`2026-04-29-phase12-radius-schema-parser.md`](2026-04-29-phase12-radius-schema-parser.md)

## Next slice

Complete the Phase 12 regression audit: compare compatibility-mode
outputs against the post-9.3 baseline, then decide whether
`RegimeResult.from_radius(...)` is useful as a convenience bridge for
external ad-hoc scripts that previously constructed rows directly.
