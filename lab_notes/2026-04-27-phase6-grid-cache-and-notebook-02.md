# 2026-04-27 — Phase 6: grid cache + notebook 02 (deliverable-3 regime map)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 6 of the breakout-note timeline (§9): turn the Phase-5
orchestration into a deliverable. Adds a CSV cache of the full §5
sweep (also serving as the design-table primitive) and notebook 02
producing the deliverable-3 regime-map figures. Notebooks 03/04 and
the polished printable design table are deferred to Phase 7.

## What was done

### `src/regime_map.py` — CSV round-trip

Two new functions plus a small helper:

- `results_to_csv(results, path)`: writes a list of `RegimeResult`
  to CSV. Floats via `repr()` for bit-exact round-trip; numpy
  scalars (which `radii_m()` and friends return) are coerced via
  `.item()` first because `repr(np.float64(5e-9))` is the
  non-round-trippable string ``'np.float64(5e-09)'``.
- `results_from_csv(path)`: reads such a CSV back into
  `RegimeResult` objects. Tolerates legacy `np.float64(...)`
  wrappers from any cache written before the writer learned to coerce.
- Header validation: a file with mismatched columns raises
  `ValueError` rather than silently mis-mapping fields.

Two new tests in `tests/test_regime_map.py`:

- `test_results_csv_round_trip_is_lossless`: walks an 8-cell slice,
  writes, reads, asserts every field bit-exact.
- `test_results_from_csv_rejects_mismatched_header`: bad header →
  `ValueError`.

### `notebooks/data/regime_map_grid.csv` — the §5 cache

The full 6300-cell sweep, computed once and checked in. 770 KB.
Distribution:

| Quantity | Count |
|---|---|
| Total cells | 6300 |
| Homogeneous | 1166 |
| Stratified | 2293 |
| Sedimented | 2841 |
| Path: homogeneous short-circuit | 840 |
| Path: equilibrated short-circuit | 3266 |
| Path: Method C asymptotic fallback | 133 |
| Path: Method C resolved mesh | 2061 |

Walk wall-time: **8836 s ≈ 147 min** — about 8× my Phase 5
extrapolation of 18 min. The slice I timed (5 radii, 1 temperature,
all depths, all t_obs) didn't capture the cost-tipping done by the
full grid:

1. The 30-radius axis covers more of the slow ~0.2-0.7 µm zone than
   the 5-radii slice. About 10 of 30 radii sit in or near the slow
   band where Method C's resolved-mesh path runs.
2. The 7-temperature axis adds a 7× factor, but cold temperatures
   shift cells into Method C: at 5 °C, η ≈ 2× → v_sed halves →
   ``h/v_sed`` doubles → the equilibrated short-circuit fires later.

The cache is checked into git despite its size because the regen
cost is two-and-a-half hours; bisectability and contributor onboarding
both win from having it as a tracked artefact. It's the authoritative
form of deliverable 5 (the design table).

### `notebooks/02_regime_map.py` — deliverable 3

Three figures, all driven from the CSV cache (with an explicit
fallback to a coarse 270-cell walk if the cache is missing — keeps
the notebook self-contained):

1. **`regime_map_room_T_1h`** — single panel at T = 25 °C and
   t_obs = 1 h. The §5.1 deliverable: blue homogeneous corner
   top-left, brown sedimented corner bottom-right, yellow stratified
   diagonal band.
2. **`regime_map_room_T_evolution`** — three-panel sweep over
   t_obs (1 min / 1 h / 1 day). The sedimented region marches into
   the stratified band as t_obs grows; by 1 day all but the smallest
   particles in the deepest cells have settled.
3. **`path_provenance_room_T_1h`** — orchestration provenance
   plot promised by `RegimeResult`'s docstring. Shows which
   execution path (homogeneous SC / equilibrated SC / Method C
   fallback / Method C resolved) handled each cell. Auditable
   without re-walking.

PNG + PDF for each, written to `notebooks/figures/02_regime_map/`.
PDFs are gitignored (matplotlib `/CreationDate` churn from Phase 2.5).

