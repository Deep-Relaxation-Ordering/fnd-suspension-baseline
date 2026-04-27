# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # 01 — Baseline validation
#
# *Endorsement Marker: Local stewardship — U. Warring, AG Schätz,
# Physikalisches Institut Freiburg.*
#
# Phase-2 deliverable surface for the breakout note
# *Numerical Pilot: Brownian Motion and Sedimentation of Diamond Particles
# in Aqueous Suspension as a Function of Particle Size* (v0.2).
#
# This notebook composes the primitives in `src/parameters.py` and
# `src/analytical.py` into the deliverable-3 first figure (radius
# dependence of v_sed, D, ℓ_g at room temperature) and a preview of
# deliverable 5 (regime classification along the radius axis at fixed h).
#
# It also evaluates the equilibrium-distribution check from
# breakout-note §4.4 (first bullet) at the analytical level: at long
# times, Method B must reproduce the barometric profile this notebook
# plots — the cross-check itself lands once Method B is implemented.
#
# Stored as a jupytext `:percent` `.py` file so the canonical source is
# diff-friendly. Convert to `.ipynb` when needed via
# `jupytext --to ipynb 01_baseline_validation.py`. See
# `docs/conventions.md`.

# %%
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from analytical import (
    barometric_profile,
    cell_summary,
    scale_height,
    settling_velocity,
    top_to_bottom_ratio,
)
from parameters import diffusivity
from scan_grid import (
    DEPTH_LABELS,
    DEPTHS_M,
    NOTEBOOK_PREVIEW_DEPTH_INDICES,
    radii_m,
)

# %% [markdown]
# ## Anchor cell: 100 nm at 25 °C, 1 mm depth
#
# Sanity print of every Method A quantity. Useful as a smoke test before
# any scan: if the numbers below disagree with hand calculations, do not
# proceed.

# %%
anchor = cell_summary(radius_m=1e-7, temperature_kelvin=298.15, sample_depth_m=1e-3)
for key, value in anchor.items():
    print(f"  {key:>22s} = {value:.6g}")

# %% [markdown]
# ### Expected order of magnitude
#
# | Quantity | Value | Interpretation |
# |---|---|---|
# | ℓ_g | ~ 40 µm | gravitational scale height |
# | v_sed | ~ 60 nm/s | bulk settling speed |
# | D | ~ 2 × 10⁻¹² m²/s | Brownian diffusivity |
# | t_settle | ~ 4 hours | latest particle to reach z = 0 |
# | t_eq | ~ 650 s (length scale = ℓ_g, not h) | order-of-magnitude relaxation |
# | c(h)/c(0) | ~ 10⁻¹¹ | fully sedimented at equilibrium |

# %% [markdown]
# ## Deliverable 3 — first figure
#
# Radius dependence of v_sed, D, ℓ_g at room temperature, log–log.
# Scan: 5 nm to 10 µm, 30 log-spaced points (breakout-note §5).

# %%
T_ROOM = 298.15
radii = radii_m()
v_sed = np.array([settling_velocity(r, T_ROOM) for r in radii])
d_brownian = np.array([diffusivity(r, T_ROOM) for r in radii])
ell_g = np.array([scale_height(r, T_ROOM) for r in radii])

fig, ax = plt.subplots(figsize=(7.5, 5.0))
ax.loglog(radii * 1e9, v_sed, label=r"$v_\mathrm{sed}$ [m/s]", lw=1.8)
ax.loglog(radii * 1e9, d_brownian, label=r"$D$ [m$^2$/s]", lw=1.8)
ax.loglog(radii * 1e9, ell_g, label=r"$\ell_g$ [m]", lw=1.8)
ax.set_xlabel("particle radius r  [nm]")
ax.set_ylabel("value (mixed units; legend specifies)")
ax.set_title(rf"Method A: $v_\mathrm{{sed}}$, $D$, $\ell_g$ vs $r$ at $T = {T_ROOM:.2f}$ K")
ax.grid(True, which="both", alpha=0.3)
ax.legend(loc="best")
fig.tight_layout()

figures_dir = Path(__file__).parent / "figures" / "01_baseline_validation"
figures_dir.mkdir(parents=True, exist_ok=True)
fig.savefig(figures_dir / "vsed_D_ellg_vs_r.png", dpi=140)
fig.savefig(figures_dir / "vsed_D_ellg_vs_r.pdf")
plt.show()

# %% [markdown]
# Reading: at the small-r end, ℓ_g ≫ h for any reasonable h and the
# suspension is homogeneous; at the large-r end, ℓ_g ≪ h and
# sedimentation dominates. The crossing of ℓ_g with the sample-depth
# scale (next plot) defines the radius where the regime flips.

