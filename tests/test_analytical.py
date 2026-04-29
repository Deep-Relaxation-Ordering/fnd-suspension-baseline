"""Method A — analytical sanity tests.

Spec: breakout-note §4.1 Method A.

These are not the cross-method consistency checks of §4.4 (those live in
test_method_consistency.py and require Methods B and C to be in place).
This module is a self-contained sanity layer on the analytical
quantities themselves: scaling laws, limit cases, mass conservation,
and dictionary completeness.
"""

from __future__ import annotations

import math

import numpy as np

from analytical import (
    barometric_mean_height,
    barometric_profile,
    cell_summary,
    equilibration_time,
    scale_height,
    settling_time,
    settling_velocity,
    top_to_bottom_ratio,
)
from parameters import K_B, diffusivity

# Anchor cell used across several tests
_R_ANCHOR = 1e-7  # 100 nm
_T_ANCHOR = 298.15  # 25 °C
_H_ANCHOR = 1e-3  # 1 mm


# ---------------------------------------------------------------------------
# Anchor-cell sanity
# ---------------------------------------------------------------------------


def test_scale_height_at_100nm_298K_is_tens_of_microns() -> None:
    """ℓ_g for 100-nm diamond at 25 °C is in the 30–50 µm range."""
    ell_g = scale_height(_R_ANCHOR, _T_ANCHOR)
    assert 30e-6 < ell_g < 50e-6


def test_settling_velocity_at_100nm_298K_is_sub_micron_per_second() -> None:
    """v_sed for 100-nm diamond at 25 °C is in the 10–100 nm/s range."""
    v = settling_velocity(_R_ANCHOR, _T_ANCHOR)
    assert 1e-8 < v < 1e-6


def test_settling_time_definition() -> None:
    """t_settle = h / v_sed exactly."""
    t = settling_time(_R_ANCHOR, _T_ANCHOR, _H_ANCHOR)
    v = settling_velocity(_R_ANCHOR, _T_ANCHOR)
    assert math.isclose(t, _H_ANCHOR / v, rel_tol=1e-15)


def test_equilibration_time_picks_minimum_length_squared_over_D() -> None:
    """t_eq = min(h, ℓ_g)^2 / D."""
    t_eq = equilibration_time(_R_ANCHOR, _T_ANCHOR, _H_ANCHOR)
    ell_g = scale_height(_R_ANCHOR, _T_ANCHOR)
    d = diffusivity(_R_ANCHOR, _T_ANCHOR)
    expected = min(_H_ANCHOR, ell_g) ** 2 / d
    assert math.isclose(t_eq, expected, rel_tol=1e-15)


# ---------------------------------------------------------------------------
# Scaling laws
# ---------------------------------------------------------------------------


def test_settling_velocity_scales_as_r_squared_in_dilute_stokes() -> None:
    """v_sed ∝ r² when ρ_p − ρ_f and η are held fixed."""
    v_small = settling_velocity(_R_ANCHOR, _T_ANCHOR)
    v_large = settling_velocity(2.0 * _R_ANCHOR, _T_ANCHOR)
    assert math.isclose(v_large / v_small, 4.0, rel_tol=1e-12)


def test_diffusivity_scales_as_inverse_radius() -> None:
    """D ∝ 1/r at fixed T."""
    d_small = diffusivity(_R_ANCHOR, _T_ANCHOR)
    d_large = diffusivity(10.0 * _R_ANCHOR, _T_ANCHOR)
    assert math.isclose(d_small / d_large, 10.0, rel_tol=1e-12)


def test_scale_height_scales_as_inverse_r_cubed() -> None:
    """ℓ_g ∝ 1 / m_eff ∝ 1 / r³ at fixed T (constant Δρ)."""
    ell_small = scale_height(_R_ANCHOR, _T_ANCHOR)
    ell_large = scale_height(2.0 * _R_ANCHOR, _T_ANCHOR)
    assert math.isclose(ell_small / ell_large, 8.0, rel_tol=1e-12)


