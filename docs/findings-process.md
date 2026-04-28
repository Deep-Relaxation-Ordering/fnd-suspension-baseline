# Process findings — engineering patterns that converged across the pilot

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

This document records the *engineering* patterns the
`fnd-suspension-baseline` pilot converged on between the scaffold
commit (`10d1d24`) and the `pilot-v0.1` release tag (`9a0fc76`). It is
practitioner-facing — written for whoever runs the next numerical
pilot in this group, or for a peer who wants to lift one of the
patterns into their own project.

The physics-side companion is [`findings-physics.md`](findings-physics.md);
the §6 artefact map is [`deliverable-index.md`](deliverable-index.md).

## 1. One phase per session, with `.1` review-driven follow-ups

| Pattern | Convention |
|---|---|
| Feature commit | `Phase N: <description>` — one numbered phase per working session, one lab note per phase. |
| Review-fix commit | `Phase N.1: <description>` — review feedback caught before the next phase starts. |
| Re-fix on the same review | `Phase N.2: <description>` — second-pass review. |

The pilot ran 9 numbered phases (0 through 8) and accumulated 6 `.1`
or `.2` commits across them. The lab-notes index in
[`../lab_notes/README.md`](../lab_notes/README.md) is the
reverse-chronological audit trail.

**Why it works:** a review hit on a `.0` commit gets fixed in a `.1`
commit *before* the next phase consumes the surface. By the time
Phase 7 starts depending on `regime_map.classify_cell`, the Phase
5.1 boundary-value `top_to_bottom_ratio` is already in. The pattern
avoids the "review feedback piles up at the end" trap.

**Cost:** more commits per session. Acceptable for a pilot where
traceability matters more than commit-count cosmetics.

## 2. Cache as a first-class deliverable

The full §5 sweep is **6300 cells × ~150 min wall time**. Phase 6
checked the resulting CSV (770 KB → corrected to 612 KB / 598 KiB
in Phase 7.1) into git as
[`../notebooks/data/regime_map_grid.csv`](../notebooks/data/regime_map_grid.csv).

**Why it works:**

- A fresh clone can render every deliverable figure in seconds.
- The CSV *is* deliverable 5 (the design table); checking in the
  data and the data-derived figures together keeps them
  bit-consistent.
- The notebook always works top-to-bottom — no "click here, wait 2
  hours, then come back".

**When this fails:** if the parameter grid is high-dimensional
enough that the cache exceeds GitHub's 100 MB warning. For 6300
rows × 10 columns × float-precision repr, 600 KB is comfortable. A
finer §5 grid (300 radii × 70 temperatures × …) would force HDF5 +
git-lfs.

**Pattern variant:** notebook 02's coarse-fallback walk renders the
deliverable even if the cache is missing. The figure is approximate
in that mode, but the notebook never fails to run.

## 3. Audit-gap pins for unresolved spec values

When the upstream spec (the breakout note) doesn't yet pin a
specific value, the pilot picks a defensible default and documents
the audit gap *in place*. Two examples:

- `scan_grid.T_OBS_S` — six observation times (1 min, 10 min, 1 h,
  4 h, 1 d, 1 w). Hand-picked physically meaningful durations; the
  comment explicitly notes "cross-check against the breakout-note
  §5 table at the next spec drift".
- `scan_grid.DEPTHS_M` — five sample depths (0.1, 0.5, 1, 2, 10 mm).
  Same pattern: experimentally-motivated default, audit-gap pin.

**Why it works:** the pilot can ship without blocking on every spec
ambiguity. The audit gaps surface in the deliverable index's
"Known caveats" section, so reviewers know to look at them at the
next spec revision.

**Anti-pattern to avoid:** picking a default and *not* documenting
the gap. The default then ossifies into "what we use" without
anyone checking against the spec.

## 4. Orchestration short-circuits before the expensive method

`regime_map.classify_cell` walks three execution paths in cost order:

