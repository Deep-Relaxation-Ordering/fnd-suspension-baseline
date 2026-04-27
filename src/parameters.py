"""SI constants and water-properties module.

Spec: breakout-note §3 (Physical model) and §4.4 (validation — Einstein relation).

Provides T-dependent water density and viscosity, plus the canonical
diamond density. Buoyant mass, settling velocity, diffusivity, and
gravitational scale height are derived in :mod:`analytical`.

Stub only — no functions implemented yet.
"""

from __future__ import annotations

# Physical constants (CODATA 2018, SI units)
K_B: float = 1.380_649e-23  # Boltzmann constant, J/K
G: float = 9.806_65  # standard gravity, m/s^2

# Diamond bulk density (breakout-note §3 and §7g)
RHO_P_DIAMOND: float = 3510.0  # kg/m^3


def rho_water(temperature_kelvin: float) -> float:
    """Water density ρ_f(T) in kg/m³ (IAPWS-95 or tabulated)."""
    raise NotImplementedError


def eta_water(temperature_kelvin: float) -> float:
    """Water dynamic viscosity η(T) in Pa·s (Kestin–Sengers or IAPWS)."""
    raise NotImplementedError
