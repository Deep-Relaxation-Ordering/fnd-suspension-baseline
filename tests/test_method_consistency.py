"""Cross-method consistency and limiting-case checks.

Spec: breakout-note §4.4 validation strategy.

- Method B and Method C agree on time-dependent moments (mean, variance)
  within numerical tolerance, on cells inside Method B's feasibility envelope.
- Method A ↔ Method C agreement on equilibrium quantities for cells
  *outside* Method B's feasibility envelope (high-r corners; round-3 fix).
- Pure-Brownian limit (gravity off):
    * displacement-MSD ⟨[z(t) − z(0)]²⟩ → 2 D t in unbounded domain;
    * displacement-MSD saturates at **h²/6** at long lag in [0, h]
      (two uncorrelated samples from uniform-on-[0,h]). NOT h²/12 — that
      is the position variance, tested separately in test_equilibrium.
- Pure-sedimentation limit (D → 0): for uniform IC on [0, h], bottom
  population reaches 100 % at t = h / v_sed, with mean arrival time
  h / (2 v_sed); particles starting at z₀ arrive at t(z₀) = z₀ / v_sed.
- Method C high/low-Pe limits: exponential-fitting FV reduces to upwind
  at high Pe, central at low Pe; asymptotic-sedimentation fallback engages
  when ℓ_g drops below the smallest representable mesh spacing (round-4).
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Awaiting Method B and Method C implementations.")
def test_method_b_c_time_dependent_moments_agree() -> None:
    pass


@pytest.mark.skip(reason="Awaiting Method C implementation.")
def test_method_a_c_equilibrium_outside_b_envelope() -> None:
    pass


@pytest.mark.skip(reason="Awaiting Method B implementation.")
def test_unbounded_msd_linear_in_time() -> None:
    pass


@pytest.mark.skip(reason="Awaiting Method B implementation.")
def test_bounded_displacement_msd_saturates_at_h2_over_6() -> None:
    pass


@pytest.mark.skip(reason="Awaiting Method B implementation.")
def test_pure_sedimentation_arrival_times() -> None:
    pass


@pytest.mark.skip(reason="Awaiting Method C implementation.")
def test_method_c_high_pe_upwind_limit() -> None:
    pass


@pytest.mark.skip(reason="Awaiting Method C implementation.")
def test_method_c_low_pe_central_limit() -> None:
    pass


@pytest.mark.skip(reason="Awaiting Method C implementation.")
def test_method_c_asymptotic_sedimentation_fallback() -> None:
    pass
