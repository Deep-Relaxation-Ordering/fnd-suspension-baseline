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
# # TUT-06 — Interactive cache explorer
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Deep-Relaxation-Ordering/fnd-suspension-baseline/blob/main/notebooks/tutorials/06_cache_explorer.ipynb)
#
# **Tutorial ID**: TUT-06
# **Purpose**: Interactive (ipywidgets) and static-fallback exploration of the
# §5 regime-map cache — slice across temperature, depth, and t_obs without
# leaving the notebook.
# **Expected runtime**: < 60 s (interactive widget render is one-shot)
# **Release tag**: `pilot-v0.4`
# **Canonical inputs**: `notebooks/data/regime_map_grid.csv`
# **Smoke command**: `PYTHONPATH=src python notebooks/tutorials/06_cache_explorer.py`
#
# **Links**:
# - Tutorial roadmap
# - Deliverable index
# - Phase 31 release-criterion gap audit (for context on what the cache covers)
#
# **Runtime modes**:
# - **Jupyter / Colab kernel + ipywidgets** → interactive sliders for
#   temperature, depth, and observation time; live regime-count summary
#   and ratio-vs-radius plot.
# - **Plain `python` smoke run** → static demo on a representative
#   (T = 298.15 K, h = 1 mm, t_obs = 1 h) slice. The smoke gate uses
#   this fallback path; the interactive code is skipped cleanly.
#
# **Citation/reuse**: Please see `CITATION.cff`, `codemeta.json`, `LICENCE`,
# and `pyproject.toml` in the repository root.

# %%
# Colab bootstrap — clones the repo on first run so cache + src are available.
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
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from regime_map import results_from_csv

# %% [markdown]
# ## Detect runtime: interactive (Jupyter/Colab) vs static (plain Python)
#
# The interactive path needs both `ipywidgets` *and* an active IPython kernel
# (so widget output is renderable). When either is missing, we render a
# static slice and exit cleanly — this is the smoke-gate path.

# %%
def _is_interactive_kernel() -> bool:
    """True only when ipywidgets are usable AND we are in a notebook kernel."""
    try:
        import ipywidgets  # noqa: F401
        from IPython import get_ipython
    except ImportError:
        return False
    ip = get_ipython()
    if ip is None:
        return False
    # ZMQInteractiveShell == Jupyter / Colab kernel.
    return type(ip).__name__ == "ZMQInteractiveShell"


INTERACTIVE = _is_interactive_kernel()
print(f"Interactive kernel detected: {INTERACTIVE}")

# %% [markdown]
# ## Load the cache

# %%
try:
    cache_path = Path(__file__).resolve().parent.parent / "data" / "regime_map_grid.csv"
except NameError:
    cache_path = Path("notebooks/data/regime_map_grid.csv")

results = list(results_from_csv(cache_path))
print(f"Loaded {len(results)} cells from {cache_path.name}")

axis_T = sorted({r.temperature_kelvin for r in results})
axis_h = sorted({r.sample_depth_m for r in results})
axis_tobs = sorted({r.t_obs_s for r in results})

print(f"  Temperatures (K): {[f'{T:.2f}' for T in axis_T]}")
print(f"  Depths (m):       {axis_h}")
print(f"  t_obs (s):        {axis_tobs}")


# %% [markdown]
# ## Slice + render helper
#
# `render_slice(T, h, t_obs)` is the single entry point — both the
# interactive and the static paths call it. It computes the regime-count
# summary and (if matplotlib's interactive backend is available) draws a
# `top_to_bottom_ratio` curve as a function of radius for that slice.

