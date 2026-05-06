"""Phase 5 — §5.1 regime classification orchestration.

Spec: breakout-note §5 (parameter scan), §5.1 (regime classification).

Pins both the threshold logic (`classify_cell`) and the grid-walking
shape (`walk_grid`). Walks are deliberately tiny — the production
6300-cell sweep takes ~150 min single-threaded (8836 s measured on
the Phase 6 commit) and belongs in a one-shot deliverable script,
not the unit suite.
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import pytest

from fokker_planck import DEFAULT_N_CELLS
from regime_map import (
    _CSV_FIELDS,
    _PHASE11_CSV_FIELDS,
    _V01_CSV_FIELDS,
    HOMOGENEOUS_RATIO_THRESHOLD,
    REGIME_MAP_N_CELLS,
    REGIME_MAP_REFINEMENT_N_CELLS,
    SEDIMENTED_BOTTOM_MASS_THRESHOLD,
    SEDIMENTED_RATIO_THRESHOLD,
    RegimeGrid,
    RegimeResult,
    _classify_from_ratio_and_bmf,
    _detect_csv_format,
    classify_cell,
    results_from_csv,
    results_to_csv,
    results_to_grid,
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
    assert not res.convection_flag
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


def test_regime_map_refines_threshold_adjacent_cells_at_method_c_default() -> None:
    """Threshold-adjacent transient labels use Method C's production resolution.

    A previous 120-cell regime-map override was fast but could put
    near-threshold transient cells on the wrong side of the homogeneous
    boundary.
    """
    assert REGIME_MAP_N_CELLS < DEFAULT_N_CELLS
    assert REGIME_MAP_REFINEMENT_N_CELLS == DEFAULT_N_CELLS


def test_resolved_threshold_cell_stays_on_converged_side_of_boundary() -> None:
    """Regression for a resolved transient that flipped at 120 cells.

    The first pass reports c(h)/c(0) just above 0.95, then the
    threshold-adjacent refinement moves it below the threshold.
    """
    res = classify_cell(2.41e-8, 298.15, 1e-2, t_obs_s=600.0)

    assert not res.used_homogeneous_short_circuit
    assert not res.used_equilibrated_short_circuit
    assert not res.used_method_c_fallback
    assert res.top_to_bottom_ratio < HOMOGENEOUS_RATIO_THRESHOLD
    assert res.regime == "stratified"


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


def test_convection_flag_is_side_channel() -> None:
    """Realistic ΔT can flag a deep cell without changing its §5.1 label."""
    base = classify_cell(5e-9, 298.15, 1e-2, t_obs_s=3600.0)
    flagged = classify_cell(5e-9, 298.15, 1e-2, t_obs_s=3600.0, delta_T_assumed=0.1)

    assert not base.convection_flag
    assert flagged.convection_flag
    assert flagged.regime == base.regime
    assert flagged.top_to_bottom_ratio == base.top_to_bottom_ratio
    assert flagged.bottom_mass_fraction == base.bottom_mass_fraction


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


def test_walk_grid_propagates_convection_flag() -> None:
    results = walk_grid(
        radii=(5e-9,),
        temperatures=(298.15,),
        depths=(1e-2,),
        t_obs=(3600.0,),
        delta_T_assumed=0.1,
    )

    assert len(results) == 1
    assert results[0].convection_flag


def test_walk_grid_parallel_byte_identical_to_serial() -> None:
    """Phase 19 item H: ``n_workers > 1`` must reproduce serial output exactly.

    Walks a small (3×2×2×2 = 24) slice including a Method-C-resolved
    radius row so the parallel path actually exercises the heavy
    Smoluchowski solver. Byte-identical equality is required because the
    §5 cache contract (ADR 0001) is machine-precision, not "approximately
    equal".
    """
    axes = {
        "radii": (5e-9, 1e-7, 1e-6),
        "temperatures": (288.15, 308.15),
        "depths": (1e-4, 1e-3),
        "t_obs": (3600.0, 86400.0),
    }

    serial = walk_grid(**axes, n_workers=1)
    parallel = walk_grid(**axes, n_workers=2)

    assert len(parallel) == len(serial) == 24
    for i, (s, p) in enumerate(zip(serial, parallel, strict=True)):
        assert s == p, f"cell {i} differs: serial={s} parallel={p}"


def test_walk_grid_spawn_rejects_stdin_main_with_clear_error(monkeypatch) -> None:
    """Spawn cannot re-import a ``<stdin>`` main; fail before pool creation."""
    monkeypatch.setattr(sys.modules["__main__"], "__file__", "<stdin>", raising=False)

    with pytest.raises(RuntimeError, match="requires an importable __main__"):
        walk_grid(
            radii=(5e-9,),
            temperatures=(298.15,),
            depths=(1e-4,),
            t_obs=(60.0,),
            n_workers=2,
        )


# ---------------------------------------------------------------------------
# CSV cache round-trip
# ---------------------------------------------------------------------------


def test_results_csv_round_trip_is_lossless(tmp_path: Path) -> None:
    """CSV round-trip preserves every RegimeResult field bit-exactly.

    This is what lets the deliverable notebooks consume the precomputed
    grid cache without re-walking — a ~150-min operation otherwise.
    """
    original = walk_grid(
        radii=(5e-9, 1e-7, 1e-6),
        temperatures=(298.15, 308.15),
        depths=(1e-4, 1e-3),
        t_obs=(60.0, 3600.0),
    )
    path = tmp_path / "cache.csv"
    results_to_csv(original, path)
    restored = results_from_csv(path)

    assert len(restored) == len(original)
    for orig, back in zip(original, restored, strict=True):
        # Floats: bit-exact via repr round-trip.
        assert orig.r_material_m == back.r_material_m
        assert orig.r_hydro_m == back.r_hydro_m
        assert orig.delta_shell_m == back.delta_shell_m
        assert orig.radius_m == back.radius_m
        assert orig.temperature_kelvin == back.temperature_kelvin
        assert orig.sample_depth_m == back.sample_depth_m
        assert orig.t_obs_s == back.t_obs_s
        assert orig.top_to_bottom_ratio == back.top_to_bottom_ratio
        assert orig.bottom_mass_fraction == back.bottom_mass_fraction
        # Strings and bools: identity.
        assert orig.regime == back.regime
        assert orig.used_homogeneous_short_circuit == back.used_homogeneous_short_circuit
        assert orig.used_equilibrated_short_circuit == back.used_equilibrated_short_circuit
        assert orig.used_method_c_fallback == back.used_method_c_fallback
        assert orig.convection_flag == back.convection_flag


def test_results_csv_back_compat_reads_pre_v02_format(tmp_path: Path) -> None:
    """Pre-v0.2 CSVs have no convection column; load them as all-False."""
    path = tmp_path / "pre_v02_cache.csv"
    path.write_text(
        "radius_m,temperature_kelvin,sample_depth_m,t_obs_s,regime,"
        "top_to_bottom_ratio,bottom_mass_fraction,"
        "used_homogeneous_short_circuit,used_equilibrated_short_circuit,"
        "used_method_c_fallback\n"
        "5e-09,298.15,0.0001,3600.0,homogeneous,"
        "0.999,0.05,True,False,False\n"
    )

    restored = results_from_csv(path)

    assert len(restored) == 1
    assert restored[0].r_material_m == 5e-9
    assert restored[0].r_hydro_m == 5e-9
    assert restored[0].delta_shell_m == 0.0
    assert not restored[0].convection_flag


def test_results_csv_back_compat_reads_phase11_format(tmp_path: Path) -> None:
    """Phase-11 CSVs have radius_m plus convection_flag."""
    path = tmp_path / "phase11_cache.csv"
    path.write_text(
        "radius_m,temperature_kelvin,sample_depth_m,t_obs_s,regime,"
        "top_to_bottom_ratio,bottom_mass_fraction,"
        "used_homogeneous_short_circuit,used_equilibrated_short_circuit,"
        "used_method_c_fallback,convection_flag\n"
        "1e-06,298.15,0.01,3600.0,sedimented,"
        "0.001,0.99,False,True,False,True\n"
    )

    restored = results_from_csv(path)

    assert len(restored) == 1
    assert restored[0].r_material_m == 1e-6
    assert restored[0].r_hydro_m == 1e-6
    assert restored[0].delta_shell_m == 0.0
    assert restored[0].convection_flag


def test_detect_csv_format_accepts_v01_phase11_and_current_headers() -> None:
    assert _detect_csv_format(_V01_CSV_FIELDS) == "v01"
    assert _detect_csv_format(_PHASE11_CSV_FIELDS) == "phase11"
    assert _detect_csv_format(_CSV_FIELDS) == "current"


def test_committed_regime_map_cache_uses_v02_zero_shell_schema() -> None:
    """Phase-13 cache migration preserves labels while using explicit radii."""
    cache_path = Path(__file__).resolve().parents[1] / "notebooks/data/regime_map_grid.csv"
    with cache_path.open(newline="") as fh:
        header = next(csv.reader(fh))

    assert _detect_csv_format(header) == "current"
    assert "radius_m" not in header
    results = results_from_csv(cache_path)
    assert len(results) == 6300
    assert {r.convection_flag for r in results} == {False}
    assert {r.delta_shell_m for r in results} == {0.0}
    assert all(r.r_material_m == r.r_hydro_m == r.radius_m for r in results)


def test_results_from_csv_rejects_mismatched_header(tmp_path: Path) -> None:
    """Wrong header raises rather than silently mis-mapping fields."""
    path = tmp_path / "broken.csv"
    path.write_text("foo,bar,baz\n1,2,3\n")
    try:
        results_from_csv(path)
    except ValueError:
        return
    raise AssertionError("expected ValueError on bad header")


# ---------------------------------------------------------------------------
# Coordinate-indexed reshape (`results_to_grid`)
# ---------------------------------------------------------------------------


def test_results_to_grid_recovers_axes_and_shape() -> None:
    """The grid axes and shape match the input cells' Cartesian product."""
    results = walk_grid(
        radii=(5e-9, 1e-7),
        temperatures=(298.15, 308.15),
        depths=(1e-4, 1e-3),
        t_obs=(60.0, 3600.0),
    )
    grid = results_to_grid(results)
    assert isinstance(grid, RegimeGrid)
    assert grid.radii == (5e-9, 1e-7)
    assert grid.temperatures == (298.15, 308.15)
    assert grid.depths == (1e-4, 1e-3)
    assert grid.t_obs == (60.0, 3600.0)
    assert grid.regime.shape == (2, 2, 2, 2)
    assert grid.r_material == grid.radii
    assert grid.r_hydro.shape == grid.regime.shape
    assert (grid.r_hydro[:, :, :, :] == grid.r_hydro[:, 0:1, 0:1, 0:1]).all()


