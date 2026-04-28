# 2026-04-28 — Phase 9.1: findings narrative corrections

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Post-merge review of the Phase-9 findings narrative (`8540e08`) caught
four issues. One is a real physics-statement error, one is a numeric
mistake against the cache, one is an over-claim about notebook 03's
fallback, and one is a section-count typo. Same review-driven-fix
pattern as 5.1 / 7.1 / 8.1.

## What was done

### Bug 1 — `Pe = 1` mis-label for the homogeneous-edge boundary (high)

Both `docs/findings-physics.md` and the Phase-9 lab note labelled the
homogeneous-edge boundary as "Pe = 1". The formula and numbers used
the §5.1 ratio threshold ``exp(-h/ℓ_g) = 0.95``, which gives
``h/ℓ_g = -ln(0.95) ≈ 0.0513``, *not* the Péclet-unity condition
``h/ℓ_g = 1`` (which would correspond to ``c(h)/c(0) = e⁻¹ ≈
0.37`` — well inside the stratified band).

The cube-root scaling ``r ∝ h^{-1/3}`` is correct in either case;
only the label was wrong. Fixed in three places:

- `docs/findings-physics.md` section header "## The Pe = 1 boundary
  follows `r ∝ h^{-1/3}`" → "## The homogeneous-edge boundary
  follows `r ∝ h^{-1/3}`", with an explicit parenthetical
  distinguishing the threshold from Pe = 1.
- `docs/findings-physics.md` "Smallest sedimented radius at 1 hour"
  table column "analytic Pe = 1 r at h" → "analytic homog-edge r at
  h"; following prose updated to match. Numerical entries also
  re-checked against the analytic formula (the rounding shifted by
  1-2 nm in two cells).
- `docs/findings-physics.md` cross-references section: "Pe=1 scaling
  findings" → "homogeneous-edge scaling findings".
- `lab_notes/2026-04-28-phase9-findings-narrative.md` summary
  bullet: "Pe = 1 boundary scaling" → "Homogeneous-edge boundary
  scaling (`exp(-h/ℓ_g) = 0.95` ⇒ `h/ℓ_g ≈ 0.051`, *not* Pe = 1)".

### Bug 2 — time-evolution table had wrong values for two rows (medium)

The `Time matters more than temperature` table at room T / h = 1 mm
listed the wrong regime counts for the 1 h and 4 h rows. Cache values
verified by re-running `walk_grid` query at `(T = 298.15 K, h = 1 mm)`:

| t_obs | committed (wrong) | cache (correct) |
|---|---|---|
| 1 h | 5 H / 11 S / 14 s | 5 H / 10 S / 15 s |
| 4 h | 5 H / 10 S / 15 s | 4 H / 9 S / 17 s |

Other rows (1 min, 10 min, 1 d, 1 w) were correct already.

The table header also said "5 cells × 30 radii" but the row sums to
30, not 150 — the slice is *one* depth × 30 radii, not five depths
× 30 radii. Header rewritten to "the §5 r-axis (30 radii) at fixed
(T, h, t_obs)" and the parenthetical clarified to "each row sums to
30 = number of §5 radii".

### Bug 3 — notebook 03 fallback claim was an over-claim (medium)

`docs/findings-process.md` section 10 said notebook 03 had the same
"coarse 270-cell fallback" as notebook 02. That is wrong: notebook
03's figure 1 (Method-A primitives vs T) computes directly from
`analytical.py` and never needs the cache; figures 2 and 3 (per-T
regime panels and the homogeneous-radius envelope) are *skipped
with a printed message* if the cache is missing — Method-C
regeneration is too expensive to run inline.

Section 10 rewritten as a three-bullet list documenting the three
distinct cache-dependence regimes (full fallback / partial fallback
+ skip / hard-error) across notebooks 02 / 03 / 04. The pattern
signature is now correctly stated.

### Bug 4 — section count typo (low)

`docs/findings-process.md` had 13 numbered pattern sections (1–13)
plus an un-numbered concluding "Failure modes the patterns avoided"
table, which had been mis-numbered as section 14. The text in the
Phase-9 lab note said "Fourteen patterns".

Fixed: section 14 heading dropped (now "## Failure modes the
patterns avoided" without the number); lab-note text changed to
"Thirteen patterns ... plus a closing summary table".

## Decisions

| Decision | Rationale |
|---|---|
| Re-checked the 1 h / 4 h numbers against a live cache query, not by re-deriving | The cache is the canonical truth; re-deriving would have invited the same mis-extraction that produced the wrong numbers in Phase 9. |
| Changed the table header to "30 radii at fixed (T, h, t_obs)" rather than "1 mm slice × 30 radii" | More general phrasing — same words could be reused if any future row of this table is at a different fixed h. |
| Notebook 03 description now lists figures 1 / 2 / 3 by their cache-dependence individually | The reviewer's correction is a real distinction (per-figure, not per-notebook); over-summarising would lose it. |
| Numeric entries in the "Smallest sedimented" table also re-checked, not just the column label | The column label was wrong, but the numbers in it should still be the analytic homogeneous-edge radii. Spot-checks against the formula caught a 1-2 nm rounding drift in three cells. |
| `pilot-v0.1` tag stays at `9a0fc76` | Same rationale as Phase 8.1 / Phase 9: the tag captures the release content; post-release narrative updates accumulate on `main` without re-tagging. |

## Verification

```
HEAD before this pass:  8540e080c6845ad2c353613f543ab2bd6967b957
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
92 passed in 3.47s
$ ruff check src/ tests/ notebooks/
All checks passed!
```

Documentation-only fixes; the test suite, the §5 cache, and every
shipped figure are unchanged.

## Cross-references

- Phase 9 lab note — what shipped at `8540e08`. The Phase-9 note's
  Pe = 1 wording is corrected in place; the table-numerics fix
  doesn't change anything in the Phase-9 note itself (the wrong
  numbers were only in the published `findings-physics.md`).
- `docs/findings-physics.md` and `docs/findings-process.md` — the
  two documents corrected.
- Phase 5.1 / 7.1 / 8.1 lab notes — the established
  review-driven-fix pattern this note continues.

## Next session

Unchanged from the Phase 9 list — sibling-repo work
(breakout-note §6 + results-section update), audit-gap pin
resolution at the next breakout-note drift, continuous-threshold
design table, parallel grid walk. None blocked by `pilot-v0.1`.
