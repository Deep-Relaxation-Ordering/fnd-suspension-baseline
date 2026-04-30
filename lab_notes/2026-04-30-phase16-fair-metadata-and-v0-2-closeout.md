# Phase 16 — FAIR metadata and v0.2 narrative closeout

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

`pilot-v0.2` is closed at
`dfbb94d34cb250a87ff9e5eb1ae286f8352d0e08`. Phase 16 is a metadata-only
`0.2.1` patch on top of that release: no physics changes, no cache
regeneration, and no notebook reruns.

The scope is recorded in
[`docs/work-plan-v0-2-1.md`](../docs/work-plan-v0-2-1.md).

## What was done

- Added [`CITATION.cff`](../CITATION.cff) using CFF 1.2.0.
- Added [`codemeta.json`](../codemeta.json) using CodeMeta /
  schema.org JSON-LD metadata.
- Added Frictionless Table Schema files under
  [`notebooks/data/schemas/`](../notebooks/data/schemas/).
- Added [`notebooks/data/README.md`](../notebooks/data/README.md)
  as the data artefact index and provenance surface.
- Added [`tests/test_data_schemas.py`](../tests/test_data_schemas.py)
  as the schema drift guard.
- Added [`docs/release-notes/v0.2.md`](../docs/release-notes/v0.2.md)
  as the v0.2-specific narrative closeout while keeping the findings
  documents cumulative.
- Added README citation guidance, deliverable-index schema links, and
  `pyproject.toml` metadata/URL updates.

## Decisions

| Decision | Rationale |
|---|---|
| Use Frictionless schema files with a local pytest validator | Keeps the metadata standard and avoids adding a heavy validation dependency just to catch CSV drift. |
| Keep DOI fields as TODOs | Zenodo mints the DOI only after the tag is pushed; patching DOI in `0.2.2` avoids rewriting tags. |
| Keep findings cumulative | Splitting v0.1 and v0.2 findings would double maintenance; the release note gives the v0.2-specific story. |
| Use the 2026-04-30 lab-note date | Phase 16 is being executed after the 2026-04-30 `pilot-v0.2` closeout; the proposed 2026-04-29 filename would be chronologically misleading. |

## Verification

```sh
.venv/bin/python -m pytest
# 135 passed

.venv/bin/python -m ruff check .
# All checks passed!

git diff --check
# clean
```

Metadata validators:

```sh
.venv/bin/cffconvert --validate -i CITATION.cff
# Citation metadata are valid according to schema version 1.2.0.

python -m json.tool codemeta.json
# clean

npx --yes codemeta-validator codemeta.json
# npm 404: package not found

npx --yes codemetar codemeta.json
# npm 404: package not found
```

No CodeMeta validator was available locally. The suggested npm
commands were attempted and both package names returned registry 404s,
so Phase 16 pins JSON parse validity plus the explicit metadata file
review in this note.

Dependency versions:

| Dependency | Version |
|---|---|
| Python | `3.13.7` |
| NumPy | `2.4.4` |
| SciPy | `1.17.1` |
| Matplotlib | `3.10.9` |

HEAD before Phase 16:
`dfbb94d34cb250a87ff9e5eb1ae286f8352d0e08`.

## What was not done

- No §5 cache regeneration.
- No notebook reruns.
- No DOI was added yet; this waits for the `pilot-v0.2.1` tag push and
  Zenodo minting.
- No v0.3 physics work.

## Next step

After review, tag and push `pilot-v0.2.1`, let Zenodo mint the DOI,
then patch the DOI into `CITATION.cff` and `codemeta.json` in a tiny
`0.2.2` follow-up.
