# 2026-04-27 — Phase 7: parameter scans + deliverable-5 design table

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 7 of the breakout-note timeline (§9): close out the §6
deliverables. Phase 6 shipped the §5 grid cache and notebook 02
(regime map / deliverable 3); Phase 7 adds notebook 03 (parameter
scans across the temperature axis) and notebook 04 (the printable
deliverable-5 design table). Also absorbs the three Phase-6 review
findings — the medium one (cache reshape was order-dependent) becomes
the new `results_to_grid` helper that all three notebooks consume.

## What was done

### `src/regime_map.results_to_grid` — coordinate-indexed reshape

Phase 6's notebook 02 reshaped the cache by *row position*, relying
on `walk_grid`'s iteration order (pinned by
`test_walk_grid_subset_iteration_order`). A sorted or shuffled CSV
would have rendered plausible-looking but axis-mis-aligned figures.

`results_to_grid(results) → RegimeGrid` reshapes by *coordinate
value*: each cell is placed at the index its (radius, temperature,
depth, t_obs) values map to in the sorted unique-axis lookup. Missing
or duplicate cells raise `ValueError` rather than leaving sentinels.
Returns a frozen dataclass `RegimeGrid` with the four channels
(`regime` int8, `ratio` float64, `bmf` float64, `path` int8) plus
the canonical sorted axes alongside.

Four new tests in `tests/test_regime_map.py`:

- shape and axis recovery match the input cells
- order-independence (shuffled list produces identical grid)
- missing cell raises with a "rectangular" message
- duplicate cell raises

Notebook 02 was updated to use the helper; the bespoke
`for i, res in enumerate(results)` reshape that previously sat in
the notebook is gone.

### `notebooks/03_parameter_scans.py`

Three figures driven from the §5 cache:

1. **`method_a_primitives_vs_T`** — `v_sed`, `D`, `ℓ_g` vs `r` for
   all 7 scan_grid temperatures, overlaid on log-log axes. Doesn't
   need the cache (Method-A primitives only). Diffusivity and
   scale-height curves are ~degenerate across T at small r; the η
   ≈ 2× factor across 5 → 35 °C shows up at large r where settling
   dominates.
2. **`regime_map_per_temperature`** — 7-panel grid, one regime map
   per scan_grid temperature, all at `t_obs = 1 h`. Sedimented
   region grows toward smaller r as T rises (η drops, settling
   speeds up).
3. **`homogeneous_envelope_vs_T`** — for each sample depth, the
   largest radius classified `homogeneous` traced across T. Five
   curves (one per depth) showing the envelope falling slightly
   with T.

PNG + PDF for each, written to `notebooks/figures/03_parameter_scans/`.
PDFs gitignored per Phase 2.5 policy.

### `notebooks/04_design_table.py` — deliverable 5

Two band-edge tables computed from the cache:

- **`design_table_max_homogeneous_r.csv`**: per `(h, t_obs, T)`,
  the largest radius from the §5 axis that is still classified
  `homogeneous`. The "stay-mixed" envelope.
- **`design_table_min_sedimented_r.csv`**: per `(h, t_obs, T)`, the
  smallest radius classified `sedimented` (round-4 second criterion
  satisfied). The "fully-settled" entry-point.

Both written to `notebooks/data/`. Plus a printable Markdown
extract `design_table_room_T.md` containing both tables at 25 °C
for inclusion in the breakout-note §6 deliverable section.

Sample of the room-T homogeneous-band upper edge:

| h \ t_obs | 1 min | 10 min | 1 h | 4 h | 1 d | 1 w |
|---|---|---|---|---|---|---|
| 0.1 mm | 31 nm | 24 nm | 24 nm | 24 nm | 24 nm | 24 nm |
| 1 mm   | 31 nm | 19 nm | 14 nm | 11 nm | 11 nm | 11 nm |
| 10 mm  | 41 nm | 24 nm | 14 nm | 11 nm | 6 nm  | 5 nm  |

The 10 mm / 1 min entry is non-monotone with h not because of a
classifier bug but because at very short t_obs the system hasn't had
time to settle — the equilibrium ratio is irrelevant; what matters
is `t_obs / t_relax`, and that ratio is *smaller* in the deeper cell
(t_relax scales like h² for the diffusive mode), so deeper cells
look more homogeneous at fixed short t_obs.

### Phase-6 lab-note erratum

