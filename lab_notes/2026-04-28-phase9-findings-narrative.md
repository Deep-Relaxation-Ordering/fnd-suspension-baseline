# 2026-04-28 — Phase 9: findings narrative (physics + process)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Post-release narrative pass. The `pilot-v0.1` deliverable index
([`docs/deliverable-index.md`](../docs/deliverable-index.md))
records *what* was shipped; this phase ships the two companion
documents that record *what was found*:

- [`docs/findings-physics.md`](../docs/findings-physics.md) — the
  experimentally-actionable conclusions extracted from the §5 sweep
  cache (numerical statements about regime boundaries, time
  evolution, temperature dependence, the round-4 second criterion).
- [`docs/findings-process.md`](../docs/findings-process.md) — the
  engineering patterns the pilot converged on across the 9 numbered
  phases (review-fix discipline, cache-as-deliverable, audit-gap
  pins, orchestration short-circuits, coordinate-indexed reshape,
  test-design tiering, etc.).

These two documents close the "what / why / how" loop: the
deliverable index says what shipped, findings-physics says what the
shipped artefacts show, findings-process says how the project ran.
A peer reviewer can read all three and have the complete picture
without reading the source.

## What was done

### `docs/findings-physics.md`

Extracted from the §5 cache:

- Regime distribution across the 6300 cells (1166 H / 2293 S /
  2841 sed = 18.5 / 36.4 / 45.1 %).
- Pe = 1 boundary scaling: `r ∝ h^{-1/3}`, with grid samples
  ~1 §5 bin below the analytic edge across all five depths.
- Temperature dependence is sub-bin (~3 % shift across 5 → 35 °C,
  invisible to the §5 r-axis at 10 % bin spacing).
- Time evolution at room T: H drops from 41/150 to 20/150 as t_obs
  goes 1 min → 1 week.
- Round-4 second criterion catches **17.2 % of cells** (1085 of 6300)
  — these have ratio ≤ 0.05 but bmf < 0.95 and are correctly
  classified `stratified` rather than `sedimented`. Some still in
  transit at t_obs = 1 week.
- Anchor-cell case study (100 nm in 1 mm at 25 °C): stratified at
  every t_obs, asymptotic bmf = 0.591 (never reaches the 0.95
  round-4 threshold) — the boundary layer is ~ 56 µm vs the
  50 µm = 5 % of h cuvette fraction the criterion measures against.
  Exactly the kind of cell §5.1 round-4 was designed to handle.
- Smallest sedimented r at 1 h vs Pe = 1 boundary: ratio 10× to
  100×, growing with h. The "sedimented within an hour" radius is
  set by the slow `h²` diffusive relaxation, not by the
  equilibrium boundary.
- Practical guidance brackets at 25 °C / 1 mm: stay-mixed below
  ~ 11 nm; sedimented within 1 h above ~ 255 nm; sedimented within
  1 minute above ~ 1.6 µm.
- Orchestration cost mix: 65 % of the grid determined analytically
  (homog SC + equilibrated SC + asymptotic fallback), only 33 %
  needs Method C resolved-mesh. The 150-min wall-time is set by
  those 2061 resolved-mesh cells.

All numbers are reproducible via the cache; the document includes
the queries used.

### `docs/findings-process.md`

Fourteen patterns the pilot converged on, with the failure mode
each averted in this project. Notable additions over the
deliverable-index "known caveats" section:

- The `.0` / `.1` / `.2` phase numbering convention.
- The cache-as-deliverable cost/benefit (770 KB on disk vs 150 min
  regen).
- Audit-gap pins as a discipline for unresolved spec values.
- The coordinate-indexed `RegimeGrid` reshape pattern (Phase 7
  fix for the position-indexed reshape risk Phase 6 shipped with).
- Test design tiering (kernel sanity / physics validation /
  cross-method consistency).
- CI-time vs production parameter overrides, with documentation
  in the test docstring.
