"""Tests for the continuous time-evolution channel (Phase 22 — item J).

Verifies:
- time_series returns monotonically evolving bmf/ratio
- crossing_time finds the correct observation time for a target
- crossing_time returns None for unreachable targets
- crossing_time returns 0.0 for targets already met at t=0
- Phase 30: crossing_parameter sweeps delta_shell_m / lambda_se
"""

from __future__ import annotations

import math

import pytest

from time_evolution import crossing_parameter, crossing_time, time_series

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


# ---------------------------------------------------------------------------
# Phase 30 (work-plan-v0-4 item J) — crossing_parameter
# ---------------------------------------------------------------------------


def test_crossing_parameter_rejects_unknown_parameter() -> None:
    r, T, h = _STRATIFIED_CELL
    with pytest.raises(ValueError, match="parameter must be one of"):
        crossing_parameter(
            r, T, h,
            parameter="not_a_thing",  # type: ignore[arg-type]
            t_obs_s=3600.0,
            p_min=0.0, p_max=1e-8,
        )


def test_crossing_parameter_validates_interval() -> None:
    r, T, h = _STRATIFIED_CELL
    with pytest.raises(ValueError, match="0 <= p_min < p_max"):
        crossing_parameter(
            r, T, h,
            parameter="delta_shell_m",
            t_obs_s=3600.0,
            p_min=1e-8, p_max=1e-9,  # inverted
        )


def test_crossing_parameter_validates_lambda_se_range() -> None:
    r, T, h = _STRATIFIED_CELL
    with pytest.raises(ValueError, match=r"lambda_se must lie in"):
        crossing_parameter(
            r, T, h,
            parameter="lambda_se",
            t_obs_s=3600.0,
            p_min=0.0, p_max=1.5,  # > 1
        )


def test_crossing_parameter_validates_t_obs_positive() -> None:
    r, T, h = _STRATIFIED_CELL
    with pytest.raises(ValueError, match="t_obs_s"):
        crossing_parameter(
            r, T, h,
            parameter="lambda_se",
            t_obs_s=0.0,
            p_min=0.1, p_max=1.0,
        )


def test_crossing_parameter_validates_n_points() -> None:
    r, T, h = _STRATIFIED_CELL
    with pytest.raises(ValueError, match="n_points"):
        crossing_parameter(
            r, T, h,
            parameter="lambda_se",
            t_obs_s=3600.0,
            p_min=0.1, p_max=1.0,
            n_points=2,
        )


@pytest.mark.slow
def test_crossing_parameter_lambda_se_brackets_and_verifies() -> None:
    """Sweep lambda_se for a stratified cell; the returned value must
    reproduce the target bmf at t_obs_s when re-run through solve_cell."""
    r, T, h = _STRATIFIED_CELL
    t_obs_s = 3600.0
    target = 0.25

    p_cross = crossing_parameter(
        r, T, h,
        parameter="lambda_se",
        t_obs_s=t_obs_s,
        p_min=0.1, p_max=1.0,
        criterion="bmf",
        target=target,
        n_points=10,
    )
    assert p_cross is not None
    assert 0.1 <= p_cross <= 1.0

    from fokker_planck import solve_cell

    result = solve_cell(r, T, h, t_total=t_obs_s, lambda_se=p_cross)
    actual = result.bottom_mass_fraction(0.05)
    # PCHIP + brentq on a coarse 10-point sweep: ~5 % relative tolerance
    assert math.isclose(actual, target, rel_tol=0.05, abs_tol=0.005)


@pytest.mark.slow
def test_crossing_parameter_lambda_se_ratio_brackets_and_verifies() -> None:
    """Parameter sweeps also support the ratio criterion shipped in Phase 22."""
    r, T, h = _STRATIFIED_CELL
    t_obs_s = 3600.0
    target = 1e-4

    p_cross = crossing_parameter(
        r, T, h,
        parameter="lambda_se",
        t_obs_s=t_obs_s,
        p_min=0.1, p_max=1.0,
        criterion="ratio",
        target=target,
        n_points=10,
    )
    assert p_cross is not None
    assert 0.1 <= p_cross <= 1.0

    from fokker_planck import solve_cell

    result = solve_cell(r, T, h, t_total=t_obs_s, lambda_se=p_cross)
    actual = result.top_to_bottom_ratio()
    assert math.isclose(actual, target, rel_tol=0.05, abs_tol=1e-5)


@pytest.mark.slow
def test_crossing_parameter_delta_shell_returns_none_when_unreachable() -> None:
    """Homogeneous cell: bmf stays near 0.05 for any delta_shell_m on [0, 50 nm]."""
    r, T, h = _HOMOGENEOUS_CELL
    p_cross = crossing_parameter(
        r, T, h,
        parameter="delta_shell_m",
        t_obs_s=3600.0,
        p_min=0.0, p_max=50e-9,
        criterion="bmf",
        target=0.5,
        n_points=8,
    )
    assert p_cross is None


@pytest.mark.slow
def test_crossing_parameter_lambda_se_returns_none_for_unreachable_target() -> None:
    """Target above equilibrium bmf is unreachable for any lambda_se in (0, 1]."""
    r, T, h = _STRATIFIED_CELL
    p_cross = crossing_parameter(
        r, T, h,
        parameter="lambda_se",
        t_obs_s=3600.0,
        p_min=0.1, p_max=1.0,
        criterion="bmf",
        target=0.999,  # above any plausible equilibrium bmf at this cell
        n_points=8,
    )
    assert p_cross is None
