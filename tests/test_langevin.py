"""Method B — kernel-level sanity tests.

Spec: breakout-note §4.1 Method B.

Covers the timestep policy, the feasibility envelope, the reflecting
boundary fold, and a determinism check on the simulator. The
*physics* validation of Method B (long-time barometric agreement,
position-variance saturation, MSD limits, arrival times) lives in
`test_equilibrium.py` and `test_method_consistency.py` per the §4.4
checklist.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from analytical import settling_velocity
from langevin import (
    ALPHA,
    BETA,
    LangevinResult,
    _reflect_into_box,
    adaptive_timestep,
    is_feasible,
    simulate,
    simulate_cell,
)
from parameters import diffusivity

# ---------------------------------------------------------------------------
# Adaptive timestep policy
# ---------------------------------------------------------------------------


def test_adaptive_timestep_pure_brownian_uses_box_diffusion_scale() -> None:
    """v_sed = 0 ⇒ dt = β · h² / D."""
    h, d = 1e-6, 2.45e-12
    dt = adaptive_timestep(0.0, d, h)
    assert math.isclose(dt, BETA * h**2 / d, rel_tol=1e-15)


def test_adaptive_timestep_pure_sedimentation_uses_drift_scale() -> None:
    """D = 0 ⇒ dt = α · h / v_sed (no diffusive term)."""
    v, h = 1e-6, 1e-3
    dt = adaptive_timestep(v, 0.0, h)
    assert math.isclose(dt, ALPHA * h / v, rel_tol=1e-15)


def test_adaptive_timestep_general_picks_min_of_two_scales() -> None:
    """In the strongly-stratified regime, ℓ_g < h: dt = min(α ℓ_g/v, β ℓ_g²/D)."""
    v_sed = settling_velocity(1e-7, 298.15)
    d = diffusivity(1e-7, 298.15)
    h = 1e-3
    ell_g = d / v_sed
    assert ell_g < h, "test premise: stratified cell"
    expected = min(ALPHA * ell_g / v_sed, BETA * ell_g**2 / d)
    assert math.isclose(adaptive_timestep(v_sed, d, h), expected, rel_tol=1e-15)


def test_adaptive_timestep_diffusion_dominated_falls_back_to_h() -> None:
    """When ℓ_g ≫ h the gravitational scale doesn't constrain the
    timestep — fall back to β·h²/D (round-2 fix)."""
    # 5 nm at 25 °C, 1 mm: ℓ_g ≈ 32 cm ≫ h.
    v_sed = settling_velocity(5e-9, 298.15)
    d = diffusivity(5e-9, 298.15)
    h = 1e-3
    assert d / v_sed > h
    dt = adaptive_timestep(v_sed, d, h)
    assert math.isclose(dt, BETA * h**2 / d, rel_tol=1e-15)


def test_adaptive_timestep_rejects_zero_drift_and_diffusion() -> None:
    with pytest.raises(ValueError):
        adaptive_timestep(0.0, 0.0, 1e-3)


# ---------------------------------------------------------------------------
# Feasibility envelope
# ---------------------------------------------------------------------------


def test_feasibility_envelope_rejects_micron_cells_at_long_t() -> None:
    """r = 10 µm cells need sub-nanosecond steps; round-3 fix flags them out."""
    v = settling_velocity(1e-5, 298.15)
    d = diffusivity(1e-5, 298.15)
    check = is_feasible(v, d, 1e-3, t_total=1e4)
    assert check.feasible is False


def test_feasibility_envelope_accepts_100nm_cells() -> None:
    v = settling_velocity(1e-7, 298.15)
    d = diffusivity(1e-7, 298.15)
    check = is_feasible(v, d, 1e-4, t_total=1000.0)
    assert check.feasible is True
    assert check.n_steps > 0
    assert check.dt_policy > 0.0


def test_feasibility_dt_policy_matches_adaptive_timestep() -> None:
    """``dt_policy`` is the round-2 upper bound, not the simulator's
    actual step. Pin that contract so callers don't confuse them."""
    v = settling_velocity(1e-7, 298.15)
    d = diffusivity(1e-7, 298.15)
    h = 1e-4
    check = is_feasible(v, d, h, t_total=1000.0)
    assert check.dt_policy == adaptive_timestep(v, d, h)


# ---------------------------------------------------------------------------
# Reflecting boundary fold
# ---------------------------------------------------------------------------


def test_reflect_into_box_inside_unchanged() -> None:
    h = 1.0
    z = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    assert np.allclose(_reflect_into_box(z, h), z)


def test_reflect_into_box_handles_single_overshoot_top_and_bottom() -> None:
    h = 1.0
    # 1.3 → 0.7 (one bounce off top); -0.3 → 0.3 (one bounce off bottom).
    z = np.array([1.3, -0.3])
    assert np.allclose(_reflect_into_box(z, h), [0.7, 0.3])


def test_reflect_into_box_handles_multiple_bounces() -> None:
    h = 1.0
    # 2.3 = top → -0.3 → 0.3 (two bounces).
    # -1.3 = bottom → 1.3 → 2 - 1.3 = 0.7 (two bounces).
    z = np.array([2.3, -1.3])
    assert np.allclose(_reflect_into_box(z, h), [0.3, 0.7])


# ---------------------------------------------------------------------------
# Simulator determinism and structural sanity
# ---------------------------------------------------------------------------


