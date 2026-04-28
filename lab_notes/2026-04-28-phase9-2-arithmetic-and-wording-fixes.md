# 2026-04-28 — Phase 9.2: arithmetic and wording fixes

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Post-merge review of `82f27d0` (Phase 9.1) caught two low-priority
follow-ups. One arithmetic mismatch and one over-claim about
documentation contents. Same review-driven-fix pattern as the rest
of the `.x` chain.

## What was done

### Bug 1 — `65 % / 4239` arithmetic mismatch (low)

`docs/findings-process.md` and the Phase 9 lab note both said "65 %
of the §5 grid (4239 / 6300 cells) determined analytically". The
two numbers don't agree:

- 4239 / 6300 = 67.3 %
- 65 % corresponds to 4106 / 6300 — which is `840 + 3266 = 4106`,
  i.e. the two short-circuits *without* the asymptotic-sedimentation
  fallback.

`docs/findings-physics.md` already used "Two-thirds of the §5 grid
(4239 / 6300 cells)", which is internally consistent. Fixed by
unifying on **67 % / 4239 cells** (which includes the asymptotic
fallback as analytic, alongside the two short-circuits) in both
findings-process.md and the Phase 9 lab note.

The choice between "65 % / 4106" and "67 % / 4239" is a grouping
decision: is the asymptotic-sedimentation fallback "analytic" or
"Method C"? It runs in `fokker_planck.py` so structurally it is
Method C, but its output is closed-form (no `expm_multiply`), so
operationally it is analytic. The "67 % including fallback"
grouping matches how the cost story actually plays out — the
fallback is sub-millisecond per cell, indistinguishable from the
short-circuits in wall-time terms, and the 33 % / 150-min cost is
entirely set by the resolved-mesh path. Documenting "Method C
asymptotic fallback" as analytic therefore matches the cost
narrative the document is making.

### Bug 2 — "the document includes the queries used" (low)

The Phase 9 lab note said `findings-physics.md` "includes the
queries used" to extract its numbers. It doesn't — it has the
reproducible numbers and references to which `classify_cell`
execution path produced each quoted figure, but not literal Python
query snippets.

Fixed: the lab note now reads "All numbers in `findings-physics.md`
are reproducible from the §5 cache via short queries against
`regime_map.results_to_grid`; the document spells out which path of
`classify_cell` produces each quoted figure." This accurately
describes the document's traceability without overpromising.

## Decisions

| Decision | Rationale |
|---|---|
| 67 % / 4239 (asymptotic fallback as analytic), not 65 % / 4106 (short-circuits only) | The asymptotic-sedimentation fallback is sub-millisecond and produces closed-form output; in the cost-narrative the document is making, it groups with the short-circuits, not with the resolved-mesh PDE solve. The findings-physics.md table already used this grouping. |
| Did not add literal Python query snippets to findings-physics.md | The numbers are reproducible from the cache; adding 6-8 inline code blocks would clutter the prose without adding traceability beyond "look at the cache and the result_to_grid output". The lab-note wording is the cheaper fix. |
| Did not increment any version numbers or re-tag | Same as 8.1, 9, 9.1: post-release narrative. |

## Verification

```
HEAD before this pass:  82f27d0e6c5de8bbf23a9e8eed0534259d3fd736
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
92 passed
$ ruff check src/ tests/ notebooks/
All checks passed!
$ grep -nE "65 ?%|two-thirds|4239|4106" docs/findings-physics.md docs/findings-process.md lab_notes/2026-04-28-phase9-findings-narrative.md
docs/findings-physics.md:215:**Two-thirds of the §5 grid (4239 / 6300 cells) is determined
docs/findings-process.md:102:**Cost saved:** 67 % of the §5 grid (4239 / 6300 cells; ...
lab_notes/2026-04-28-phase9-findings-narrative.md:60:- Orchestration cost mix: 67 % of the grid (4239 / 6300 cells)
```

All three references now agree on 67 % / two-thirds / 4239.

## Cross-references

- Phase 9 lab note — corrected in place; the original 65 %/4239
  mismatch + "queries used" claim are resolved.
- Phase 9.1 lab note — the prior corrections pass; this one
  follows the same pattern at smaller scope.
