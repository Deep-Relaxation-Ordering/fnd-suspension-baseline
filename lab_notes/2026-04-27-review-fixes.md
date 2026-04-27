# 2026-04-27 — Review fixes (Phase 2.5)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

After-action review pass over the Phase 0 → Phase 2 surfaces. Two
independent reviews (mine, plus a second pass shared by the user)
converged on a small set of inconsistencies and traceability gaps that
were cheap to fix while context is fresh — and that compound badly if
left until Method B / Method C land. This note records the fixes; the
README "Status" table now lists this as Phase 2.5.

## What was done

### Dependency contract

- `pyproject.toml`: `numpy>=1.26` → `numpy>=2.0`. `tests/test_analytical.py`
  and the notebook use `np.trapezoid`, which is NumPy 2.0+. The local
  `.venv` has 2.4.4 so it had been working, but a fresh install picking
  up 1.26 would `AttributeError` at first call.
- `pyproject.toml`: added `jupytext>=1.16` to `[notebooks]` extras —
  `docs/conventions.md` already instructs readers to run
  `jupytext --to ipynb`.
- `pyproject.toml`: Development Status `1 - Planning` → `2 - Pre-Alpha`.

### Spec-to-implementation traceability

- `docs/conventions.md`: pinned the breakout-note commit hash to
  `3b7b18af7bd1739f3cb7b3360d2b75264dd5ad07` (PR #2 merge into `main`,
  verified via `git ls-remote https://github.com/Deep-Relaxation-Ordering/diamonds_in_water HEAD`).
  The pin had been blank since scaffold; the spec-to-impl link is now
  auditable.
- `README.md`: rewrote the "Status" section. Now shows phase-by-phase
  state with links to each phase's lab note instead of the stale
  "Day 0 — repository scaffold only" prose.
- `lab_notes/README.md`: new lab-notes index, reverse-chronological.
  Convention: prepend a row when adding a note, do not edit prior rows.

### Centralised scan grid

- `src/scan_grid.py`: new module owning the breakout-note §5 axes
  (radii, temperatures, depths). Single source of truth shared by
  notebook 01 and (eventually) `regime_map.py`. Resolves three places
  that previously restated `np.geomspace(5e-9, 1e-5, 30)` independently.
- `src/regime_map.py` docstring: defers axis ownership to `scan_grid.py`.
- `notebooks/01_baseline_validation.py`: now imports `radii_m()`,
  `DEPTHS_M`, `DEPTH_LABELS`, `NOTEBOOK_PREVIEW_DEPTH_INDICES` from
  `scan_grid`. Restated prose: previously claimed the four depths it
  showed *were* the §5 grid; now correctly labels them as a 4-of-5
  short-path subset, with the full sweep deferred to the deliverable-3
  figure produced by `regime_map.py`.
- `tests/test_scan_grid.py`: pins shape and endpoints of all three axes,
  plus that `NOTEBOOK_PREVIEW_DEPTH_INDICES` is a well-formed subset.

### Test polish

- `tests/test_water_properties.py`: `test_viscosity_at_5C_within_1pct_of_iapws`
  → `..._within_2pct_...`, same for 35 °C. The names had been
  contradicting their tolerances (`rel_tol=2e-2`).
- `tests/test_equilibrium.py`: skip reason "Awaiting Method A and
  Method B implementations" → "Awaiting Method B implementation"
  (Method A landed in Phase 2).
- `tests/test_method_consistency.py`: same correction for the
  Method A ↔ Method C row.

### Notebook hygiene

- `notebooks/01_baseline_validation.py`: `diffusivity` is now imported
  from `parameters` (its true owner) rather than `analytical` (which
  had been re-exposing it as a side-effect of its own imports).