# ---------------------------------------------------------------------------
# Limit behaviour of the top-to-bottom ratio
# ---------------------------------------------------------------------------


def test_top_to_bottom_ratio_is_one_in_homogeneous_limit() -> None:
    """For r → 0 (ℓ_g ≫ h), c(h)/c(0) → 1.

    At r = 5 nm, T = 25 °C, h = 1 mm we have ℓ_g ≈ 32 cm so h / ℓ_g ≈ 3·10⁻³,
    giving c(h)/c(0) ≈ 0.997 — well inside the §5.1 "homogeneous" band
    (≥ 0.95) but not at unity. The 1 % tolerance reflects that we are *in*
    the homogeneous regime, not at its asymptote.
    """
    ratio = top_to_bottom_ratio(5e-9, _T_ANCHOR, _H_ANCHOR)
    assert math.isclose(ratio, 1.0, abs_tol=1e-2)


def test_top_to_bottom_ratio_is_zero_in_sedimented_limit() -> None:
    """For r → 10 µm (ℓ_g ≪ h), c(h)/c(0) → 0."""
    ratio = top_to_bottom_ratio(1e-5, _T_ANCHOR, _H_ANCHOR)
    assert ratio < 1e-6


def test_top_to_bottom_ratio_at_5pct_threshold_corresponds_to_h_over_lg_about_3() -> None:
    """At c(h)/c(0) = 0.05 the regime classification flips; this requires h / ℓ_g ≈ ln(20) ≈ 3."""
    # Search for the radius where ratio = 0.05 by bisection.
    rs = np.geomspace(5e-9, 1e-5, 1000)
    ratios = np.array([top_to_bottom_ratio(r, _T_ANCHOR, _H_ANCHOR) for r in rs])
    idx = int(np.argmin(np.abs(ratios - 0.05)))
    r_threshold = float(rs[idx])
    ell_g = scale_height(r_threshold, _T_ANCHOR)
    h_over_lg = _H_ANCHOR / ell_g
    assert 2.5 < h_over_lg < 3.5


# ---------------------------------------------------------------------------
# Barometric mean height
# ---------------------------------------------------------------------------


def test_barometric_mean_height_homogeneous_limit_is_h_over_2() -> None:
    """For ℓ_g ≫ h the profile is uniform, so ⟨z⟩ → h / 2.

    5 nm at 25 °C gives ℓ_g ≈ 32 cm; with h = 100 µm we sit at
    h / ℓ_g ≈ 3·10⁻⁴, well inside the homogeneous band.
    """
    ell_g = scale_height(5e-9, _T_ANCHOR)
    h = 1e-4
    assert h / ell_g < 1e-3, "test premise: homogeneous limit"
    z_mean = barometric_mean_height(h, ell_g)
    assert math.isclose(z_mean, h / 2.0, rel_tol=1e-3)


def test_barometric_mean_height_sedimented_limit_is_ell_g() -> None:
    """For h ≫ ℓ_g the profile is a decaying exponential confined near
    z = 0, so ⟨z⟩ → ℓ_g.

    1 µm at 25 °C gives ℓ_g ≈ 40 nm; with h = 1 mm we sit at
    h / ℓ_g ≈ 2.5·10⁴, well inside the sedimented band.
    """
    ell_g = scale_height(1e-6, _T_ANCHOR)
    h = 1e-3
    assert h / ell_g > 1e4, "test premise: sedimented limit"
    z_mean = barometric_mean_height(h, ell_g)
    assert math.isclose(z_mean, ell_g, rel_tol=1e-3)


def test_barometric_mean_height_zero_depth_is_zero() -> None:
    assert barometric_mean_height(0.0, 1e-5) == 0.0


# ---------------------------------------------------------------------------
# Barometric profile
# ---------------------------------------------------------------------------


