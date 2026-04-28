# 2026-04-28 — Phase 7.1: review-driven fixes (envelope figure + table semantics + stale comments)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Post-merge review of `6e13229` (Phase 7) raised one medium and two
low-priority findings — none correctness bugs, all about traceability
and figure narrative. Same review-driven-fix pattern as 3.1 / 3.2 /
4.1 / 5.1.

## What was done

### Bug 1 — `homogeneous_envelope_vs_T` figure was effectively flat (medium)

The committed Phase-7 figure plotted a single panel at `t_obs = 1 h`
showing one line per depth. Reviewer correctly noted the curves
overplotted and the figure didn't support the lab note's "envelope
falls with temperature" narrative — the §5 r-axis (~10 % bin spacing)
is too coarse to resolve the genuine ~3 % rise in `r ∝ T^(1/3)` across
5 → 35 °C, and the finite-time markers at 1 h sit above the analytic
equilibrium boundary because Method C hasn't equilibrated.

Fix: redesigned `homogeneous_envelope_vs_T` as a two-panel figure
(`t_obs = 1 h` and `t_obs = 1 d`) with two complementary curves per
depth:

- Continuous line — analytic *equilibrium* boundary
  ``exp(-h/ℓ_g) = 0.95``, computed by inverting the formula for `ℓ_g`
  to get
  ``r = ((3/4π) · k_B T · |ln 0.95| / (g h Δρ))^(1/3)``. Shows the
  smooth physical T-dependence the §5 axis can't resolve.
- Markers — finite-time §5 grid samples at the panel's `t_obs`,
  snapped to the §5 r-axis. At 1 h the markers stack across depths
  (system not yet equilibrated, all r ≲ 14 nm cells stay homogeneous
  regardless of h); at 1 d they spread out and track the analytic
  line, showing the grid-snap effect (markers shift down a bin at
  warmer T).

Notebook 03's narrative section now spells out the line-vs-marker
distinction explicitly. Image inspection confirms the new figure
reads cleanly — the "system at finite time vs system at equilibrium"
contrast is the actual story, and the grid resolution limit is now
visible rather than hidden.

### Bug 2 — design-table wording implied interpolated thresholds (low)

`design_table_room_T.md` and notebook 04's prose called the table
entries "band edges" and "the largest radius that stays
homogeneous". They are §5 r-axis samples — discrete points on a
log-spaced grid — not interpolated transition radii. The true
homogeneous → stratified threshold sits between adjacent §5 samples;
the table reports the largest §5 sample that's still inside the
band, not the threshold itself.

Fix: notebook 04's prose, the per-table caption, and the auto-generated
Markdown header all now say "largest *tested* radius" / "smallest
*tested* radius", with explicit caveats that:

- the values are *grid-snapped* to the §5 r-axis (30 log-spaced
  points, ~10 % bin spacing);
- the true regime transition lies between adjacent §5 samples;
- continuous interpolated boundaries are in notebook 03's
  `homogeneous_envelope_vs_T` analytic overlay.

The two CSVs (`design_table_max_homogeneous_r.csv`,
`design_table_min_sedimented_r.csv`) are unchanged in content;
only the surrounding documentation was tightened.

### Bug 3 — stale traceability comments (low)

Three stale references to the original 18-min runtime estimate / a
"next session" pointer that's now done:

- `tests/test_regime_map.py` line 7: "the production 6300-cell sweep
  takes O(20 min)" → "takes ~150 min single-threaded (8836 s
  measured on the Phase 6 commit)".
- `tests/test_regime_map.py` line 205 (the `results_csv_round_trip`
  test docstring): "an 18-min operation otherwise" →
  "a ~150-min operation otherwise".
- `notebooks/02_regime_map.py` final-cell prose: "pretty-printing it
  as a polished table is a separate notebook (03/04, next session)"
  → "ships in notebook 04 (Phase 7) ... notebook 03".

## Decisions

| Decision | Rationale |
|---|---|
| Two-panel envelope figure (1 h + 1 d) rather than one | The 1-h panel alone is the original "flat" figure; the 1-d panel shows the markers tracking the analytic line. Together they tell the finite-time-vs-equilibrium story that motivated `t_obs` being an axis at all. |
| Analytic boundary uses `parameters.K_B`, `G`, `RHO_P_DIAMOND`, `rho_water(T)` directly | Re-deriving the formula from these primitives keeps the boundary definition transparent; pulling it from `analytical.scale_height` would obscure the inversion `h/ℓ_g = ln(1/0.95)`. |
| Did *not* regenerate the §5 cache | Phase 7.1 is documentation/figure semantics; no Method-C output changes. The cache content is unchanged. |
| Phase 7 lab note edited only via an Errata pointer (not in this commit) | Phase 7's note already documents what shipped at `6e13229`; this lab note documents the deltas. The errata pattern from Phase 5.1 is left as-is — a more elaborate cross-reference would be churn. |

## Verification

```
HEAD before this pass:  6e132296120c6b06fd17b82cf467a46886afc296
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
92 passed in 3.33s
$ ruff check src/ tests/ notebooks/
All checks passed!
$ PYTHONPATH=src MPLBACKEND=Agg python notebooks/02_regime_map.py
notebook 02 complete
$ PYTHONPATH=src MPLBACKEND=Agg python notebooks/03_parameter_scans.py
notebook 03 complete
$ PYTHONPATH=src python notebooks/04_design_table.py
notebook 04 complete
```

The 92-test count is unchanged from Phase 7 — these are
documentation, figure, and prose fixes, no behaviour change.

## What was *not* done

- **Continuous interpolated entries in the design-table CSV** —
  considered but defer. The §5 grid-snapped form is the
  spec-conformant deliverable; an interpolated form would be a
  derived secondary table, useful but out of scope for the
  breakout-note §6 closeout.
- **Multi-T (one Markdown table per scan_grid temperature)
  presentation** — still Phase-7-deferred. The full multi-T data is
  in the CSVs; the printable Markdown stays at 25 °C.

## Cross-references

- breakout-note §5 (parameter scan), §5.1 (regime classification),
  §6 (deliverables) — Phase 7.1 doesn't change scope, only sharpens
  the existing Phase-7 deliverables.
- Phase 7 lab note — what shipped at `6e13229`; this note is the
  delta.
- Phase 5.1 / 4.1 / 3.x lab notes — same review-driven-fix pattern.

## Next session

Unchanged from Phase 7: Phase 8 — release tag (`pilot-v0.1`),
`docs/deliverable-index.md` mapping the §6 deliverable list to the
shipped artefacts, and a final cross-check against the breakout-note
v0.2 pin that nothing in §6 is unimplemented.
