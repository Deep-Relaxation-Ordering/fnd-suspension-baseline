# Tutorial notebooks

Visitor-facing tutorials live here as jupytext `.py` notebooks.
They are accessibility surfaces, not release artefacts.

## Ready tutorials (`pilot-v0.4`)

| ID | File | Description | Smoke command |
|---|---|---|---|
| TUT-01 | `01_quick_start_regime_map.py` | Load the §5 cache and inspect a single (r, h) cell. | `PYTHONPATH=src python notebooks/tutorials/01_quick_start_regime_map.py` |
| TUT-02 | `02_geometry_and_shell_calibration.py` | Instantiate FND classes and inspect hydrodynamic-radius shifts. | `PYTHONPATH=src python notebooks/tutorials/02_geometry_and_shell_calibration.py` |
| TUT-03 | `03_polydispersity_intuition.py` | Compare log-normal smearing under classification vs number-density weighting. | `PYTHONPATH=src python notebooks/tutorials/03_polydispersity_intuition.py` |
| TUT-04 | `04_time_and_parameter_crossings.py` | Demonstrate `crossing_time` and `crossing_parameter` root-finding. | `PYTHONPATH=src python notebooks/tutorials/04_time_and_parameter_crossings.py` |
| TUT-05 | `05_experimental_envelope.py` | Narrative walkthrough of model validity caveats and open S-slice gates. | `PYTHONPATH=src python notebooks/tutorials/05_experimental_envelope.py` |

All tutorials were smoke-tested against the `pilot-v0.4` tag.

## Rules

Tutorial conventions (front matter, runtime budget, FAIR floor, smoke-test gate)
are in [`../../docs/conventions.md`](../../docs/conventions.md) §"Tutorial notebooks".
The roadmap with stable IDs and canonical inputs is in
[`../../docs/tutorial-roadmap.md`](../../docs/tutorial-roadmap.md).