def test_barometric_profile_is_normalised_in_stratified_regime() -> None:
    """∫₀ʰ c_eq(z) dz = 1 for a clearly stratified cell."""
    z = np.linspace(0.0, _H_ANCHOR, 10001)
    c = barometric_profile(z, _R_ANCHOR, _T_ANCHOR, _H_ANCHOR)
    integral = float(np.trapezoid(c, z))
    assert math.isclose(integral, 1.0, rel_tol=1e-4)


def test_barometric_profile_is_normalised_in_homogeneous_limit() -> None:
    """The expm1 normalisation must remain accurate when h / ℓ_g → 0."""
    z = np.linspace(0.0, _H_ANCHOR, 10001)
    c = barometric_profile(z, 5e-9, _T_ANCHOR, _H_ANCHOR)
    integral = float(np.trapezoid(c, z))
    assert math.isclose(integral, 1.0, rel_tol=1e-4)


def test_barometric_profile_is_uniform_in_homogeneous_limit() -> None:
    """For ℓ_g ≫ h, c_eq(z) ≈ 1 / h independent of z.

    Same anchor cell as the top/bottom ratio test: r = 5 nm, h = 1 mm
    sits at h / ℓ_g ≈ 3·10⁻³, so the profile is uniform to ~0.3 %.
    Using a 1 % tolerance to stay safely above that.
    """
    z = np.linspace(0.0, _H_ANCHOR, 1001)
    c = barometric_profile(z, 5e-9, _T_ANCHOR, _H_ANCHOR)
    expected = 1.0 / _H_ANCHOR
    assert np.all(np.abs(c - expected) / expected < 1e-2)


def test_barometric_profile_drops_to_5pct_at_top_for_sedimented_cell() -> None:
    """At a cell on the sedimented side, c(h) is ≪ c(0)."""
    r = 5e-7  # 500 nm — clearly stratified-to-sedimented at h = 1 mm
    c0 = float(barometric_profile(0.0, r, _T_ANCHOR, _H_ANCHOR))
    ch = float(barometric_profile(_H_ANCHOR, r, _T_ANCHOR, _H_ANCHOR))
    assert ch / c0 < 0.05


# ---------------------------------------------------------------------------
# cell_summary structure
# ---------------------------------------------------------------------------


def test_cell_summary_contains_all_expected_keys() -> None:
    summary = cell_summary(_R_ANCHOR, _T_ANCHOR, _H_ANCHOR)
    expected_keys = {
        "r_m",
        "r_material_m",
        "r_hydro_m",
        "delta_shell_m",
        "T_K",
        "h_m",
        "rho_p_kg_per_m3",
        "rho_f_kg_per_m3",
        "eta_Pa_s",
        "m_eff_kg",
        "gamma_N_s_per_m",
        "D_m2_per_s",
        "v_sed_m_per_s",
        "ell_g_m",
        "t_eq_s",
        "t_settle_s",
        "z_mean_m",
        "ratio_top_bottom",
    }
    assert set(summary.keys()) == expected_keys


def test_cell_summary_z_mean_matches_standalone_function() -> None:
    """`cell_summary['z_mean_m']` and `barometric_mean_height` must agree
    — pins the public Method-A API as the single source of truth."""
    summary = cell_summary(_R_ANCHOR, _T_ANCHOR, _H_ANCHOR)
    direct = barometric_mean_height(_H_ANCHOR, scale_height(_R_ANCHOR, _T_ANCHOR))
    assert math.isclose(summary["z_mean_m"], direct, rel_tol=1e-15)


def test_cell_summary_einstein_relation_internal_consistency() -> None:
    """D · γ = k_B T inside the cell summary too."""
    summary = cell_summary(_R_ANCHOR, _T_ANCHOR, _H_ANCHOR)
    product = summary["D_m2_per_s"] * summary["gamma_N_s_per_m"]
    expected = K_B * summary["T_K"]
    assert math.isclose(product, expected, rel_tol=1e-15)