def test_simulate_is_deterministic_under_seed() -> None:
    a = simulate(v_sed=1e-7, diff=1e-12, h=1e-4, t_total=10.0, n_trajectories=200, seed=1234)
    b = simulate(v_sed=1e-7, diff=1e-12, h=1e-4, t_total=10.0, n_trajectories=200, seed=1234)
    assert np.array_equal(a.final_z, b.final_z)


def test_simulate_unbounded_requires_explicit_dt() -> None:
    with pytest.raises(ValueError):
        simulate(
            v_sed=0.0, diff=1e-12, h=1.0, t_total=1.0,
            n_trajectories=10, bounded=False,
        )


def test_simulate_keeps_trajectories_inside_box_when_bounded() -> None:
    h = 1e-4
    res = simulate(
        v_sed=0.0, diff=2.45e-12, h=h, t_total=10.0,
        n_trajectories=500, seed=0,
    )
    assert (res.final_z >= 0.0).all()
    assert (res.final_z <= h).all()


def test_simulate_cell_returns_langevin_result_with_provenance() -> None:
    """Wrapper records the kernel parameters it derived."""
    res = simulate_cell(1e-7, 298.15, 1e-4, t_total=10.0, n_trajectories=100, seed=0)
    assert isinstance(res, LangevinResult)
    assert math.isclose(res.v_sed, settling_velocity(1e-7, 298.15), rel_tol=1e-15)
    assert math.isclose(res.diffusivity, diffusivity(1e-7, 298.15), rel_tol=1e-15)
    assert res.h == 1e-4
    assert res.n_trajectories == 100


def test_simulate_snapshots_recorded_at_evenly_spaced_times() -> None:
    """Use a tight box and the 100-nm diamond D so dt is small enough
    that n_steps comfortably exceeds n_snapshots."""
    res = simulate(
        v_sed=0.0, diff=2.45e-12, h=1e-6, t_total=1.0,
        n_trajectories=50, seed=0, n_snapshots=5,
    )
    assert res.n_steps >= 5
    assert res.snapshots is not None
    assert res.snapshots.shape == (5, 50)
    assert res.snapshot_times is not None
    diffs = np.diff(res.snapshot_times)
    assert np.allclose(diffs, diffs[0])


def test_simulate_snapshots_span_full_run_in_awkward_divisibility() -> None:
    """Regression: previously the interval-based snapshot scheduler
    front-loaded indices when n_steps was not cleanly divisible by
    n_snapshots (e.g. n_steps=10, n_snapshots=6 → steps 1..6, missing
    the back half). The linspace-based scheduler must hit the final step.
    """
    res = simulate(
        v_sed=0.0, diff=2.45e-12, h=1e-6, t_total=1.0,
        n_trajectories=20, seed=0, n_snapshots=6, dt=0.1,
    )
    assert res.n_steps == 10  # ceil(1.0 / 0.1)
    assert res.snapshot_times is not None
    # Final snapshot should sit at (or extremely close to) t_total.
    assert math.isclose(float(res.snapshot_times[-1]), res.t_total, rel_tol=1e-12)


def test_simulate_snapshots_capped_at_n_steps_when_oversubscribed() -> None:
    """When n_snapshots > n_steps the unique-integer-index dedupe means
    we get exactly n_steps snapshots, not n_snapshots — pin that
    contract so callers know not to rely on the requested count."""
    res = simulate(
        v_sed=0.0, diff=2.45e-12, h=1e-6, t_total=1.0,
        n_trajectories=10, seed=0, n_snapshots=50, dt=0.25,
    )
    assert res.n_steps == 4
    assert res.snapshots is not None
    assert res.snapshots.shape == (4, 10)


# ---------------------------------------------------------------------------
# t_total honouring (regression — previously rounded up to a full policy step)
# ---------------------------------------------------------------------------


def test_simulate_honours_requested_t_total_when_dt_auto() -> None:
    """Auto-dt path: result.t_total must equal the requested t_total
    exactly, even when policy dt would have been larger.

    Previously: pure-Brownian h=1mm, D=2.45e-12 has dt_policy ≈ 4080 s;
    requesting t_total=1 s ran for 4080 s. After the fix, n_steps is set
    so that t_total/n_steps ≤ dt_policy and the run covers exactly t_total.
    """
    requested = 1.0
    res = simulate(
        v_sed=0.0, diff=2.45e-12, h=1e-3, t_total=requested,
        n_trajectories=10, seed=0,
    )
    assert math.isclose(res.t_total, requested, rel_tol=1e-12)
    # Sanity: the policy upper bound is still respected.
    assert res.dt <= adaptive_timestep(0.0, 2.45e-12, 1e-3) + 1e-15


def test_simulate_zero_t_total_returns_initial_condition() -> None:
    res = simulate(
        v_sed=1e-7, diff=2.45e-12, h=1e-4, t_total=0.0,
        n_trajectories=20, seed=0,
    )
    assert res.n_steps == 0
    assert res.t_total == 0.0
    assert np.array_equal(res.final_z, res.initial_z)


def test_simulate_negative_t_total_raises() -> None:
    with pytest.raises(ValueError):
        simulate(
            v_sed=1e-7, diff=2.45e-12, h=1e-4, t_total=-1.0,
            n_trajectories=10,
        )
