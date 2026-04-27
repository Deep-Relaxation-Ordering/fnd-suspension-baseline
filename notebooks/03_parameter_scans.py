# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # 03 — Parameter scans
#
# *Endorsement Marker: Local stewardship — U. Warring, AG Schätz,
# Physikalisches Institut Freiburg.*
#
# Phase-7 deliverable surface for the breakout note
# *Numerical Pilot: Brownian Motion and Sedimentation of Diamond Particles
# in Aqueous Suspension as a Function of Particle Size* (v0.2).
#
# Notebook 02 showed the §5.1 regime classification at room temperature.
# This notebook scans across the full breakout-note §5 grid:
#
# 1. **Method-A primitives across temperature** — `v_sed`, `D`, `ℓ_g`
#    vs `r` for each of the 7 scan_grid temperatures, overlaid.
# 2. **Regime maps at each temperature** — 7-panel grid showing how the
#    regime boundaries shift between 5 °C and 35 °C at fixed `t_obs = 1 h`.
# 3. **Homogeneous radius envelope** — for each `(h, t_obs)` cell, the
#    largest `r` that keeps the suspension homogeneous, traced across
#    temperatures.
#
# All figures read from the precomputed cache
# `notebooks/data/regime_map_grid.csv` written by Phase 6. If the cache
# is missing the notebook still runs Method-A primitives directly (no
# Method C needed for figure 1).

# %%
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from analytical import diffusivity, scale_height, settling_velocity
from regime_map import results_from_csv, results_to_grid
from scan_grid import T_OBS_LABELS, T_OBS_S, radii_m, temperatures_k

# %% [markdown]
# ## Method-A primitives across temperature
#
# `v_sed`, `D`, `ℓ_g` vs particle radius, overlaid for each scan_grid
# temperature. At small `r` the curves are nearly degenerate (diffusion
# dominates and depends weakly on T-induced viscosity changes); at
# large `r` the temperature spread is the η ~ 2× factor across 5 → 35 °C.

# %%
figures_dir = Path(__file__).parent / "figures" / "03_parameter_scans"
figures_dir.mkdir(parents=True, exist_ok=True)

radii = radii_m()
temps = temperatures_k()
# Cool-to-warm temperature colours.
T_CMAP = plt.get_cmap("coolwarm")
T_COLOURS = [T_CMAP((T - temps[0]) / (temps[-1] - temps[0])) for T in temps]


