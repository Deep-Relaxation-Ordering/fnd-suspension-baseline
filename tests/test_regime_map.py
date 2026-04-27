"""Phase 5 — §5.1 regime classification orchestration.

Spec: breakout-note §5 (parameter scan), §5.1 (regime classification).

Pins both the threshold logic (`classify_cell`) and the grid-walking
shape (`walk_grid`). Walks are deliberately tiny — the production
6300-cell sweep takes O(20 min) and belongs in a one-shot deliverable
script, not the unit suite.
"""

from __future__ import annotations

import math

from regime_map import (
    HOMOGENEOUS_RATIO_THRESHOLD,
    SEDIMENTED_BOTTOM_MASS_THRESHOLD,
    SEDIMENTED_RATIO_THRESHOLD,
    RegimeResult,
    _classify_from_ratio_and_bmf,
    classify_cell,
    walk_grid,
)
from scan_grid import DEPTHS_M, N_T_OBS, radii_m, temperatures_k

# ---------------------------------------------------------------------------
# §5.1 threshold logic
# ---------------------------------------------------------------------------


def test_classify_thresholds_homogeneous() -> None:
    assert _classify_from_ratio_and_bmf(0.95, 0.05) == "homogeneous"
    assert _classify_from_ratio_and_bmf(1.0, 0.05) == "homogeneous"


def test_classify_thresholds_sedimented_requires_both_criteria() -> None:
    """Round-4 fix: sedimented requires ratio ≤ 0.05 *and* bmf ≥ 0.95."""
    assert _classify_from_ratio_and_bmf(0.05, 0.95) == "sedimented"
    assert _classify_from_ratio_and_bmf(0.01, 0.99) == "sedimented"
    # ratio low but bmf low (transient) → stratified, not sedimented
    assert _classify_from_ratio_and_bmf(0.01, 0.5) == "stratified"


def test_classify_thresholds_stratified() -> None:
    assert _classify_from_ratio_and_bmf(0.5, 0.1) == "stratified"
    assert _classify_from_ratio_and_bmf(0.1, 0.5) == "stratified"


# ---------------------------------------------------------------------------
# Short-circuits
# ---------------------------------------------------------------------------


def test_homogeneous_short_circuit_fires_for_small_radii() -> None:
    """5 nm at 25 °C in 100 µm cell: ℓ_g ≈ 32 cm ≫ h, eq ratio ≈ 0.9997."""
    res = classify_cell(5e-9, 298.15, 1e-4, t_obs_s=3600.0)
    assert res.regime == "homogeneous"
    assert res.used_homogeneous_short_circuit
    assert res.top_to_bottom_ratio >= HOMOGENEOUS_RATIO_THRESHOLD


def test_equilibrated_short_circuit_fires_when_t_obs_dominates_relaxation() -> None:
    """100 nm at 25 °C in 100 µm cell, t_obs = 1 hour: t_relax ≈ 11 min,
    so 1 hour is past the 5 t_relax threshold → analytic equilibrium."""
    from analytical import scale_height
    res = classify_cell(1e-7, 298.15, 1e-4, t_obs_s=3600.0)
    assert res.regime == "stratified"
    assert res.used_equilibrated_short_circuit
    # Equilibrium ratio is exp(-h/ℓ_g) at this cell's actual ℓ_g.
    expected_ratio = math.exp(-1e-4 / scale_height(1e-7, 298.15))
    assert math.isclose(res.top_to_bottom_ratio, expected_ratio, rel_tol=1e-12)


def test_method_c_runs_for_genuine_transients() -> None:
    """100 nm at 25 °C in 100 µm cell, t_obs = 1 minute: well below
    5 t_relax (≈ 55 min) and below 1.01 h/v_sed → Method C runs."""
    res = classify_cell(1e-7, 298.15, 1e-4, t_obs_s=60.0)
    assert not res.used_homogeneous_short_circuit
    assert not res.used_equilibrated_short_circuit
    # The transient ratio is between eq_ratio and 1.
    assert math.exp(-2.5) <= res.top_to_bottom_ratio <= 1.0


