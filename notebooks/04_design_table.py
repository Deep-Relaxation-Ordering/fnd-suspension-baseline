# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # 04 — Design table (deliverable 5)
#
# *Endorsement Marker: Local stewardship — U. Warring, AG Schätz,
# Physikalisches Institut Freiburg.*
#
# Phase-7 deliverable-5 surface for the breakout note. Reads the §5
# grid cache (`notebooks/data/regime_map_grid.csv`, written by
# Phase 6's `regime_map.walk_grid`) and renders the experimental
# design table:
#
# *"For each (sample depth h, observation time t_obs, temperature T),
# what is the largest tested radius that stays `homogeneous`, and the
# smallest tested radius that classifies as `sedimented`?"*
#
# Two tables result:
#
# 1. **Largest tested homogeneous radius**: the largest `r` *from the
#    §5 r-axis* per (h, t_obs, T) with regime ≡ `homogeneous`. The
#    true homogeneous-stratified transition lies between this radius
#    and the next §5 sample (~10 % bin spacing) — this is a snapped
#    upper bound, not an interpolated threshold.
# 2. **Smallest tested sedimented radius**: the smallest `r` from
#    the §5 r-axis classified `sedimented` (and the round-4
#    bottom-mass criterion satisfied). Same caveat: the true
#    transition lies between this radius and the previous §5 sample.
#
# Both tables are written as CSV (machine-readable, full precision)
# and a printable Markdown table at room temperature
# (`notebooks/data/design_table_*.csv`,
# `notebooks/data/design_table_room_T.md`). The full multi-T CSVs
# are the §5/§6 deliverable; the Markdown is the at-a-glance summary.
# For continuous interpolated boundaries see notebook 03's analytic
# equilibrium overlay.

# %%
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from regime_map import RegimeGrid, results_from_csv, results_to_grid

# %% [markdown]
# ## Load the cache
#
# Same coordinate-indexed reshape used by notebooks 02 and 03, so the
# table indices below are by physical value, not by row position in
# the cache.

# %%
CACHE_PATH = Path(__file__).parent / "data" / "regime_map_grid.csv"
DATA_DIR = CACHE_PATH.parent

if not CACHE_PATH.exists():
    raise FileNotFoundError(
        f"design table requires the §5 grid cache at {CACHE_PATH}; "
        "run `regime_map.walk_grid` and `results_to_csv` first "
        "(takes ~2.5 hours single-threaded)."
    )

grid: RegimeGrid = results_to_grid(results_from_csv(CACHE_PATH))
n_cells = (
    len(grid.radii) * len(grid.temperatures) * len(grid.depths) * len(grid.t_obs)
)
print(f"loaded grid {grid.regime.shape} ({n_cells} cells)")
print(f"temperatures: {[f'{T-273.15:.0f}°C' for T in grid.temperatures]}")
print(f"depths: {[f'{h*1e3:.1f}mm' for h in grid.depths]}")
print(f"t_obs: {[f'{t:.0f}s' for t in grid.t_obs]}")

# %% [markdown]
# ## Compute the band edges
#
# Per (h, t_obs, T), scan the 30-radius axis from small → large and
# find the regime transitions. The §5 axis is monotone in r (larger
# r = more sedimented), so the first non-homogeneous index is the
# upper edge of the homogeneous band, and the first sedimented index
# is the lower edge of the sedimented band. NaN if no such cell
# exists at this (h, t_obs, T).

# %%
REGIME_HOMOGENEOUS = 0
REGIME_SEDIMENTED = 2


def _band_edges(grid: RegimeGrid) -> tuple[np.ndarray, np.ndarray]:
    """Return (max_r_homogeneous, min_r_sedimented) arrays of shape (n_h, n_t_obs, n_T)."""
    n_r, n_T, n_h, n_t_obs = grid.regime.shape
    rs = np.asarray(grid.radii)

    max_homog = np.full((n_h, n_t_obs, n_T), np.nan, dtype=np.float64)
    min_sed = np.full((n_h, n_t_obs, n_T), np.nan, dtype=np.float64)

    for hi in range(n_h):
        for oi in range(n_t_obs):
            for ti in range(n_T):
                col = grid.regime[:, ti, hi, oi]
                homog_idx = np.where(col == REGIME_HOMOGENEOUS)[0]
                sed_idx = np.where(col == REGIME_SEDIMENTED)[0]
                if homog_idx.size > 0:
                    max_homog[hi, oi, ti] = rs[homog_idx[-1]]
                if sed_idx.size > 0:
                    min_sed[hi, oi, ti] = rs[sed_idx[0]]
    return max_homog, min_sed


max_homog_r, min_sed_r = _band_edges(grid)
print(f"max_homog_r shape: {max_homog_r.shape}  (h, t_obs, T)")

# %% [markdown]
# ## Write the full multi-T tables (deliverable 5 — machine-readable)

# %%
def _write_band_csv(
    path: Path,
    band: np.ndarray,
    grid: RegimeGrid,
    label: str,
) -> None:
    """One row per (h, t_obs); one column per T."""
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = ["sample_depth_m", "t_obs_s"] + [
        f"{label}_T_{T-273.15:.0f}C_m" for T in grid.temperatures
    ]
    with path.open("w", newline="\n") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(headers)
        for hi, h in enumerate(grid.depths):
            for oi, t in enumerate(grid.t_obs):
                row = [repr(float(h)), repr(float(t))]
                for ti in range(len(grid.temperatures)):
                    val = band[hi, oi, ti]
                    row.append("" if np.isnan(val) else repr(float(val)))
                writer.writerow(row)


