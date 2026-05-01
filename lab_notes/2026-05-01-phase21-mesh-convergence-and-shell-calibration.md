# Phase 21 — Mesh-convergence audit + δ_shell literature calibration

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 20 (commit `f0996d2`) shipped continuous regime thresholds
(`src/continuous_thresholds.py`).  Phase 21 is the audit-and-docs phase:
item C (mesh-convergence audit) and item F (δ_shell calibration).

## Item C — Mesh-convergence audit

### What was done

Ran `notebooks/07_mesh_convergence_audit.py` on 5 focus cells spanning
the threshold-adjacent regime (cells where the 120-cell first pass is
known to sit close to a §5.1 boundary):

| Cell | r (m) | h (m) | t_obs (s) | Method C? |
|---|---|---|---|---|
| Phase-5 regression | 2.41e-8 | 1e-2 | 600 | Yes |
| High-Pe transient | 1e-7 | 1e-4 | 60 | Yes |
| Stratified resolved | 1e-7 | 1e-3 | 60 | Yes |
| Homogeneous corner | 5e-9 | 1e-4 | 3600 | No (short-circuit) |
| Cold-T homogeneous | 5e-9 | 1e-3 | 3600 | No (short-circuit) |

Mesh resolutions: 30, 60, 120, 240, 480, 960 cells.

### Key findings

**bmf converges faster than ratio.**

| Cell | 120→240 bmf drift | 120→240 ratio drift | 240→960 ratio drift |
|---|---|---|---|
| Phase-5 regression | 9.3e-08 (0.0 %) | 8.3e-03 (0.8 %) | 1.0e-03 (0.1 %) |
| High-Pe transient | 2.4e-05 (0.0 %) | 3.7e-02 (3.7 %) | 3.9e-03 (0.4 %) |
| Stratified resolved | 2.4e-05 (0.0 %) | 3.7e-02 (3.7 %) | 3.9e-03 (0.4 %) |

- **bmf** is machine-precision stable from 30 cells upward (< 0.006 % drift).
- **ratio** needs the 240-cell refinement to drop below 1 % drift.
- The 120-cell first pass is sufficient for bmf-based classification
  (sedimented boundary at `bmf = 0.95`).
- The 240-cell refinement is justified for ratio-based classification
  (homogeneous boundary at `ratio = 0.95`).

**No Phase 21.1 escalation needed.** Drift is well below the 1 % empirical
tolerance for all observables at the refinement resolution.

### Honest deferral

Short-circuit cells (homogeneous / equilibrated corners) were skipped for
n_cells > 120 because `solve_cell` bypasses the short-circuit logic and
would run an expensive `expm_multiply` on a profile that is already
analytically known. The audit script detects these cells via a
`_cell_uses_method_c` pre-check.

### Script

`notebooks/07_mesh_convergence_audit.py` — produces
`notebooks/data/mesh_convergence_audit.csv` (gitignored).

## Item F — δ_shell literature calibration

### What was done

Surveyed open-literature DLS measurements for functionalised FND
hydrodynamic radii.  Source: manufacturer data sheets (Adámas, PlasmaChem)
and peer-reviewed DLS studies.

### Key findings

| FND class | r_material (nm) | r_hydro (nm) | δ_shell (nm) | Confidence |
|---|---|---|---|---|
| Bare / oxidised | 25 (TEM typical) | 35 | 10 | Low — high batch variance |
| Carboxylated | 25 | 40 | 15 | Low — depends on COOH density |
| Hydroxylated | 25 | 30 | 5 | Very low — sparse data |
| PEG (dense brush) | 25 | 50 | 25 | Moderate — PEG2000 ~8 nm |
| PEG (sparse) | 25 | 35 | 10 | Low — depends on grafting density |

**Critical caveat:** DLS hydrodynamic diameter for non-spherical FNDs
measures the major axis, not the Stokes-equivalent sphere. For a 3:1
prolate ellipsoid, the effective Stokes radius is ~24 % of the DLS
diameter (not 50 %). This is a **significant correction** for drag and
diffusivity calculations.

**Resolution path:** When the experimental campaign identifies its FND
batch, run DLS on that batch in the same buffer as the tracking
experiment. Compare TEM material radius with DLS hydrodynamic radius.
The difference is the calibrated δ_shell.

### Document

`docs/delta_shell_calibration.md` — full survey with sources and audit-gap
pin language.

## Files changed

| File | Change |
|---|---|
| `.gitignore` | Add `notebooks/*_audit.csv` and `notebooks/data/*_audit.csv` |
| `notebooks/07_mesh_convergence_audit.py` | Mesh-convergence audit script |
| `docs/delta_shell_calibration.md` | δ_shell literature survey and provisional defaults |

## Next step

Phase 22: Item J — continuous time-evolution channel (root-find on Method-C
output for the time at which a fixed criterion is crossed).
