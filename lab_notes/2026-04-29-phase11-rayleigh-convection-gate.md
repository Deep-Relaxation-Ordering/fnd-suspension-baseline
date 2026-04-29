# 2026-04-29 — Phase 11: Rayleigh-number convection gate

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

First implementation phase of the accepted `pilot-v0.2` work plan. The
goal is to add a Rayleigh-number side channel that marks cells where
buoyancy-driven convection would invalidate the 1-D diffusion /
sedimentation assumption, without changing the §5.1 regime label.

The accepted work plan resolves the D1 default split as:

- API / cache compatibility mode: `delta_T_assumed = 0.0 K`, so
  `convection_flag = False` and v0.1 outputs reproduce exactly.
- Experimental-facing notebook overlays: explicitly pass
  `DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1 K`.

## What was done

### `src/convection.py`

New module for the Rayleigh side channel:

- `RAYLEIGH_CRITICAL_RIGID_RIGID = 1707.762`
- `RAYLEIGH_CRITICAL_RIGID_FREE = 1100.65`
- `WATER_THERMAL_DIFFUSIVITY_M2_PER_S = 1.4e-7`
- `DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1`
- `thermal_expansion_coefficient(T)`
- `rayleigh_number(h, delta_T, T)`
- `is_convection_dominated(Ra, boundary=...)`

The thermal expansion coefficient is derived by analytically
differentiating the same Tanaka (2001) density fit used by
`parameters.rho_water`:

```text
α(T) = -(1 / ρ(T)) · dρ/dT
```

The signed value is intentional. Below the density maximum near 4 °C,
`α < 0`; the code does not take `abs(α)` because that would turn the
water-density anomaly into a false Rayleigh-Bénard flag.

### `src/regime_map.py`

`classify_cell` gained:

```python
delta_T_assumed: float = 0.0
boundary: BoundaryCondition = "rigid-rigid"
```

`RegimeResult` gained:

```python
convection_flag: bool = False
```

`walk_grid` propagates the two new kwargs, and `RegimeGrid` now carries
a `convection_flag` boolean channel alongside `regime`, `ratio`, `bmf`,
and `path`.

The CSV reader now accepts pre-v0.2 cache files that lack the
`convection_flag` column and synthesises `False`. The writer emits the
new field.

### Tests

New `tests/test_convection.py` covers:

- h = 1 mm, ΔT = 1 K, 25 °C: `Ra ≈ 20`, not convective.
- h = 10 mm, ΔT = 1 K, 25 °C: `Ra ≈ 2.0e4`, convective.
- h = 10 mm, ΔT = 0.1 K, 25 °C: `Ra ≈ 2.0e3`, marginally convective.
- h = 10 mm, ΔT = 0.01 K, 25 °C: below threshold.
- strict threshold convention: `Ra == Ra_c` is not dominated.
- rigid-free threshold flips earlier than rigid-rigid.
- Tanaka-derived `α(T)` pins at 5 / 25 / 35 °C.
- 4 °C density-maximum convention: `α(277.15 K)` is tiny and positive;
  `α(275.15 K)` is negative.

`tests/test_regime_map.py` now covers:

- default `convection_flag = False`.
- ΔT = 0.1 K flags a deep cell without changing its §5.1 label or
  stored numerical classification channels.
- `walk_grid` propagates the flag.
- CSV round-trip preserves the flag.
- pre-v0.2 CSVs load with all-False flags.
- `results_to_grid` preserves the flag under input shuffling.

## Decisions

| Decision | Rationale |
|---|---|
| API/cache default is `delta_T_assumed = 0.0 K` | This is the v0.1 compatibility mode and keeps the current cache / tests reproducible. |
| Experimental default constant is `DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1 K` | This is the accepted D1 choice for notebook overlays and experimental consumers. It is explicit at call sites. |
| Default boundary is `"rigid-rigid"` | Closed cuvettes are the controlled default and use the more conservative threshold. |
| `α(T)` is Tanaka-derived | Keeps density and thermal expansion internally consistent. |
| `Ra > Ra_c`, not `>=` | Strict inequality avoids classifying a threshold-exact float as convective. |
| Pre-v0.2 CSVs are accepted | Current committed cache lacks `convection_flag`; consumers should not break before Phase 13 regenerates the cache. |

## Notebook / cache handoff

No cache or figure artefacts were regenerated in this phase. Phase 13
owns the §5 cache re-walk and cache-derived artefact regeneration.

For notebook overlays in Phase 13, the intended call pattern is:

```python
from convection import DEFAULT_EXPERIMENTAL_DELTA_T_K, is_convection_dominated, rayleigh_number

flag = is_convection_dominated(
    rayleigh_number(h, DEFAULT_EXPERIMENTAL_DELTA_T_K, T),
    boundary="rigid-rigid",
)
```

This keeps the persisted compatibility-mode cache all-False while
allowing experimental figures to show the realistic 0.1 K Rayleigh
mask.

## Verification

```text
$ .venv/bin/python -m pytest tests/test_convection.py tests/test_regime_map.py
33 passed

$ .venv/bin/python -m pytest
107 passed

$ .venv/bin/python -m ruff check .
All checks passed!

$ MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python notebooks/02_regime_map.py
notebook 02 complete; figures written to notebooks/figures/02_regime_map

$ MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python notebooks/03_parameter_scans.py
notebook 03 complete; figures written to notebooks/figures/03_parameter_scans
```

## Cross-references

- [`docs/work-plan-v0-2.md`](../docs/work-plan-v0-2.md) — accepted
  v0.2 work plan and D1-D6 decisions.
- [`docs/adr/0001-v0.2-spec-anchoring.md`](../docs/adr/0001-v0.2-spec-anchoring.md)
  — spec-anchoring decision for v0.2.

## Next session

Phase 11.1 review pass, if needed. Main likely review surfaces:

- whether `α(T)` should also be compared numerically against an
  independent IAPWS table in tests or only in prose;
- whether notebook overlays should land before or with Phase 13 cache
  regeneration;
- whether CSV back-compat should remain in Phase 11 or be moved to
  the Phase 13 patch.
