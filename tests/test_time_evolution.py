"""Tests for the continuous time-evolution channel (Phase 22 — item J).

Verifies:
- time_series returns monotonically evolving bmf/ratio
- crossing_time finds the correct observation time for a target
- crossing_time returns None for unreachable targets
- crossing_time returns 0.0 for targets already met at t=0
"""

from __future__ import annotations

import math

import pytest

from time_evolution import crossing_time, time_series

# Representative cells
_HOMOGENEOUS_CELL = (5e-9, 298.15, 1e-4)  # small r, shallow h → homogeneous
_STRATIFIED_CELL = (1e-7, 298.15, 1e-3)   # mid r, mid h → stratified
_SEDIMENTED_CELL = (1e-6, 298.15, 1e-4)   # large r, shallow h → sedimented


def test_time_series_structure() -> None:
    r, T, h = _STRATIFIED_CELL
    series = time_series(r, T, h)
    assert len(series) == 6  # default t_obs axis
    for t, ratio, bmf, regime in series:
        assert t > 0
        assert 0.0 <= ratio <= 1.0
        assert 0.0 <= bmf <= 1.0
        assert regime in ("homogeneous", "stratified", "sedimented")


def test_time_series_bmf_increases_monotonically() -> None:
    """For a stratified cell, bmf increases with t_obs."""
    r, T, h = _STRATIFIED_CELL
    series = time_series(r, T, h)
    bmfs = [bmf for _, _, bmf, _ in series]
    assert bmfs == sorted(bmfs)


def test_time_series_ratio_decreases_monotonically() -> None:
    """For a stratified cell, ratio decreases with t_obs."""
    r, T, h = _STRATIFIED_CELL
    series = time_series(r, T, h)
    ratios = [ratio for _, ratio, _, _ in series]
    assert ratios == sorted(ratios, reverse=True)


@pytest.mark.slow
@pytest.mark.parametrize(
    "cell, criterion, target",
    [
        (_STRATIFIED_CELL, "bmf", 0.06),
        (_STRATIFIED_CELL, "ratio", 0.5),
    ],
)
def test_crossing_time_hits_target(
    cell: tuple[float, float, float],
    criterion: str,
    target: float,
) -> None:
    """crossing_time finds a t where the criterion is within tolerance."""
    r, T, h = cell
    t_cross = crossing_time(r, T, h, criterion=criterion, target=target, n_points=20)
    assert t_cross is not None
    assert t_cross > 0.0

    # Verify by re-running solve_cell at the found time
    from fokker_planck import solve_cell

    result = solve_cell(r, T, h, t_total=t_cross)
    if criterion == "bmf":
        actual = result.bottom_mass_fraction(0.05)
    else:
        actual = result.top_to_bottom_ratio()

    # PCHIP + brentq should get us within ~1 % relative of the target
    assert math.isclose(actual, target, rel_tol=0.01, abs_tol=0.005)


def test_crossing_time_none_for_unreachable_target() -> None:
    """If target > equilibrium bmf, crossing is impossible."""
    r, T, h = _HOMOGENEOUS_CELL
    t_cross = crossing_time(r, T, h, criterion="bmf", target=0.99)
    assert t_cross is None


def test_crossing_time_zero_for_already_met() -> None:
    """bmf = 0.05 at t=0 (uniform IC), so target <= 0.05 is already met."""
    r, T, h = _STRATIFIED_CELL
    t_cross = crossing_time(r, T, h, criterion="bmf", target=0.05)
    assert t_cross == 0.0


def test_crossing_time_none_for_homogeneous_cell() -> None:
    """A homogeneous cell has bmf ≈ 0.05 for all t — target = 0.1 is unreachable."""
    r, T, h = _HOMOGENEOUS_CELL
    t_cross = crossing_time(r, T, h, criterion="bmf", target=0.1)
    assert t_cross is None