_write_band_csv(
    DATA_DIR / "design_table_max_homogeneous_r.csv",
    max_homog_r,
    grid,
    label="max_homog_r",
)
_write_band_csv(
    DATA_DIR / "design_table_min_sedimented_r.csv",
    min_sed_r,
    grid,
    label="min_sed_r",
)
print(f"wrote {DATA_DIR / 'design_table_max_homogeneous_r.csv'}")
print(f"wrote {DATA_DIR / 'design_table_min_sedimented_r.csv'}")

# %% [markdown]
# ## Printable Markdown summary at room temperature
#
# At-a-glance table for the 25 °C slice — one Markdown table per
# band, indexed by (h × t_obs). The full multi-T CSVs above are the
# authoritative form; the Markdown here is the human-readable
# extract for inclusion in lab notes / paper drafts.

# %%
ROOM_T_K = 298.15
ti_room = grid.temperatures.index(ROOM_T_K) if ROOM_T_K in grid.temperatures else 4


def _format_radius(value: float) -> str:
    """Human-readable radius: '12 nm', '350 nm', '1.2 µm', or '—'."""
    if np.isnan(value):
        return "—"
    nm = value * 1e9
    if nm < 1.0:
        return f"{nm:.2f} nm"
    if nm < 1000.0:
        return f"{nm:.0f} nm"
    return f"{nm/1000:.2f} µm"


def _format_t_obs(t: float) -> str:
    if t < 60:
        return f"{t:.0f} s"
    if t < 3600:
        return f"{t/60:.0f} min"
    if t < 86400:
        return f"{t/3600:.0f} h"
    if t < 604800:
        return f"{t/86400:.0f} d"
    return f"{t/604800:.0f} w"


def _format_h(h: float) -> str:
    return f"{h*1e3:g} mm"


def _markdown_band_table(
    band: np.ndarray,
    grid: RegimeGrid,
    ti: int,
    title: str,
    rule: str,
) -> str:
    """Render `band[:, :, ti]` as a Markdown table."""
    out: list[str] = []
    out.append(f"### {title}")
    out.append("")
    out.append(rule)
    out.append("")
    header = "| h \\ t_obs | " + " | ".join(_format_t_obs(t) for t in grid.t_obs) + " |"
    sep = "|---" * (len(grid.t_obs) + 1) + "|"
    out.append(header)
    out.append(sep)
    for hi, h in enumerate(grid.depths):
        cells = " | ".join(_format_radius(band[hi, oi, ti]) for oi in range(len(grid.t_obs)))
        out.append(f"| {_format_h(h)} | {cells} |")
    out.append("")
    return "\n".join(out)


md_path = DATA_DIR / "design_table_room_T.md"
md_lines: list[str] = []
md_lines.append("# Design table — room temperature (25 °C)")
md_lines.append("")
md_lines.append(
    "Auto-generated by `notebooks/04_design_table.py` from "
    "`notebooks/data/regime_map_grid.csv` (the Phase-6 §5 cache). "
    "Values are *grid-snapped* radii from the §5 r-axis (30 log-spaced "
    "points, ~10 % bin spacing) — not interpolated thresholds. The "
    "true regime transition lies between adjacent §5 samples; for a "
    "continuous analytic equilibrium boundary see notebook 03's "
    "`homogeneous_envelope_vs_T` figure. '—' = no §5 cell at this "
    "(h, t_obs) reaches that band."
)
md_lines.append("")
md_lines.append(_markdown_band_table(
    max_homog_r,
    grid,
    ti_room,
    title="Largest tested radius that stays homogeneous",
    rule=(
        "*Largest §5 r-axis sample whose Method-C ratio ≥ 0.95 at the "
        "given (h, t_obs). The true homogeneous→stratified transition "
        "is between this radius and the next §5 sample.*"
    ),
))
md_lines.append(_markdown_band_table(
    min_sed_r,
    grid,
    ti_room,
    title="Smallest tested radius that classifies as sedimented",
    rule=(
        "*Smallest §5 r-axis sample with ratio ≤ 0.05 *and* "
        "bottom-5 % mass fraction ≥ 0.95 (round-4 second criterion: "
        "cells in transit are not sedimented). The true "
        "stratified→sedimented transition is between the previous §5 "
        "sample and this one.*"
    ),
))
md_path.write_text("\n".join(md_lines))
print(f"wrote {md_path}")

# %%
print(_markdown_band_table(
    max_homog_r,
    grid,
    ti_room,
    title="Largest tested homogeneous radius (preview)",
    rule=(
        "*(grid-snapped to the §5 r-axis at 25 °C; full multi-T CSV in "
        "design_table_max_homogeneous_r.csv)*"
    ),
))

# %% [markdown]
# ## Status
#
# Notebook 04 produces deliverable 5. The two band-edge CSVs are the
# machine-readable design table; `design_table_room_T.md` is the
# at-a-glance Markdown summary for inclusion in the breakout-note
# §6 deliverable section. The full §5 grid cache remains the
# authoritative form — these tables are derived projections.

print("notebook 04 complete; tables written under", DATA_DIR)
