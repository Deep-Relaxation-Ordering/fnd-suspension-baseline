# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # 05 — Polydispersity smearing (deliverable 6)
#
# *Endorsement Marker: Local stewardship — U. Warring, AG Schätz,
# Physikalisches Institut Freiburg.*
#
# Phase-14 deliverable surface for log-normal particle-size
# polydispersity. Reads the v0.2 §5 regime-map cache and converts the
# sharp-radius classifications into probabilities over
# `(r̄, σ_geom, T, h, t_obs)` using CDF bin masses on the §5 r-axis.

# %%
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from polydispersity import SIGMA_GEOM_AXIS, lognormal_smear
from regime_map import RegimeGrid, results_from_csv, results_to_grid

# %% [markdown]
# ## Load cache and smear
#
# `lognormal_smear(..., on_truncation="mask")` keeps every cell in the
# output and marks cells with more than 5 % tail mass outside the §5
# radius support as `accepted=False`. Deliverable tables can therefore
# show rejected cells explicitly rather than creating gaps.

# %%
CACHE_PATH = Path(__file__).parent / "data" / "regime_map_grid.csv"
DATA_DIR = CACHE_PATH.parent
FIGURES_DIR = Path(__file__).parent / "figures" / "05_polydispersity"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

grid: RegimeGrid = results_to_grid(results_from_csv(CACHE_PATH))
smeared = lognormal_smear(
    grid,
    r_geom_mean_axis=np.asarray(grid.r_material),
    sigma_geom_axis=SIGMA_GEOM_AXIS,
    on_truncation="mask",
)

ROOM_T_K = 298.15
ti_room = grid.temperatures.index(ROOM_T_K)
hi_1mm = grid.depths.index(1e-3)
oi_1h = grid.t_obs.index(3600.0)

print(f"loaded grid {grid.regime.shape} from {CACHE_PATH}")
print(
    "smeared shape:",
    smeared.p_stratified.shape,
    "(r_geom_mean, sigma_geom, T, h, t_obs)",
)
print("sigma_geom axis:", smeared.sigma_geom_axis)

# %% [markdown]
# ## Figure 1 — probabilistic regime RGB
#
# At room temperature, `h = 1 mm`, `t_obs = 1 h`, map
# `(p_homogeneous, p_stratified, p_sedimented)` to RGB channels.

# %%
r_axis = np.asarray(smeared.r_geom_mean_axis)
sigma_axis = np.asarray(smeared.sigma_geom_axis)

rgb = np.stack([
    smeared.p_homogeneous[:, :, ti_room, hi_1mm, oi_1h],
    smeared.p_stratified[:, :, ti_room, hi_1mm, oi_1h],
    smeared.p_sedimented[:, :, ti_room, hi_1mm, oi_1h],
], axis=-1)
rgb = np.clip(rgb, 0.0, 1.0)

fig, ax = plt.subplots(figsize=(8.0, 4.8))
ax.imshow(
    np.transpose(rgb, (1, 0, 2)),
    origin="lower",
    aspect="auto",
    extent=(
        np.log10(r_axis[0]),
        np.log10(r_axis[-1]),
        sigma_axis[0],
        sigma_axis[-1],
    ),
)
xticks_nm = np.array([5, 10, 30, 100, 300, 1000, 3000, 10000], dtype=float)
ax.set_xticks(np.log10(xticks_nm * 1e-9))
ax.set_xticklabels(["5", "10", "30", "100", "300", "1e3", "3e3", "1e4"])
ax.set_yticks(sigma_axis)
ax.set_xlabel("geometric-mean material radius r_bar  [nm]")
ax.set_ylabel("sigma_geom")
ax.set_title("Regime probabilities as RGB, 25 C, h = 1 mm, t_obs = 1 h")
fig.tight_layout()
fig.savefig(FIGURES_DIR / "probabilistic_regime_rgb_room_T_1mm_1h.png", dpi=140)
fig.savefig(FIGURES_DIR / "probabilistic_regime_rgb_room_T_1mm_1h.pdf")
plt.show()

