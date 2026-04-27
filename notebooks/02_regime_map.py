# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # 02 — Regime map (deliverable 3)
#
# *Endorsement Marker: Local stewardship — U. Warring, AG Schätz,
# Physikalisches Institut Freiburg.*
#
# Phase-6 deliverable surface for the breakout note
# *Numerical Pilot: Brownian Motion and Sedimentation of Diamond Particles
# in Aqueous Suspension as a Function of Particle Size* (v0.2).
#
# Reads the precomputed §5 grid cache produced by `regime_map.walk_grid`
# (`notebooks/data/regime_map_grid.csv`) and produces the §5.1 regime map
# across (radius, sample depth) at a fixed temperature, plus a comparison
# panel across observation times. The cache itself is the source of
# deliverable 5 (the design table); this notebook turns it into figures.
#
# If the cache is missing, the notebook falls back to walking a coarse
# 6×3×5×3 = 270-cell sub-grid so the figures still render. To regenerate
# the full 6300-cell cache, run::
#
#     PYTHONPATH=src python -c "from regime_map import walk_grid, results_to_csv; \
#                               results_to_csv(walk_grid(), 'notebooks/data/regime_map_grid.csv')"
#
# Stored as a jupytext `:percent` `.py` file per `docs/conventions.md`.

# %%
from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from regime_map import results_from_csv, results_to_grid, walk_grid
from scan_grid import DEPTHS_M, T_OBS_LABELS, T_OBS_S

# %% [markdown]
# ## Load the §5 grid cache and reshape
#
# `regime_map.results_to_grid` does the reshape by *coordinate value*,
# not by row position — a sorted or shuffled CSV produces the same
# RegimeGrid as a freshly-walked one. Missing or duplicate cells raise
# rather than silently leaving sentinel values, so the figures below
# can't accidentally render a non-rectangular slice.

# %%
CACHE_PATH = Path(__file__).parent / "data" / "regime_map_grid.csv"

if CACHE_PATH.exists():
    results = results_from_csv(CACHE_PATH)
    cache_source = f"cache: {CACHE_PATH}"
else:
    # Coarse fallback so the notebook always renders. Production figures
    # should always come from the full grid cache.
    results = walk_grid(
        radii=tuple(np.geomspace(5e-9, 1e-5, 6)),
        temperatures=(278.15, 298.15, 308.15),
        depths=DEPTHS_M,
        t_obs=(60.0, 3600.0, 86400.0),
    )
    cache_source = "fallback (coarse) walk"

grid = results_to_grid(results)
unique_radii = list(grid.radii)
unique_temps = list(grid.temperatures)
unique_depths = list(grid.depths)
unique_t_obs = list(grid.t_obs)
n_r, n_T, n_h, n_t = grid.regime.shape

print(f"loaded {len(results)} cells from {cache_source}")
print(f"axes: r={n_r}, T={n_T}, h={n_h}, t_obs={n_t}  (total = {n_r*n_T*n_h*n_t})")
print("regime distribution:", dict(Counter(r.regime for r in results)))

# Channel views (preserves the names notebook 02 already uses).
REGIME_LABELS = ["homogeneous", "stratified", "sedimented"]
# Colour-blind-friendly: blue (homog), yellow (stratified), brown (sedim).
REGIME_COLOURS = ["#4575b4", "#fee090", "#a50026"]

regime_grid = grid.regime
ratio_grid = grid.ratio
bmf_grid = grid.bmf
path_grid = grid.path

ti_room = unique_temps.index(298.15) if 298.15 in unique_temps else len(unique_temps) // 2
T_room = unique_temps[ti_room]
print(f"using T = {T_room:.2f} K (index {ti_room}) as the 'room temperature' slice")

# %% [markdown]
# ## Figure 1 — regime map at fixed (T, t_obs)
#
# Single (radius × depth) panel at room temperature and `t_obs = 1 hour`
# (the canonical "did the suspension stay stratified during the
# experiment?" timescale). Each cell is coloured by its §5.1 label.

