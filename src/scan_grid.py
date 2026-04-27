"""Single source of truth for the breakout-note §5 parameter scan grid.

Spec: breakout-note §5 (parameter scan), §5.1 (regime classification).

The full scan declared in §5 is 30 (radii) × 7 (temperatures) × 5 (depths)
× 6 (observation times) = 6300 cells. This module exposes the first three
axes; the observation-time axis is deferred until Method B / Method C
land and the t_obs grid stops being a stub in `regime_map.py`.

Until then, both `notebooks/01_baseline_validation.py` and
`src/regime_map.py` should read radius / temperature / depth axes from
*here* rather than restating the bounds with their own `np.geomspace`.
This is the centralisation called out in the 2026-04-27 review-fixes
lab note: a single edit to the scan widens or narrows every consumer,
which is what the §5 framing actually wants.
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
# The §5 grid declares 5 depths; the current pin captures the four
# physically-motivated short-path values (Ibidi µ-slide regime through
# 2 mm) plus the standard 10 mm cuvette. Confirm the 10 mm value against
# the breakout-note §5 table when the next spec drift is reconciled —
# tracked in the 2026-04-27 review-fixes lab note as the single
# remaining spec-vs-impl ambiguity from this pass.

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
