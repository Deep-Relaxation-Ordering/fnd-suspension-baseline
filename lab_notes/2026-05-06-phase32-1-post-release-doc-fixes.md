# 2026-05-06 - Phase 32.1: post-release doc fixes

*Endorsement Marker: Local stewardship - U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Post-release documentation pass after `pilot-v0.4` and the two tutorial
batches. The release tag stays at `9118cd2`: these are documentation
repairs and tutorial-status reconciliations on `main`, not a package
version bump and not a retag.

The pass follows the Phase 8.1 pattern: keep the published release
reference stable, repair downstream prose and indexes, and leave a
small lab-note trail so future release audits do not have to infer why
post-tag docs changed.

## What was done

### Release-pin backfill

Backfilled the `pilot-v0.4` commit row in:

- [`docs/release-notes/v0.4.md`](../docs/release-notes/v0.4.md)
- [`lab_notes/2026-05-06-phase32-pilot-v0-4-release.md`](2026-05-06-phase32-pilot-v0-4-release.md)

Both now record `9118cd2` explicitly instead of carrying the
`git rev-list -n 1 pilot-v0.4` command placeholder.

### Tutorial-status reconciliation

Updated the tutorial accessibility tables in:

- [`docs/tutorial-roadmap.md`](../docs/tutorial-roadmap.md)
- [`docs/deliverable-index.md`](../docs/deliverable-index.md)

The tables now list TUT-01 through TUT-06 as `ready`, with
`pilot-v0.4` as the release line they were validated against. This
matches Tutorial phase 1 (TUT-01 through TUT-05) and Tutorial phase 2
(Colab path plus TUT-06).

### Deliverable-index tail cleanup

Removed a duplicated preserved v0.2 caveats / "What `pilot-v0.3` would
change" tail from [`docs/deliverable-index.md`](../docs/deliverable-index.md).
The historical v0.2 and v0.3 sections remain; the duplicate copy no
longer appears twice in the same cumulative closeout document.

### Stale tutorial lab-note pin

Updated [`lab_notes/2026-05-06-phase1-tutorials.md`](2026-05-06-phase1-tutorials.md)
to refer to the current `pilot-v0.4` tag target (`9118cd2`) rather than
the earlier Phase 32 release-ceremony commit (`a3b6107`).

## Decisions

| Decision | Rationale |
|---|---|
| No new version bump | No runtime, API, package metadata, or release artefact content changed. |
| No new tag | Re-tagging `pilot-v0.4` would mutate a published reference; a `pilot-v0.4.1` tag would be heavier than this documentation repair. |
| Keep tutorial surfaces outside §6 deliverables | Tutorials are accessibility surfaces. They can be ready and linked without changing the breakout-note §6 deliverable count. |
| Add a Phase 32.1 lab note | This mirrors the earlier `.1` post-release repair pattern and makes the doc-only provenance explicit. |

## Verification

```bash
git rev-list -n 1 pilot-v0.4
# 9118cd2be9f948d826b0e90f07a4d47a527492f9

rg -n 'git rev-list -n 1 pilot-v0\.4|pilot-v0\.4` tag target \(`git rev-list -n 1 pilot-v0\.4`\)' \
  docs/release-notes/v0.4.md \
  lab_notes/2026-05-06-phase32-pilot-v0-4-release.md
# no output

git diff --check
# clean
```

No Python tests were rerun for this pass; the touched files are
documentation and lab-note surfaces only.

## Cross-references

- [Phase 32 release note](2026-05-06-phase32-pilot-v0-4-release.md)
  - the release ceremony this fixes downstream.
- [Tutorial phase 1](2026-05-06-phase1-tutorials.md) and
  [Tutorial phase 2](2026-05-06-phase2-tutorials.md) - the tutorial
  batches whose status tables are reconciled here.
- [Phase 8.1](2026-04-28-phase8-1-post-release-doc-fixes.md) - the
  earlier post-release doc-fix pattern.
