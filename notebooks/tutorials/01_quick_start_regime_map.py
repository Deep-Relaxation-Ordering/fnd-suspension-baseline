# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # TUT-01 — Quick-start regime map
#
# **Tutorial ID**: TUT-01
# **Purpose**: Load the §5 cache, select a slice, and inspect a single cell.
# **Expected runtime**: < 60 s
# **Release tag**: `pilot-v0.4`
# **Canonical inputs**: `notebooks/data/regime_map_grid.csv`
# **Smoke command**: `PYTHONPATH=src python notebooks/tutorials/01_quick_start_regime_map.py`
#
# **Links**:
# - Tutorial roadmap
# - Deliverable index
#
# **Citation/reuse**: Please see `CITATION.cff`, `codemeta.json`, `LICENCE`, and `pyproject.toml` in the repository root.

# %%
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from regime_map import results_from_csv

# Load cache
cache_path = Path(__file__).resolve().parent.parent / "data" / "regime_map_grid.csv"
results = list(results_from_csv(cache_path))
print(f"Loaded {len(results)} cells from cache.")

# Select slice at Room Temperature (298.15 K) and t_obs = 1 h (3600 s)
slice_results = [
    r for r in results 
    if np.isclose(r.temperature_kelvin, 298.15) and np.isclose(r.t_obs_s, 3600.0)
]

# Inspect a single cell — pick a radius near 100 nm that exists on the §5 grid
# (the grid is log-spaced; 100 nm is not an exact grid point)
target_r = 100e-9
target_h = 1e-3

available_radii = np.array(sorted({r.r_material_m for r in slice_results}))
nearest_r = available_radii[np.argmin(np.abs(available_radii - target_r))]

cell = next(
    r for r in slice_results 
    if np.isclose(r.r_material_m, nearest_r) and np.isclose(r.sample_depth_m, target_h)
)

print("\n--- Single Cell Inspection ---")
print(f"Radius: {cell.r_material_m * 1e9:.2f} nm (nearest grid point to {target_r*1e9:.0f} nm), Depth: {cell.sample_depth_m * 1e3} mm")
print(f"Regime label: {cell.regime}")
print(f"c(h)/c(0) ratio: {cell.top_to_bottom_ratio:.4g}")
print(f"Bottom mass fraction: {cell.bottom_mass_fraction:.4g}")
print(f"Convection warning: {cell.convection_flag}")

# %% [markdown]
# ## Where to go next
#
# - Next tutorial: TUT-02 — Geometry and shell calibration
# - Related finding: Findings — Physics