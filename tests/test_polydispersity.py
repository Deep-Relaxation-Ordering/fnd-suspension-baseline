"""Phase 14 — log-normal polydispersity smearing tests."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from polydispersity import SIGMA_GEOM_AXIS, lognormal_cdf, lognormal_smear
from regime_map import results_from_csv, results_to_grid


@pytest.fixture(scope="module")
def grid():
    cache_path = Path(__file__).resolve().parents[1] / "notebooks/data/regime_map_grid.csv"
    return results_to_grid(results_from_csv(cache_path))


def _nearest_log_index(axis: tuple[float, ...], value: float) -> int:
    arr = np.asarray(axis)
    return int(np.argmin(np.abs(np.log(arr / value))))


def test_lognormal_cdf_median_is_half() -> None:
    assert math.isclose(lognormal_cdf(1e-7, 1e-7, 1.2), 0.5, rel_tol=1e-15)


def test_sigma_axis_is_phase14_deliverable_axis() -> None:
    assert SIGMA_GEOM_AXIS == (1.05, 1.10, 1.20, 1.40, 1.60)


def test_degenerate_limit_recovers_sharp_labels(grid) -> None:
    ri = _nearest_log_index(grid.radii, 1e-7)
    r_mean = grid.radii[ri]

    smeared = lognormal_smear(
        grid,
        r_geom_mean_axis=(r_mean,),
        sigma_geom_axis=(1.001,),
        on_truncation="mask",
    )

    sharp_h = (grid.regime[ri] == 0).astype(float)
    sharp_s = (grid.regime[ri] == 1).astype(float)
    sharp_sed = (grid.regime[ri] == 2).astype(float)
    assert np.allclose(smeared.p_homogeneous[0, 0], sharp_h, atol=0.01)
    assert np.allclose(smeared.p_stratified[0, 0], sharp_s, atol=0.01)
    assert np.allclose(smeared.p_sedimented[0, 0], sharp_sed, atol=0.01)


def test_conservation_at_every_accepted_cell(grid) -> None:
    r_axis = (grid.radii[4], grid.radii[14], grid.radii[24])
    smeared = lognormal_smear(
        grid,
        r_geom_mean_axis=r_axis,
        sigma_geom_axis=(1.05, 1.20, 1.60),
        on_truncation="mask",
    )

    total = (
        smeared.p_homogeneous
        + smeared.p_stratified
        + smeared.p_sedimented
    )
    assert np.allclose(total[smeared.accepted], 1.0, rtol=1e-15, atol=1e-15)
    assert np.isfinite(smeared.expected_top_to_bottom_ratio[smeared.accepted]).all()
    assert np.isfinite(smeared.expected_bottom_mass_fraction[smeared.accepted]).all()


def test_truncation_rejection(grid) -> None:
    with pytest.raises(ValueError, match="outside the §5 radius axis"):
        lognormal_smear(
            grid,
            r_geom_mean_axis=(1e-9,),
            sigma_geom_axis=(1.05,),
            on_truncation="raise",
        )


def test_truncation_mask_mode_marks_rejected_cells(grid) -> None:
    smeared = lognormal_smear(
        grid,
        r_geom_mean_axis=(1e-9,),
        sigma_geom_axis=(1.05,),
        on_truncation="mask",
    )

    assert not smeared.accepted.any()
    assert np.isfinite(smeared.truncation_loss).all()
    assert (smeared.truncation_loss > 0.95).all()


def test_smear_at_homog_anchor_broadens_into_stratified(grid) -> None:
    ti = grid.temperatures.index(298.15)
    hi = grid.depths.index(1e-3)
    oi = grid.t_obs.index(3600.0)

    smeared = lognormal_smear(
        grid,
        r_geom_mean_axis=(5e-9,),
        sigma_geom_axis=(1.05, 1.40, 1.60),
        on_truncation="mask",
    )

    values = smeared.p_stratified[0, :, ti, hi, oi]
    assert values[0] == 0.0
    assert math.isclose(values[1], 0.00034995565925409787, rel_tol=1e-12)
    assert math.isclose(values[2], 0.009914498245427426, rel_tol=1e-12)
    assert values[0] < values[1] < values[2]


def test_smear_at_sedim_anchor_broadens_into_stratified(grid) -> None:
    ti = grid.temperatures.index(298.15)
    hi = grid.depths.index(1e-3)
    oi = grid.t_obs.index(86400.0)
    ri = _nearest_log_index(grid.radii, 1e-6)

    smeared = lognormal_smear(
        grid,
        r_geom_mean_axis=(grid.radii[ri],),
        sigma_geom_axis=(1.05, 1.40, 1.60),
        on_truncation="mask",
    )

    values = smeared.p_stratified[0, :, ti, hi, oi]
    assert values[0] == 0.0
    assert math.isclose(values[1], 2.5752190380147843e-09, rel_tol=1e-12)
    assert math.isclose(values[2], 1.4421389185990441e-05, rel_tol=1e-12)
    assert values[0] < values[1] < values[2]


def test_smear_at_strat_anchor_dilutes_at_high_sigma(grid) -> None:
    ti = grid.temperatures.index(298.15)
    hi = grid.depths.index(1e-3)
    oi = grid.t_obs.index(3600.0)
    ri = _nearest_log_index(grid.radii, 1e-7)

    smeared = lognormal_smear(
        grid,
        r_geom_mean_axis=(grid.radii[ri],),
        sigma_geom_axis=(1.05, 1.40, 1.60),
        on_truncation="mask",
    )

    values = smeared.p_stratified[0, :, ti, hi, oi]
    assert values[0] == 1.0
    assert math.isclose(values[1], 0.9967981070016865, rel_tol=1e-12)
    assert math.isclose(values[2], 0.9743740560867108, rel_tol=1e-12)
    assert values[0] > values[1] > values[2]


def test_smear_axis_extension_outside_radius_axis_is_rejected(grid) -> None:
    for r_mean in (1e-9, 2e-5):
        with pytest.raises(ValueError, match="outside the §5 radius axis"):
            lognormal_smear(
                grid,
                r_geom_mean_axis=(r_mean,),
                sigma_geom_axis=(1.20,),
                on_truncation="raise",
            )
