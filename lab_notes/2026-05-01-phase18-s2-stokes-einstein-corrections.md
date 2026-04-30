# Phase 18 — S2: Stokes–Einstein corrections at sub-150-nm radii

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 17 (commits `197ce24`, `9a1ef60`, `92d4022`) accepted the v0.3 work-plan
contract, fixing D1–D9 and clearing S2 (Stokes–Einstein corrections at
sub-150-nm radii) as the first implementation slice.

## What was done

### 1. Core physics change — `lambda_se` parameter

Added the Stokes–Einstein breakdown coefficient `lambda_se` to the
diffusivity primitives in `src/parameters.py`:

- `diffusivity_geom(geom, T, *, lambda_se=1.0)`
- `diffusivity(r_or_geom, T, *, lambda_se=1.0)`

Formula: `D = lambda_se · k_B · T / γ`.  At `lambda_se = 1.0` the
bare continuum SE relation is recovered to machine precision (forward-
compat contract verified).

### 2. Propagation through regime classification

Propagated `lambda_se` through the orchestration layer so that
`classify_cell` and `solve_cell` can run with corrected diffusivity:

- `src/fokker_planck.py`: `solve_cell(..., lambda_se=1.0)`
- `src/regime_map.py`: `classify_cell(..., lambda_se=1.0)`

Existing call sites are unchanged (default preserves v0.2 behaviour).

### 3. Side-computation module

Created `src/stokes_einstein_correction.py` with:

- `LAMBDA_SE_AXIS = (0.1, 0.5, 1.0)`
- `classify_cell_lambda(...)` → returns `(RegimeResult, provisional: bool)`
- `audit_lambda_impact(...)` → maps λ → RegimeResult for one cell
- `count_label_flips(...)` → bool comparison helper

### 4. Audit — regime-label flip prevalence

Ran `notebooks/06_lambda_se_audit.py` on a focused grid (5 radii ≤ 150 nm,
room T, all 5 depths, all 6 t_obs = 150 cells):

| Baseline λ | Corrected λ | Flips | Prevalence |
|---|---|---|---|
| 1.0 | 0.1 | 8 / 150 | **5.3%** |
| 1.0 | 0.5 | 3 / 150 | **2.0%** |

**Interpretation:** Moderate flip rate.  Side-computation remains the
cheap path for v0.3.  A partial §5 cache regen for the sub-150-nm band
is worth evaluating in Phase 18.1 if the design-table sweet spot
overlaps the flipped cells.

### 5. Tests

New test file `tests/test_stokes_einstein_correction.py` (16 tests):

- `test_lambda_one_reproduces_v0_2` — identity at λ = 1.0
- `test_lambda_scales_diffusivity_linearly` — parametrized over 3 radii × 3 λ
- `test_einstein_relation_with_lambda` — D·γ = λ·k_B·T to machine precision
- `test_classify_cell_default_lambda_unchanged` — default path is byte-identical
- `test_classify_cell_with_lambda_changes_diffusivity_path` — λ < 1 steepens profile

Full suite: **151 passed**, zero regressions.

## Decisions recorded

| Decision | Resolution | Rationale |
|---|---|---|
| λ on `ParticleGeometry` or `diffusivity_geom` kwarg | **kwarg** | λ is a transport-physics knob, not geometric |
| §5 scan axis or side-computation | **Side-computation first** | 5.3% flip rate at λ=0.1 is moderate, not dominant |
| Cache schema bump now or defer | **Defer to Phase 18.1** | Audit result does not demand immediate promotion |

## Open questions (for Phase 18.1 or later)

- **Q-18-1.** Does the design-table sweet spot (the radii/depths/t_obs bands
  an experimentalist actually queries) overlap the flipped cells?  The
  audit counted flips across the full focused grid, not weighted by
  experimental relevance.
- **Q-18-2.** Laloyaux z₂ calibration: the audit used the phenomenological
  λ axis {0.1, 0.5, 1.0}.  The actual gold-nanoparticle benchmark may
  suggest a radius-dependent λ(r) rather than a single scalar.  That
  refinement is deferred until the calibration data is loaded.
- **Q-18-3.** `provisional=True` metadata: currently lives on the side-
  computation wrapper, not on `RegimeResult`.  If λ is promoted to a §5
  axis, `RegimeResult` will need a `provisional` field and the CSV round-
  trip will need a backward-compat handler.

## Files changed

| File | Change |
|---|---|
| `src/parameters.py` | `lambda_se` kwarg on `diffusivity_geom` and `diffusivity` |
| `src/fokker_planck.py` | `lambda_se` propagated through `solve_cell` |
| `src/regime_map.py` | `lambda_se` propagated through `classify_cell` |
| `src/stokes_einstein_correction.py` | New side-computation module |
| `tests/test_stokes_einstein_correction.py` | 16 new tests |
| `notebooks/06_lambda_se_audit.py` | Audit script + CSV output |

## Next step

Phase 19: Items A + H (resolve audit-gap pins `T_OBS_S` / `DEPTHS_M` +
parallel §5 walk).