# %%
figures_dir = Path(__file__).parent / "figures" / "02_regime_map"
figures_dir.mkdir(parents=True, exist_ok=True)


def _draw_regime_panel(
    ax: plt.Axes,
    radii_axis: list[float],
    depths_axis: list[float],
    regime_slice: np.ndarray,
    title: str,
) -> None:
    """Render a single (radius × depth) regime panel on `ax`.

    `regime_slice` has shape (n_r, n_h) with integer regime codes.
    """
    # pcolormesh expects edges, not centres. Build log-mid edges.
    rs = np.asarray(radii_axis)
    hs = np.asarray(depths_axis)
    log_r = np.log10(rs)
    log_h = np.log10(hs)
    edges_r = np.concatenate([
        [log_r[0] - (log_r[1] - log_r[0]) / 2],
        (log_r[:-1] + log_r[1:]) / 2,
        [log_r[-1] + (log_r[-1] - log_r[-2]) / 2],
    ])
    edges_h = np.concatenate([
        [log_h[0] - (log_h[1] - log_h[0]) / 2],
        (log_h[:-1] + log_h[1:]) / 2,
        [log_h[-1] + (log_h[-1] - log_h[-2]) / 2],
    ])
    edges_r_lin = 10.0**edges_r
    edges_h_lin = 10.0**edges_h

    cmap = ListedColormap(REGIME_COLOURS)
    ax.pcolormesh(
        edges_r_lin * 1e9,  # radius in nm
        edges_h_lin * 1e3,  # depth in mm
        regime_slice.T,
        cmap=cmap,
        vmin=-0.5,
        vmax=2.5,
        edgecolors="white",
        linewidth=0.4,
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("particle radius r  [nm]")
    ax.set_ylabel("sample depth h  [mm]")
    ax.set_title(title)


t_idx_1h = unique_t_obs.index(3600.0) if 3600.0 in unique_t_obs else len(unique_t_obs) // 2
_t_value_1h = unique_t_obs[t_idx_1h]
t_obs_label_1h = (
    T_OBS_LABELS[T_OBS_S.index(_t_value_1h)]
    if _t_value_1h in T_OBS_S
    else f"{_t_value_1h:.0f} s"
)

fig, ax = plt.subplots(figsize=(8.0, 5.5))
_draw_regime_panel(
    ax,
    unique_radii,
    unique_depths,
    regime_grid[:, ti_room, :, t_idx_1h],
    title=rf"Regime map at $T = {T_room:.2f}$ K, $t_\mathrm{{obs}} = $ {t_obs_label_1h}",
)
# Manual legend.
legend_handles = [
    plt.Rectangle((0, 0), 1, 1, color=REGIME_COLOURS[i], label=REGIME_LABELS[i])
    for i in range(3)
]
ax.legend(handles=legend_handles, loc="upper right", framealpha=0.95)
fig.tight_layout()
fig.savefig(figures_dir / "regime_map_room_T_1h.png", dpi=140)
fig.savefig(figures_dir / "regime_map_room_T_1h.pdf")
plt.show()

# %% [markdown]
# ## Figure 2 — regime evolution across observation times
#
# Same room-temperature slice as figure 1, scanned across three t_obs
# values (short / medium / long). The sedimented region (brown) grows
# at the expense of the stratified band as t_obs increases — by 1 day
# all but the smallest particles in the deepest cells have settled.

# %%
# Pick three t_obs panels: shortest, mid, longest available.
selected_t_indices = [0, len(unique_t_obs) // 2, len(unique_t_obs) - 1]
selected_t_values = [unique_t_obs[i] for i in selected_t_indices]
selected_t_labels = []
for v in selected_t_values:
    if v in T_OBS_S:
        selected_t_labels.append(T_OBS_LABELS[T_OBS_S.index(v)])
    else:
        selected_t_labels.append(f"{v:.0f} s")

fig, axes = plt.subplots(1, 3, figsize=(16.0, 5.0), sharey=True)
for ax, t_idx, t_label in zip(axes, selected_t_indices, selected_t_labels, strict=True):
    _draw_regime_panel(
        ax,
        unique_radii,
        unique_depths,
        regime_grid[:, ti_room, :, t_idx],
        title=rf"$t_\mathrm{{obs}} = $ {t_label}",
    )
# One legend on the rightmost panel.
axes[-1].legend(handles=legend_handles, loc="upper right", framealpha=0.95)
fig.suptitle(rf"Regime map at $T = {T_room:.2f}$ K, evolution across $t_\mathrm{{obs}}$")
fig.tight_layout()
fig.savefig(figures_dir / "regime_map_room_T_evolution.png", dpi=140)
fig.savefig(figures_dir / "regime_map_room_T_evolution.pdf")
plt.show()

# %% [markdown]
# ## Figure 3 — orchestration provenance
#
# Same slice, coloured by *which execution path* `classify_cell` took.
# The homogeneous corner (top-left) and the long-equilibrated corner
# (bottom-right) skip Method C entirely; the asymptotic-sedimentation
# fallback handles the high-Pe corner with sub-millisecond cost; the
# resolved-mesh `expm_multiply` runs in the diagonal stripe of
# transient stratified cells. This is the provenance plot Phase 5
# committed to in `RegimeResult`'s docstring — auditing the cache
# without having to re-walk.

# %%
PATH_LABELS = [
    "homogeneous short-circuit",
    "equilibrated short-circuit",
    "Method C asymptotic fallback",
    "Method C resolved mesh",
]
PATH_COLOURS = ["#9ecae1", "#a1d99b", "#fdae6b", "#bcbddc"]
path_cmap = ListedColormap(PATH_COLOURS)


def _draw_path_panel(
    ax: plt.Axes,
    radii_axis: list[float],
    depths_axis: list[float],
    path_slice: np.ndarray,
    title: str,
) -> None:
    rs = np.asarray(radii_axis)
    hs = np.asarray(depths_axis)
    log_r = np.log10(rs)
    log_h = np.log10(hs)
    edges_r = np.concatenate([
        [log_r[0] - (log_r[1] - log_r[0]) / 2],
        (log_r[:-1] + log_r[1:]) / 2,
        [log_r[-1] + (log_r[-1] - log_r[-2]) / 2],
    ])
    edges_h = np.concatenate([
        [log_h[0] - (log_h[1] - log_h[0]) / 2],
        (log_h[:-1] + log_h[1:]) / 2,
        [log_h[-1] + (log_h[-1] - log_h[-2]) / 2],
    ])
    ax.pcolormesh(
        10.0**edges_r * 1e9,
        10.0**edges_h * 1e3,
        path_slice.T,
        cmap=path_cmap,
        vmin=-0.5,
        vmax=3.5,
        edgecolors="white",
        linewidth=0.4,
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("particle radius r  [nm]")
    ax.set_ylabel("sample depth h  [mm]")
    ax.set_title(title)


fig, ax = plt.subplots(figsize=(8.5, 5.5))
_path_title = (
    rf"Execution-path provenance at $T = {T_room:.2f}$ K, "
    rf"$t_\mathrm{{obs}} = $ {t_obs_label_1h}"
)
_draw_path_panel(
    ax,
    unique_radii,
    unique_depths,
    path_grid[:, ti_room, :, t_idx_1h],
    title=_path_title,
)
path_handles = [
    plt.Rectangle((0, 0), 1, 1, color=PATH_COLOURS[i], label=PATH_LABELS[i])
    for i in range(4)
]
ax.legend(handles=path_handles, loc="upper right", framealpha=0.95)
fig.tight_layout()
fig.savefig(figures_dir / "path_provenance_room_T_1h.png", dpi=140)
fig.savefig(figures_dir / "path_provenance_room_T_1h.pdf")
plt.show()

# %% [markdown]
# ## Status
#
# Notebook 02 covers deliverable 3 (regime map). The full §5 grid cache
# (`notebooks/data/regime_map_grid.csv`) doubles as deliverable 5 (the
# design table); pretty-printing it as a polished table is a separate
# notebook (03/04, next session).

print("notebook 02 complete; figures written to", figures_dir)
