"""Single source of truth for the breakout-note §5 parameter scan grid.

Spec: breakout-note §5 (parameter scan), §5.1 (regime classification).

The full scan declared in §5 is 30 (radii) × 7 (temperatures) × 5 (depths)
× 6 (observation times) = 6300 cells. This module owns all four axes.
Phase 5 added the t_obs axis once Method C had landed and `regime_map.py`
needed it for finite-time regime classification.

Both `notebooks/01_baseline_validation.py` and `src/regime_map.py`
should read all four axes from *here* rather than restating bounds with
their own `np.geomspace`. This is the centralisation called out in the
2026-04-27 review-fixes lab note: a single edit to the scan widens or
narrows every consumer, which is what the §5 framing actually wants.
"""

from __future__ import annotations

from typing import Final

import numpy as np
from numpy.typing import NDArray

# ---------------------------------------------------------------------------
# Radius axis — breakout-note §5 (5 nm to 10 µm, 30 log-spaced points)
# ---------------------------------------------------------------------------

RADIUS_MIN_M: Final[float] = 5e-9
RADIUS_MAX_M: Final[float] = 1e-5
N_RADII: Final[int] = 30


def radii_m() -> NDArray[np.float64]:
    """30 log-spaced radii covering the §5 scan range, in metres."""
    return np.geomspace(RADIUS_MIN_M, RADIUS_MAX_M, N_RADII)


# ---------------------------------------------------------------------------
# Temperature axis — breakout-note §5 (5 °C to 35 °C, 7 evenly-spaced points)
# ---------------------------------------------------------------------------

TEMPERATURE_MIN_K: Final[float] = 278.15
TEMPERATURE_MAX_K: Final[float] = 308.15
N_TEMPERATURES: Final[int] = 7


def temperatures_k() -> NDArray[np.float64]:
    """7 evenly-spaced temperatures (5 K steps from 5 °C to 35 °C), in kelvin."""
    return np.linspace(TEMPERATURE_MIN_K, TEMPERATURE_MAX_K, N_TEMPERATURES)


# ---------------------------------------------------------------------------
# Sample-depth axis — breakout-note §5 (Ibidi µ-slide → standard cuvette)
# ---------------------------------------------------------------------------
#
# The §5 grid declares 5 depths: four physically-motivated short-path
# values (Ibidi µ-slide regime through 2 mm) plus the standard 10 mm
# cuvette. Resolved in Phase 19 against ADR 0002 D1 (work-plan-v0-3
# anchored to breakout-note v0.2 commit `3b7b18af`); the v0.2 spec is
# the authority and does not override these values. No longer an
# audit-gap pin.

DEPTHS_M: Final[tuple[float, ...]] = (1e-4, 5e-4, 1e-3, 2e-3, 1e-2)
"""Sample depths h, in metres: 0.1, 0.5, 1, 2, 10 mm."""

DEPTH_LABELS: Final[tuple[str, ...]] = ("0.1 mm", "0.5 mm", "1 mm", "2 mm", "10 mm")
"""Human-readable labels aligned with `DEPTHS_M`."""

NOTEBOOK_PREVIEW_DEPTH_INDICES: Final[tuple[int, ...]] = (0, 1, 2, 3)
"""Indices into `DEPTHS_M` shown in notebook 01's regime preview.

Notebook 01 plots only the four short-path depths (≤ 2 mm) to keep the
log-x figure legible; the 10 mm curve sits in the deeply-sedimented
corner across most of the radius range and would crowd the threshold
lines. This index list is the explicit, auditable subset — not an
ad-hoc literal in the notebook.
"""


# ---------------------------------------------------------------------------
# Observation-time axis — breakout-note §5 (six hand-picked t_obs values)
# ---------------------------------------------------------------------------
#
# The §5 grid declares 6 observation times spanning the experimentally
# meaningful range from a single-frame microscopy capture (~1 min) up to
# a several-day session. The values pinned here are *not* strictly
# log-spaced — they are physically-motivated experimental durations
# whose ratios vary (e.g. 600s → 3600s is 6×, 14400s → 86400s is 6×, but
# 60s → 600s is 10×). If a strict log spacing is preferred for plotting
# axes, callers should use `np.geomspace` over the range. The committed
# values are:
#
#   - 1 min      (fast microscopy)
#   - 10 min     (slow microscopy / equilibration check)
#   - 1 h        (typical experiment session)
#   - 4 h        (single-day half-experiment / settling check)
#   - 1 day      (overnight)
#   - 1 week     (long observation / shelf life)
#
# Resolved in Phase 19 against ADR 0002 D1 (anchored to breakout-note
# v0.2 commit `3b7b18af`); the v0.2 spec is the authority and does
# not override these values. No longer an audit-gap pin.

T_OBS_S: Final[tuple[float, ...]] = (60.0, 600.0, 3600.0, 14400.0, 86400.0, 604800.0)
"""Observation times t_obs, in seconds: 1 min, 10 min, 1 h, 4 h, 1 d, 1 w."""

T_OBS_LABELS: Final[tuple[str, ...]] = ("1 min", "10 min", "1 h", "4 h", "1 d", "1 w")
"""Human-readable labels aligned with `T_OBS_S`."""

N_T_OBS: Final[int] = 6
"""Length of the t_obs axis."""
