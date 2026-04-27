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

import math

import numpy as np
from scipy.sparse.linalg import expm_multiply

from analytical import barometric_mean_height, scale_height, settling_velocity
from fokker_planck import (
    build_operator,
    equilibrium_cell,
    make_mesh,
    sg_flux_coefficients,
    solve,
    solve_cell,
)
from langevin import simulate, simulate_cell
from parameters import diffusivity


def test_method_b_c_time_dependent_moments_agree() -> None:
    """Method B and Method C agree on time-dependent moments inside B's envelope.

    Tolerance is keyed to the *value*, not h: a 3 %-of-h slop on the mean
    is effectively a 7-10 % relative tolerance for a stratified cell, which
    is much looser than the actual 0.4 % seeded agreement.
    """
    r = 1e-7
    temperature_kelvin = 298.15
    h = 1e-4
    t_total = 200.0

    method_b = simulate_cell(
        r,
        temperature_kelvin,
        h,
        t_total=t_total,
        n_trajectories=30_000,
        seed=42,
    )
    method_c = solve_cell(r, temperature_kelvin, h, t_total=t_total, n_cells=180)

    mean_b = float(np.mean(method_b.final_z))
    var_b = float(np.var(method_b.final_z))
    mean_c = method_c.mean_height()
    var_c = method_c.variance_height()

    assert abs(mean_b - mean_c) / mean_c < 0.01
    assert abs(var_b - var_c) / var_c < 0.02


def test_method_a_c_equilibrium_inside_b_envelope_resolved_mesh() -> None:
    """Method A ↔ Method C equilibrium agreement on a *resolved-mesh* cell
    (i.e. without the asymptotic fallback). This is the gap left by the
    Phase 4 test set, which only validated the fallback path.

    100-nm diamond at 25 °C in a 100-µm cell sits at h/ℓ_g ≈ 2.5 — clearly
    stratified, fully resolved by a uniform mesh.

    `n_cells = 60` and `t_factor = 10` are CI-time settings: at these
    values the test runs in well under a second while still resolving
    each Method-A reference to better than ~2·10⁻⁴ relative error.
    Production scans (`regime_map.py`) should use the
    `equilibrium_cell` defaults.
    """
    r, temperature_kelvin, h = 1e-7, 298.15, 1e-4
    ell_g = scale_height(r, temperature_kelvin)

    method_c = equilibrium_cell(
        r, temperature_kelvin, h,
        n_cells=60,
        t_factor=10.0,
    )
    assert not method_c.used_asymptotic_fallback

    z_mean_a = barometric_mean_height(h, ell_g)
    ratio_a = math.exp(-h / ell_g)
    bmf_a = (1.0 - math.exp(-0.05 * h / ell_g)) / (1.0 - math.exp(-h / ell_g))

    assert abs(method_c.mean_height() - z_mean_a) / z_mean_a < 1e-3
    # Log-linear extrapolation is exact for exponential profiles, modulo
    # the tiny finite-time correction from t = 10·t_relax.
    assert abs(method_c.top_to_bottom_ratio() - ratio_a) / ratio_a < 1e-6
    # bottom_mass_fraction is exact integration over the equilibrium profile.
    assert abs(method_c.bottom_mass_fraction(0.05) - bmf_a) / bmf_a < 1e-3


def test_method_c_operator_conserves_mass_to_machine_precision() -> None:
    """The Scharfetter-Gummel finite-volume operator is mass-conservative
    by construction; verify the raw expm_multiply output (before
    `_normalise_density` clips and renormalises) preserves total mass to
    well below 1 ppb. Pinning this protects against silent operator
    bugs whose drift could otherwise be hidden by the renormalisation.
    """
    r, temperature_kelvin, h = 1e-7, 298.15, 1e-4
    v = settling_velocity(r, temperature_kelvin)
    d = diffusivity(r, temperature_kelvin)

    edges, unresolved, _ = make_mesh(h, ell_g=d / v, n_cells=240)
    assert not unresolved
    widths = np.diff(edges)
    operator = build_operator(edges, diff=d, v_sed=v)

    c0 = np.full(widths.size, 1.0 / h)
    initial_mass = float(np.sum(c0 * widths))

    c_t = expm_multiply(operator * 100.0, c0)
    final_mass = float(np.sum(c_t * widths))

    assert abs(final_mass - initial_mass) / initial_mass < 1e-9


def test_method_a_c_equilibrium_outside_b_envelope() -> None:
    """High-r cells outside Method B's envelope use Method C's asymptotic fallback."""
    r = 1e-5
    temperature_kelvin = 298.15
    h = 1e-4

    ell_g = scale_height(r, temperature_kelvin)
    expected_mean = barometric_mean_height(h, ell_g)
    method_c = equilibrium_cell(r, temperature_kelvin, h)

    assert method_c.used_asymptotic_fallback
    assert method_c.top_to_bottom_ratio() == 0.0
    assert method_c.bottom_mass_fraction() > 0.99
    assert math.isclose(method_c.mean_height(), expected_mean, rel_tol=1e-12)


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


def test_method_c_high_pe_upwind_limit() -> None:
    """At high Pe, Scharfetter-Gummel flux becomes drift-upwind."""
    diff = 1.0
    v_sed = 100.0
    dx = 1.0
    a_left, a_right = sg_flux_coefficients(diff, v_sed, dx)

    assert abs(a_left) < 1e-35
    assert math.isclose(a_right, -v_sed, rel_tol=1e-12)


def test_method_c_low_pe_central_limit() -> None:
    """At low Pe, Scharfetter-Gummel flux recovers central drift-diffusion."""
    diff = 1.0
    v_sed = 1e-6
    dx = 0.25
    c_left = 2.0
    c_right = 1.0

    a_left, a_right = sg_flux_coefficients(diff, v_sed, dx)
    flux = a_left * c_left + a_right * c_right
    central = -diff * (c_right - c_left) / dx - v_sed * 0.5 * (c_left + c_right)

    assert math.isclose(flux, central, rel_tol=1e-10, abs_tol=1e-12)


def test_method_c_refined_mesh_resolves_bottom_scale_height() -> None:
    """When a uniform mesh would be too coarse, Method C refines toward z=0."""
    h = 1e-4
    ell_g = 4e-8
    edges, unresolved, reason = make_mesh(h, ell_g=ell_g)
    widths = np.diff(edges)

    assert unresolved is False
    assert reason is None
    assert widths[0] <= ell_g / 5.0
    assert widths[-1] > widths[0]


def test_method_c_asymptotic_sedimentation_fallback() -> None:
    """Unresolved sub-nanometric scale heights are tagged, not meshed fictionally."""
    result = solve(
        v_sed=1e-3,
        diff=1e-14,
        h=1e-3,
        t_total=1.0,
    )

    assert result.used_asymptotic_fallback
    assert result.method == "asymptotic-sedimentation"
    assert result.fallback_reason is not None
    assert result.pe_global > 1e7


def test_method_c_asymptotic_fallback_keeps_finite_time_transient() -> None:
    """Before h/v_sed, fallback follows the pure-sedimentation transient."""
    v_sed = 1e-3
    h = 1e-3
    t_total = 0.25 * h / v_sed
    result = solve(
        v_sed=v_sed,
        diff=1e-14,
        h=h,
        t_total=t_total,
    )

    front = h - v_sed * t_total
    expected_mean = front**2 / (2.0 * h)

    assert result.method == "asymptotic-sedimentation-transient"
    assert result.bottom_mass_fraction() < 0.35
    assert math.isclose(result.mean_height(), expected_mean, rel_tol=1e-12)
