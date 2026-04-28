# 2026-04-28 — Phase 8: `pilot-v0.1` release

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 8 of the breakout-note timeline (§9): the closeout. All five
§6 deliverables exist (Phase 7 closed the last of them); this commit
stamps the release tag, ships the §6 ↔ artefact mapping, and bumps
the package metadata to reflect that the pilot is feature-complete.

## What was done

### `pyproject.toml`

- `version`: `0.0.0` → `0.1.0`. The 0.x prefix flags the pilot
  status (per cd-rules §0.5 "Markdown first" the version is the
  authoritative artefact version, not the pin in the breakout note).
- `Development Status` classifier: `2 - Pre-Alpha` → `3 - Alpha`. The
  validation surface is complete and pinned by the test suite, but
  the breakout-note pin is still v0.2; promotion to `4 - Beta` would
  require breakout-note v1.0 closure.

### `docs/deliverable-index.md`

The §6 ↔ artefact map is the document the principal investigator
pastes into the breakout note's §6 section when finalising. Structure:

- Pin block (repo, tag, breakout-note commit, cd-rules commit, suite
  state at release).
- §6 deliverable table (one row per deliverable, with file paths and
  regen commands).
- §4.4 validation-surface map (one row per validation check with the
  pinning test).
- Cache-as-deliverable section (the 6300-cell `regime_map_grid.csv`
  is both deliverable 5's source and a derived artefact).
- Provenance trail (lab-notes index, pinned commit hashes).
- Known caveats (the four documented audit-gaps, none blocking v0.1).
- "What `pilot-v1.0` would change" section (interpolated thresholds,
  parallel walks, prose pass) for downstream planning.

### README

Status block rewritten as the release announcement. Phase 8 row
added to the phase-by-phase table. Pointer to the deliverable index.

### Tag and push

Annotated tag `pilot-v0.1` created on the release commit with a
message summarising the contents (set in the commit / tag dance below).
Push includes the commit and the tag together, so the GitHub release
view picks both up atomically.

## Decisions

| Decision | Rationale |
|---|---|
| `0.1.0`, not `1.0.0` | The breakout-note pin is v0.2 (not yet v1.0); promoting the artefact past the spec would be a misalignment. v0.1 is the canonical pilot-status mark. |
| `3 - Alpha`, not `4 - Beta` | Validation surface complete, but the audit-gap pins (`T_OBS_S` and the 5th depth value) are still tracked TODOs against the breakout-note table. Beta = "spec-aligned"; alpha = "feature-complete pending spec". |
| Single Phase-8 commit (not split into "version bump" + "deliverable index" + "tag") | Atomic. The tag points to a state where the version, the deliverable index, and the README all agree. |
| Annotated tag (`-a -m`) rather than lightweight tag | Annotated tags carry a message and an author, which makes them first-class objects in `git log --tags` and on the GitHub releases page. |
| Did not create a GitHub release page (UI / `gh release create`) | Out of scope for a numerical pilot; the tag + the deliverable index are the closeout. If a release page is needed later it can be created from the tag without re-tagging. |

## Verification

```
HEAD before this pass:  22a25a1ff7f342e7ed115e920e541c819983188c
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
92 passed in 3.41s
$ ruff check src/ tests/ notebooks/
All checks passed!
$ git tag --list pilot-v0.1
pilot-v0.1
```

## What was *not* done

- **GitHub release page** — see decision table above.
- **Resolution of the two audit-gap pins** (`T_OBS_S`, 5th depth) —
  documented in the deliverable index as known caveats. They wait
  on a breakout-note drift.
- **Interpolated design-table thresholds** — listed in
  "What `pilot-v1.0` would change". Not a v0.1 closure item.
- **Paper-grade prose pass on the notebooks** — same. Cite-grade
  prose rewrite is downstream paper-draft work.

## Cross-references

- breakout-note §6 (deliverables), §9 (timeline) — Phase 8 closes
  both: §6 has the artefact-mapping document, §9 ends with the
  release tag.
- All previous lab notes — collectively the audit trail from
  scaffold to release. Reverse-chronological from
  [`lab_notes/README.md`](README.md).
- [`docs/deliverable-index.md`](../docs/deliverable-index.md) — the
  §6 closeout document this lab note ships.
- [`docs/conventions.md`](../docs/conventions.md) — pinned
  dependencies (cd-rules, breakout-note) referenced from the
  deliverable index.

## Next session (post-v0.1)

Per the deliverable-index "What `pilot-v1.0` would change" list, the
follow-on work is presentation-grade rather than correctness-grade:

- Resolve audit-gap pins against the next breakout-note revision.
- Continuous-threshold design table.
- Parallel grid walk to bring the 150-min wall time down for
  parameter sensitivity studies.
- Notebook prose rewrites for paper-draft inclusion.

None of these block downstream consumption of `pilot-v0.1`.