Cache size corrected in place: 612 530 bytes (≈ 598 KiB), not
"770 KB". Phase-6 commit message will read with this caveat for
future archaeologists; the lab-note text is now accurate.

### `src/regime_map.py` runtime comment

Updated from "~18 min single-threaded" (Phase 5 extrapolation) to
"~150 min single-threaded (8836 s measured on the Phase 6 commit)"
with a one-line explanation of why the extrapolation was off.

## Decisions

| Decision | Rationale |
|---|---|
| `RegimeGrid` is a frozen dataclass with NDArray channels, not a dict-of-arrays | Type-checkable, IDE-completable, immutable enough that callers can pass it around without worrying about mutation. The "bag of arrays" form would be marginally simpler but loses the structural guarantee that all channels share the same shape. |
| Missing-cell + duplicate-cell raise rather than warn | Silent partial grids would render figures with sentinel-valued patches that read as "stratified" (regime int 1) on the colormap. Loud failure here is the right call. |
| Notebook 04 writes both full-precision CSVs *and* a Markdown extract | The CSVs are the deliverable-5 archival form (full precision, multi-T, machine-readable); the Markdown is the human-readable summary that will paste into the breakout-note §6 deliverable section. Different audiences, different formats. |
| Markdown table at 25 °C only, not all 7 temperatures | The full multi-T design is in the CSVs; the Markdown is a specimen for inclusion. 7 separate Markdown tables would crowd the file. |
| `_format_radius` snaps below-1 nm to two decimals, ≥ 1 µm to three significant figures | Readable "5 nm" / "350 nm" / "1.20 µm" rendering rather than "5.0e-09" scientific notation. |
| Notebook 03's regime-per-T panels are 7 wide, not 4×2 | Wide format keeps the radius axis legible; depth is the same across panels so a shared y-axis works. 4×2 would force smaller axes and lose the small-r resolution. |
| Notebook 04 raises if the cache is missing rather than coarse-fallback | The design table is structurally a *projection* of the §5 grid; without the cache there is nothing to project. Notebook 02's coarse fallback exists to keep the regime-map figure renderable for fresh clones; the design table needs the real cache. |

## Verification

```
HEAD before this pass:  7a17ba4b307c39a27641d42da452dafd3fb1fff5
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
92 passed in 3.44s
$ ruff check src/ tests/ notebooks/
All checks passed!
$ PYTHONPATH=src MPLBACKEND=Agg python notebooks/02_regime_map.py
notebook 02 complete; figures written to notebooks/figures/02_regime_map
$ PYTHONPATH=src MPLBACKEND=Agg python notebooks/03_parameter_scans.py
notebook 03 complete; figures written to notebooks/figures/03_parameter_scans
$ PYTHONPATH=src python notebooks/04_design_table.py
notebook 04 complete; tables written under notebooks/data
```

The +4 passing tests over Phase 6 are the four new `results_to_grid`
tests (shape recovery, order independence, missing-cell rejection,
duplicate-cell rejection). Skipped count remains at 0.

## What was *not* done

- **Spec re-check on `T_OBS_S`** — still tracked as the audit-gap pin
  from Phase 5; will move at the next breakout-note drift.
- **Pretty LaTeX rendering of the design table** — Markdown is the
  Phase-7 deliverable form; LaTeX is downstream paper-draft work,
  not a §6 deliverable.
- **Per-temperature animation / interactive figure** — out of scope
  for a numerical pilot; static figures are the deliverable surface.

## Cross-references

- breakout-note §5 / §5.1 / §6 — Phase 7 closes the deliverable list
  (1 = methods/code, 2 = unit-test reports — already in the
  breakout-note artefact list, 3 = regime map figure, 4 = parameter
  scans, 5 = design table).
- Phase 5 lab note — `walk_grid` iteration order; `results_to_grid`
  no longer relies on it but the contract is still pinned by
  `test_walk_grid_subset_iteration_order` for the legacy reshape
  pattern.
- Phase 5.1 lab note — `RegimeResult` per-path interpretation;
  notebooks 02 / 03 / 04 all read those flags via `RegimeGrid.path`.
- Phase 6 lab note — the cache that Phase 7 consumes.

## Next session

Phase 8 (final) — release tagging and paper-draft hooks per the
breakout-note §9 wrap. Likely a single small commit: tag
`pilot-v0.1`, fold deliverable references into a `docs/`
deliverable-index, and confirm against the breakout-note v0.2 pin
that nothing in §6 is unimplemented.