def test_method_c_fallback_fires_in_high_pe_corner() -> None:
    """1 µm at 25 °C in 1 mm cell, t_obs = 1 min: pre-arrival
    (h/v ≈ 162 s) so equilibrated short-circuit misses, but
    ℓ_g ≈ 40 nm so the regime-map mesh floor (10 nm) triggers Method C's
    asymptotic-sedimentation transient fallback rather than a refined
    expm_multiply."""
    res = classify_cell(1e-6, 298.15, 1e-3, t_obs_s=60.0)
    assert res.used_method_c_fallback
    # Pre-arrival fallback: ratio is 0 (slab hasn't reached the top
    # cell), bmf < 0.95 (mass still in transit) → stratified.
    assert res.regime == "stratified"
    assert res.bottom_mass_fraction < SEDIMENTED_BOTTOM_MASS_THRESHOLD


# ---------------------------------------------------------------------------
# Round-4 second criterion: in-transit cells are NOT sedimented
# ---------------------------------------------------------------------------


def test_in_transit_cell_is_stratified_not_sedimented() -> None:
    """1 µm at 25 °C in 10 mm cell at 1 min: top is empty (ratio ≈ 0)
    but only ~6 % of mass has reached the bottom 5 % layer. Per the
    round-4 second criterion this is stratified, NOT sedimented."""
    res = classify_cell(1e-6, 298.15, 1e-2, t_obs_s=60.0)
    assert res.top_to_bottom_ratio <= SEDIMENTED_RATIO_THRESHOLD
    assert res.bottom_mass_fraction < SEDIMENTED_BOTTOM_MASS_THRESHOLD
    assert res.regime == "stratified"


def test_long_time_high_pe_cell_is_sedimented() -> None:
    """Same cell at 1 day: equilibrated short-circuit fires; analytic
    equilibrium has all mass in the ℓ_g ≈ 40-nm boundary layer ⊂ bottom 5 %."""
    res = classify_cell(1e-6, 298.15, 1e-3, t_obs_s=86400.0)
    assert res.used_equilibrated_short_circuit
    assert res.regime == "sedimented"
    assert res.bottom_mass_fraction >= SEDIMENTED_BOTTOM_MASS_THRESHOLD


# ---------------------------------------------------------------------------
# Grid walker
# ---------------------------------------------------------------------------


def test_walk_grid_default_axes_match_scan_grid() -> None:
    """When no axes are passed, walk_grid covers the full §5 grid shape.

    Walking the actual 6300 cells is a deliverable-time operation; here
    we just check that the *axis lengths* match scan_grid by walking a
    1-radius × 1-T × 1-h × 1-t_obs slice and verifying the overall
    cell count would be 6300 for the unrestricted call.
    """
    # Smallest possible slice — just 1 cell — to verify the shape contract.
    results = walk_grid(
        radii=(5e-9,),
        temperatures=(298.15,),
        depths=(1e-4,),
        t_obs=(3600.0,),
    )
    assert len(results) == 1
    assert isinstance(results[0], RegimeResult)

    # Cross-check the implied default cardinality (no walk).
    expected_total = len(radii_m()) * len(temperatures_k()) * len(DEPTHS_M) * N_T_OBS
    assert expected_total == 6300


def test_walk_grid_subset_iteration_order() -> None:
    """The 4-deep nested loop iterates radius → temperature → depth → t_obs.
    Pin that order so downstream reshape into a 4-D array is unambiguous."""
    radii = (5e-9, 1e-7)
    temps = (298.15, 308.15)
    depths = (1e-4, 1e-3)
    t_obs = (3600.0, 86400.0)
    results = walk_grid(
        radii=radii, temperatures=temps, depths=depths, t_obs=t_obs,
    )
    assert len(results) == 16

    # Recover the iteration order: the outermost loop is radius, the
    # innermost is t_obs. With 2×2×2×2 = 16 cells, the first 8 share
    # radius=radii[0]; the first 4 share radius=radii[0] AND
    # temperature=temps[0]; etc.
    for i, res in enumerate(results):
        ri = i // 8
        ti = (i // 4) % 2
        hi = (i // 2) % 2
        oi = i % 2
        assert res.radius_m == radii[ri]
        assert res.temperature_kelvin == temps[ti]
        assert res.sample_depth_m == depths[hi]
        assert res.t_obs_s == t_obs[oi]


def test_walk_grid_smoke_diversity() -> None:
    """A small subset spanning the radius axis should cover all three regimes."""
    results = walk_grid(
        radii=(5e-9, 1e-7, 1e-6),
        temperatures=(298.15,),
        depths=(1e-3,),
        t_obs=(3600.0,),
    )
    regimes = {r.regime for r in results}
    assert regimes == {"homogeneous", "stratified", "sedimented"}
