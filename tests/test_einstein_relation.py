"""Einstein–Smoluchowski relation: D · γ = k_B · T to machine precision.

Spec: breakout-note §4.4 validation strategy, fifth bullet ("recovered to
machine precision in the parameter module").

This is the simplest possible identity in the model — and a well-known
trap when γ and D are derived through different code paths. The check
here protects against accidental re-rounding or unit mismatches.
"""

from __future__ import annotations

import math

from parameters import K_B, diffusivity, gamma_stokes

_REPRESENTATIVE_CELLS = [
    # (radius_m, temperature_K) — corners and a midpoint of the breakout-note scan grid
    (5e-9, 278.15),
    (5e-9, 308.15),
    (1e-7, 293.15),
    (1e-6, 298.15),
    (1e-5, 308.15),
]


def test_einstein_smoluchowski_machine_precision() -> None:
    for radius_m, temperature_kelvin in _REPRESENTATIVE_CELLS:
        gamma = gamma_stokes(radius_m, temperature_kelvin)
        d = diffusivity(radius_m, temperature_kelvin)
        product = d * gamma
        expected = K_B * temperature_kelvin
        assert math.isclose(product, expected, rel_tol=1e-15), (
            f"Einstein relation failed at r={radius_m}, T={temperature_kelvin}: "
            f"D·γ = {product}, k_B·T = {expected}"
        )
