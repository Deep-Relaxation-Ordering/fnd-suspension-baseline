"""Equilibrium-distribution checks.

Spec: breakout-note §4.4 validation strategy, first bullet.

- Method B at long times reproduces Method A barometric equilibrium to
  ≤ 2 % deviation in mean height.
- Position variance ⟨z²⟩ − ⟨z⟩² of the uniform-on-[0,h] equilibrium
  saturates at h²/12 (round-4 distinction from the displacement-MSD
  saturation at h²/6 — see test_method_consistency).
"""

from __future__ import annotations

import numpy as np

from analytical import barometric_mean_height, equilibration_time, scale_height
from langevin import simulate, simulate_cell

# 100-nm diamond at 25 °C in a 100-µm cell: stratified (h/ℓ_g ≈ 2.5),
# t_eq ≈ 650 s, fast enough for tests yet clearly non-trivial.
_R, _T, _H = 1e-7, 298.15, 1e-4


def test_method_b_long_time_matches_barometric() -> None:
    """N = 1e4 (rather than 1e5) buys ~5× test runtime; with seeded RNG
    the 2 % tolerance is comfortably met."""
    ell_g = scale_height(_R, _T)
    z_mean_method_a = barometric_mean_height(_H, ell_g)

    t_eq = equilibration_time(_R, _T, _H)
    result = simulate_cell(
        _R, _T, _H,
        t_total=20.0 * t_eq,
        n_trajectories=10_000,
        seed=42,
    )
    z_mean_method_b = float(np.mean(result.final_z))

    rel_err = abs(z_mean_method_b - z_mean_method_a) / z_mean_method_a
    assert rel_err < 0.02, (
        f"⟨z⟩_B = {z_mean_method_b:.4e} m, ⟨z⟩_A = {z_mean_method_a:.4e} m, "
        f"relative error {rel_err:.4f} > 0.02"
    )


def test_position_variance_saturates_at_h2_over_12() -> None:
    """Pure-Brownian equilibrium on [0, h] is uniform; Var(z) = h²/12.

    Round-4 distinction from the displacement-MSD saturation at h²/6
    (see `test_method_consistency.test_bounded_displacement_msd_saturates_at_h2_over_6`).
    """
    h = 1e-6
    d = 2.45e-12
    # Saturation timescale h²/D ≈ 0.4 s; integrate well past it.
    result = simulate(
        v_sed=0.0, diff=d, h=h,
        t_total=10.0,
        n_trajectories=20_000,
        seed=42,
    )
    var_z = float(np.var(result.final_z))
    expected = h**2 / 12.0
    rel_err = abs(var_z - expected) / expected
    assert rel_err < 0.02, (
        f"Var(z) = {var_z:.4e}, h²/12 = {expected:.4e}, relative error {rel_err:.4f}"
    )
