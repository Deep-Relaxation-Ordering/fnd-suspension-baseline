"""Method A — closed-form equilibrium quantities and characteristic timescales.

Spec: breakout-note §4.1 Method A.

Per (r, T, h) cell delivers:

- ℓ_g       gravitational scale height = k_B T / (m_eff g)
- v_sed     settling velocity            = m_eff g / γ
- D         Stokes-Einstein diffusivity  = k_B T / γ
- t_eq      ~ min(h, ℓ_g)² / D           order-of-magnitude relaxation
- t_settle  = h / v_sed                  uniform-IC arrival time of the
                                         z = h particle in the pure-
                                         sedimentation limit
- c_eq(z)   barometric equilibrium       ∝ exp(-z / ℓ_g) on [0, h],
                                         normalised to ∫₀ʰ c dz = 1
- ratio_top_bottom = c_eq(h)/c_eq(0)     = exp(-h / ℓ_g)

t_eq is a *scaling estimate*, not a spectral-gap relaxation time
(breakout-note §4.1 round-3 follow-up). For strongly-sedimenting cells,
t_settle is the operative experimental timescale.

The barometric profile assumes the canonical initial condition
c(z, 0) = 1/h (uniform after mixing) and reflecting boundaries — see
breakout-note §3 and §5.1.
"""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import ArrayLike, NDArray

from parameters import (
    K_B,
    RHO_P_DIAMOND,
    G,
    buoyant_mass,
    diffusivity,
    eta_water,
    gamma_stokes,
    rho_water,
)

# ---------------------------------------------------------------------------
# Per-cell scalar quantities
# ---------------------------------------------------------------------------


def scale_height(
    radius_m: float,
    temperature_kelvin: float,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
) -> float:
    """Gravitational scale height ℓ_g = k_B T / (m_eff g), in m.

    Assumes m_eff > 0 (denser-than-water particles); diamond satisfies
    this across the full 5–35 °C scan range.
    """
    m_eff = buoyant_mass(radius_m, temperature_kelvin, rho_particle_kg_per_m3)
    return K_B * temperature_kelvin / (m_eff * G)


def settling_velocity(
    radius_m: float,
    temperature_kelvin: float,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
) -> float:
    """Settling velocity v_sed = m_eff g / γ, in m/s.

    Stokes-regime; valid only at low Reynolds number, which holds across
    the entire scan grid for diamond in water.
    """
    m_eff = buoyant_mass(radius_m, temperature_kelvin, rho_particle_kg_per_m3)
    gamma = gamma_stokes(radius_m, temperature_kelvin)
    return m_eff * G / gamma


def equilibration_time(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
) -> float:
    """Order-of-magnitude relaxation time t_eq ~ min(h, ℓ_g)² / D, in s.

    Scaling estimate only. The actual relaxation time of the bounded
    Smoluchowski operator depends on the spectral gap and the initial
    condition; t_eq is a useful first-order timescale, not a precise
    decay constant. For strongly-sedimenting cells, prefer
    `settling_time`.
    """
    ell_g = scale_height(radius_m, temperature_kelvin, rho_particle_kg_per_m3)
    d = diffusivity(radius_m, temperature_kelvin)
    return min(sample_depth_m, ell_g) ** 2 / d


def settling_time(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
) -> float:
    """Settling time t_settle = h / v_sed, in s.

    In the pure-sedimentation limit (D → 0) and for a uniform initial
    distribution on [0, h], the latest particle arrives at z = 0 at this
    time; the mean arrival time is h / (2 v_sed).
    """
    v_sed = settling_velocity(radius_m, temperature_kelvin, rho_particle_kg_per_m3)
    return sample_depth_m / v_sed


def top_to_bottom_ratio(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
) -> float:
    """Equilibrium concentration ratio c(h)/c(0) = exp(-h / ℓ_g).

    The 5 % threshold of breakout-note §5.1 corresponds to h / ℓ_g ≈ 3.
    """
    ell_g = scale_height(radius_m, temperature_kelvin, rho_particle_kg_per_m3)
    return math.exp(-sample_depth_m / ell_g)


