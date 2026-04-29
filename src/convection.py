"""Rayleigh-number convection side-channel for the §5 regime map.

The §5.1 labels remain diffusion/sedimentation labels. This module
answers the separate question: at a specified vertical temperature
difference, would buoyancy-driven convection invalidate the 1-D
transport assumption?
"""

from __future__ import annotations

from typing import Final, Literal

from parameters import G, eta_water, rho_water

RAYLEIGH_CRITICAL_RIGID_RIGID: Final[float] = 1707.762
"""Critical Rayleigh number for a rigid-rigid horizontal layer."""

RAYLEIGH_CRITICAL_RIGID_FREE: Final[float] = 1100.65
"""Critical Rayleigh number for a rigid-free horizontal layer."""

WATER_THERMAL_DIFFUSIVITY_M2_PER_S: Final[float] = 1.4e-7
"""Thermal diffusivity of liquid water used for pilot-v0.2, m²/s."""

DEFAULT_EXPERIMENTAL_DELTA_T_K: Final[float] = 0.1
"""Experimental-facing vertical ΔT convention for notebook overlays.

The programmatic regime-map API defaults to ``delta_T_assumed = 0.0 K``
for v0.1 compatibility. Notebooks pass this constant explicitly when
they want the convection side-channel populated for realistic laboratory
thermostat hysteresis.
"""

BoundaryCondition = Literal["rigid-rigid", "rigid-free"]


def thermal_expansion_coefficient(temperature_kelvin: float) -> float:
    """Return water's volumetric thermal expansion coefficient α(T), K⁻¹.

    The implementation analytically differentiates the same Tanaka
    (2001) density fit used by `parameters.rho_water`, so the density
    and expansion models stay internally consistent:

    ``α = -(1 / ρ) · dρ/dT``.

    The signed value is intentional. Below the density maximum near
    4 °C, α < 0 and the standard Rayleigh-Bénard heating-from-below
    criterion does not apply by simply taking an absolute value.
    """
    x = temperature_kelvin - 273.15
    a1 = -3.983_035
    a2 = 301.797
    a3 = 522_528.9
    a4 = 69.348_81
    a5 = 999.974_950

    u = x + a1
    v = x + a2
    numerator = u**2 * v
    numerator_prime = 2.0 * u * v + u**2
    q_prime = (
        numerator_prime * (x + a4) - numerator
    ) / (a3 * (x + a4) ** 2)

    return a5 * q_prime / rho_water(temperature_kelvin)


def rayleigh_number(
    sample_depth_m: float,
    delta_T_kelvin: float,
    temperature_kelvin: float,
) -> float:
    """Return the signed Rayleigh number for a horizontal water layer."""
    if sample_depth_m <= 0.0:
        raise ValueError("sample_depth_m must be positive.")

    alpha = thermal_expansion_coefficient(temperature_kelvin)
    rho = rho_water(temperature_kelvin)
    nu = eta_water(temperature_kelvin) / rho
    return (
        G
        * alpha
        * delta_T_kelvin
        * sample_depth_m**3
        / (nu * WATER_THERMAL_DIFFUSIVITY_M2_PER_S)
    )


def is_convection_dominated(
    rayleigh: float,
    *,
    boundary: BoundaryCondition = "rigid-rigid",
) -> bool:
    """Return True when ``rayleigh`` is strictly above the boundary threshold."""
    if boundary == "rigid-rigid":
        threshold = RAYLEIGH_CRITICAL_RIGID_RIGID
    elif boundary == "rigid-free":
        threshold = RAYLEIGH_CRITICAL_RIGID_FREE
    else:
        raise ValueError(f"unsupported boundary condition {boundary!r}")
    return rayleigh > threshold