# %%
def render_slice(T_k: float, depth_m: float, t_obs_s: float, draw: bool = True):
    """Filter the cache to one (T, h, t_obs) slice and report it."""
    sliced = [
        r for r in results
        if np.isclose(r.temperature_kelvin, T_k)
        and np.isclose(r.sample_depth_m, depth_m)
        and np.isclose(r.t_obs_s, t_obs_s)
    ]
    if not sliced:
        print(f"No cells found at T={T_k} K, h={depth_m} m, t_obs={t_obs_s} s.")
        return None
    counts = Counter(r.regime for r in sliced)
    print(
        f"\nSlice: T={T_k:.2f} K, h={depth_m * 1e3:.2f} mm, t_obs={t_obs_s:.0f} s "
        f"-> {len(sliced)} cells",
    )
    print(
        f"  homogeneous: {counts.get('homogeneous', 0):3d} | "
        f"stratified:  {counts.get('stratified',  0):3d} | "
        f"sedimented:  {counts.get('sedimented',  0):3d}",
    )

    if not draw:
        return sliced

    sliced.sort(key=lambda r: r.r_material_m)
    radii_nm = np.array([r.r_material_m * 1e9 for r in sliced])
    ratios = np.array([r.top_to_bottom_ratio for r in sliced])
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.semilogx(radii_nm, ratios, marker="o", linewidth=1.0)
    ax.axhline(0.95, color="C2", linestyle=":", label="homog threshold")
    ax.axhline(0.05, color="C3", linestyle=":", label="sedim threshold")
    ax.set_xlabel("material radius / nm")
    ax.set_ylabel("c(h) / c(0)")
    ax.set_title(f"T={T_k:.2f} K, h={depth_m*1e3:.2f} mm, t_obs={t_obs_s:.0f} s")
    ax.legend(loc="best", fontsize="small")
    ax.set_ylim(-0.05, 1.05)
    plt.tight_layout()
    if INTERACTIVE:
        plt.show()
    else:
        plt.close(fig)
    return sliced


# %% [markdown]
# ## Static fallback (smoke-gate path)
#
# Always runs. In an interactive kernel, this seeds the example before the
# widget mounts; in plain Python, this *is* the demo.

# %%
DEFAULT_T = 298.15
DEFAULT_H = 1e-3
DEFAULT_TOBS = 3600.0
_ = render_slice(DEFAULT_T, DEFAULT_H, DEFAULT_TOBS, draw=False)

# %% [markdown]
# ## Interactive widgets (Jupyter / Colab only)
#
# In a notebook kernel, the cell below mounts three dropdowns (one per
# axis) and re-renders the slice + plot live as the user changes any
# axis value. In plain Python this cell prints a one-line skip message
# and returns.

# %%
if INTERACTIVE:
    from IPython.display import display
    from ipywidgets import Dropdown, HBox, VBox, interactive_output

    T_widget = Dropdown(
        options=[(f"{T:.2f} K", T) for T in axis_T],
        value=DEFAULT_T,
        description="T",
    )
    h_widget = Dropdown(
        options=[(f"{h*1e3:.2f} mm", h) for h in axis_h],
        value=DEFAULT_H,
        description="depth",
    )
    tobs_widget = Dropdown(
        options=[(f"{t:.0f} s", t) for t in axis_tobs],
        value=DEFAULT_TOBS,
        description="t_obs",
    )
    out = interactive_output(
        render_slice,
        {"T_k": T_widget, "depth_m": h_widget, "t_obs_s": tobs_widget},
    )
    display(VBox([HBox([T_widget, h_widget, tobs_widget]), out]))
else:
    print("\n[non-interactive] ipywidgets unavailable or no notebook kernel; "
          "static demo above is the full output.")

# %% [markdown]
# ## Where to go next
#
# - Previous tutorial: TUT-05 — Experimental envelope (model validity caveats).
# - Open v1.0 gates the cache does *not* yet cover: see Phase 31
#   release-criterion gap audit (`lab_notes/2026-05-06-phase31-...md`).
# - To regenerate the cache itself, see notebook `04_design_table.py` and
#   `regime_map.walk_grid` (Phase 19 / Phase 30 macOS-safe parallel walk).