def _scan_curves(temperature: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (v_sed, D, ℓ_g) arrays evaluated on `radii` at one temperature."""
    v = np.array([settling_velocity(r, temperature) for r in radii])
    d = np.array([diffusivity(r, temperature) for r in radii])
    ell = np.array([scale_height(r, temperature) for r in radii])
    return v, d, ell


fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.6), sharex=True)
for T, colour in zip(temps, T_COLOURS, strict=True):
    v, d, ell = _scan_curves(T)
    axes[0].loglog(radii * 1e9, v, color=colour, lw=1.6, label=f"{T-273.15:.0f} °C")
    axes[1].loglog(radii * 1e9, d, color=colour, lw=1.6)
    axes[2].loglog(radii * 1e9, ell, color=colour, lw=1.6)
axes[0].set_title(r"settling velocity $v_\mathrm{sed}$  [m/s]")
axes[1].set_title(r"diffusivity $D$  [m$^2$/s]")
axes[2].set_title(r"scale height $\ell_g$  [m]")
for ax in axes:
    ax.set_xlabel("particle radius r  [nm]")
    ax.grid(True, which="both", alpha=0.3)
axes[0].legend(loc="lower right", fontsize=8, ncol=2)
fig.suptitle(rf"Method-A primitives across the §5 temperature grid ({len(temps)} curves)")
fig.tight_layout()
fig.savefig(figures_dir / "method_a_primitives_vs_T.png", dpi=140)
fig.savefig(figures_dir / "method_a_primitives_vs_T.pdf")
plt.show()

# %% [markdown]
# ## Regime map at each temperature
#
# 7-panel grid: one (radius × depth) regime panel per scan_grid
# temperature, all at `t_obs = 1 h`. Loads the §5 cache produced by
# Phase 6; if the cache is missing the panels are skipped (Method-C
# regeneration is too expensive without it).

# %%
CACHE_PATH = Path(__file__).parent / "data" / "regime_map_grid.csv"
have_cache = CACHE_PATH.exists()

REGIME_LABELS = ["homogeneous", "stratified", "sedimented"]
REGIME_COLOURS = ["#4575b4", "#fee090", "#a50026"]

if have_cache:
    grid = results_to_grid(results_from_csv(CACHE_PATH))
    print(f"loaded grid {grid.regime.shape} from {CACHE_PATH}")

    # Pick t_obs = 1 h from the cache axis if present, otherwise the
    # closest available value.
    if 3600.0 in grid.t_obs:
        t_idx_1h = grid.t_obs.index(3600.0)
    else:
        t_idx_1h = min(range(len(grid.t_obs)), key=lambda i: abs(grid.t_obs[i] - 3600.0))
    t_label_1h = (
        T_OBS_LABELS[T_OBS_S.index(grid.t_obs[t_idx_1h])]
        if grid.t_obs[t_idx_1h] in T_OBS_S
        else f"{grid.t_obs[t_idx_1h]:.0f} s"
    )

    # Mesh edges in log-space.
    rs = np.asarray(grid.radii)
    hs = np.asarray(grid.depths)
    log_r = np.log10(rs)
    log_h = np.log10(hs)
    edges_r = 10.0 ** np.concatenate([
        [log_r[0] - (log_r[1] - log_r[0]) / 2],
        (log_r[:-1] + log_r[1:]) / 2,
        [log_r[-1] + (log_r[-1] - log_r[-2]) / 2],
    ])
    edges_h = 10.0 ** np.concatenate([
        [log_h[0] - (log_h[1] - log_h[0]) / 2],
        (log_h[:-1] + log_h[1:]) / 2,
        [log_h[-1] + (log_h[-1] - log_h[-2]) / 2],
    ])

    n_T_cache = len(grid.temperatures)
    fig, axes = plt.subplots(1, n_T_cache, figsize=(3.6 * n_T_cache, 4.5), sharey=True)
    cmap = ListedColormap(REGIME_COLOURS)
    for ax, ti, T in zip(axes, range(n_T_cache), grid.temperatures, strict=True):
        ax.pcolormesh(
            edges_r * 1e9,
            edges_h * 1e3,
            grid.regime[:, ti, :, t_idx_1h].T,
            cmap=cmap,
            vmin=-0.5,
            vmax=2.5,
            edgecolors="white",
            linewidth=0.3,
        )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("r  [nm]")
        ax.set_title(f"{T-273.15:.0f} °C")
    axes[0].set_ylabel("h  [mm]")
    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, color=REGIME_COLOURS[i], label=REGIME_LABELS[i])
        for i in range(3)
    ]
    axes[-1].legend(handles=legend_handles, loc="upper right", fontsize=8, framealpha=0.95)
    fig.suptitle(rf"Regime map across the §5 temperature axis at $t_\mathrm{{obs}}$ = {t_label_1h}")
    fig.tight_layout()
    fig.savefig(figures_dir / "regime_map_per_temperature.png", dpi=140)
    fig.savefig(figures_dir / "regime_map_per_temperature.pdf")
    plt.show()
else:
    print(f"cache {CACHE_PATH} not found; skipping per-temperature regime panels")

# %% [markdown]
# ## Homogeneous-radius envelope vs temperature
#
# For each `(h, t_obs)` cell, the *largest* radius in the §5 axis that
# is still classified `homogeneous`, traced across temperatures. Curves
# fall slightly with T because higher temperature → lower viscosity
# → faster settling at the same r → boundary moves to smaller r.
#
# (For the full design table — every `(h, t_obs)` envelope at every T —
# see notebook 04.)

# %%
if have_cache:
    # Pick a fixed t_obs (1 h) and one h per panel for legibility.
    h_indices = list(range(len(grid.depths)))

    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    for hi, h in zip(h_indices, grid.depths, strict=True):
        max_homog_r = []
        for ti in range(len(grid.temperatures)):
            mask = grid.regime[:, ti, hi, t_idx_1h] == 0  # homogeneous
            if mask.any():
                # Largest radius-index that is still classified homogeneous.
                idxs = np.where(mask)[0]
                last_homog = int(idxs[-1])
                max_homog_r.append(grid.radii[last_homog])
            else:
                max_homog_r.append(np.nan)
        ax.semilogy(
            np.array(grid.temperatures) - 273.15,
            np.array(max_homog_r) * 1e9,
            marker="o",
            lw=1.5,
            label=f"h = {h*1e3:.1f} mm",
        )
    ax.set_xlabel("temperature  [°C]")
    ax.set_ylabel("max homogeneous radius  [nm]")
    ax.set_title(rf"Homogeneous-radius envelope at $t_\mathrm{{obs}}$ = {t_label_1h}")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(figures_dir / "homogeneous_envelope_vs_T.png", dpi=140)
    fig.savefig(figures_dir / "homogeneous_envelope_vs_T.pdf")
    plt.show()
else:
    print(f"cache {CACHE_PATH} not found; skipping homogeneous-envelope figure")

# %% [markdown]
# ## Status
#
# Notebook 03 covers the parameter-scan supporting deliverable for §5.
# The §5.1 regime classification is in notebook 02; the printable
# design table that consumes the same cache lives in notebook 04.

print("notebook 03 complete; figures written to", figures_dir)
