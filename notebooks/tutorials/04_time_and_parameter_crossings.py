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
# # TUT-04 — Time and parameter crossings
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Deep-Relaxation-Ordering/fnd-suspension-baseline/blob/main/notebooks/tutorials/04_time_and_parameter_crossings.ipynb)
#
# **Tutorial ID**: TUT-04
# **Purpose**: Demonstrate root-finding for crossing times and crossing parameters.
# **Expected runtime**: < 60 s
# **Release tag**: `pilot-v0.4`
# **Canonical inputs**: `src/time_evolution.py`, `src/fokker_planck.py`
# **Smoke command**: `PYTHONPATH=src python notebooks/tutorials/04_time_and_parameter_crossings.py`
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
from time_evolution import crossing_parameter, crossing_time

print("--- Crossing Time ---")
print("Finding t where a 100 nm FND crosses ratio = 0.5 (mixed -> stratified)")
t_cross = crossing_time(
    radius_m=100e-9, temperature_kelvin=298.15, sample_depth_m=1e-3,
    criterion="ratio", target=0.5, t_min=1.0, t_max=3600.0, n_points=5
)
print("Interval: [1.0, 3600.0] s")
if t_cross:
    print(f"Crossing time: {t_cross:.1f} s ({t_cross/60:.1f} min)")
else:
    print("No crossing found in interval.")

print("\n--- Crossing Parameter ---")
print("Finding delta_shell_m where BMF = 0.5 at 1 hour for a 150 nm particle")
p_cross = crossing_parameter(
    radius_m=150e-9, temperature_kelvin=298.15, sample_depth_m=1e-3, parameter="delta_shell_m",
    t_obs_s=3600.0, p_min=0.0, p_max=50e-9, criterion="bmf", target=0.5, n_points=5
)
print("Interval: [0.0, 50.0] nm")
if p_cross:
    print(f"Crossing parameter (delta_shell_m): {p_cross * 1e9:.2f} nm")
else:
    print("No crossing found in interval.")

# %% [markdown]
# ## Where to go next
#
# - Next tutorial: TUT-05 — Experimental envelope
# - Related finding: Release notes v0.4
