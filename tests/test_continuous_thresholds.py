"""Tests for ``src/continuous_thresholds.py`` (Phase 20 — item B).

Pin the root-finder behaviour:

- Returns a radius that lies *between* the bracketing §5 cells.
- The recovered radius produces ratio ≈ 0.95 (homogeneous boundary)
  or bmf ≈ 0.95 (sedimented boundary).
- Sedimented finder honours the round-4 second criterion guard
  (``ratio ≤ 0.05``).
- Returns ``None`` when no transition exists in the bracket.
- Bracket helpers find the right adjacent §5 grid cells.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from continuous_thresholds import (  # noqa: E402
    DEFAULT_RTOL,
    bracket_homogeneous_from_grid,
    bracket_sedimented_from_grid,
    find_max_homogeneous_radius,
    find_min_sedimented_radius,
    is_finite_radius,
)
from regime_map import (  # noqa: E402
    HOMOGENEOUS_RATIO_THRESHOLD,
    SEDIMENTED_BOTTOM_MASS_THRESHOLD,
    SEDIMENTED_RATIO_THRESHOLD,
    classify_cell,
)
from scan_grid import radii_m  # noqa: E402

# A (T, h, t_obs) tuple that produces a clean homogeneous → stratified
# → sedimented sweep across the §5 r-axis at room temperature, 1-mm
# depth, 1-day observation.
ROOM_T_K = 298.15
DEPTH_1MM_M = 1e-3
T_OBS_1D_S = 86400.0


def _grid_column(temperature_k: float, sample_depth_m: float, t_obs_s: float):
    """Walk the §5 r-axis at fixed (T, h, t_obs); return (radii, labels)."""
    radii = tuple(float(r) for r in radii_m())
    labels = tuple(
        classify_cell(r, temperature_k, sample_depth_m, t_obs_s).regime for r in radii
    )
    return radii, labels


@pytest.fixture(scope="module")
def room_t_1mm_1day_column():
    """Memoised §5 r-axis walk at (298.15 K, 1 mm, 1 day) — reused by 4 tests."""
    return _grid_column(ROOM_T_K, DEPTH_1MM_M, T_OBS_1D_S)


# ---------------------------------------------------------------------------
# Bracket helpers
# ---------------------------------------------------------------------------


def test_bracket_homogeneous_finds_adjacent_cells_in_grid(room_t_1mm_1day_column) -> None:
    radii, labels = room_t_1mm_1day_column
    bracket = bracket_homogeneous_from_grid(radii, labels)
    assert bracket is not None
    r_lo, r_hi = bracket
    assert r_lo < r_hi
    # The bracket must straddle the boundary: r_lo is the last
    # homogeneous radius, r_hi is the next one (not homogeneous).
    lo_idx = radii.index(r_lo)
    assert labels[lo_idx] == "homogeneous"
    assert labels[lo_idx + 1] != "homogeneous"


def test_bracket_sedimented_finds_adjacent_cells_in_grid(room_t_1mm_1day_column) -> None:
    radii, labels = room_t_1mm_1day_column
    bracket = bracket_sedimented_from_grid(radii, labels)
    assert bracket is not None
    r_lo, r_hi = bracket
    assert r_lo < r_hi
    hi_idx = radii.index(r_hi)
    assert labels[hi_idx] == "sedimented"
    assert labels[hi_idx - 1] != "sedimented"


def test_bracket_homogeneous_returns_none_for_all_homogeneous_column() -> None:
    radii = (5e-9, 1e-8, 2e-8)
    labels = ("homogeneous", "homogeneous", "homogeneous")
    assert bracket_homogeneous_from_grid(radii, labels) is None


def test_bracket_sedimented_returns_none_for_no_sedimented_column() -> None:
    radii = (5e-9, 1e-8, 2e-8)
    labels = ("homogeneous", "stratified", "stratified")
    assert bracket_sedimented_from_grid(radii, labels) is None


def test_bracket_lengths_must_match() -> None:
    with pytest.raises(ValueError):
        bracket_homogeneous_from_grid((1.0, 2.0), ("homogeneous",))


# ---------------------------------------------------------------------------
# find_max_homogeneous_radius
# ---------------------------------------------------------------------------


def test_find_max_homogeneous_radius_recovers_threshold_ratio(
    room_t_1mm_1day_column,
) -> None:
    """At the recovered radius, classify_cell.top_to_bottom_ratio ≈ 0.95."""
    radii, labels = room_t_1mm_1day_column
    bracket = bracket_homogeneous_from_grid(radii, labels)
    assert bracket is not None
    r_lo, r_hi = bracket

    r_star = find_max_homogeneous_radius(
        ROOM_T_K, DEPTH_1MM_M, T_OBS_1D_S, r_lo=r_lo, r_hi=r_hi
    )
    assert is_finite_radius(r_star)
    assert r_lo <= r_star <= r_hi

    result = classify_cell(r_star, ROOM_T_K, DEPTH_1MM_M, T_OBS_1D_S)
    assert result.top_to_bottom_ratio == pytest.approx(
        HOMOGENEOUS_RATIO_THRESHOLD, rel=DEFAULT_RTOL * 5
    )


def test_find_max_homogeneous_radius_returns_none_when_no_transition() -> None:
    """If the bracket sits entirely on one side, return None."""
    # Both endpoints in the deeply-homogeneous corner (5 nm at 0.1 mm
    # / 1 week — both should reach the homogeneous label).
    result = find_max_homogeneous_radius(
        ROOM_T_K, sample_depth_m=1e-4, t_obs_s=604800.0, r_lo=5e-9, r_hi=8e-9
    )
    assert result is None


def test_find_max_homogeneous_radius_handles_endpoint_at_threshold(
    room_t_1mm_1day_column,
) -> None:
    """If r_lo or r_hi sits exactly on f(r) = 0, return that endpoint."""
    radii, labels = room_t_1mm_1day_column
    bracket = bracket_homogeneous_from_grid(radii, labels)
    assert bracket is not None
    r_lo, r_hi = bracket

    # Pin r_lo to the recovered root — second call should return r_lo
    # (since f(r_lo) is now 0 by construction).
    r_star = find_max_homogeneous_radius(
        ROOM_T_K, DEPTH_1MM_M, T_OBS_1D_S, r_lo=r_lo, r_hi=r_hi
    )
    assert r_star is not None
    r_star2 = find_max_homogeneous_radius(
        ROOM_T_K, DEPTH_1MM_M, T_OBS_1D_S, r_lo=r_star, r_hi=r_hi
    )
    assert r_star2 is not None
    assert abs(r_star2 - r_star) <= max(DEFAULT_RTOL * r_star, 1e-12)


# ---------------------------------------------------------------------------
# find_min_sedimented_radius
# ---------------------------------------------------------------------------


def test_find_min_sedimented_radius_recovers_threshold_bmf(
    room_t_1mm_1day_column,
) -> None:
    """At the recovered radius, classify_cell.bottom_mass_fraction ≈ 0.95."""
    radii, labels = room_t_1mm_1day_column
    bracket = bracket_sedimented_from_grid(radii, labels)
    assert bracket is not None
    r_lo, r_hi = bracket

    r_star = find_min_sedimented_radius(
        ROOM_T_K, DEPTH_1MM_M, T_OBS_1D_S, r_lo=r_lo, r_hi=r_hi
    )
    assert is_finite_radius(r_star)
    assert r_lo <= r_star <= r_hi

    result = classify_cell(r_star, ROOM_T_K, DEPTH_1MM_M, T_OBS_1D_S)
    assert result.bottom_mass_fraction == pytest.approx(
        SEDIMENTED_BOTTOM_MASS_THRESHOLD, rel=DEFAULT_RTOL * 5
    )
    # Round-4 guard must pass at the root.
    assert result.top_to_bottom_ratio <= SEDIMENTED_RATIO_THRESHOLD


def test_find_min_sedimented_radius_returns_none_when_no_transition() -> None:
    # 5 nm to 8 nm at 0.1 mm / 1 min — too small to sediment.
    result = find_min_sedimented_radius(
        ROOM_T_K, sample_depth_m=1e-4, t_obs_s=60.0, r_lo=5e-9, r_hi=8e-9
    )
    assert result is None


# ---------------------------------------------------------------------------
# is_finite_radius
# ---------------------------------------------------------------------------


def test_is_finite_radius_handles_none_and_nan_and_zero() -> None:
    assert is_finite_radius(1e-7)
    assert not is_finite_radius(None)
    assert not is_finite_radius(0.0)
    assert not is_finite_radius(-1e-7)
    assert not is_finite_radius(float("nan"))
    assert not is_finite_radius(float("inf"))
