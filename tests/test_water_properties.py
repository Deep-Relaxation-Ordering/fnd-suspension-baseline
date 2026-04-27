"""Sanity tests on the water-properties module.

Spec: breakout-note §3 (Material parameters) and §10 (stop condition on
vendor data sheet η or ρ deviation > 10 % from pure water).

References for assertion values
-------------------------------
- Tanaka et al. (2001), Metrologia 38, 301, Table 1: ρ(20 °C) = 998.2071 kg/m³,
  ρ(4 °C) ≈ 999.9750 kg/m³ (water density max).
- IAPWS R12-08 reference: η(20 °C) = 1.0016 × 10⁻³ Pa·s,
  η(5 °C) = 1.5188 × 10⁻³ Pa·s, η(35 °C) = 7.1909 × 10⁻⁴ Pa·s.

Tolerances honour the formulation-class accuracy: ~1 ppm for Tanaka,
~1 % for the compact Vogel form used for η.
"""

from __future__ import annotations

import math

import pytest

from parameters import (
    T_DENSITY_MAX_K,
    T_VISCOSITY_MIN_K,
    eta_water,
    rho_water,
)

# ---------------------------------------------------------------------------
# Density
# ---------------------------------------------------------------------------


def test_density_at_20C_matches_iapws_reference() -> None:
    rho = rho_water(293.15)
    assert math.isclose(rho, 998.2071, abs_tol=1e-3)


def test_density_at_4C_is_water_density_maximum() -> None:
    rho_4 = rho_water(277.15)
    rho_3 = rho_water(276.15)
    rho_5 = rho_water(278.15)
    assert math.isclose(rho_4, 999.9750, abs_tol=1e-3)
    assert rho_4 > rho_3
    assert rho_4 > rho_5


def test_density_monotonic_decrease_above_4C() -> None:
    temperatures = [278.15, 283.15, 293.15, 303.15, 308.15]
    densities = [rho_water(t) for t in temperatures]
    assert all(densities[i] > densities[i + 1] for i in range(len(densities) - 1))


def test_density_temperature_range_guard() -> None:
    with pytest.raises(ValueError):
        rho_water(T_DENSITY_MAX_K + 1.0)
    with pytest.raises(ValueError):
        rho_water(250.0)


# ---------------------------------------------------------------------------
# Viscosity
# ---------------------------------------------------------------------------


def test_viscosity_at_20C_within_1pct_of_iapws() -> None:
    eta = eta_water(293.15)
    assert math.isclose(eta, 1.0016e-3, rel_tol=1e-2)


def test_viscosity_at_5C_within_1pct_of_iapws() -> None:
    eta = eta_water(278.15)
    assert math.isclose(eta, 1.5188e-3, rel_tol=2e-2)


def test_viscosity_at_35C_within_1pct_of_iapws() -> None:
    eta = eta_water(308.15)
    assert math.isclose(eta, 7.1909e-4, rel_tol=2e-2)


def test_viscosity_decreases_monotonically_with_T() -> None:
    temperatures = [278.15, 283.15, 293.15, 303.15, 308.15]
    viscosities = [eta_water(t) for t in temperatures]
    assert all(viscosities[i] > viscosities[i + 1] for i in range(len(viscosities) - 1))


def test_viscosity_factor_two_across_5_to_35C() -> None:
    """Breakout-note §2c: η(T) varies by ~2× across the 5–35 °C scan."""
    ratio = eta_water(278.15) / eta_water(308.15)
    assert 1.9 < ratio < 2.2


def test_viscosity_temperature_range_guard() -> None:
    with pytest.raises(ValueError):
        eta_water(T_VISCOSITY_MIN_K - 1.0)
    with pytest.raises(ValueError):
        eta_water(400.0)
