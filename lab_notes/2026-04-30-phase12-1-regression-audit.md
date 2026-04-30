# 2026-04-30 — Phase 12.1: regression audit

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 12 split material and hydrodynamic radii while keeping
`delta_shell_m = 0.0` as the compatibility default. This audit checks
the forward-compatibility contract against the post-9.3 baseline commit
`94b102aa1838c957bb6189ccdfb622f90423b4b6`.

## Added gap-closing test

Added `test_regime_result_carries_both_radii_through_csv` to
`tests/test_hydrodynamic_split.py`. It classifies a cell with
`delta_shell_m != 0`, writes it through `results_to_csv(...)`, reads it
back through `results_from_csv(...)`, and asserts that
`r_material_m`, `r_hydro_m`, and `delta_shell_m` survive bit-exactly
and remain distinct.

## Baseline-suite audit

Created a detached worktree at `../fnd-baseline-94b102a`:

```text
$ git worktree add --detach ../fnd-baseline-94b102a 94b102a
HEAD is now at 94b102a Phase 9.3: adversarial review fixes (threshold refinement, CI, validity envelope)
```

Then ran the baseline tests unchanged against the current `src`:

```text
$ PYTHONPATH=/Users/uwarring/Documents/GitHub/fnd-suspension-baseline/src .venv/bin/python -m pytest ../fnd-baseline-94b102a/tests
94 passed
```

This pins that the post-9.3 pre-v0.2 suite still passes at the v0.2
defaults (`delta_shell_m = 0.0`, `delta_T_assumed = 0.0 K`).

## Snapshot audit

Compared the notebook-01 anchor cell
`cell_summary(radius_m=1e-7, temperature_kelvin=298.15, sample_depth_m=1e-3)`
between `94b102a` and current `main`. The 15 keys common to both
schemas match exactly / within the `rtol <= 1e-15` contract. Current
`cell_summary(...)` adds the intentional radius keys
`r_material_m`, `r_hydro_m`, and `delta_shell_m`.

The §5 cache was also checked:

```text
anchor_common_keys=15
cache_rows=6300
cache_file_byte_identical=True
legacy_cache_loaded_with_zero_shell=True
```

The current `notebooks/data/regime_map_grid.csv` is byte-identical to
the `94b102a` cache. Loading the baseline cache with current
`results_from_csv(...)` maps every row to
`r_material_m = r_hydro_m = radius_m`, `delta_shell_m = 0.0`, and
`convection_flag = False`, with labels and numeric channels preserved.

## Verification

```text
$ .venv/bin/python -m pytest tests/test_hydrodynamic_split.py tests/test_regime_map.py
36 passed

$ .venv/bin/python -m pytest
122 passed

$ .venv/bin/python -m ruff check .
All checks passed!

$ git diff --check
(no output)
```

## Decision

Phase 12.1 is complete. The v0.2 radius split satisfies the
compatibility contract at `delta_shell_m = 0.0`; Phase 13 can start.

## Cross-references

- [`docs/work-plan-v0-2.md`](../docs/work-plan-v0-2.md)
- [`2026-04-29-phase12-radius-schema-parser.md`](2026-04-29-phase12-radius-schema-parser.md)
- [`2026-04-29-phase12-physics-propagation.md`](2026-04-29-phase12-physics-propagation.md)
