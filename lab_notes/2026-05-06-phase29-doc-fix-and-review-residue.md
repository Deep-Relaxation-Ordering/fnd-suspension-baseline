# Phase 29 — doc-fix bundle (S-slice nomenclature) + v0.3 review residue

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 28 closed item E (S5 — number-density polydispersity kernel)
at commit `7f84951`. Phase 29 closes the housekeeping bundle from
[`docs/work-plan-v0-4.md` §4](../docs/work-plan-v0-4.md):

- **Item L** — reconcile the S-slice nomenclature in
  [`docs/deliverable-index.md`](../docs/deliverable-index.md) §"What
  `pilot-v0.4` would change" and [`docs/release-notes/v0.3.md`](../docs/release-notes/v0.3.md)
  §"What `pilot-v0.4` would change" against
  [`docs/program-context.md` §3.1](../docs/program-context.md), the
  authoritative L1 slice menu.
- **Item H** — sweep v0.3 review residue: `TODO` / `FIXME` / `TBD`
  markers, stale forward-looking references, and unfilled placeholder
  values left behind by the v0.3 release ceremony.

## What was done

### Item L — S-slice nomenclature reconciliation

Two release-time documents listed candidate v0.4 tightenings under
S-slice labels (S3 = "Salinity correction", S4 = "pH-dependent
surface charge", S5 = "Multi-particle interaction", S6 = "Viscosity
T-dependence", S7 = "Full 3-D convection") that did not appear in
[`docs/program-context.md` §3.1](../docs/program-context.md). The
authoritative program-context labels are:

| Slice | Label (program-context §3.1) | v0.4 status |
|---|---|---|
| S1 | DLVO aggregation pre-screen (cell trustworthiness flag) | Out of scope (D3) |
| S2 | Stokes-Einstein corrections at sub-150-nm radii | Closed in v0.3 (Phase 18) |
| S3 | Hydrodynamic-shell calibration per FND class | Closed in v0.4 (Phase 27) |
| S4 | Capsule-geometry port (1-D radial, spherical) | Out of scope (D — parallel cycle) |
| S5 | Concentration-weighted polydispersity kernel | Closed in v0.4 (Phase 28) |
| S6 | Wall-hydrodynamic Faxén/Brenner corrections | Out of scope (defer to v0.5/v1.1) |
| S7 | Thermal control as a first-class axis | Out of scope (defer to v0.5/v1.0) |

- **[`docs/deliverable-index.md`](../docs/deliverable-index.md)
  §"What `pilot-v0.4` would change".** Replaced the mislabelled
  bullet list with a corrected list keyed to program-context §3.1,
  with each S-slice's v0.4 status (in / out / parallel cycle)
  inline. Added a tactical-follow-up subsection for the
  `lambda_se` → §5 axis question (which is *not* an S-slice but is
  a real candidate). Cross-referenced [`work-plan-v0-4.md` §1](../docs/work-plan-v0-4.md)
  for per-item decision rationale.
- **[`docs/release-notes/v0.3.md`](../docs/release-notes/v0.3.md)
  §"What `pilot-v0.4` would change".** Replaced the same
  mislabelled list with the program-context-corrected version. Added
  a labelled "Phase 29 doc-fix" callout above the list explaining
  that the S-slice labels were corrected post-release and that no
  release contract changed (the original mislabelled bullets remain
  recoverable from pre-Phase-29 git history if needed). This
  preserves the v0.3 release narrative's intent while correcting
  the labels that future readers would otherwise be misled by.

### Item H — v0.3 review residue sweep

A `grep -rn "TODO\|FIXME\|XXX\|TBD"` audit across `docs/`, `src/`,
`tests/`, and `notebooks/` surfaced:

- **`docs/release-notes/v0.3.md:18`** — `| Commit | TBD |` in the
  release pin table. The release commit is `ad48b0b` (the
  `pilot-v0.3` tag's pointed-to commit, verified via
  `git rev-list -n 1 pilot-v0.3`). **Filled in.**
- **`lab_notes/2026-05-01-phase24-pilot-v0-3-release.md:40`** —
  same `| Commit | TBD |` placeholder in the Phase 24 lab note's
  release-pin table. **Filled in** with `ad48b0b`.
- `docs/adr/0002-v0.3-spec-anchoring.md:262` — "the v0.3 → v1.0
  transition ADR (currently TBD)". **Left as-is** — the transition
  ADR genuinely does not exist yet; the TBD is honest forward-
  looking text, not stale state.
- `docs/work-plan-v0-3.md:19` — `[TBD]` mention in scaffold prose.
  **Left as-is** — frozen v0.3 contract artefact; editing
  retroactively would be a stealth substantive edit.
- No `TODO` / `FIXME` / `XXX` markers were found in source code or
  tests. The codebase is clean of debt markers.

The "What `pilot-v0.3` would change" sections at
[`deliverable-index.md:401, 463`](../docs/deliverable-index.md) are
preserved-for-reference v0.2 historical content (the deliverable
index keeps both v0.2 and v0.3 sections side by side); they are
not stale, they are intentionally archived.

## Decisions

| Decision | Rationale |
|---|---|
| Add a "Phase 29 doc-fix" callout to `release-notes/v0.3.md`, but not to `deliverable-index.md` | The release notes are an artefact pinned to the `pilot-v0.3` tag; readers may already have referenced the pre-Phase-29 version. A callout makes the post-release correction visible and explains why future readers will see different labels. The deliverable-index is a living document; no callout needed. |
| Treat `TBD` commit-hash placeholders as in-scope review residue (item H) | These are placeholder values waiting for the actual hash — exactly the kind of "fill in after the tag lands" debt that v0.3 release ceremony deliberately deferred. Phase 29's "sweep v0.3 review residue" line in the work plan §4 covers this. The fix is mechanical (look up the tag, fill in the hash). |
| Leave `docs/work-plan-v0-3.md` `[TBD]` references alone | Frozen contract artefact. Editing retroactively would amount to a stealth substantive edit. Pattern parallel to leaving `program-context.md` "deliverable-index 'What pilot-v0.3 would change'" supersession reference alone. |
| Leave `docs/adr/0002-v0.3-spec-anchoring.md` "TBD" alone | The TBD is honest forward-looking text ("v0.3 → v1.0 transition ADR currently TBD"). Filling it in would require writing the transition ADR, which is a v1.0-cycle deliverable. |
| Phase 29 ships as one phase covering both items L and H | [`work-plan-v0-4.md` §4](../docs/work-plan-v0-4.md) bundles them into a single tactical phase ("doc-fix + housekeeping bundle"). Both touch only documentation; they're cheaper as one commit than as two. No code surface is affected by either item. |

## Verification

```sh
.venv/bin/python -m pytest -q
# 189 passed, 0 skipped (no test changes; ensures lab-note edits
# didn't break anything via stale paths or symbol references)

.venv/bin/python -m ruff check .
# All checks passed!

git diff --check
# clean
```

HEAD before Phase 29: `7f84951` (Phase 28 — S5 number-density kernel).

## Risk register entries this phase activated

- **R-L1 (S-slice nomenclature discrepancy may indicate other stale
  S-slice references repo-wide).** Mitigation honoured via
  `grep -rn "S[1-9] — "` across `docs/` and `README.md`: only
  `deliverable-index.md` and `release-notes/v0.3.md` carried the
  mislabelled list. All other documents (program-context.md,
  work-plan-v0-4.md, ADR 0003, ADR 0002) were already
  consistent. No additional stale S-slice references found.

## What was not done

- **No code changes.** Phase 29 is documentation-only.
- **No retroactive edits to frozen v0.3 contract artefacts**
  beyond the TBD-commit-hash backfill (which is filling in
  *missing* information, not changing settled content). Specifically,
  `docs/work-plan-v0-3.md` is preserved as-is.
- **No deliverable-index v0.3 historical-section edit.** The
  preserved-for-reference v0.2 content under "v0.2 deliverable
  index (preserved for reference)" stays intact.
- **No new ADR.** Item L is a label-correction housekeeping task,
  not a decision worthy of an ADR. Per [`docs/adr/README.md` §"Conventions"](../docs/adr/README.md),
  ADRs are reserved for spec-anchoring and layer-defining decisions.

## Next step

**Phase 30 — Tactical bundle** (items I + J per
[`docs/work-plan-v0-4.md` §4](../docs/work-plan-v0-4.md)):

1. **Item I.** Switch `regime_map.walk_grid`'s `ProcessPoolExecutor`
   to a `multiprocessing.get_context("spawn")` context to remove
   the macOS fork-safety footgun documented in the v0.3 release
   notes §H.
2. **Item J.** Extend `time_evolution`'s root-finding API to
   support `top_to_bottom_ratio` crossings and parameter sweeps,
   preserving the v0.3 `crossing_time(bottom_mass_fraction = ...)`
   call signature byte-identically.

Effort: 1 session per §7. Risk register entries R-I1 and R-J1
apply.

## Cross-references

- [`docs/work-plan-v0-4.md` §1 items L and H](../docs/work-plan-v0-4.md)
  — the in-scope decisions this phase implements.
- [`docs/program-context.md` §3.1](../docs/program-context.md) —
  authoritative S1–S7 menu; the source of truth this doc-fix
  honours.
- [Phase 28 lab note](2026-05-06-phase28-s5-number-density-kernel.md)
  — predecessor v0.4 phase.
- [Phase 24 lab note](2026-05-01-phase24-pilot-v0-3-release.md) —
  v0.3 release ceremony; left a `Commit | TBD` placeholder that
  this phase backfills.
- [Pattern 11 in `findings-process.md`](../docs/findings-process.md#11-spec-pinning-at-commit-hash-precision)
  — spec pinning at commit-hash precision; the convention item L
  honours by treating program-context as authoritative.