1. **Homogeneous-corner short-circuit**: if `exp(-h/ℓ_g) ≥ 0.95`,
   the regime is `homogeneous` regardless of `t_obs` — the
   finite-time ratio from uniform IC is bounded in `[eq_ratio, 1]`
   and so always meets the threshold. No PDE solve.
2. **Equilibrated-corner short-circuit**: if `t_obs ≥ 5·t_relax`,
   the analytic equilibrium values are within 0.7 % of the
   finite-time values; use them directly. No PDE solve.
3. **Method C with mesh floor at 10 nm**: only for genuinely
   transient cells, and bumped above the production 1-nm floor
   so the high-Pe corner routes through the asymptotic fallback
   rather than a refined-mesh `expm_multiply`.

**Cost saved:** 67 % of the §5 grid (4239 / 6300 cells; the two
short-circuits plus the asymptotic-sedimentation fallback) is
determined analytically; only 33 % (2061 / 6300) goes through
Method C resolved-mesh. The walk takes 150 min instead of an
estimated 6+ hours without these.

Post-release adversarial review added one extra guard to this pattern:
the resolved-Method-C path now keeps the 120-cell first pass for
runtime, but reruns cells near the `c(h)/c(0)` thresholds at the
240-cell Method-C default before assigning labels. That repaired 8
near-boundary `homogeneous` labels without forcing the whole §5 cache
through a pathological all-240-cell sweep.

**Pattern signature:** every short-circuit is a *physics* statement
about the regime in which the analytic answer dominates the
numerical correction. They're not engineering hacks — each one is a
provable bound.

## 5. Coordinate-indexed reshape (`RegimeGrid`)

A flat list of `RegimeResult` from `walk_grid` reshapes naturally
into a 4-D `(n_r, n_T, n_h, n_t)` array — *if* the iteration order
is fixed. Phase 6 used position-based reshape in the notebook,
relying on the walker's `r → T → h → t_obs` order. A sorted CSV
(or a parallelised walk that returns out-of-order) would silently
mis-align axes and render plausible-looking but wrong figures.

Phase 7 fixed this with `regime_map.results_to_grid(results)`:

- Reshape by *coordinate value*, not row position.
- Raise on missing or duplicate cells.
- Return a frozen `RegimeGrid` dataclass (with the canonical
  sorted axes alongside the channel arrays).

**Pattern signature:** when ingesting a flat list into an N-D
array, never trust iteration order. The coordinate-indexed reshape
is one extra `dict` lookup per cell — negligible compared to the
silent-failure cost.

**Generalisation:** any time you find yourself relying on
"upstream produces this in the right order", build the destination
by coordinate value instead.

## 6. Test design tiering

Three test layers, each with its own runtime and concern:

| Layer | Example | Runtime | What it pins |
|---|---|---|---|
| Kernel sanity | `test_adaptive_timestep_pure_brownian_uses_box_diffusion_scale` | < 1 ms | Math correctness of one function |
| Physics validation | `test_method_b_long_time_matches_barometric` | ~0.4 s | Method against analytic limit |
| Cross-method consistency | `test_method_b_c_time_dependent_moments_agree` | ~1 s | Two methods on the same cell |

The current post-release pilot suite (94 tests; 92 at `pilot-v0.1`)
runs in ~3 s. Slow physics tests use *CI-time* parameter overrides
(e.g. `n_cells=60`, `t_factor=10`) with an explicit comment that
production scans should use the defaults — the test pins the
contract, not the resolution.

**Pattern signature:** if a test is slower than ~5 s, it's probably
testing the wrong thing. Either the contract is at the wrong layer
(use a faster surrogate at the kernel level) or the parameters are
overspecified (use a smaller representative cell).

## 7. Bit-exact serialization with `repr()`

The CSV cache uses Python's `repr()` for floats — guaranteed by the
language to be a round-trippable string for `float`. Two pitfalls
the writer learned to handle:

