# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # TUT-02 — Geometry + shell calibration
#
# **Tutorial ID**: TUT-02
# **Purpose**: Instantiate FND classes and inspect hydrodynamic radius shifts.
# **Expected runtime**: < 60 s
# **Release tag**: `pilot-v0.4`
# **Canonical inputs**: `src/parameters.py`, `docs/delta_shell_calibration.md`
# **Smoke command**: `PYTHONPATH=src python notebooks/tutorials/02_geometry_and_shell_calibration.py`
#
# **Links**:
# - Tutorial roadmap
# - Deliverable index
#
# **Citation/reuse**: Please see `CITATION.cff`, `codemeta.json`, `LICENCE`, and `pyproject.toml` in the repository root.

# %%
from pathlib import Path
import matplotlib.pyplot as plt

from parameters import ParticleGeometry

r_mat = 50e-9
fnd_classes = ["bare", "carboxylated", "hydroxylated", "peg_functionalised"]
delta_shells = []

print("--- FND Class Calibration ---")
for cls in fnd_classes:
    geom = ParticleGeometry.from_fnd_class(r_material_m=r_mat, fnd_class=cls)
    delta_shells.append(geom.delta_shell_m)
    print(f"\nClass: {cls}")
    print(f"  r_material:  {geom.r_material_m * 1e9:.1f} nm")
    print(f"  delta_shell: {geom.delta_shell_m * 1e9:.1f} nm")
    print(f"  r_hydro:     {geom.r_hydro_m * 1e9:.1f} nm")

# %% [markdown]
# ## Where to go next
#
# - Next tutorial: TUT-03 — Polydispersity intuition
# - Related finding: delta_shell_calibration.md