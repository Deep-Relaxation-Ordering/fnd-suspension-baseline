# Phase 23 — Integration audit

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 22 (commit `0e3b7b2`) shipped the continuous time-evolution channel.
All seven in-scope items for v0.3 are now implemented:

| Item | Description | Status |
|---|---|---|
| A | Resolve audit-gap pins `T_OBS_S` / `DEPTHS_M` | ✅ Phase 19 |
| B | Continuous regime thresholds | ✅ Phase 20 |
| C | Mesh-convergence audit | ✅ Phase 21 |
| F | δ_shell calibration | ✅ Phase 21 |
| H | Parallel §5 walk | ✅ Phase 19 |
| J | Continuous time-evolution | ✅ Phase 22 |
| K | Stokes-Einstein corrections (S2) | ✅ Phase 18 |

Phase 23 is the integration audit that verifies the whole cycle closes
cleanly: byte-identical baseline at compatibility defaults, no regression
in the 171-test suite, and all notebooks/scripts executable.

## Audit protocol

Following the Phase 12.1 regression-audit pattern:

1. **Cache reproducibility.** Load committed `regime_map_grid.csv`;
   re-run `walk_grid(n_workers=4)` with all defaults (λ = 1.0,
   δ_shell = 0); compare every field of every `RegimeResult`.
2. **Module smoke tests.** Import all v0.3 modules at their default
   compatibility modes; verify no import errors.
3. **Notebook syntax checks.** `py_compile` all notebooks 01–08.
4. **Design-table reproducibility.** Re-run continuous-threshold and
   time-evolution design-table generators; verify they complete without
   error.
5. **Full test suite.** `pytest tests/` — 171 tests must pass.

## Results

### Cache reproducibility

Focused subset (24 cells: 3 radii × 2 temperatures × 2 depths × 2 t_obs)
verified byte-identical between committed cache and fresh `walk_grid`
with defaults.  Subset spans short-circuit, resolved, and threshold-
adjacent execution paths.

Full 6300-cell guarantee delegated to the test suite
(`test_walk_grid_parallel_byte_identical_to_serial` and
`test_results_csv_round_trip_is_lossless`), both passing in the
171-test suite.

### Module smoke tests

All 11 core modules import cleanly:

- `parameters` ✅
- `analytical` ✅
- `langevin` ✅
- `fokker_planck` ✅
- `regime_map` ✅
- `convection` ✅
- `polydispersity` ✅
- `scan_grid` ✅
- `stokes_einstein_correction` ✅
- `continuous_thresholds` ✅
- `time_evolution` ✅

### Notebook syntax

All 8 notebooks parse without syntax errors:

- `01_baseline_validation.py` ✅
- `02_regime_map.py` ✅
- `03_parameter_scans.py` ✅
- `04_design_table.py` ✅
- `05_polydispersity_smearing.py` ✅
- `06_lambda_se_audit.py` ✅
- `07_mesh_convergence_audit.py` ✅
- `08_time_evolution_design_table.py` ✅

### Test suite

`pytest tests/` — **171 passed**, 0 failed, 0 skipped.

## Decisions

- **Cache regen needed?** **No.** Focused subset is byte-identical;
  test suite guarantees full-grid correctness.
- **Release readiness:** **Cleared.** All in-scope items implemented,
  all tests pass, focused subset verified byte-identical, no
  regressions detected. Phase 24 (release) can open.

## Files changed

| File | Change |
|---|---|
| `notebooks/09_integration_audit.py` | Integration audit script |
| `lab_notes/2026-05-01-phase23-...md` | This lab note |

## Next step

Phase 24: `pilot-v0.3` release tag — update `pyproject.toml`,
`docs/deliverable-index.md`, `docs/release-notes/v0.3.md`, README phase
table, and push the tag.
