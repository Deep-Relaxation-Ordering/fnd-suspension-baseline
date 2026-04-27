# 2026-04-27 — Phase 4: Method C (Smoluchowski finite volume)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 4 of the breakout-note timeline (§9): implement Method C, the
overdamped Smoluchowski / Fokker-Planck PDE solver. This closes the five
remaining §4.4 skipped tests left after Method B.

## What was done

### `src/fokker_planck.py`

Implemented:

- `FokkerPlanckResult` with profile arrays, provenance fields, mass,
  probabilities, mean height, variance, top/bottom ratio, and bottom-layer
  mass fraction.
- `bernoulli(x)` and `sg_flux_coefficients(D, v_sed, dx)` for the
  Scharfetter-Gummel interface flux
  `J = a_left c_left + a_right c_right`.
- `make_mesh(h, ell_g)` with uniform cells when possible and exponential
  refinement toward `z = 0` when the bottom boundary layer needs it.
- `build_operator(edges, D, v_sed)` as a conservative finite-volume
  operator with no-flux boundaries.
- `solve(...)` and `solve_cell(...)` for time-dependent Method-C profiles
  from the canonical uniform initial condition.
- `equilibrium_cell(...)` as a long-time Method-C equilibrium wrapper.
- Asymptotic-sedimentation fallback for unresolved high-Pe cells whose
  `ell_g / 5` is below the configured mesh floor (`1 nm`). Before
  `h / v_sed`, the fallback keeps the finite-time pure-sedimentation
  transient; after arrival, it reports the narrow barometric equilibrium.

### `tests/test_method_consistency.py`

Un-skipped and replaced all five Method-C placeholders:

- Method B ↔ Method C time-dependent mean and variance agree inside
  Method B's feasibility envelope.
- Method A ↔ Method C equilibrium agrees outside Method B's envelope via
  the high-r asymptotic fallback.
- Scharfetter-Gummel high-Pe limit reduces to drift upwind.
- Scharfetter-Gummel low-Pe limit reduces to central drift-diffusion.
- Asymptotic-sedimentation fallback is explicitly tagged rather than
  silently meshing a sub-nanometric layer.
- The finite-time high-Pe fallback is not prematurely treated as fully
  sedimented before `h / v_sed`.

Added one extra mesh-regression check: when a uniform mesh would be too
coarse, `make_mesh` refines toward the bottom and resolves `ell_g / 5`.

## Decisions

| Decision | Rationale |
|---|---|
| Use `scipy.sparse.linalg.expm_multiply` for the linear ODE | Deterministic, no CFL tuning in Method C tests, and mass conservation stays tied to the finite-volume operator. |
| Keep the initial condition fixed to `"uniform"` for now | This is the canonical §5.1 regime-map initial condition; alternative preparations can be added later with explicit tests. |
| Fallback threshold is `ell_g / 5 < 1 nm` | Matches the round-4 requirement to avoid pretending to resolve sub-nanometric layers on a practical mesh. |
| Report fallback results as tagged Method-C outputs | Downstream regime-map code can branch on `used_asymptotic_fallback` instead of inferring from mesh shape. |

## Verification

```
$ PYTHONPATH=src pytest -q
70 passed in 1.81s
$ ruff check src/ tests/ notebooks/
All checks passed!
```

The skipped-test count is now zero. The remaining project work is not
validation infrastructure; it is orchestration and deliverable generation.

## What is not done

- `regime_map.py` is still a stub. It should now compose Methods A/C
  across the §5 grid and use Method B only where the feasibility envelope
  says it is useful for cross-validation.
- The `t_obs` axis still needs to move into `scan_grid.py` when regime-map
  orchestration lands.
- No notebook 02–04 outputs were generated in this phase.

## Next session

Phase 5 — regime-map orchestration and deliverables 3 / 5: full
`(r, T, h, t_obs)` classification, design table, and scan notebooks.
