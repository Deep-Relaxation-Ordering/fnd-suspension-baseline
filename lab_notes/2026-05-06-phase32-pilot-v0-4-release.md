# Phase 32 — `pilot-v0.4` release

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## What was done

Release ceremony for `pilot-v0.4`. All seven in-scope items (B, E,
H, I, J, K, L) were implemented and verified during Phases 27–31.
This phase is mechanical: version bumps, metadata updates,
release-note authorship, deliverable-index refresh, Pages landing
update, and the git tag. Mirrors [Phase 24 (v0.3 release)](2026-05-01-phase24-pilot-v0-3-release.md).

## Checklist

| Step | File / Action | Detail |
|---|---|---|
| 1 | [`pyproject.toml`](../pyproject.toml) | version `0.3.0` → `0.4.0`; release-notes URL → v0.4 |
| 2 | [`CITATION.cff`](../CITATION.cff) | version `0.3.0` → `0.4.0`; date `2026-05-01` → `2026-05-06`; abstract updated for v0.4 scope; cite-tag comment refreshed to `pilot-v0.4` |
| 3 | [`codemeta.json`](../codemeta.json) | version `0.4.0`; dates `2026-05-06`; description expanded for v0.4 scope; downloadUrl → `pilot-v0.4.zip`; tag identifier → `pilot-v0.4`; release-notes link → v0.4 |
| 4 | [`docs/release-notes/v0.4.md`](../docs/release-notes/v0.4.md) | New file. Release pin, scope delta (B / E / I / J / L+H), forward-compat contract, narrative closeout, DOI deferral, v0.5 candidates. |
| 5 | [`docs/deliverable-index.md`](../docs/deliverable-index.md) | Header updated to v0.4. Added v0.4 deliverable mapping (items 11–15). Preserved full v0.3 + v0.2 sections below as reference. Updated "What `pilot-v0.5` would change" with the open v1.0 punch-list (S1, S4, S6, S7 plus campaign D-PC-1). |
| 6 | [`README.md`](../README.md) | Status section rewritten: v0.4 paragraph first, then v0.3 / v0.2 / v0.1 retrospective. Phase table extended with the Phase 32 release row. |
| 7 | [`docs/index.html`](../docs/index.html) | Eyebrow / hero panel / status section / scope-delta table / open-repair callout / evidence-grid release-tag + release-notes cards / footer status all updated to v0.4. Test count `171 → 199`. v0.3 release-notes link kept as a carry-forward reference. |
| 8 | [`lab_notes/README.md`](README.md) | Added Phase 32 entry. |

## Verification

```text
$ .venv/bin/python -m pytest -q
199 passed in 272.99s

$ .venv/bin/python -m ruff check .
All checks passed!

$ .venv/bin/cffconvert --validate -i CITATION.cff
Citation metadata are valid according to schema version 1.2.0.

$ .venv/bin/python -c "import json; json.load(open('codemeta.json'))"
# (no output — valid JSON)

$ git diff --check
(clean)
```

## Release pin

| Field | Value |
|---|---|
| Tag | `pilot-v0.4` |
| Commit | `9118cd2` (`pilot-v0.4` tag target) |
| Package version | `0.4.0` |
| Test suite | `199 passed, 0 skipped` |
| Lint | `ruff check .` clean |
| Spec anchor | breakout-note v0.2 commit `3b7b18af` ([ADR 0003](../docs/adr/0003-v0.4-spec-anchoring.md)) |
| Predecessor | `pilot-v0.3` at `ad48b0b` |

## Forward-compat reminder

Zero-default paths (`lambda_se = 1.0`, `delta_shell_m = 0`,
`delta_T_assumed = 0.0 K`, `n_workers = 1`,
`weighting = "classification"`) reproduce the v0.3 §5 cache to
machine precision. Verified in
[Phase 31](2026-05-06-phase31-integration-audit-and-release-gap.md)
on a 24-cell focused subset, and pinned by the test suite
(`test_walk_grid_parallel_byte_identical_to_serial` plus the
Phase 28 / 30 byte-identity smoke tests).

## v0.4 scope summary

| Item | Phase | Module / Notebook | What it does |
|---|---|---|---|
| B (S3) | 27 | [`src/parameters.py`](../src/parameters.py), [`docs/delta_shell_calibration.md`](../docs/delta_shell_calibration.md) | Citation-anchored hydrodynamic-shell defaults per FND class; `ParticleGeometry.from_fnd_class` |
| E (S5) | 28 | [`src/polydispersity.py`](../src/polydispersity.py) | `lognormal_smear(weighting="number_density")` opt-in; per-regime `E[r│R]` and `E[r²│R]` |
| L | 29 | [`docs/deliverable-index.md`](../docs/deliverable-index.md), [`docs/release-notes/v0.3.md`](../docs/release-notes/v0.3.md) | S-slice nomenclature reconciled against `program-context.md` §3.1 |
| H | 29 | (multiple) | v0.3 review residue swept; `Commit | TBD` placeholders backfilled with `ad48b0b` |
| I | 30 | [`src/regime_map.py`](../src/regime_map.py) | `walk_grid` ProcessPoolExecutor → `multiprocessing.get_context("spawn")` for macOS fork-safety; stdin/heredoc guard |
| J | 30 | [`src/time_evolution.py`](../src/time_evolution.py) | `crossing_parameter(...)` parameter-sweep root-finder for `delta_shell_m` / `lambda_se` at fixed `t_obs` |
| K | 31 | [`notebooks/09_integration_audit.py`](../notebooks/09_integration_audit.py); Phase 31 lab note | Release-criterion gap audit against `program-context.md` §4.1 |