# %% [markdown]
# ## Figure 2 — σ_geom sensitivity at the 100-nm anchor
#
# The §5 r-axis does not land exactly on 100 nm. For this continuous
# sensitivity strip, the geometric mean is set to exactly 100 nm and the
# CDF-bin quadrature determines how the distribution falls over the
# neighbouring §5 bins.

# %%
sigma_strip = np.linspace(1.0, 1.5, 101)
strip = lognormal_smear(
    grid,
    r_geom_mean_axis=(1e-7,),
    sigma_geom_axis=sigma_strip,
    on_truncation="mask",
)

fig, ax = plt.subplots(figsize=(7.5, 4.6))
ax.plot(
    sigma_strip,
    strip.p_homogeneous[0, :, ti_room, hi_1mm, oi_1h],
    lw=2.0,
    label="homogeneous",
)
ax.plot(
    sigma_strip,
    strip.p_stratified[0, :, ti_room, hi_1mm, oi_1h],
    lw=2.0,
    label="stratified",
)
ax.plot(
    sigma_strip,
    strip.p_sedimented[0, :, ti_room, hi_1mm, oi_1h],
    lw=2.0,
    label="sedimented",
)
ax.set_xlabel("sigma_geom")
ax.set_ylabel("regime probability")
ax.set_ylim(-0.02, 1.02)
ax.set_title("100-nm preparation sensitivity, 25 C, h = 1 mm, t_obs = 1 h")
ax.grid(True, alpha=0.3)
ax.legend(loc="best")
fig.tight_layout()
fig.savefig(FIGURES_DIR / "sigma_sensitivity_100nm_room_T_1mm_1h.png", dpi=140)
fig.savefig(FIGURES_DIR / "sigma_sensitivity_100nm_room_T_1mm_1h.pdf")
plt.show()

# %% [markdown]
# ## Figure 3 — experimental suitability map
#
# At room temperature, `h = 1 mm`, `t_obs = 1 h`, plot
# `p_stratified`. This highlights preparations likely to remain
# experimentally informative rather than fully homogeneous or fully
# sedimented.

# %%
p_strat = smeared.p_stratified[:, :, ti_room, hi_1mm, oi_1h]
accepted = smeared.accepted[:, :, ti_room, hi_1mm, oi_1h]

fig, ax = plt.subplots(figsize=(8.0, 4.8))
image = ax.imshow(
    np.ma.masked_where(~accepted.T, p_strat.T),
    origin="lower",
    aspect="auto",
    extent=(
        np.log10(r_axis[0]),
        np.log10(r_axis[-1]),
        sigma_axis[0],
        sigma_axis[-1],
    ),
    vmin=0.0,
    vmax=1.0,
    cmap="viridis",
)
ax.imshow(
    np.ma.masked_where(accepted.T, np.ones_like(p_strat.T)),
    origin="lower",
    aspect="auto",
    extent=(
        np.log10(r_axis[0]),
        np.log10(r_axis[-1]),
        sigma_axis[0],
        sigma_axis[-1],
    ),
    cmap="Greys",
    alpha=0.25,
)
ax.set_xticks(np.log10(xticks_nm * 1e-9))
ax.set_xticklabels(["5", "10", "30", "100", "300", "1e3", "3e3", "1e4"])
ax.set_yticks(sigma_axis)
ax.set_xlabel("geometric-mean material radius r_bar  [nm]")
ax.set_ylabel("sigma_geom")
ax.set_title("p_stratified suitability, 25 C, h = 1 mm, t_obs = 1 h")
cbar = fig.colorbar(image, ax=ax)
cbar.set_label("p_stratified")
fig.tight_layout()
fig.savefig(FIGURES_DIR / "p_stratified_suitability_room_T_1mm_1h.png", dpi=140)
fig.savefig(FIGURES_DIR / "p_stratified_suitability_room_T_1mm_1h.pdf")
plt.show()

# %% [markdown]
# ## Deliverable-6 table
#
# For room temperature and `t_obs = 1 h`, summarise the r̄ interval that
# reaches `p_stratified >= 0.8` for each `(h, σ_geom)`. Rejected
# truncation is included as explicit status and diagnostic columns.

