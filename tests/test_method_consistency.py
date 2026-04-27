"""Cross-method consistency and limiting-case checks.

Spec: breakout-note §4.4 validation strategy.

- Method B and Method C agree on time-dependent moments (mean, variance)
  within numerical tolerance, on cells inside Method B's feasibility envelope.
- Method A ↔ Method C agreement on equilibrium quantities for cells
  *outside* Method B's feasibility envelope (high-r corners; round-3 fix).
- Pure-Brownian limit (gravity off):
    * displacement-MSD ⟨[z(t) − z(0)]²⟩ → 2 D t in unbounded domain;
    * displacement-MSD saturates at **h²/6** at long lag in [0, h]
      (two uncorrelated samples from uniform-on-[0,h]). NOT h²/12 — that
      is the position variance, tested separately in test_equilibrium.
- Pure-sedimentation limit (D → 0): for uniform IC on [0, h], bottom
  population reaches 100 % at t = h / v_sed, with mean arrival time
  h / (2 v_sed); particles starting at z₀ arrive at t(z₀) = z₀ / v_sed.
- Method C high/low-Pe limits: exponential-fitting FV reduces to upwind
  at high Pe, central at low Pe; asymptotic-sedimentation fallback engages
  when ℓ_g drops below the smallest representable mesh spacing (round-4).
"""

from __future__ import annotations

import numpy as np
import pytest

from langevin import simulate


@pytest.mark.skip(reason="Awaiting Method C implementation.")
def test_method_b_c_time_dependent_moments_agree() -> None:
    pass


@pytest.mark.skip(reason="Awaiting Method C implementation.")
def test_method_a_c_equilibrium_outside_b_envelope() -> None:
    pass


def test_unbounded_msd_linear_in_time() -> None:
    """⟨[z(t) − z(0)]²⟩ = 2 D t on an unbounded domain (free Brownian)."""
    d = 2.45e-12
    t_total = 1.0
    # Pick dt small enough that random-walk error is well below the
    # sample-mean error for N = 20000 (~0.7 % at this size).
    dt = 1e-3
    result = simulate(
        v_sed=0.0, diff=d, h=1.0,  # h irrelevant when bounded=False
        t_total=t_total,
        n_trajectories=20_000,
        z0=0.0,
        dt=dt,
        bounded=False,
        seed=42,
    )
    msd = float(np.mean((result.final_z - result.initial_z) ** 2))
    expected = 2.0 * d * result.t_total
    rel_err = abs(msd - expected) / expected
    assert rel_err < 0.02, (
        f"unbounded MSD = {msd:.4e}, 2Dt = {expected:.4e}, relative error {rel_err:.4f}"
    )


def test_bounded_displacement_msd_saturates_at_h2_over_6() -> None:
    """For uniform-on-[0,h] equilibrium with the same uniform IC, two
    statistically-independent samples z(0), z(t→∞) give::

        ⟨[z(t) − z(0)]²⟩ = E[X²] + E[Y²] − 2 E[XY] = 2·h²/3 − 2·(h/2)² = h²/6.

    Round-4 distinction from the position-variance saturation at h²/12.
    """
    h = 1e-6
    d = 2.45e-12
    result = simulate(
        v_sed=0.0, diff=d, h=h,
        t_total=10.0,  # ≫ h²/D ≈ 0.4 s
        n_trajectories=20_000,
        seed=42,
    )
    msd = float(np.mean((result.final_z - result.initial_z) ** 2))
    expected = h**2 / 6.0
    rel_err = abs(msd - expected) / expected
    assert rel_err < 0.02, (
        f"bounded MSD = {msd:.4e}, h²/6 = {expected:.4e}, relative error {rel_err:.4f}"
    )


def test_pure_sedimentation_arrival_times() -> None:
    """D = 0, uniform IC on [0, h]: first-passage times are uniform on
    [0, h/v_sed], with mean h/(2 v_sed) and max h/v_sed."""
    h = 1e-3
    v = 1e-6
    t_arrival_max = h / v
    result = simulate(
        v_sed=v, diff=0.0, h=h,
        t_total=1.05 * t_arrival_max,  # small over-shoot guarantees coverage
        n_trajectories=5_000,
        track_first_passage_to_bottom=True,
        seed=42,
    )
    fpt = result.first_passage_times
    assert fpt is not None
    assert not np.isnan(fpt).any(), "every particle should reach the bottom in pure sedimentation"

    mean_arrival = float(np.mean(fpt))
    expected_mean = h / (2.0 * v)
    rel_err = abs(mean_arrival - expected_mean) / expected_mean
    # Tolerance covers the dt rounding (arrivals quantised in steps of dt).
    assert rel_err < 0.02, (
        f"mean arrival = {mean_arrival:.4e}, h/(2 v_sed) = {expected_mean:.4e}, "
        f"rel err {rel_err:.4f}"
    )

    # The max arrival should be close to (but not exceed by more than a dt) h/v_sed.
    max_arrival = float(np.max(fpt))
    assert max_arrival <= t_arrival_max + result.dt
    assert max_arrival > 0.95 * t_arrival_max


@pytest.mark.skip(reason="Awaiting Method C implementation.")
def test_method_c_high_pe_upwind_limit() -> None:
    pass


@pytest.mark.skip(reason="Awaiting Method C implementation.")
def test_method_c_low_pe_central_limit() -> None:
    pass


@pytest.mark.skip(reason="Awaiting Method C implementation.")
def test_method_c_asymptotic_sedimentation_fallback() -> None:
    pass
