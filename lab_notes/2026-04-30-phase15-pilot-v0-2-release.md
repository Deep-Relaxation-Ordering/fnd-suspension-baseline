# Phase 15 — `pilot-v0.2` release closeout

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 14 completed the last v0.2 implementation slice: log-normal
polydispersity smearing, notebook 05, and deliverable 6. Phase 15
closes the release by updating the narrative deliverables, recording
the experimental envelope, bumping the package version, and tagging
`pilot-v0.2`.

The v0.2 scope is anchored by
[`docs/adr/0001-v0.2-spec-anchoring.md`](../docs/adr/0001-v0.2-spec-anchoring.md).

## What was done

- Hardened notebook 05's deliverable-table builder so an all-masked
  future `(h, sigma_geom)` slice cannot raise from `np.nanargmax`.
- Updated [`docs/deliverable-index.md`](../docs/deliverable-index.md)
  for the `pilot-v0.2` tag, `0.2.0` package version, 133-test release
  suite, v0.2 cache schema, deliverable 6, and new validation surfaces.
- Extended [`docs/findings-physics.md`](../docs/findings-physics.md)
  with the Rayleigh convection caveat and polydispersity boundary
  interpretation.
- Extended [`docs/findings-process.md`](../docs/findings-process.md)
  with Pattern 14: forward-compatible parameter splits via
  zero-default extension.
- Added
  [`docs/experimental-envelope.md`](../docs/experimental-envelope.md)
  as the explicit Veto-2 closeout surface.
- Updated [`README.md`](../README.md), this lab-note index, the work
  plan status, and [`pyproject.toml`](../pyproject.toml).

## Release pin

| Item | Value |
|---|---|
| Release tag | `pilot-v0.2` |
| HEAD before release-tag pass | `0b35726b09c7d5fc0ec5582dd1563f646ab327ad` |
| Package version | `0.2.0` |
| v0.1 test count | `92 passed, 0 skipped` |
| v0.2 test count | `133 passed, 0 skipped` |
| Suite-count delta | `+41 tests` |
| Python | `3.13.7` |
| NumPy | `2.4.4` |
| SciPy | `1.17.1` |
| Matplotlib | `3.10.9` |

## Verification

```sh
.venv/bin/python -m pytest
# 133 passed

.venv/bin/python -m ruff check .
# All checks passed!

git diff --check
# clean
```

Notebook smoke runs:

```sh
MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python notebooks/01_baseline_validation.py
MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python notebooks/02_regime_map.py
MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python notebooks/03_parameter_scans.py
MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python notebooks/04_design_table.py
MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python notebooks/05_polydispersity_smearing.py
# all completed successfully
```

## Decisions

| Decision | Rationale |
|---|---|
| Keep Development Status classifier at `3 - Alpha` | v0.2 adds forward-compatible realism, but aggregation, wall hydrodynamics, and continuous thresholds are still deferred. |
| Tag after documentation and validation, not before | The tag should point at the audited release surface, including the deliverable index and experimental-envelope closeout. |
| Keep the `pilot-v0.1` tag as historical reference | v0.2 is forward-compatible with v0.1 but not a retag; historical cache and release evidence remain useful. |

## What was not done

- No new physics model was added in Phase 15.
- No aggregation, adsorption, surfactant, or wall-hydrodynamic model
  was implemented; those remain outside `pilot-v0.2`.
- No remote push was performed as part of the local release closeout.

## Cross-references

- [`docs/work-plan-v0-2.md`](../docs/work-plan-v0-2.md) — accepted
  v0.2 scope and Phase 15 acceptance checklist.
- [`docs/deliverable-index.md`](../docs/deliverable-index.md) — §6
  artefact map for `pilot-v0.2`.
- [`docs/findings-physics.md`](../docs/findings-physics.md) —
  experimental conclusions.
- [`docs/findings-process.md`](../docs/findings-process.md) —
  reusable engineering patterns.
- [`docs/experimental-envelope.md`](../docs/experimental-envelope.md)
  — assumptions and experimental knobs.
