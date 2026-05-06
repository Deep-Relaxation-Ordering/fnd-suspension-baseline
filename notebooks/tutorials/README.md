# Tutorial notebooks

Visitor-facing tutorials live here as jupytext `.py` notebooks paired
with `.ipynb` files (jupytext format `ipynb,py:percent`). The `.py`
file is canonical for review; the `.ipynb` is regenerated via
`jupytext --sync` whenever the `.py` changes and lets external
readers launch the tutorial in Colab one-click.

They are accessibility surfaces, not release artefacts.

## Ready tutorials (`pilot-v0.4`)

| ID | File | Description | Colab | Smoke command |
|---|---|---|---|---|
| TUT-01 | `01_quick_start_regime_map.py` | Load the §5 cache and inspect a single (r, h) cell. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Deep-Relaxation-Ordering/fnd-suspension-baseline/blob/main/notebooks/tutorials/01_quick_start_regime_map.ipynb) | `PYTHONPATH=src python notebooks/tutorials/01_quick_start_regime_map.py` |
| TUT-02 | `02_geometry_and_shell_calibration.py` | Instantiate FND classes and inspect hydrodynamic-radius shifts. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Deep-Relaxation-Ordering/fnd-suspension-baseline/blob/main/notebooks/tutorials/02_geometry_and_shell_calibration.ipynb) | `PYTHONPATH=src python notebooks/tutorials/02_geometry_and_shell_calibration.py` |
| TUT-03 | `03_polydispersity_intuition.py` | Compare log-normal smearing under classification vs number-density weighting. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Deep-Relaxation-Ordering/fnd-suspension-baseline/blob/main/notebooks/tutorials/03_polydispersity_intuition.ipynb) | `PYTHONPATH=src python notebooks/tutorials/03_polydispersity_intuition.py` |
| TUT-04 | `04_time_and_parameter_crossings.py` | Demonstrate `crossing_time` and `crossing_parameter` root-finding. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Deep-Relaxation-Ordering/fnd-suspension-baseline/blob/main/notebooks/tutorials/04_time_and_parameter_crossings.ipynb) | `PYTHONPATH=src python notebooks/tutorials/04_time_and_parameter_crossings.py` |
| TUT-05 | `05_experimental_envelope.py` | Narrative walkthrough of model validity caveats and open S-slice gates. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Deep-Relaxation-Ordering/fnd-suspension-baseline/blob/main/notebooks/tutorials/05_experimental_envelope.ipynb) | `PYTHONPATH=src python notebooks/tutorials/05_experimental_envelope.py` |
| TUT-06 | `06_cache_explorer.py` | Interactive (ipywidgets) and static-fallback exploration of the §5 regime-map cache. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Deep-Relaxation-Ordering/fnd-suspension-baseline/blob/main/notebooks/tutorials/06_cache_explorer.ipynb) | `PYTHONPATH=src python notebooks/tutorials/06_cache_explorer.py` |

All tutorials were smoke-tested against the `pilot-v0.4` tag.

## How to launch in Colab

Click the badge in any row above. Colab opens the paired `.ipynb`,
the bootstrap cell clones the repo (one-time per session), and the
tutorial runs against the same cache and `src/` modules a local
checkout uses.

## How to keep `.py` and `.ipynb` in sync

After editing a `.py` source, re-pair its `.ipynb`:

```sh
.venv/bin/jupytext --sync notebooks/tutorials/<stem>.py
```

The tutorial-notebooks convention forbids drift between the two —
[`docs/conventions.md`](../../docs/conventions.md) §"Tutorial notebooks".

## Rules

Tutorial conventions (front matter, runtime budget, FAIR floor, smoke-test gate)
are in [`../../docs/conventions.md`](../../docs/conventions.md) §"Tutorial notebooks".
The roadmap with stable IDs and canonical inputs is in
[`../../docs/tutorial-roadmap.md`](../../docs/tutorial-roadmap.md).