## Decisions

| Decision | Rationale |
|---|---|
| Bundle the Pages landing update into Phase 32 | The Pages page is the public-facing release surface; leaving it pointing at v0.3 while the rest of the repo says v0.4 would be misleading to external readers. The page rewrite touches release-pin metadata, scope-delta table, and open-repair callout — all release-time concerns. |
| Replace the v0.3 scope-delta table on the Pages page rather than appending | The "Scope delta vs pilot-v0.3" framing is what readers want at v0.4 release time. The v0.3 narrative is preserved via the `release-notes/v0.3.md` link. Leaving both tables would be visually noisy on a page already constrained by the cd-rules visual register. |
| Update `deliverable-index.md` "What `pilot-v0.5` would change" header rather than adding a new section | The previous heading was "What `pilot-v0.4` would change" — now that v0.4 is shipping, the same forward-looking section needs a renamed heading and updated bullets. The "preserved" v0.3 / v0.2 sections below it stay intact as historical reference. |
| Keep the codemeta.json `isBasedOn` pin at the v0.2 breakout-note commit | ADR 0003 D1 = Option 2 (stay on `3b7b18af`) carries forward through v0.4. The `isBasedOn` field reflects the spec anchor, not the implementation tag. Updating it would imply a re-anchor that did not happen. |
| Defer the actual `git tag pilot-v0.4` invocation to a Bash step inside Phase 32 (not the user) | Phase 24 precedent: the release ceremony's tag is part of the phase's automated checklist. The tag starts locally and is published only after the release-review findings are fixed. |
| Use the 2026-05-06 release date | Matches Phase 27–31 calendar dates; v0.4 cycle ran 2026-05-05 (Phase 25) → 2026-05-06 (Phases 26 → 32) — single working day for the implementation phases, consistent with the v0.3 working-tempo pattern. |

## What was not done

- **No Zenodo DOI mint.** D8 carried forward as resolved (hold to
  v1.0 per [Phase 16.1](2026-04-30-phase16-1-defer-doi-to-v1-0.md)).
  v0.4 is cited by GitHub URL and tag; the citation comment in
  `CITATION.cff` was refreshed to point at `pilot-v0.4` accordingly.
- **No notebook regeneration.** v0.4 ships kernel additions, not
  new design tables. v0.3's design tables remain authoritative
  under v0.4. Regenerating notebooks would only reflow figure
  metadata without changing pixel data or CSV content.
- **No new ADR.** Phase 32 is mechanical; the spec-anchoring and
  first-slice decisions for v0.4 were recorded in
  [ADR 0003](../docs/adr/0003-v0.4-spec-anchoring.md) (Phase 26).
- **No push during the initial Phase 32 ceremony.** The branch was
  committed and tagged locally first; publication happens after the
  release-review findings are resolved.
- **No release-criterion ADR.** v1.0 release criterion 4 (calibration
  ADR) is gated on the campaign existing (D-PC-1); it is in the
  v1.0 release path, not v0.4.

## Next step

The v0.4 cycle is closed. The natural next move is **opening the
v0.5 deliberation surfaces** (mirror of Phase 25 for v0.5):
SCAFFOLD work-plan-v0-5, ADR 0004 stub for spec-anchoring + first-
slice decisions. Candidate first slices for v0.5:

1. **S1 — DLVO aggregation pre-screen**, if upstream
   `Deep-Relaxation-Ordering/diamonds_in_water` v0.3 breakout note
   has landed by v0.5 cycle open. Closing S1 retires the
   `provisional = True` API contract.
2. **S6 — Wall-hydrodynamic Faxén/Brenner corrections**, if a
   sibling-repo breakout note exists.
3. **`lambda_se` → §5 scan axis** if the calibration-in-FND-band
   prerequisite (run as a pre-Phase-27-of-v0.5 step) shows working
   values ≤ 0.3.
4. **Concentration-weighted design-table notebook** (post-Phase-28
   follow-up) if the design-tool consumer exists.

The v0.5 first-slice ordering is genuinely open; it depends on
upstream breakout-note status and on whether D-PC-1 (campaign) has
moved by v0.5 cycle open.

## Cross-references

- [`docs/work-plan-v0-4.md`](../docs/work-plan-v0-4.md) — v0.4
  contract this release closes; remains in `docs/` as a release
  artefact alongside `work-plan-v0-2.md` and `work-plan-v0-3.md`.
- [`docs/adr/0003-v0.4-spec-anchoring.md`](../docs/adr/0003-v0.4-spec-anchoring.md)
  — the spec-anchoring decision this tag honours.
- [`docs/release-notes/v0.4.md`](../docs/release-notes/v0.4.md) —
  release narrative.
- [`docs/deliverable-index.md`](../docs/deliverable-index.md) —
  v0.4 §6 deliverable mapping.
- [Phase 24 lab note](2026-05-01-phase24-pilot-v0-3-release.md) —
  the v0.3 release ceremony this phase mirrors.
- [Phase 31 lab note](2026-05-06-phase31-integration-audit-and-release-gap.md)
  — integration audit + release-criterion gap audit that cleared
  this release.
- [Pattern 14 in `findings-process.md`](../docs/findings-process.md#14-forward-compatible-parameter-splits-via-zero-default-extension)
  — zero-default extension contract that v0.4's compatibility
  defaults honour against v0.3.