- Notebook fallback patterns (cache-required vs
  self-contained-with-fallback).
- Spec pinning at commit-hash precision.
- Lab notes as the audit trail (one note per session, errata
  pointers).
- README-as-status-report.

The "What I'd carry forward to the next pilot" section calls out
which patterns generalise (most of them) and which are project-
specific (`min_resolvable_dz_m = 10 nm`, `t_factor = 50`).

### README + lab-notes index

- README's "Status" block now points to both findings docs in
  addition to the deliverable index.
- Phase 9 row added to the README phase table.
- Lab-notes index extended with this note.

## Decisions

| Decision | Rationale |
|---|---|
| Two separate findings documents (physics + process), not one combined | They serve different audiences. Physics findings are paper-draft material for the breakout-note results section; process findings are practitioner-facing knowledge transfer for future pilots. Combining them would dilute both. |
| No new release tag (`pilot-v0.1` stays at `9a0fc76`) | Same rationale as Phase 8.1 — re-tagging is destructive. The findings docs are post-release narrative on top of an unchanged release reference. |
| Numbered as Phase 9 (not "Phase 8.2") | Phase 9 is post-release narrative work; Phase 8.x was tightening artefacts that shipped at the tag. Different scope warrants different numbering. |
| Physics-findings tables include both grid and analytic numbers | The grid-snap caveat from Phase 7.1 is load-bearing for any reader interpreting the design table. Showing both columns is honest and self-documenting. |
| Process-findings "failure modes averted" table | The "why these patterns" question is most concretely answered by "without them, this specific bug would have shipped". Each row maps a pattern to a real risk encountered in this pilot. |

## Verification

```
HEAD before this pass:  da3e3723a3d68789a0df2aebc5750e9d85161a2c
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
92 passed in 3.47s
$ ruff check src/ tests/ notebooks/
All checks passed!
```

The 92-test count is unchanged from `pilot-v0.1` — these are
documentation-only additions. No code, no tests, no figures
modified.

## What was *not* done

- **Pretty-printed PDF / LaTeX rendering of the findings docs** —
  out of scope. Markdown is the cd-rules-canonical authored form;
  paper-draft conversion happens in the breakout-note repo.
- **Cross-link from the breakout note to these findings** — same.
  This is the pilot side; the breakout-note side is a sibling-repo
  task.
- **Rerun of the §5 cache** — explicitly *not* needed. Phase 9 is
  narrative; the cache content is unchanged.

## Cross-references

- [`pilot-v0.1` tag at `9a0fc76`](https://github.com/Deep-Relaxation-Ordering/fnd-suspension-baseline/releases/tag/pilot-v0.1)
- [`docs/deliverable-index.md`](../docs/deliverable-index.md) — the
  third document in the closeout triad.
- breakout-note §6 (deliverables) — the spec section the
  deliverable index closes; the findings documents inform the
  results-section narrative the breakout note will eventually
  carry.
- All earlier lab notes — the "Decisions" tables in each are the
  raw material for findings-process.

## Next session

The pilot is feature-complete and narratively documented. Possible
follow-ups, in priority order:

1. **Breakout-note §6 + results-section update** — sibling-repo
   task in `Deep-Relaxation-Ordering/diamonds_in_water`. The
   findings docs here are the source.
2. **Audit-gap pin resolution** — when the breakout-note v0.3
   lands with explicit `T_OBS_S` and 5th-depth values, update
   `scan_grid.py` and re-walk the §5 cache.
3. **Continuous-threshold design table** — root-find on
   `top_to_bottom_ratio = 0.95` and `bmf = 0.95` for interpolated
   transition radii (listed in the deliverable index's
   "What `pilot-v1.0` would change" section).
4. **Parallel grid walk** — the 150-min wall time is dominated by
   2061 Method-C-resolved cells; embarrassingly parallel via
   `multiprocessing` or `joblib`.

None of these block consumption of `pilot-v0.1`.
