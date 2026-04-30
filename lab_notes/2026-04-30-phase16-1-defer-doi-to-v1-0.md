# Phase 16.1 — Defer Zenodo DOI minting to `pilot-v1.0`

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 16 (commit `c7d6aaf`) shipped FAIR metadata for `pilot-v0.2.1`
with DOI fields left as `TODO(v0.2.2)` placeholders. The plan was to
push the `pilot-v0.2.1` tag, let the Zenodo–GitHub integration mint
the DOI, then patch the resolved DOI into `CITATION.cff` and
`codemeta.json` in a tiny `0.2.2` follow-up.

After review, the decision was changed: **defer DOI minting to the
`pilot-v1.0` release.** The v0.2.x series is a pre-v1.0 pilot with a
deliberately unstable physics scope — aggregation, wall hydrodynamics,
capsule geometry, surfactants, and T-control are all out-of-scope and
slated for later cycles. Minting a citation-grade DOI now would either
need to be reissued at v1.0 (concept-DOI churn) or lock pre-v1.0
pilots into a citation surface they were not designed to carry.

## What was done

Forward-looking docs were repointed from `v0.2.2` to `v1.0`:

- `CITATION.cff` — replaced the `TODO(v0.2.2)` comment with a deferral
  note pointing to `pilot-v1.0` and this lab note.
- `codemeta.json` — `DOI status` property value rewritten from "TODO"
  to "Deferred to pilot-v1.0".
- `README.md` — layout block annotation and the "How to cite" section
  rewritten so the DOI deferral and the rationale (moving physics
  scope) are explicit. Until v1.0 the citation is the GitHub URL plus
  the release tag.
- `docs/release-notes/v0.2.md` — `## DOI status` section rewritten to
  state the deferral and the reason.
- `docs/work-plan-v0-2-1.md` — §1 FAIR-metadata table, §2 out-of-scope
  list, §3 DOI handling, and §5 risk register all repointed to v1.0.
  Section 3 in particular now explains *why* deferral is the right
  call rather than the original two-step `0.2.1 → 0.2.2` path.

The Phase 16 lab note itself is left as a historical record — its
"Decisions" table captures the state at Phase 16 closeout, which this
Phase 16.1 note now amends.

## Decisions

| Decision | Rationale |
|---|---|
| Defer Zenodo DOI to `pilot-v1.0` | Pre-v1.0 pilots have a moving physics scope; a citation-grade DOI should not be minted against a deliberately unstable surface. Avoids concept-DOI churn at v1.0. |
| Remove DOI TODO placeholders rather than keep them | Placeholders rot silently; explicit deferral notes pointing at this lab note are auditable. |
| Leave the Phase 16 lab note untouched | Lab notes are historical session records. The Phase 16.1 note records the decision change; readers follow the chain. |
| No tag rename or rewrite | `pilot-v0.2.1` does not yet exist on `origin`; nothing to rewrite. The next tag push will reflect the new metadata directly. |

## Verification

```sh
.venv/bin/python -m pytest -q
# 135 passed

.venv/bin/python -m ruff check .
# All checks passed!

.venv/bin/cffconvert --validate -i CITATION.cff
# Citation metadata are valid according to schema version 1.2.0.

.venv/bin/python -c "import json; json.load(open('codemeta.json'))"
# parses cleanly

git diff --check
# clean
```

HEAD before Phase 16.1: `c7d6aaff75fc4d1a2ad1f1bff750e09cb75d73f3`.

## What was not done

- No physics, no cache regeneration, no notebook reruns.
- No version bump in `pyproject.toml` — Phase 16.1 is documentation-
  only and ships under the `pilot-v0.2.1` version.
- No edits to the Phase 16 lab note (historical record).

## Next step

Tag-push of `pilot-v0.2.1` is now the only remaining release action.
DOI minting will happen at the v1.0 release boundary, not before.

## Cross-references

- [Phase 16 lab note](2026-04-30-phase16-fair-metadata-and-v0-2-closeout.md)
  — original FAIR-metadata phase.
- [`docs/work-plan-v0-2-1.md`](../docs/work-plan-v0-2-1.md) §3
  — updated DOI handling rationale.
- [`docs/release-notes/v0.2.md`](../docs/release-notes/v0.2.md)
  — v0.2 release narrative (with the updated DOI status section).
