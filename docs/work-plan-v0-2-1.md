# Work plan — `pilot-v0.2.1`

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

| Field | Value |
|---|---|
| Status | **Implemented — validation clean; `pilot-v0.2.1` tag pending review.** FAIR metadata patch on top of `pilot-v0.2`. |
| Date | 2026-04-30 |
| Base tag | `pilot-v0.2` at `dfbb94d34cb250a87ff9e5eb1ae286f8352d0e08` |
| Target version | `0.2.1` |
| Scope class | Additive metadata and narrative closeout only |

This patch does not change physics, regenerate the §5 cache, rerun
notebooks, or introduce v0.3 features. It makes the already-shipped
v0.2 artefact easier to cite, index, validate, and reuse.

## 1. In Scope

### FAIR metadata

| File | Purpose | FAIR |
|---|---|---|
| `CITATION.cff` | CFF 1.2.0 citation metadata; DOI deferred to pilot-v1.0 (Phase 16.1) | F2, F3, R1.1 |
| `codemeta.json` | CodeMeta / schema.org JSON-LD software metadata | F2, I2, R1 |
| `notebooks/data/schemas/*.json` | Frictionless Table Schema for each committed CSV | I1, I2, R1.3 |
| `notebooks/data/README.md` | Data-file index, schema pointers, provenance lineage | F2, R1.2 |
| `tests/test_data_schemas.py` | Drift guard for CSV headers, row counts, and scalar values | R1 |

CSV schemas cover:

- `regime_map_grid.csv`
- `design_table_max_homogeneous_r.csv`
- `design_table_min_sedimented_r.csv`
- `design_table_polydispersity_room_T.csv`

### v0.2 narrative closeout

- `docs/release-notes/v0.2.md` — v0.2 release summary with links to
  the cumulative physics and process findings.
- README "How to cite" section pointing to `CITATION.cff`.
- `docs/deliverable-index.md` data-schema subsection.

### Version and lab note

- `pyproject.toml`: `0.2.0` → `0.2.1`, plus metadata URL and keyword
  expansion.
- `lab_notes/2026-04-30-phase16-fair-metadata-and-v0-2-closeout.md`.

## 2. Out of Scope

- No physics changes.
- No `regime_map_grid.csv` regeneration.
- No notebook re-runs.
- No split of cumulative findings into v0.1-only and v0.2-only
  documents. The v0.2-specific story lives in
  `docs/release-notes/v0.2.md` and in the existing v0.2 sections of
  the cumulative findings documents.
- No Zenodo DOI mint or DOI badge for the v0.2.x series — deferred to
  `pilot-v1.0` (Phase 16.1 decision; see lab note
  [`2026-04-30-phase16-1-defer-doi-to-v1-0.md`](../lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md)).
- No v0.3 features.

## 3. DOI Handling

DOI minting is deferred to the `pilot-v1.0` release. Rationale:
the v0.2.x series is a pre-v1.0 pilot with a deliberately unstable
physics scope (aggregation, wall hydrodynamics, capsule geometry are
all out-of-scope and slated for later cycles). Minting a Zenodo DOI
now would either need to be reissued at v1.0 (concept-DOI churn) or
lock pre-v1.0 pilots into a citation surface they were not designed
to carry.

Until v1.0:

- `CITATION.cff` and `codemeta.json` carry no DOI field; both record
  the deferral reason in a comment / property.
- Citations use the GitHub repository URL plus the release tag
  (e.g. `pilot-v0.2.1`).
- Lab notes cross-reference the Phase 16.1 decision so the trail
  is auditable.

At v1.0 a DOI will be minted by enabling the Zenodo–GitHub integration
and pushing the v1.0 tag; the resolved DOI will then be added to
`CITATION.cff` and `codemeta.json` as part of the v1.0 release.

## 4. Acceptance Criteria

- [x] `cffconvert --validate` passes on `CITATION.cff`.
- [x] `codemeta.json` parses as JSON-LD and validates with an
      available CodeMeta validator, or the lab note records the local
      validator absence.
- [x] Every CSV in `notebooks/data/` has a Frictionless schema.
- [x] `pytest tests/test_data_schemas.py` passes.
- [x] Full suite passes.
- [x] `ruff check .` clean.
- [x] `docs/release-notes/v0.2.md` exists and cross-references
      findings + deliverable index.
- [x] `pyproject.toml` bumped to `0.2.1`.
- [x] Phase 16 lab note records dependency versions and HEAD SHA.

## 5. Risks

| Risk | Mitigation |
|---|---|
| DOI placeholder rot | Deferral to v1.0 means no placeholder lives in metadata; CITATION.cff and codemeta.json record the deferral reason directly. |
| Schema drift later | `tests/test_data_schemas.py` fails on CSV/header/value drift |
| Frictionless dependency weight | Use Frictionless schema files but validate with a small local pytest helper instead of adding a heavy dependency |