# %% [markdown]
# ## Regime preview at fixed h — top-to-bottom equilibrium ratio
#
# c(h)/c(0) = exp(-h / ℓ_g) at room temperature. The breakout-note §5
# scan defines five sample depths (`scan_grid.DEPTHS_M`); this preview
# shows the four short-path depths (≤ 2 mm,
# `scan_grid.NOTEBOOK_PREVIEW_DEPTH_INDICES`) for legibility — the
# 10 mm curve sits in the deeply-sedimented corner across most of the
# radius range and would crowd the threshold lines. The full five-depth
# sweep is the deliverable-3 figure produced by `regime_map.py`.
# Horizontal dashed lines mark the §5.1 thresholds (0.95 and 0.05).

# %%
sample_depths = [(DEPTHS_M[i], DEPTH_LABELS[i]) for i in NOTEBOOK_PREVIEW_DEPTH_INDICES]
fig, ax = plt.subplots(figsize=(7.5, 5.0))
for h, label in sample_depths:
    ratio = np.array([top_to_bottom_ratio(r, T_ROOM, h) for r in radii])
    ax.semilogx(radii * 1e9, ratio, lw=1.8, label=f"h = {label}")
ax.axhline(0.95, ls="--", color="grey", alpha=0.7, label="homogeneous threshold (0.95)")
ax.axhline(0.05, ls="--", color="black", alpha=0.7, label="sedimented threshold (0.05)")
ax.set_xlabel("particle radius r  [nm]")
ax.set_ylabel(r"equilibrium ratio $c(h)/c(0) = e^{-h/\ell_g}$")
ax.set_title(rf"Regime preview at $T = {T_ROOM:.2f}$ K")
ax.set_ylim(-0.05, 1.05)
ax.grid(True, which="both", alpha=0.3)
ax.legend(loc="best", fontsize=9)
fig.tight_layout()
fig.savefig(figures_dir / "regime_preview_ratio_vs_r.png", dpi=140)
fig.savefig(figures_dir / "regime_preview_ratio_vs_r.pdf")
plt.show()

# %% [markdown]
# Reading: each h-curve crosses the homogeneous and sedimented
# thresholds at definite radii, with the crossings shifting to smaller r
# as h grows. The §5.1 design table (deliverable 5) is the inverse of
# this view: for a given (h, t_obs), what is the largest r that stays
# inside the homogeneous band? Method C will turn the *equilibrium*
# crossings into time-dependent crossings at finite t_obs.

# %% [markdown]
# ## Equilibrium profile at three illustrative radii
#
# Stratified, transition, sedimented. Lines span [0, h] with
# normalisation ∫₀ʰ c(z) dz = 1, so the area under each curve equals 1.

# %%
illustrative = [
    (3e-8, "30 nm — ~ homogeneous"),
    (1e-7, "100 nm — stratified"),
    (3e-7, "300 nm — sedimented"),
]
h_demo = 1e-3
z_demo = np.linspace(0.0, h_demo, 1001)

fig, ax = plt.subplots(figsize=(7.5, 5.0))
for r, label in illustrative:
    c = barometric_profile(z_demo, r, T_ROOM, h_demo)
    ax.semilogy(z_demo * 1e3, c * h_demo, lw=1.8, label=label)
ax.set_xlabel("z [mm]  (sample bottom at z = 0)")
ax.set_ylabel(r"$c_\mathrm{eq}(z) \cdot h$  (normalised so area = 1; log scale)")
ax.set_title(rf"Barometric equilibrium at $T = {T_ROOM:.2f}$ K, $h = 1$ mm")
ax.grid(True, which="both", alpha=0.3)
ax.legend(loc="best")
fig.tight_layout()
fig.savefig(figures_dir / "barometric_profile_three_radii.png", dpi=140)
fig.savefig(figures_dir / "barometric_profile_three_radii.pdf")
plt.show()

# %% [markdown]
# ## Validation status
#
# This notebook covers the analytical layer of breakout-note §4.4:
#
# - **Einstein–Smoluchowski**: machine-precision identity asserted in
#   `tests/test_einstein_relation.py` and inside every `cell_summary` row
#   (`tests/test_analytical.py::test_cell_summary_einstein_relation_internal_consistency`).
# - **Equilibrium profile shape**: barometric exponential, normalised,
#   recovers the uniform limit when ℓ_g ≫ h (tested in
#   `test_analytical.py`).
#
# Outstanding (awaits Methods B and C):
#
# - Method B vs Method A at long times (mean-height ≤ 2 % deviation).
# - Method B vs Method C time-dependent moments.
# - Pure-Brownian MSD recovery (h²/6 displacement, h²/12 position).
# - Pure-sedimentation arrival times (h / v_sed and h / (2 v_sed)).
# - Method C high-/low-Pe limits and asymptotic-sedimentation fallback.
#
# All those checks have skipped pytest stubs already in place; they will
# be un-skipped as the underlying methods land.

print("notebook 01 complete; figures written to", figures_dir)