The walk-order reshape (`r → T → h → t_obs`) into a 4-D array is
exactly the contract pinned by
`test_walk_grid_subset_iteration_order` in Phase 5; if the walker
ever changes order, the test fires before the notebook silently
mis-aligns axes.

## Decisions

| Decision | Rationale |
|---|---|
| Track the CSV cache in git | Regen is 2.5 hours single-threaded; that's a contributor-onboarding cost too high for the deliverable-3 figures. The CSV is also the design table itself, not just a derived artefact. |
| `repr()` for floats, with numpy-scalar coercion via `.item()` | Bit-exact round-trip preserved (Python 3 guarantees `eval(repr(x)) == x` for floats); the numpy-scalar coercion is needed because `radii_m()` returns ndarray elements. The reader tolerates legacy `np.float64(...)` wrappers so the existing 2.5-hour walk's CSV didn't have to be regenerated when the writer was tightened. |
| Notebook fallback to a coarse 270-cell walk if cache is missing | Keeps the notebook self-contained for fresh clones / CI. Documented at the top of the notebook with the regen one-liner. |
| Figures committed as PNGs only (PDFs gitignored) | Phase 2.5 policy: matplotlib embeds non-deterministic `/CreationDate` in PDFs. PNGs are diff-stable enough to track; PDFs regenerate locally. |
| Path-provenance figure shipped in this commit | Phase 5's `RegimeResult` docstring promised it. Cheaper to ship the figure now than to leave the promise dangling. |
| Notebooks 03/04 and the polished design-table deferred | Scope control. The CSV cache is the design-table primitive; pretty-printing it (LaTeX, HTML, PDF) and the parameter-scan figures are clean follow-up commits, not blocked on anything in this one. |

## Verification

```
HEAD before this pass:  461477dc2292ab7b864838c2565635a4c8289035
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
88 passed in 3.25s
$ ruff check src/ tests/ notebooks/
All checks passed!
$ PYTHONPATH=src MPLBACKEND=Agg python notebooks/02_regime_map.py
loaded 6300 cells from cache: notebooks/data/regime_map_grid.csv
axes: r=30, T=7, h=5, t_obs=6  (total = 6300)
regime distribution: {'homogeneous': 1166, 'stratified': 2293, 'sedimented': 2841}
notebook 02 complete; figures written to notebooks/figures/02_regime_map
```

The +2 passing tests over Phase 5.1 are the CSV round-trip and the
mismatched-header-rejection tests. Skipped count remains at 0.

## What was *not* done

- **Polished printable design table** (deliverable 5 in its presentation
  form). The CSV is the data; LaTeX / Markdown / HTML rendering is a
  Phase 7 task. Caller can already grep the CSV by regime to extract
  the "what (r, h, t_obs) keeps the suspension homogeneous?" question.
- **Notebooks 03 / 04** for parameter scans (settling-velocity
  contours, equilibration-time isolines). The §5 grid contains all
  the inputs; these are presentation, not computation.
- **Per-temperature regime-map panels** (a 7-panel grid, one per
  scan_grid temperature). Notebook 02 only renders the room-temperature
  slice. Easy follow-up — the cache supports it.
- **Caching infrastructure beyond CSV** (e.g., HDF5 / pickle for
  faster loads on subsequent runs). The CSV reads in < 1 s; not worth
  the complexity yet.
- **Spec-pin re-check on `T_OBS_S`**. Still tracked as the audit-gap
  pin from Phase 5; will move at the next breakout-note drift.

## Cross-references

- breakout-note §5 / §5.1 — the orchestration target Phase 5 built and
  Phase 6 visualised.
- breakout-note §6 (deliverables) — deliverable 3 (regime map figure)
  shipped here; deliverable 5 (design table) is the cache itself, with
  presentation polish deferred.
- Phase 5 lab note — `walk_grid` iteration order; notebook 02's
  reshape relies on it.
- Phase 5.1 lab note — `RegimeResult` per-path interpretation;
  notebook 02's path-provenance figure is the visual companion.

## Next session

Phase 7 — notebooks 03/04 (parameter scans + the polished
deliverable-5 design table). The cache is the input; the work is
presentation. After that the breakout-note timeline §9 has only the
final wrap-up (release tag, paper draft hooks) remaining.