- **Numpy scalars**: `repr(np.float64(5e-9))` is the string
  `'np.float64(5e-09)'` — *not* parseable by `float()`. The fix is
  to coerce numpy scalars to Python floats via `.item()` before
  reading their repr. The reader tolerates legacy
  `np.float64(...)` wrappers so a one-time-bad cache can be repaired
  by load-and-rewrite without regenerating.
- **Line endings**: Python's `csv` module defaults to `\r\n`, which
  triggers `git diff --check` "trailing whitespace" warnings on every
  row of a checked-in CSV. Forcing `lineterminator="\n"` keeps the
  diff clean.

**Pattern signature:** if you're checking in serialized numerical
data, eyeball the bytes once. Both gotchas above were invisible to
the test suite — the cache loaded fine — but caught by `git diff
--check`.

## 8. Lab notes as the audit trail

One Markdown lab note per working session, named
`YYYY-MM-DD-<topic>.md`, indexed in
[`../lab_notes/README.md`](../lab_notes/README.md). Each note
follows the same structure:

1. **Context** — what session this was, what motivated it.
2. **What was done** — file-by-file summary of the changes.
3. **Decisions** — table of choice + rationale.
4. **Verification** — exact `pytest` / `ruff` output, HEAD SHA,
   dependency versions.
5. **What was *not* done** — explicit deferrals.
6. **Cross-references** — links to the spec sections + earlier
   notes the change extends.
7. **Next session** — pointer to what comes next.

**Why it works:** the verification block contains the *exact* test
output and dependency versions — anyone six months later can
reproduce that exact state. The "what was not done" section makes
deferrals first-class rather than implicit. The "decisions" table
is searchable for "why X" questions.

**Cost:** ~10 minutes of writing per session. Cheaper than
re-deriving the rationale from a code review six months later.

## 9. CI-time vs. production parameter overrides

The §4.4 `test_method_a_c_equilibrium_inside_b_envelope_resolved_mesh`
test (Phase 4.1) explicitly uses `n_cells=60, t_factor=10` rather
than the production defaults `n_cells=240, t_factor=50`:

```python
method_c = equilibrium_cell(
    r, temperature_kelvin, h,
    n_cells=60,
    t_factor=10.0,
)
```

The docstring spells out: "These are CI-time settings: at these
values the test runs in well under a second while still resolving
each Method-A reference to better than ~2·10⁻⁴ relative error.
Production scans (`regime_map.py`) should use the `equilibrium_cell`
defaults."

**Pattern signature:** if a test has knobs that production calls
don't, document them as test-time choices in the test docstring,
not in a comment that drifts.

## 10. Notebook fallback patterns

Three different cache-dependence regimes across the four notebooks:

- **Notebook 02 — full fallback**: reads
  `notebooks/data/regime_map_grid.csv` if it exists, otherwise
  walks a coarse 270-cell grid live. Every figure is renderable on
  a fresh clone.
- **Notebook 03 — partial fallback**: figure 1 (Method-A primitives
  vs T) is computed directly from `analytical.py` and never needs
  the cache. Figures 2 and 3 (per-T regime panels and the
  homogeneous-radius envelope) require the cache and are *skipped
  with a printed message* if it is missing — Method-C regeneration
  is too expensive to run inline.
- **Notebook 04 — cache required**: raises `FileNotFoundError` if
  the cache is missing, because the design table is structurally a
  *projection* of the §5 cache; without the cache there is nothing
  to project.

**Pattern signature:** decide per notebook (and per figure within
a notebook) whether the artefact is renderable without the cache.
Self-contained-with-fallback for cheap visualisations,
skip-with-message for expensive cache-derived figures, and
hard-error for derived artefacts that have no meaningful fallback.
State the choice in the notebook header.

## 11. Spec pinning at commit-hash precision

`docs/conventions.md` pins both the cd-rules dependency and the
breakout-note dependency to specific commit hashes:

