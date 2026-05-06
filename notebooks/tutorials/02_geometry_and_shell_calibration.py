# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
# ---

# %% [markdown]
# # TUT-02 — Geometry + shell calibration
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Deep-Relaxation-Ordering/fnd-suspension-baseline/blob/main/notebooks/tutorials/02_geometry_and_shell_calibration.ipynb)
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
# Colab bootstrap — clones the repo on first run so `src` is importable.
# No-op outside Colab.
import os
import sys

if "google.colab" in sys.modules:
    REPO_DIR = "/content/fnd-suspension-baseline"
    if not os.path.exists(REPO_DIR):
        import subprocess
        subprocess.run(
            [
                "git", "clone", "-q",
                "https://github.com/Deep-Relaxation-Ordering/fnd-suspension-baseline.git",
                REPO_DIR,
            ],
            check=True,
        )
    os.chdir(REPO_DIR)
    if "src" not in sys.path:
        sys.path.insert(0, "src")

# %%

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
