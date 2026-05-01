"""Continuous regime-boundary radii via root-finding (Phase 20 — item B).

The §5 cache labels each (r, T, h, t_obs) cell with a regime, but the
30-radius axis snaps the *boundary* to the grid step (~10 % bin
spacing). This module replaces the snap with a continuous radius via
``scipy.optimize.brentq`` on the underlying ratio / bmf channels.

Two boundaries:

- **Homogeneous → stratified.** Solve ``ratio(r) = 0.95``. Returns the
  largest radius whose Method-C top-to-bottom ratio still meets the
  homogeneous threshold.
- **Stratified → sedimented.** Solve ``bmf(r) = 0.95`` under the guard
  that ``ratio(r) ≤ 0.05`` at the root (round-4 second criterion).
  If the guard ever fails, the search short-circuits and returns
  ``None`` — see the Phase 20 lab note for the design rationale.

The forward-compat contract (work-plan-v0-3 §3, D2 = Option 1) is
preserved: the §5 cache and grid-snapped design-table CSVs are
unchanged. This module ships *additional* continuous-threshold
outputs alongside.

Spec: work-plan-v0-3 §1 item B; ADR 0002 D1 = Option 2 (anchored to
breakout-note v0.2 commit ``3b7b18af``).
"""

from __future__ import annotations

import math
from typing import Final

from scipy.optimize import brentq  # type: ignore[import-untyped]

from regime_map import (
    HOMOGENEOUS_RATIO_THRESHOLD,
    SEDIMENTED_BOTTOM_MASS_THRESHOLD,
    SEDIMENTED_RATIO_THRESHOLD,
    classify_cell,
)

# ---------------------------------------------------------------------------
# Tolerances and constants
# ---------------------------------------------------------------------------

DEFAULT_RTOL: Final[float] = 1e-3
"""Relative tolerance on the recovered radius (brentq ``rtol``)."""

DEFAULT_XTOL: Final[float] = 1e-12
"""Absolute floor on the bracket width passed to brentq (in metres)."""

# ---------------------------------------------------------------------------
# Objective functions (kept at module scope for clarity / testability)
# ---------------------------------------------------------------------------


def _ratio_minus_threshold(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    t_obs_s: float,
    **classify_kwargs,
) -> float:
    """``classify_cell.top_to_bottom_ratio - 0.95``. Positive when homogeneous."""
    result = classify_cell(
        radius_m, temperature_kelvin, sample_depth_m, t_obs_s, **classify_kwargs
    )
    return result.top_to_bottom_ratio - HOMOGENEOUS_RATIO_THRESHOLD


def _bmf_minus_threshold(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    t_obs_s: float,
    **classify_kwargs,
) -> float:
    """``classify_cell.bottom_mass_fraction - 0.95``. Positive when sedimented-bmf."""
    result = classify_cell(
        radius_m, temperature_kelvin, sample_depth_m, t_obs_s, **classify_kwargs
    )
    return result.bottom_mass_fraction - SEDIMENTED_BOTTOM_MASS_THRESHOLD


# ---------------------------------------------------------------------------
# Root finders
# ---------------------------------------------------------------------------


def find_max_homogeneous_radius(
    temperature_kelvin: float,
    sample_depth_m: float,
    t_obs_s: float,
    *,
    r_lo: float,
    r_hi: float,
    rtol: float = DEFAULT_RTOL,
    xtol: float = DEFAULT_XTOL,
    **classify_kwargs,
) -> float | None:
    """Continuous radius at which the top-to-bottom ratio equals 0.95.

    The caller supplies a bracket ``[r_lo, r_hi]`` straddling the
    boundary — typically two adjacent cells from the §5 grid where
    ``r_lo`` is labelled homogeneous and ``r_hi`` is labelled
    stratified. Use :func:`bracket_homogeneous_from_grid` to derive
    the bracket from a ``RegimeGrid``.

    Returns ``None`` if the bracket does not straddle the boundary
    (both endpoints homogeneous, or both stratified). Otherwise
    returns the brentq root.
    """
    f_lo = _ratio_minus_threshold(
        r_lo, temperature_kelvin, sample_depth_m, t_obs_s, **classify_kwargs
    )
    f_hi = _ratio_minus_threshold(
        r_hi, temperature_kelvin, sample_depth_m, t_obs_s, **classify_kwargs
    )

    if f_lo * f_hi > 0.0:
        return None

    if f_lo == 0.0:
        return r_lo
    if f_hi == 0.0:
        return r_hi

    return brentq(
        _ratio_minus_threshold,
        r_lo,
        r_hi,
        args=(temperature_kelvin, sample_depth_m, t_obs_s),
        rtol=rtol,
        xtol=xtol,
    )


