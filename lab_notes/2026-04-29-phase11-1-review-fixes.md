# 2026-04-29 — Phase 11.1: review fixes and Phase-12 data-model amendments

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Review after Phase 11 accepted the Rayleigh side-channel implementation
but flagged several risks before Phase 12 starts. The highest-risk item
was the hydrodynamic-vs-material radius split: a single `radius_m` field
is ambiguous once `delta_shell_m != 0`, and `cell_summary` would report
drag / diffusion values that no longer match the lone radius key.

This pass applies the low-risk Phase 11 fixes and amends the accepted
work plan so Phase 12 has an explicit data model before implementation.

## Code fixes

### `src/convection.py`

`rayleigh_number` now rejects `sample_depth_m <= 0`, matching the rest
of the cell APIs' positive-depth convention.

### `tests/test_convection.py`

Added:

- `test_rejects_nonpositive_depth`
- `test_alpha_matches_iapws95_sanity_values`

The IAPWS-95 values are a loose independent sanity check at 5 / 25 /
35 °C and 0.101325 MPa. Tanaka remains the implementation source of
truth because it is already used by `parameters.rho_water`.

## Work-plan amendments

### Phase 12 radius schema

Phase 12 now requires explicit `r_material_m` and `r_hydro_m` in the
cache and public summaries:

- `r_material_m` drives buoyant mass, scale height, equilibrium
  profiles, top/bottom ratio, and bottom-mass fraction.
- `r_hydro_m` drives Stokes drag, diffusivity, settling velocity, and
  relaxation / settling times.
- `delta_shell_m` is recorded where row-level summaries could otherwise
  look inconsistent.
- `radius_m` / `r_m` survive only as compatibility aliases for
  `r_material_m` through v0.2.

`cell_summary` must gain `r_material_m`, `r_hydro_m`, and
`delta_shell_m`; `gamma_N_s_per_m` and `D_m2_per_s` must be checked
against `r_hydro_m`.

### Forward-compatibility tolerance

The old "bit-identical" wording was too brittle for a wrapper refactor.
The amended contract is exact equality for labels / booleans / integer
path codes and machine-precision equality for numeric channels.

### Phase 14 ownership and truncation handling

`SIGMA_GEOM_AXIS` is now owned by `src/polydispersity.py`, not
`src/scan_grid.py`, because polydispersity is post-processing rather
than a §5 scan axis. The deliverable-6 table must expose
`truncation_loss` and mark rejected cells explicitly instead of leaving
gaps.

### Phase 13 notebook work

The work plan no longer describes Phase 13 as a pure mechanical rerun.
Notebook 02 / 03 edits are required for the experimental convection
overlays.

### Second-pass Phase 12 decisions

The second review pass tightened the implementation strategy before
Phase 12 starts:

- `results_from_csv` gets a dedicated `_detect_csv_format(header)`
  helper covering all three cache formats: v0.1 (`radius_m`, no
  `convection_flag`), Phase 11 (`radius_m` plus `convection_flag`),
  and Phase 12+ (`r_material_m`, `r_hydro_m`, `delta_shell_m`, plus
  `convection_flag`).
- `RegimeGrid.radii` remains the field name and is documented as the
  material-radius coordinate axis. New `r_material` / `r_hydro`
  aliases or channels may be added without breaking notebooks 02-04.
- `analytical.py` uses explicit `_geom` suffixed primaries
  (`scale_height_geom`, `settling_velocity_geom`, etc.) and keeps
  the existing unsuffixed functions as scalar-radius wrappers.
- `classify_cell` accepts `float | ParticleGeometry` in its first
  positional parameter, with `@overload` typing and one internal
  coercion step.

## Decisions

| Decision | Rationale |
|---|---|
| Carry both radii in cache rows | Prevents downstream consumers from recomputing drag with the material radius. |
| Keep `r_m` / `radius_m` only as compatibility aliases | Maintains v0.1 ergonomics while making new code unambiguous. |
| Machine-precision numeric regression tolerance | Avoids false failures from harmless wrapper evaluation-order changes. |
| `SIGMA_GEOM_AXIS` lives in `polydispersity.py` | Keeps `scan_grid.py` scoped to normative §5 axes. |
| Design tables mark truncation rejects | Avoids silent gaps near the §5 radius-axis boundaries. |
| Use `_detect_csv_format` for cache parsing | Makes the three cache formats explicit and testable. |
| Keep `RegimeGrid.radii` stable | Avoids needless notebook churn while documenting material-radius semantics. |
| Use `_geom` Method-A primaries plus scalar wrappers | Keeps geometry-aware code explicit without breaking v0.1 callers. |

## Verification

```text
$ .venv/bin/python -m pytest tests/test_convection.py
12 passed

$ .venv/bin/python -m pytest
109 passed

$ .venv/bin/python -m ruff check .
All checks passed!

$ git diff --check
(no output)
```

## Cross-references

- [`docs/work-plan-v0-2.md`](../docs/work-plan-v0-2.md)
- [`2026-04-29-phase11-rayleigh-convection-gate.md`](2026-04-29-phase11-rayleigh-convection-gate.md)

## Next session

Phase 12 can start from the explicit radius schema above. The first
implementation step should be `ParticleGeometry` plus wrapper tests
before touching Method A/B/C call sites.