| Pin | Commit | Date |
|---|---|---|
| cd-rules | `ee01c80352dd8446f189c3159a3d9e347463902c` | 2026-04-17 |
| breakout-note | `3b7b18af7bd1739f3cb7b3360d2b75264dd5ad07` | 2026-04-27 |

When the upstream moves, the pin is updated in a dedicated commit
with a lab-note explanation. This is the convention `cd-rules` §0.10
sets out and the pilot inherits.

**Pattern signature:** never write "version v0.2" in a spec
reference. Versions are mutable in the upstream's mind; commit
hashes are not.

## 12. README-as-status-report

The repo's [`README.md`](../README.md) carries a phase-by-phase
table that's updated every commit. The "Status" prose block at the
top is also rewritten each phase. By the time the README claims a
state, the corresponding lab note backs it.

**Why it works:** the README is the first thing a reviewer reads.
Keeping it bit-exact with the actual repo state means the reviewer
trusts what they see; out-of-date READMEs train reviewers to
ignore them.

**Cost:** ~2 minutes per phase to bump the status block. Trivial.

## 13. Endorsement marker on every authored document

Every Markdown file in this repo opens with the cd-rules §0.7
endorsement marker:

```markdown
*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*
```

**Why it works:** organisational provenance is bound to the
document, not to a sidecar metadata file. If a single file gets
copied out (paper draft, slides, etc.), the marker travels with it.

## Failure modes the patterns avoided

For each of the thirteen patterns above, the failure mode it avoided
in this pilot:

| Pattern | Failure averted |
|---|---|
| `.1` review-fix discipline | `top_to_bottom_ratio` cell-average proxy slipping into Phase 5's classifier and silently mis-classifying cells near the §5.1 threshold |
| Cache as deliverable | 150-min onboarding wait for every reviewer |
| Audit-gap pins | Default `T_OBS_S` ossifying as "what we use" without checking against §5 |
| Orchestration short-circuits | 6+ hours per §5 walk → every grid update needs an overnight |
| `RegimeGrid` reshape | A sorted CSV silently mis-aligning all the figures |
| Test tiering | A 30-second physics test in the kernel suite blocking commits |
| Bit-exact `repr()` round-trip | Lossy CSVs corrupting the cache silently between commits |
| Lab notes audit trail | "Why is `t_factor = 50`?" with no documented answer |
| CI-time overrides | The §4.4 test running for 30 s in CI |
| Notebook fallbacks | Notebook 02 unable to render on a fresh clone |
| Spec pinning | "v0.2" of the breakout note silently changing under our feet |
| README-as-status | Reviewer ignoring README claims because they're stale |
| Endorsement marker | Documents losing organisational provenance when paper-copied |

Each was a real risk; the pilot caught and documented each one.

## What I'd carry forward to the next pilot

The patterns above. Most of them generalise. The two that are
specific to this project:

- **`scan_grid` as a single source of truth** for the parameter axes
  (Phase 2.5 and Phase 5 added this). Generalises to any pilot with a
  Cartesian-product parameter scan.
- **The Markdown deliverable index** as the §6 closeout document.
  Generalises to any pilot whose spec has a numbered deliverable list.

The two that are unlikely to be reusable:

- **`min_resolvable_dz_m = 10 nm`** in `regime_map`. This is
  specific to the diamond-water boundary-layer scaling and the §5
  Method-C cost profile. Other physics will have different
  thresholds.
- **`t_factor = 50`** in `equilibrium_cell`. Same — empirically
  tuned to the §5 grid's slowest mode.

## Cross-references

- [`findings-physics.md`](findings-physics.md) — physics-side
  findings.
- [`deliverable-index.md`](deliverable-index.md) — §6 ↔ artefact
  map.
- [`conventions.md`](conventions.md) — cd-rules and breakout-note
  pins.
- [`../lab_notes/README.md`](../lab_notes/README.md) — phase-by-phase
  audit trail.