def find_min_sedimented_radius(
    temperature_kelvin: float,
    sample_depth_m: float,
    t_obs_s: float,
    *,
    r_lo: float,
    r_hi: float,
    rtol: float = DEFAULT_RTOL,
    xtol: float = DEFAULT_XTOL,
    **classify_kwargs,
) -> float | None:
    """Continuous radius at which the bottom-mass fraction equals 0.95.

    Solves ``bmf(r) = 0.95`` on ``[r_lo, r_hi]`` under the guard that
    ``ratio(r) ≤ 0.05`` at the recovered root (the round-4 second
    criterion). If the guard fails, returns ``None`` — this would
    indicate the bmf-only target is the wrong binding constraint at
    this (T, h, t_obs) and the caller should treat the boundary as
    not-found rather than silently accept a label mismatch.

    The caller supplies a bracket ``[r_lo, r_hi]`` straddling the
    boundary — typically two adjacent cells from the §5 grid where
    ``r_lo`` is *not* labelled sedimented and ``r_hi`` *is*. Use
    :func:`bracket_sedimented_from_grid` to derive the bracket from a
    ``RegimeGrid``.
    """
    f_lo = _bmf_minus_threshold(
        r_lo, temperature_kelvin, sample_depth_m, t_obs_s, **classify_kwargs
    )
    f_hi = _bmf_minus_threshold(
        r_hi, temperature_kelvin, sample_depth_m, t_obs_s, **classify_kwargs
    )

    if f_lo * f_hi > 0.0:
        return None

    if f_lo == 0.0:
        root = r_lo
    elif f_hi == 0.0:
        root = r_hi
    else:
        root = brentq(
            _bmf_minus_threshold,
            r_lo,
            r_hi,
            args=(temperature_kelvin, sample_depth_m, t_obs_s),
            rtol=rtol,
            xtol=xtol,
        )

    # Guard: confirm the round-4 second criterion holds at the root.
    guard_result = classify_cell(
        root, temperature_kelvin, sample_depth_m, t_obs_s, **classify_kwargs
    )
    if guard_result.top_to_bottom_ratio > SEDIMENTED_RATIO_THRESHOLD:
        return None

    return root


# ---------------------------------------------------------------------------
# Grid-bracketing helpers
# ---------------------------------------------------------------------------


def bracket_homogeneous_from_grid(
    radii: tuple[float, ...],
    regime_column: tuple[str, ...],
) -> tuple[float, float] | None:
    """Return ``(r_lo, r_hi)`` straddling the homogeneous→stratified boundary.

    ``radii`` and ``regime_column`` align: ``regime_column[i]`` is the
    §5.1 label of the cell at ``radii[i]`` for a fixed (T, h, t_obs).
    Radii are assumed sorted ascending (the §5 axis is monotone in r).

    Returns ``None`` if no transition is present in the column (all
    homogeneous, or no cell is labelled homogeneous at all).
    """
    if len(radii) != len(regime_column):
        raise ValueError("radii and regime_column must have equal length")
    last_homog_idx = -1
    for i, label in enumerate(regime_column):
        if label == "homogeneous":
            last_homog_idx = i
    if last_homog_idx == -1 or last_homog_idx == len(radii) - 1:
        return None
    return radii[last_homog_idx], radii[last_homog_idx + 1]


def bracket_sedimented_from_grid(
    radii: tuple[float, ...],
    regime_column: tuple[str, ...],
) -> tuple[float, float] | None:
    """Return ``(r_lo, r_hi)`` straddling the stratified→sedimented boundary.

    Mirror of :func:`bracket_homogeneous_from_grid` for the sedimented
    edge. Returns ``None`` if no transition is present (no sedimented
    cell, or the smallest grid radius is already sedimented).
    """
    if len(radii) != len(regime_column):
        raise ValueError("radii and regime_column must have equal length")
    first_sed_idx = -1
    for i, label in enumerate(regime_column):
        if label == "sedimented":
            first_sed_idx = i
            break
    if first_sed_idx <= 0:
        return None
    return radii[first_sed_idx - 1], radii[first_sed_idx]


# ---------------------------------------------------------------------------
# Sanity helper
# ---------------------------------------------------------------------------


def is_finite_radius(value: float | None) -> bool:
    """``True`` iff ``value`` is a finite positive radius (not ``None``, not NaN)."""
    return value is not None and math.isfinite(value) and value > 0.0
