# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # TUT-03 — Polydispersity intuition
#
# **Tutorial ID**: TUT-03
# **Purpose**: Compare log-normal polydispersity smearing across classification and number-density weightings.
# **Expected runtime**: < 60 s
# **Release tag**: `pilot-v0.4`
# **Canonical inputs**: `notebooks/data/regime_map_grid.csv`, `src/polydispersity.py`
# **Smoke command**: `PYTHONPATH=src python notebooks/tutorials/03_polydispersity_intuition.py`
#
# **Links**:
# - Tutorial roadmap
# - Deliverable index
#
# **Citation/reuse**: Please see `CITATION.cff`, `codemeta.json`, `LICENCE`, and `pyproject.toml` in the repository root.

# %%
from pathlib import Path
import numpy as np

from regime_map import results_from_csv, results_to_grid
from polydispersity import lognormal_smear

cache_path = Path(__file__).resolve().parent.parent / "data" / "regime_map_grid.csv"
results = list(results_from_csv(cache_path))
grid = results_to_grid(results)

# Pick a representative cell
r_anchor = 100e-9
sigma = 1.2
T_idx = grid.temperatures.index(298.15)
h_idx = grid.depths.index(1e-3)
t_idx = grid.t_obs.index(3600.0)

smear_class = lognormal_smear(
    grid, r_geom_mean_axis=[r_anchor], sigma_geom_axis=[sigma], 
    weighting="classification", on_truncation="mask"
)

smear_nd = lognormal_smear(
    grid, r_geom_mean_axis=[r_anchor], sigma_geom_axis=[sigma], 
    weighting="number_density", on_truncation="mask"
)

print("--- Polydispersity Smeared Regime Probabilities ---")
print("\nClassification Weighting:")
print(f"  p_homogeneous: {smear_class.p_homogeneous[0, 0, T_idx, h_idx, t_idx]:.4f}")
print(f"  p_stratified:  {smear_class.p_stratified[0, 0, T_idx, h_idx, t_idx]:.4f}")
print(f"  p_sedimented:  {smear_class.p_sedimented[0, 0, T_idx, h_idx, t_idx]:.4f}")

print("\nNumber Density Weighting:")
print(f"  p_homogeneous: {smear_nd.p_homogeneous[0, 0, T_idx, h_idx, t_idx]:.4f}")
print(f"  p_stratified:  {smear_nd.p_stratified[0, 0, T_idx, h_idx, t_idx]:.4f}")
print(f"  p_sedimented:  {smear_nd.p_sedimented[0, 0, T_idx, h_idx, t_idx]:.4f}")

print("\nConditional Radius Moments (Number Density):")
for reg_idx, reg_name in enumerate(["Homogeneous", "Stratified", "Sedimented"]):
    e_r = smear_nd.expected_radius_by_regime[reg_idx, 0, 0, T_idx, h_idx, t_idx]
    e_r2 = smear_nd.expected_radius_sq_by_regime[reg_idx, 0, 0, T_idx, h_idx, t_idx]
    e_r_str = f"{e_r * 1e9:.2f} nm" if not np.isnan(e_r) else "N/A"
    e_r2_str = f"{e_r2 * 1e18:.2f} nm^2" if not np.isnan(e_r2) else "N/A"
    print(f"  {reg_name}:")
    print(f"    E[r|R]   = {e_r_str}")
    print(f"    E[r^2|R] = {e_r2_str}")

# %% [markdown]
# ## Where to go next
#
# - Next tutorial: TUT-04 — Time and parameter crossings
# - Related finding: Deliverable index