"""Phase 11 — Rayleigh-number convection side-channel."""

from __future__ import annotations

import math

import pytest

from convection import (
    RAYLEIGH_CRITICAL_RIGID_FREE,
    RAYLEIGH_CRITICAL_RIGID_RIGID,
    is_convection_dominated,
    rayleigh_number,
    thermal_expansion_coefficient,
)


def test_rayleigh_anchor_shallow_lab_dT() -> None:
    """h = 1 mm, ΔT = 1 K at 25 °C gives Ra ≈ 20."""
    ra = rayleigh_number(1e-3, 1.0, 298.15)
    assert math.isclose(ra, 20.0, rel_tol=0.05)
    assert not is_convection_dominated(ra)


def test_rayleigh_anchor_deep_lab_dT() -> None:
    """h = 10 mm, ΔT = 1 K at 25 °C gives Ra ≈ 2.0e4."""
    ra = rayleigh_number(1e-2, 1.0, 298.15)
    assert math.isclose(ra, 2.0e4, rel_tol=0.05)
    assert is_convection_dominated(ra)


def test_threshold_round_trip() -> None:
    assert not is_convection_dominated(RAYLEIGH_CRITICAL_RIGID_RIGID)
    assert is_convection_dominated(RAYLEIGH_CRITICAL_RIGID_RIGID * (1.0 + 1e-12))


def test_rigid_free_threshold_lower() -> None:
    ra = 0.5 * (RAYLEIGH_CRITICAL_RIGID_FREE + RAYLEIGH_CRITICAL_RIGID_RIGID)
    assert not is_convection_dominated(ra, boundary="rigid-rigid")
    assert is_convection_dominated(ra, boundary="rigid-free")


def test_rejects_unknown_boundary() -> None:
    with pytest.raises(ValueError, match="unsupported boundary"):
        is_convection_dominated(1.0, boundary="free-free")  # type: ignore[arg-type]


def test_rejects_nonpositive_depth() -> None:
    with pytest.raises(ValueError, match="positive"):
        rayleigh_number(0.0, 1.0, 298.15)
    with pytest.raises(ValueError, match="positive"):
        rayleigh_number(-1e-3, 1.0, 298.15)


def test_thin_cell_not_convective_at_any_realistic_dT() -> None:
    ra = rayleigh_number(1e-4, 10.0, 298.15)
    assert math.isclose(ra, 0.2, rel_tol=0.05)
    assert not is_convection_dominated(ra)


def test_marginal_deep_cell() -> None:
    ra = rayleigh_number(1e-2, 0.1, 298.15)
    assert math.isclose(ra, 2.0e3, rel_tol=0.05)
    assert is_convection_dominated(ra, boundary="rigid-rigid")
    assert is_convection_dominated(ra, boundary="rigid-free")


def test_deep_sub_mK_cell_is_not_convective() -> None:
    ra = rayleigh_number(1e-2, 0.01, 298.15)
    assert math.isclose(ra, 2.0e2, rel_tol=0.05)
    assert not is_convection_dominated(ra)


def test_alpha_matches_tanaka_derivative_grid_points() -> None:
    """Pin the analytic derivative of the Tanaka density fit."""
    expected = {
        278.15: 1.5979017092549795e-5,
        298.15: 2.5731151607865575e-4,
        308.15: 3.459286660878207e-4,
    }
    for temperature_kelvin, alpha_expected in expected.items():
        assert math.isclose(
            thermal_expansion_coefficient(temperature_kelvin),
            alpha_expected,
            rel_tol=1e-10,
        )


def test_alpha_matches_iapws95_sanity_values() -> None:
    """Independent sanity check against IAPWS-95 at 0.101325 MPa.

    Reference values were computed once with the `iapws` package's
    IAPWS95 implementation and are intentionally used with a loose
    tolerance. Tanaka remains the implementation source of truth.
    """
    expected = {
        278.15: 1.6041845918258578e-5,
        298.15: 2.572889019481004e-4,
        308.15: 3.4589395647891495e-4,
    }
    for temperature_kelvin, alpha_expected in expected.items():
        assert math.isclose(
            thermal_expansion_coefficient(temperature_kelvin),
            alpha_expected,
            rel_tol=0.05,
        )


def test_alpha_handles_4C_inversion() -> None:
    assert 0.0 < thermal_expansion_coefficient(277.15) < 1e-6
    assert thermal_expansion_coefficient(275.15) < 0.0
    assert rayleigh_number(1e-2, 1.0, 275.15) < 0.0
