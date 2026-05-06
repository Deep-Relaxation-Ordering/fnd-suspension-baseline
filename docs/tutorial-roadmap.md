# Tutorial roadmap

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

This file tracks the proposed and shipped visitor-facing tutorials.
Tutorials are accessibility surfaces, not §6 deliverables; they are
covered by the convention in [`conventions.md`](conventions.md)
§"Tutorial notebooks". Each tutorial has a stable ID so links,
smoke-test logs, and lab notes can refer to it even if the file name
changes later.

| ID | Tutorial | Status | Target phase | Planned path | Canonical inputs | Smoke command | Linked from |
|---|---|---|---|---|---|---|---|
| TUT-01 | Quick-start regime map | proposed | v0.5 | `notebooks/tutorials/01_quick_start_regime_map.py` | `notebooks/data/regime_map_grid.csv` | `PYTHONPATH=src python notebooks/tutorials/01_quick_start_regime_map.py` | README / Pages |
| TUT-02 | Geometry + shell calibration | proposed | v0.5 | `notebooks/tutorials/02_geometry_and_shell_calibration.py` | `src/parameters.py`, `docs/delta_shell_calibration.md` | `PYTHONPATH=src python notebooks/tutorials/02_geometry_and_shell_calibration.py` | release notes / envelope |
| TUT-03 | Polydispersity intuition | proposed | v0.5 | `notebooks/tutorials/03_polydispersity_intuition.py` | `notebooks/data/regime_map_grid.csv`, `src/polydispersity.py` | `PYTHONPATH=src python notebooks/tutorials/03_polydispersity_intuition.py` | deliverable index |
| TUT-04 | Time + parameter crossings | proposed | v0.5 | `notebooks/tutorials/04_time_and_parameter_crossings.py` | `src/time_evolution.py`, `src/fokker_planck.py` | `PYTHONPATH=src python notebooks/tutorials/04_time_and_parameter_crossings.py` | API docs / README |
| TUT-05 | Experimental envelope | proposed | v0.5 | `notebooks/tutorials/05_experimental_envelope.py` | `docs/experimental-envelope.md`, `docs/program-context.md` | `PYTHONPATH=src python notebooks/tutorials/05_experimental_envelope.py` | Pages / envelope |

## Legend

- **proposed** — scoped and linked, not yet written.
- **draft** — notebook exists on a branch, not merged.
- **ready** — merged to `main`, smoke-tested at the current tag.
- **stale** — smoke-test fails or content is out of date with the release tag.

## FAIR tracking

For every tutorial promoted to `ready`, check:

- The tutorial ID, path, release tag, canonical inputs, and smoke
  command appear in this roadmap.
- The notebook front matter links to `CITATION.cff`, `codemeta.json`,
  `LICENCE`, and the license metadata in `pyproject.toml`.
- The notebook uses committed inputs only, unless the roadmap marks it
  `<!-- EXPENSIVE -->` and explains the non-default input path.
- Any committed figures name the notebook command and input files that
  produced them.

## Standing checklist

Tutorial/accessibility surface audit: are current tutorials still runnable,
linked, FAIR-enough for discovery/reuse, and aligned with the release status?
