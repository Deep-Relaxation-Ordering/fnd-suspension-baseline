"""Continuous time-evolution channel (Phase 22 — item J).

Provides time-series evaluation and crossing-time root-finding for a
single (r, T, h) cell, treating ``t_obs`` as a continuous variable rather
than the six discrete points of the §5 cache.

The implementation evaluates ``solve_cell`` at a modest number of
log-spaced times and interpolates with a monotonicity-preserving spline
(PCHIP).  This is accurate enough for design-table work while keeping
the per-cell cost tractable (~1–2 s for short-circuit cells, ~10–30 s
for resolved Method-C cells).

Spec: work-plan-v0-3 §1 item J.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

from analytical import equilibration_time_geom
from fokker_planck import solve_cell
from parameters import ParticleGeometry
from regime_map import _classify_from_ratio_and_bmf


def time_series(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    *,
    t_values: tuple[float, ...] | None = None,
    **solve_kwargs,
) -> list[tuple[float, float, float, str]]:
    """Evaluate a cell at a sequence of observation times.

    Returns a list of ``(t_obs_s, ratio, bmf, regime)`` tuples.
    If ``t_values`` is None, uses the §5 default axis
    ``(60, 600, 3600, 14400, 86400, 604800)``.
    """
    if t_values is None:
        t_values = (60.0, 600.0, 3600.0, 14400.0, 86400.0, 604800.0)

    results: list[tuple[float, float, float, str]] = []
    for t in t_values:
        result = solve_cell(
            radius_m,
            temperature_kelvin,
            sample_depth_m,
            t_total=t,
            **solve_kwargs,
        )
        ratio = result.top_to_bottom_ratio()
        bmf = result.bottom_mass_fraction(0.05)
        regime = _classify_from_ratio_and_bmf(ratio, bmf)
        results.append((t, ratio, bmf, regime))

    return results


def crossing_time(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    *,
    criterion: Literal["bmf", "ratio"] = "bmf",
    target: float = 0.5,
    t_min: float = 1.0,
    t_max: float | None = None,
    n_points: int = 15,
    **solve_kwargs,
) -> float | None:
    """Return the observation time at which ``criterion`` crosses ``target``.

    Uses a two-stage approach:

    1. **Bracketing sweep** — evaluate ``solve_cell`` at ``n_points``
       log-spaced times between ``t_min`` and ``t_max``.
    2. **Root-find** — if the target is bracketed, use PCHIP
       interpolation + Brent's method to refine the crossing time.

    Returns ``None`` when:

    - The cell is homogeneous (bmf ≈ 0.05, ratio ≈ 1.0 for all t).
    - The target is above the equilibrium value (never reached).
    - The target is below the initial value (already true at t = 0).

    Parameters
    ----------
    criterion
        ``"bmf"`` searches for ``bottom_mass_fraction(t) = target``.
        ``"ratio"`` searches for ``top_to_bottom_ratio(t) = target``.
    target
        The threshold to cross.
    t_min, t_max
        Search window in seconds.  If ``t_max`` is ``None``, it defaults
        to ``10 · equilibration_time_geom``.
    n_points
        Number of log-spaced samples in the bracketing sweep.
    """
    geom = ParticleGeometry.from_radius(radius_m)

    # ------------------------------------------------------------------
    # Trivial rejections
    # ------------------------------------------------------------------

    if t_max is None:
        t_max = 10.0 * equilibration_time_geom(
            geom, temperature_kelvin, sample_depth_m
        )

    if t_min >= t_max:
        return None

    # Evaluate at equilibrium to see if target is reachable
    t_eq = equilibration_time_geom(geom, temperature_kelvin, sample_depth_m)
    eq_result = solve_cell(
        radius_m,
        temperature_kelvin,
        sample_depth_m,
        t_total=max(t_eq, t_min),
        **solve_kwargs,
    )
    eq_ratio = eq_result.top_to_bottom_ratio()
    eq_bmf = eq_result.bottom_mass_fraction(0.05)

    if criterion == "bmf":
        if target <= 0.05:
            # Already true at t = 0 (uniform IC has bmf = 0.05)
            return 0.0
        if target > eq_bmf:
            return None
    else:  # criterion == "ratio"
        if target >= 1.0:
            return 0.0
        if target < eq_ratio:
            return None

    # ------------------------------------------------------------------
    # Bracketing sweep
    # ------------------------------------------------------------------

    t_vals = np.geomspace(t_min, t_max, n_points)
    y_vals = np.empty(n_points)

    for i, t in enumerate(t_vals):
        result = solve_cell(
            radius_m,
            temperature_kelvin,
            sample_depth_m,
            t_total=t,
            **solve_kwargs,
        )
        if criterion == "bmf":
            y_vals[i] = result.bottom_mass_fraction(0.05) - target
        else:
            y_vals[i] = result.top_to_bottom_ratio() - target

    # ------------------------------------------------------------------
    # Check for bracketing
    # ------------------------------------------------------------------

    # Find the first index where the sign changes
    sign_changes = np.where(np.sign(y_vals[:-1]) != np.sign(y_vals[1:]))[0]
    if sign_changes.size == 0:
        return None

    idx = sign_changes[0]
    t_lo, t_hi = float(t_vals[idx]), float(t_vals[idx + 1])
    y_lo, y_hi = float(y_vals[idx]), float(y_vals[idx + 1])

    # Guard against exact zero (already on target)
    if abs(y_lo) < 1e-12:
        return t_lo
    if abs(y_hi) < 1e-12:
        return t_hi

    # ------------------------------------------------------------------
    # PCHIP interpolation + Brent root-find
    # ------------------------------------------------------------------

    interpolator = PchipInterpolator(t_vals, y_vals)

    try:
        root = brentq(interpolator, t_lo, t_hi)
    except ValueError:
        # PCHIP may not bracket exactly — fall back to linear interpolation
        root = t_lo - y_lo * (t_hi - t_lo) / (y_hi - y_lo)

    return float(root)