def test_results_to_grid_is_order_independent() -> None:
    """Reshape is by coordinate value, not row position — shuffling the
    input list reproduces an identical grid. This is the contract that
    notebook 02 / 03 / 04 rely on so a sorted or otherwise-reordered
    cache cannot silently mis-map axes onto figures.
    """
    import random

    results = walk_grid(
        radii=(5e-9, 1e-7),
        temperatures=(298.15, 308.15),
        depths=(1e-4, 1e-3),
        t_obs=(60.0, 3600.0),
    )
    grid_in_order = results_to_grid(results)

    shuffled = list(results)
    random.Random(42).shuffle(shuffled)
    grid_shuffled = results_to_grid(shuffled)

    assert (grid_in_order.regime == grid_shuffled.regime).all()
    assert (grid_in_order.ratio == grid_shuffled.ratio).all()
    assert (grid_in_order.bmf == grid_shuffled.bmf).all()
    assert (grid_in_order.path == grid_shuffled.path).all()
    assert (grid_in_order.convection_flag == grid_shuffled.convection_flag).all()
    assert (grid_in_order.r_hydro == grid_shuffled.r_hydro).all()


def test_results_to_grid_rejects_missing_cell() -> None:
    """A non-rectangular set of cells is rejected rather than silently
    leaving sentinel values in the grid."""
    results = walk_grid(
        radii=(5e-9, 1e-7),
        temperatures=(298.15,),
        depths=(1e-4, 1e-3),
        t_obs=(60.0,),
    )
    # Drop one cell to break the Cartesian product.
    with pytest.raises(ValueError, match="rectangular"):
        results_to_grid(results[:-1])


def test_results_to_grid_rejects_duplicate_cell() -> None:
    """A cell repeated for the same coordinates is rejected."""
    results = walk_grid(
        radii=(5e-9, 1e-7),
        temperatures=(298.15,),
        depths=(1e-4, 1e-3),
        t_obs=(60.0,),
    )
    with pytest.raises(ValueError, match="(rectangular|duplicate)"):
        results_to_grid(results + [results[0]])
