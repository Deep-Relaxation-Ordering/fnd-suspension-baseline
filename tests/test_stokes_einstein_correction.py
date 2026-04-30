"""Stokes–Einstein breakdown coefficient (λ) tests.

Phase 18 — S2: sub-150-nm SE corrections.

Verifies:
- λ = 1.0 reproduces v0.2 exactly (forward-compat contract).
- λ scales diffusivity linearly.
- λ propagates through classify_cell without changing the v0.2 default path.
- The Einstein–Smoluchowski relation holds with λ.
"""

from __future__ import annotations

import math

import pytest

from parameters import K_B, ParticleGeometry, diffusivity_geom, gamma_stokes_geom
from regime_map import classify_cell

_REPRESENTATIVE_CELLS = [
    (5e-9, 298.15),
    (1e-7, 298.15),
    (1e-6, 298.15),
]

_LAMBDA_VALUES = (0.1, 0.5, 1.0)


def test_lambda_one_reproduces_v0_2() -> None:
    """λ = 1.0 is the identity — diffusivity equals the v0.2 value."""
    geom = ParticleGeometry.from_radius(1e-7)
    d_default = diffusivity_geom(geom, 298.15)
    d_explicit = diffusivity_geom(geom, 298.15, lambda_se=1.0)
    assert d_default == d_explicit
    assert math.isclose(d_default, d_explicit, rel_tol=1e-15)


@pytest.mark.parametrize("radius_m, temperature_kelvin", _REPRESENTATIVE_CELLS)
@pytest.mark.parametrize("lambda_se", _LAMBDA_VALUES)
def test_lambda_scales_diffusivity_linearly(
    radius_m: float, temperature_kelvin: float, lambda_se: float
) -> None:
    """D(λ) = λ · D(1.0) to machine precision."""
    geom = ParticleGeometry.from_radius(radius_m)
    d_bare = diffusivity_geom(geom, temperature_kelvin, lambda_se=1.0)
    d_scaled = diffusivity_geom(geom, temperature_kelvin, lambda_se=lambda_se)
    assert math.isclose(d_scaled, lambda_se * d_bare, rel_tol=1e-15)


@pytest.mark.parametrize("radius_m, temperature_kelvin", _REPRESENTATIVE_CELLS)
def test_einstein_relation_with_lambda(radius_m: float, temperature_kelvin: float) -> None:
    """D · γ = λ · k_B · T must hold for any λ."""
    geom = ParticleGeometry.from_radius(radius_m)
    gamma = gamma_stokes_geom(geom, temperature_kelvin)
    for lambda_se in _LAMBDA_VALUES:
        d = diffusivity_geom(geom, temperature_kelvin, lambda_se=lambda_se)
        product = d * gamma
        expected = lambda_se * K_B * temperature_kelvin
        assert math.isclose(product, expected, rel_tol=1e-15), (
            f"Einstein relation failed at r={radius_m}, T={temperature_kelvin}, λ={lambda_se}: "
            f"D·γ = {product}, λ·k_B·T = {expected}"
        )


def test_classify_cell_default_lambda_unchanged() -> None:
    """classify_cell without lambda_se kwarg reproduces the v0.2 path."""
    result_default = classify_cell(1e-7, 298.15, 1e-3, 3600.0)
    result_explicit = classify_cell(1e-7, 298.15, 1e-3, 3600.0, lambda_se=1.0)
    assert result_default.regime == result_explicit.regime
    assert math.isclose(
        result_default.top_to_bottom_ratio,
        result_explicit.top_to_bottom_ratio,
        rel_tol=1e-15,
    )
    assert math.isclose(
        result_default.bottom_mass_fraction,
        result_explicit.bottom_mass_fraction,
        rel_tol=1e-15,
    )


@pytest.mark.parametrize("lambda_se", (0.1, 0.5))
def test_classify_cell_with_lambda_changes_diffusivity_path(lambda_se: float) -> None:
    """Non-default λ changes the diffusivity used inside Method C.

    This is a smoke test, not a regime-label audit — the audit that
    checks label-flip prevalence lives in the Phase-18 lab note.
    """
    # Pick a cell that goes through Method C (not a short-circuit).
    # 100 nm, 1 mm, 1 min is well below equilibration.
    result_bare = classify_cell(1e-7, 298.15, 1e-3, 60.0, lambda_se=1.0)
    result_scaled = classify_cell(1e-7, 298.15, 1e-3, 60.0, lambda_se=lambda_se)
    # Diffusivity is reduced → effective Péclet number increases →
    # settling dominates more over diffusion → the profile is steeper
    # (more mass at bottom, less at top).  ratio = c(h)/c(0) drops.
    assert result_scaled.top_to_bottom_ratio < result_bare.top_to_bottom_ratio
