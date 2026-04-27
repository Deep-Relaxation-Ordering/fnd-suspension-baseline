"""Sanity tests on the water-properties module.

Spec: breakout-note §3 (Material parameters) and §10 (stop condition on
vendor data sheet deviation > 10 %).

Currently a placeholder; concrete checks land alongside the parameters.py
implementation:

- ρ_water(T) within ±0.1 % of IAPWS reference values at T = 278, 298, 308 K
- η_water(T) within ±0.5 % of Kestin–Sengers reference at the same points
- monotonic ρ-decrease and η-decrease across 278–308 K
- temperature-range guard rails (raises outside 273–373 K)
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Awaiting parameters.py implementation.")
def test_density_iapws_reference() -> None:
    pass


@pytest.mark.skip(reason="Awaiting parameters.py implementation.")
def test_viscosity_kestin_sengers_reference() -> None:
    pass