- `notebooks/.gitkeep`: removed; the directory now has real content.
- `.gitignore` + `git rm --cached`: `notebooks/figures/**/*.pdf` is no
  longer tracked. Matplotlib embeds `/CreationDate` in PDFs, so PDFs
  churned byte-for-byte on every notebook re-run even when the plotted
  data was identical. PNG previews remain tracked; PDFs are regenerated
  on demand.

## Anchor-cell snapshot (regression check)

Re-ran notebook 01 end-to-end after the refactor. Anchor cell (100 nm
diamond, 25 °C, 1 mm sample) reproduces the Phase 2 snapshot to all
displayed digits:

| Quantity | Phase 2 note | After refactor |
|---|---|---|
| ρ_f [kg/m³] | 997.05 | 997.047 |
| η [Pa·s] | 8.90·10⁻⁴ | 8.90439·10⁻⁴ |
| m_eff [kg] | 1.05·10⁻¹⁷ | 1.05262·10⁻¹⁷ |
| γ [N·s/m] | 1.68·10⁻⁹ | 1.67844·10⁻⁹ |
| D [m²/s] | 2.45·10⁻¹² | 2.45252·10⁻¹² |
| v_sed [m/s] | 6.15·10⁻⁸ | 6.15019·10⁻⁸ |
| ℓ_g [m] | 3.99·10⁻⁵ | 3.98772·10⁻⁵ |
| t_eq [s] | 648 | 648.39 |
| t_settle [s] | 1.63·10⁴ | 16259.7 |
| c(h)/c(0) | 1.29·10⁻¹¹ | 1.28587·10⁻¹¹ |

No physics moved; only the surface restructured.

## What was *not* done (deliberate deferrals)

- **t_obs axis in `scan_grid.py`** — deferred until Method B / Method C
  land and the t_obs grid stops being a stub in `regime_map.py`.
- **Sidecar provenance JSON for figures** (the consolidated review's
  recommendation 2) — Phase-3 prerequisite. Need a `regenerate_figures.py`
  driver to make the metadata deterministic; not worth retrofitting just
  notebook 01 ahead of that.
- **`src/` → `src/fnd_suspension/` package layout** (second reviewer's
  suggestion 3) — defer. Flat `src/` is *explicitly defended* in the
  scaffold note as matching breakout-note §4.3 literally; would require
  a spec change first.
- **Confirm 5th depth value (10 mm) against breakout-note §5 table** —
  the centralised `scan_grid.DEPTHS_M` lists `(0.1, 0.5, 1, 2, 10) mm`
  on the inferred Ibidi → standard cuvette framing; the §5 table value
  should be cross-checked at the next spec drift.
- **GitHub-remote-provisioning addendum to scaffold note** — not added;
  this note discharges the audit-trail need by recording that
  `origin → Deep-Relaxation-Ordering/fnd-suspension-baseline` is now
  configured, while the scaffold note's prose still reflects its
  point-in-time accuracy.

## Verification

```
HEAD before this pass:  5df0d7e73a5b4a396300287bf18b8c2c0c6f71d9
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
33 passed, 10 skipped in 0.13s
$ ruff check src/ tests/ notebooks/
All checks passed!
$ PYTHONPATH=src MPLBACKEND=Agg python notebooks/01_baseline_validation.py
notebook 01 complete; figures written to notebooks/figures/01_baseline_validation
```

The +6 passing tests are `tests/test_scan_grid.py`. Skipped count
unchanged at 10 (Method B and C dependencies).

## Cross-references

- breakout-note §5 (parameter scan) — now owned by `src/scan_grid.py`.
- cd-rules §0.10 propagation rule — applied to the breakout-note pin
  the same way as to the cd-rules pin.
- conventions.md §"Authoring conventions" — extended implicitly by the
  new `lab_notes/README.md` index convention (prepend, don't rewrite).

## Next session

Phase 3 — Method B (Langevin), as previously planned. The `scan_grid`
module makes the radius / temperature / depth axes a one-line import
for the trajectory ensemble; t_obs joins the module when Method B's
output requires it.