def barometric_mean_height(
    sample_depth_m: float,
    scale_height_m: float,
) -> float:
    """Mean height ⟨z⟩ of the normalised barometric profile on [0, h].

        ⟨z⟩ = ℓ_g − h / (exp(h / ℓ_g) − 1)

    Uses ``math.expm1`` so the homogeneous limit (h / ℓ_g → 0) is
    recovered without catastrophic cancellation: ⟨z⟩ → h / 2 −
    h²/(12 ℓ_g) + O(h⁴/ℓ_g³). The deeply-sedimented branch
    (h / ℓ_g ≳ 700, where ``expm1`` overflows) returns ℓ_g directly —
    the missing correction term is h · exp(-h/ℓ_g), which is below
    double-precision floor at that point.

    This is the analytic reference value the long-time Method-B
    ensemble mean is compared against in
    `tests/test_equilibrium.py::test_method_b_long_time_matches_barometric`.
    Promoted from a private test helper to a public Method-A
    quantity in Phase 3.2 so notebooks and `regime_map.py` can reuse it.
    """
    if sample_depth_m == 0.0:
        return 0.0
    h_over_ell = sample_depth_m / scale_height_m
    if h_over_ell > 700.0:
        return scale_height_m
    return scale_height_m - sample_depth_m / math.expm1(h_over_ell)


# ---------------------------------------------------------------------------
# Equilibrium concentration profile
# ---------------------------------------------------------------------------


def barometric_profile(
    z_m: ArrayLike,
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
) -> NDArray[np.float64]:
    """Normalised barometric equilibrium c_eq(z) on [0, h], in 1/m.

    c_eq(z) = exp(-z / ℓ_g) / [ℓ_g · (1 − exp(-h / ℓ_g))]

    so that ∫₀ʰ c_eq(z) dz = 1. Uses `expm1` to remain accurate in the
    homogeneous limit ℓ_g ≫ h (where the naive `1 − exp(...)` underflows).
    """
    ell_g = scale_height(radius_m, temperature_kelvin, rho_particle_kg_per_m3)
    z = np.asarray(z_m, dtype=np.float64)
    norm = ell_g * (-math.expm1(-sample_depth_m / ell_g))
    return np.exp(-z / ell_g) / norm


# ---------------------------------------------------------------------------
# Convenience: dump every Method A quantity for a single cell
# ---------------------------------------------------------------------------


def cell_summary(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
) -> dict[str, float]:
    """Return all Method A quantities for one (r, T, h) cell, with units in keys.

    Useful as the per-row record in the §5 1 050-cell sub-grid output.
    """
    return {
        "r_m": radius_m,
        "T_K": temperature_kelvin,
        "h_m": sample_depth_m,
        "rho_p_kg_per_m3": rho_particle_kg_per_m3,
        "rho_f_kg_per_m3": rho_water(temperature_kelvin),
        "eta_Pa_s": eta_water(temperature_kelvin),
        "m_eff_kg": buoyant_mass(radius_m, temperature_kelvin, rho_particle_kg_per_m3),
        "gamma_N_s_per_m": gamma_stokes(radius_m, temperature_kelvin),
        "D_m2_per_s": diffusivity(radius_m, temperature_kelvin),
        "v_sed_m_per_s": settling_velocity(radius_m, temperature_kelvin, rho_particle_kg_per_m3),
        "ell_g_m": scale_height(radius_m, temperature_kelvin, rho_particle_kg_per_m3),
        "t_eq_s": equilibration_time(
            radius_m, temperature_kelvin, sample_depth_m, rho_particle_kg_per_m3
        ),
        "t_settle_s": settling_time(
            radius_m, temperature_kelvin, sample_depth_m, rho_particle_kg_per_m3
        ),
        "z_mean_m": barometric_mean_height(
            sample_depth_m,
            scale_height(radius_m, temperature_kelvin, rho_particle_kg_per_m3),
        ),
        "ratio_top_bottom": top_to_bottom_ratio(
            radius_m, temperature_kelvin, sample_depth_m, rho_particle_kg_per_m3
        ),
    }
