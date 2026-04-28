# 2026-04-28 — Phase 9.3: adversarial review fixes

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Internal adversarial review found that the Phase-9 findings were mostly
sound, but a few weaknesses should be fixed before treating the
post-release narrative as stable:

- a small set of resolved Method-C cells near `c(h)/c(0) = 0.95`
  changed label under a 240-cell solve;
- the repository had no CI workflow despite the environment being
  Python-version-sensitive;
- `findings-physics.md` needed a visible model-validity envelope and
  clearer row-count vs unique-cell wording;
- one regime-map docstring still claimed the homogeneous shortcut cut
  roughly half the grid.

## What changed

- `src/regime_map.py`
  - Added `REGIME_MAP_N_CELLS = 120` as the explicit first-pass
    regime-map resolution.
  - Added `REGIME_MAP_REFINEMENT_N_CELLS = DEFAULT_N_CELLS` and a
    `REGIME_MAP_REFINEMENT_MARGIN = 1e-2` ratio-threshold guard.
  - Resolved Method-C cells close to the homogeneous/sedimented ratio
    thresholds now rerun at 240 cells before classification.
  - The bottom-mass threshold is intentionally not included in this
    refinement guard: direct 240-cell `expm_multiply` near that
    high-Pe boundary can be pathological, so the 10-nm fallback
    remains part of the documented fidelity envelope.

- `tests/test_regime_map.py`
  - Added a regression test for the known false-homogeneous transient
    cell (`r ≈ 24.1 nm`, `T = 298.15 K`, `h = 10 mm`, `t_obs = 600 s`).
  - Pinned the relationship between the 120-cell first pass and the
    240-cell Method-C refinement.

- `.github/workflows/ci.yml`
  - Added GitHub Actions for Python 3.11 and 3.12:
    `pytest -q` plus `ruff check src/ tests/ notebooks/`.

- Cache and artefacts
  - Repaired `notebooks/data/regime_map_grid.csv` by recomputing the
    90 resolved ratio-threshold-adjacent rows.
  - 8 rows moved from `homogeneous` to `stratified`; no `sedimented`
    labels changed.
  - Regenerated notebook-02/03/04 derived outputs that depend on the
    cache.

- Docs
  - `findings-physics.md` now reports the repaired distribution
    (1158 homogeneous / 2301 stratified / 2841 sedimented), distinguishes
    row-count and unique-cell interpretations, and states the model
    validity envelope explicitly.
  - `deliverable-index.md` records the Method-C regime-map fidelity
    envelope as a known caveat.
  - `README.md` now includes a Python 3.11+ environment block and notes
    the current 94-test suite vs the 92-test release tag.

## Verification

```
$ PYTHONPATH=src MPLBACKEND=Agg .venv/bin/python notebooks/02_regime_map.py
notebook 02 complete; figures written to notebooks/figures/02_regime_map

$ PYTHONPATH=src MPLBACKEND=Agg .venv/bin/python notebooks/03_parameter_scans.py
notebook 03 complete; figures written to notebooks/figures/03_parameter_scans

$ PYTHONPATH=src MPLBACKEND=Agg .venv/bin/python notebooks/04_design_table.py
notebook 04 complete; tables written under notebooks/data

$ .venv/bin/python -m pytest -q
94 passed in 2.82s

$ .venv/bin/python -m ruff check src/ tests/ notebooks/
All checks passed!

$ git diff --check
clean
```

## Remaining Caveat

The finite-time bottom-mass threshold still deserves a formal
mesh-convergence audit before a paper-grade v1.0. The current pilot is
honest about that boundary: it uses the 10-nm regime-map fallback for
runtime and documents the fidelity envelope rather than claiming a full
1-nm resolved-mesh convergence sweep.
