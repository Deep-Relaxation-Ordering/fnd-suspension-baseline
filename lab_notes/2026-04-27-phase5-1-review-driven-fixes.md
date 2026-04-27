# 2026-04-27 — Phase 5.1: review-driven fixes (semantics + traceability)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Post-merge review of `5bc89f3` (Phase 5) raised four findings — two
medium and two low. None are correctness bugs; all are
semantics/traceability slips that would mislead the Phase 6 notebook
authors and external readers if left in. Same review-driven-fix
pattern as Phases 3.1 / 3.2 / 4.1.

## What was done

### Bug 1 — `T_OBS_S` mis-described as "log-spaced" (medium)

`src/scan_grid.py` line 81 and Phase 5 lab note line 21 both
described `T_OBS_S = (60, 600, 3600, 14400, 86400, 604800)` s as
"log-spaced". They are not — successive ratios are
``(10, 6, 4, 6, 7)``, not constant. The values are *hand-picked
experimental durations* (1 min / 10 min / 1 h / 4 h / 1 d / 1 w).

Fix:

- `src/scan_grid.py`: section header changed from
  "six log-spaced t_obs values" to "six hand-picked t_obs values",
  with an explicit note that the ratios vary and a pointer to
  `np.geomspace` for callers who want strict log spacing.
- Phase 5 lab note: "six log-spaced values" → "six hand-picked
  experimental durations", with a Phase 5.1 cross-reference.

The radius axis (`np.geomspace`) is genuinely log-spaced and was
left untouched.

### Bug 2 — homogeneous short-circuit reported a static `bmf = 0.05` (medium)

`classify_cell` short-circuited the homogeneous corner with
`bottom_mass_fraction = SEDIMENTED_BOTTOM_LAYER_FRACTION = 0.05` —
the layer fraction itself, i.e. the bmf of a perfectly-uniform
profile. Two issues:

1. `RegimeResult`'s docstring claimed downstream callers could reuse
   the stored threshold inputs without re-running Method C, but the
   stored bmf wasn't a finite-time *or* equilibrium value — it was
   neither.
2. For the deliverable-3 plotting surface, returning a static `0.05`
   across the entire homogeneous corner suppresses the actual
   structure (the equilibrium bmf there is `0.05 + small h/ℓ_g
   correction`).

Fix:

- The homogeneous short-circuit now returns the analytic equilibrium
  bmf via `_equilibrium_bottom_mass_fraction(h, ℓ_g)` — internally
  consistent with the equilibrated short-circuit's bmf.
- `RegimeResult` docstring rewritten as an explicit
  per-execution-path interpretation list. Each of the four paths
  (homogeneous short-circuit / equilibrated short-circuit / Method C
  fallback / full Method C) now has documented semantics for both
  `top_to_bottom_ratio` and `bottom_mass_fraction`. Plot consumers
  who need exact finite-time numbers in the homogeneous corner are
  pointed to re-run Method C with their preferred mesh fidelity.

The regime *label* was correct on the original implementation; this
fix is about the auxiliary numbers that ship alongside it.

### Bug 3 — README and Phase 5 note over-claimed the orchestration scope (low)

The Phase 5 commit message and README's status block both stated that
`classify_cell` and `walk_grid` "compose Methods A / B / C". Reality:
they compose A and C only. Method B remains in place as the
cross-validation harness for Method C inside its feasibility envelope
(`test_method_b_c_time_dependent_moments_agree` from Phase 4.1) but
isn't called from `classify_cell`.

Fix: README's status block now reads "Methods A and C are composed by
`regime_map.classify_cell` and `walk_grid`; Method B remains in place
as the cross-validation harness for Method C". Phase 5 note's
"What was *not* done" section already had the correct framing; only
the status text needed tightening.

### Bug 4 — Phase 5 lab note test counts didn't add up (low)

The note said "20 tests covering" for `test_regime_map.py`, then
elsewhere "+14 total from 3 scan-grid and 11 classifier tests". The
actual committed shape is:

- `test_regime_map.py`: **12 tests** (3 threshold-logic, 4 path-firing,
  2 round-4 sedimentation criterion, 3 grid-walker shape).
- `test_scan_grid.py`: **+2 t_obs tests** (axis shape and spec
  contract).
- Total Phase 5 additions: **14 new tests** (72 → 86).

Fix: counts corrected in place; "20 tests" → "12 tests"; "+14 from 3
scan-grid and 11 classifier" → "+14 from 2 scan-grid and 12
classifier"; cross-reference to this note added below the verification
block.

## Decisions

| Decision | Rationale |
|---|---|
| Homogeneous short-circuit now returns analytic equilibrium bmf, not the layer-fraction constant | Internally consistent with the equilibrated-corner path, and gives the deliverable-3 plot a smoother "value across the homogeneous corner" surface than a flat 0.05. |
| `RegimeResult` semantics as a bullet list per execution path, not a markdown table | Markdown tables blow past the 100-character line limit; bullet list reads cleaner in editors and avoids ruff E501 complaints. |
| Phase 5 lab note edited in-place, not preserved verbatim | Phase 5 note is dated today (2026-04-27); the typos are session-fresh, not a historical record. Errata pointer added at the end of the note for future readers. |
| Did not change `T_OBS_S` values to be actually log-spaced | The hand-picked experimental durations are physically meaningful (and easier to plot-axis-label than `geomspace` ticks). The audit-gap pin for the actual §5 spec values still stands. |

## Verification

```
HEAD before this pass:  5bc89f38ddb8b16e3c775dc49f5212148443ec1a
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
86 passed in 2.42s
$ ruff check src/ tests/ notebooks/
All checks passed!
```

The 86-test count is unchanged from Phase 5 — these are
documentation/semantics fixes, not new behavior. The seeded Method C
runs aren't perturbed: the only code change in `classify_cell` is the
homogeneous-corner bmf computation, which feeds an analytic formula
that produces the same regime classification but a slightly more
informative number.

## What was *not* done

- **Test that explicitly asserts the homogeneous corner's
  `bottom_mass_fraction` matches `_equilibrium_bottom_mass_fraction`**.
  Considered, but the short-circuit's reported value is now
  identically what that helper computes — the existing
  `test_homogeneous_short_circuit_fires_for_small_radii` confirms the
  path fires; pinning the equilibrium-formula equality would be
  testing the implementation, not a behavioural contract. Skipped.
- **Reflowing every wide markdown table** in lab notes / docstrings.
  Only the `RegimeResult` table was triggering ruff line-length
  errors; the rest are in markdown files where the line-length limit
  doesn't apply.

## Cross-references

- Phase 5 lab note — corrected in place; full audit trail of what
  shipped at `5bc89f3` plus the deltas applied here.
- Phase 4.1 lab note — same review-driven-fix pattern, where it was
  established that medium-priority semantics issues warrant their own
  `.1` commit rather than waiting for the next phase.
- `notebooks/02_regime_map.py` (Phase 6, future) — the consumer that
  the `RegimeResult` semantics table is written for.

## Next session

Unchanged: Phase 6 — deliverable notebooks 02 / 03 / 04 +
deliverable-5 design table.