# %%
TARGET_P_STRATIFIED = 0.8


def _format_radius(value: float) -> str:
    if np.isnan(value):
        return "--"
    nm = value * 1e9
    if nm < 1000.0:
        return f"{nm:.0f} nm"
    return f"{nm / 1000.0:.2f} um"


def _format_depth(value: float) -> str:
    return f"{value * 1e3:g} mm"


def _table_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for hi, depth in enumerate(grid.depths):
        for si, sigma in enumerate(smeared.sigma_geom_axis):
            probs = smeared.p_stratified[:, si, ti_room, hi, oi_1h]
            ok = smeared.accepted[:, si, ti_room, hi, oi_1h]
            trunc = smeared.truncation_loss[:, si, ti_room, hi, oi_1h]
            admissible = ok & (probs >= TARGET_P_STRATIFIED)
            rejected_count = int((~ok).sum())
            best_idx = int(np.nanargmax(probs))
            if admissible.any():
                rs = r_axis[admissible]
                status = "accepted" if rejected_count == 0 else "partial_rejected_truncation"
                r_min = float(rs[0])
                r_max = float(rs[-1])
            elif ok.any():
                status = "no_admissible"
                r_min = np.nan
                r_max = np.nan
            else:
                status = "rejected_truncation"
                r_min = np.nan
                r_max = np.nan
            rows.append({
                "sample_depth_m": repr(float(depth)),
                "sample_depth": _format_depth(depth),
                "sigma_geom": repr(float(sigma)),
                "status": status,
                "r_geom_mean_min_m": "" if np.isnan(r_min) else repr(r_min),
                "r_geom_mean_max_m": "" if np.isnan(r_max) else repr(r_max),
                "r_geom_mean_interval": (
                    "--"
                    if np.isnan(r_min)
                    else f"{_format_radius(r_min)} - {_format_radius(r_max)}"
                ),
                "best_p_stratified": repr(float(probs[best_idx])),
                "best_r_geom_mean_m": repr(float(r_axis[best_idx])),
                "max_truncation_loss": repr(float(np.nanmax(trunc))),
                "rejected_rbar_count": str(rejected_count),
            })
    return rows


rows = _table_rows()
csv_path = DATA_DIR / "design_table_polydispersity_room_T.csv"
with csv_path.open("w", newline="\n") as fh:
    fieldnames = list(rows[0])
    writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

md_path = DATA_DIR / "design_table_polydispersity_room_T.md"
md_lines = [
    "# Polydispersity design table -- room temperature (25 C)",
    "",
    "Auto-generated by `notebooks/05_polydispersity_smearing.py` from "
    "`notebooks/data/regime_map_grid.csv`. Rows summarise the geometric-mean "
    "radius interval whose smeared probability satisfies "
    "`p_stratified >= 0.8` at `T = 298.15 K` and `t_obs = 1 h`. "
    "`partial_rejected_truncation` means some r_bar samples at this "
    "sigma lose more than 5 % log-normal mass outside the §5 radius axis; "
    "see the diagnostic columns.",
    "",
    "| h | sigma_geom | status | admissible r_bar interval | "
    "best p_stratified | max truncation_loss | rejected r_bar count |",
    "|---|---|---|---|---|---|---|",
]
for row in rows:
    md_lines.append(
        "| "
        + " | ".join([
            row["sample_depth"],
            row["sigma_geom"],
            row["status"],
            row["r_geom_mean_interval"],
            f"{float(row['best_p_stratified']):.3f}",
            f"{float(row['max_truncation_loss']):.3f}",
            row["rejected_rbar_count"],
        ])
        + " |"
    )
md_path.write_text("\n".join(md_lines) + "\n")

print(f"wrote {csv_path}")
print(f"wrote {md_path}")

# %% [markdown]
# ## Status
#
# Notebook 05 produces deliverable 6: probabilistic regime figures and
# the room-temperature polydispersity design table. The full probability
# tensor is regenerated from the §5 cache by `lognormal_smear`.

print("notebook 05 complete; figures written to", FIGURES_DIR)
