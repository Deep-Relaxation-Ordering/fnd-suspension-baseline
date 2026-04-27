"""Equilibrium-distribution checks.

Spec: breakout-note §4.4 validation strategy, first bullet.

- Method B at long times reproduces Method A barometric equilibrium to
  ≤ 2 % deviation in mean height for N = 1e5.
- Position variance ⟨z²⟩ − ⟨z⟩² of the uniform-on-[0,h] equilibrium
  saturates at h²/12 (round-4 distinction from the displacement-MSD
  saturation at h²/6 — see test_method_consistency).
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Awaiting Method A and Method B implementations.")
def test_method_b_long_time_matches_barometric() -> None:
    pass


@pytest.mark.skip(reason="Awaiting Method B implementation.")
def test_position_variance_saturates_at_h2_over_12() -> None:
    pass
