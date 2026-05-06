"""Phase 14 — log-normal polydispersity smearing tests."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from polydispersity import (
    REGIME_INDEX_HOMOGENEOUS,
    REGIME_INDEX_SEDIMENTED,
    REGIME_INDEX_STRATIFIED,
    SIGMA_GEOM_AXIS,
    lognormal_cdf,
    lognormal_smear,
)
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


# ---------------------------------------------------------------------------
# Phase 28 — number-density kernel (program-context S5)
# ---------------------------------------------------------------------------


def test_classification_kernel_omits_phase28_moment_arrays(grid) -> None:
    smeared = lognormal_smear(
        grid,
        r_geom_mean_axis=(grid.radii[14],),
        sigma_geom_axis=(1.20,),
        on_truncation="mask",
    )
    assert smeared.weighting == "classification"
    assert smeared.expected_radius_by_regime is None
    assert smeared.expected_radius_sq_by_regime is None


def test_number_density_kernel_reproduces_classification_marginals(grid) -> None:
    r_axis = (grid.radii[4], grid.radii[14], grid.radii[24])
    sigma_axis = (1.05, 1.20, 1.60)
    classification = lognormal_smear(
        grid,
        r_geom_mean_axis=r_axis,
        sigma_geom_axis=sigma_axis,
        on_truncation="mask",
    )
    number_density = lognormal_smear(
        grid,
        r_geom_mean_axis=r_axis,
        sigma_geom_axis=sigma_axis,
        on_truncation="mask",
        weighting="number_density",
    )

    np.testing.assert_array_equal(
        number_density.p_homogeneous, classification.p_homogeneous,
    )
    np.testing.assert_array_equal(
        number_density.p_stratified, classification.p_stratified,
    )
    np.testing.assert_array_equal(
        number_density.p_sedimented, classification.p_sedimented,
    )
    np.testing.assert_array_equal(
        number_density.expected_top_to_bottom_ratio,
        classification.expected_top_to_bottom_ratio,
    )
    np.testing.assert_array_equal(
        number_density.expected_bottom_mass_fraction,
        classification.expected_bottom_mass_fraction,
    )


def test_number_density_kernel_recovers_law_of_total_expectation(grid) -> None:
    """sum_R p_R · E[r | R] equals the unconditional E[r] from the kernel."""
    r_axis = (grid.radii[4], grid.radii[14], grid.radii[24])
    sigma_axis = (1.05, 1.20, 1.60)
    smeared = lognormal_smear(
        grid,
        r_geom_mean_axis=r_axis,
        sigma_geom_axis=sigma_axis,
        on_truncation="mask",
        weighting="number_density",
    )

    radii = np.asarray(grid.r_material, dtype=np.float64)
    expected_radius_unconditional = np.full(
        smeared.p_homogeneous.shape, np.nan, dtype=np.float64,
    )
    for ri, r_mean in enumerate(r_axis):
        for si, sigma_geom in enumerate(sigma_axis):
            from polydispersity import _bin_weights

            weights, covered_mass = _bin_weights(radii, r_mean, sigma_geom)
            if covered_mass <= 0.0:
                continue
            w = weights / covered_mass
            expected_radius_unconditional[ri, si] = np.sum(
                w[:, None, None, None] * radii[:, None, None, None], axis=0,
            )

    band_h = smeared.expected_radius_by_regime[REGIME_INDEX_HOMOGENEOUS]
    band_s = smeared.expected_radius_by_regime[REGIME_INDEX_STRATIFIED]
    band_sed = smeared.expected_radius_by_regime[REGIME_INDEX_SEDIMENTED]

    contributions = np.zeros_like(expected_radius_unconditional)
    for p_regime, e_r_regime in (
        (smeared.p_homogeneous, band_h),
        (smeared.p_stratified, band_s),
        (smeared.p_sedimented, band_sed),
    ):
        valid = p_regime > 0.0
        contributions[valid] += p_regime[valid] * e_r_regime[valid]

    accepted = smeared.accepted
    np.testing.assert_allclose(
        contributions[accepted],
        expected_radius_unconditional[accepted],
        rtol=1e-12,
        atol=0.0,
    )


def test_number_density_kernel_marks_empty_bands_with_nan(grid) -> None:
    """Anchor a strongly homogeneous cell so the sedimented band is empty."""
    ti = grid.temperatures.index(298.15)
    hi = grid.depths.index(1e-3)
    oi = grid.t_obs.index(3600.0)
    ri = _nearest_log_index(grid.radii, 5e-9)

    smeared = lognormal_smear(
        grid,
        r_geom_mean_axis=(grid.radii[ri],),
        sigma_geom_axis=(1.05,),
        on_truncation="mask",
        weighting="number_density",
    )

    p_sed_cell = smeared.p_sedimented[0, 0, ti, hi, oi]
    e_r_sed_cell = smeared.expected_radius_by_regime[
        REGIME_INDEX_SEDIMENTED, 0, 0, ti, hi, oi
    ]
    assert p_sed_cell == 0.0
    assert math.isnan(e_r_sed_cell)


def test_number_density_kernel_radius_squared_dominates_radius(grid) -> None:
    """Sanity: E[r² | R] ≥ E[r | R]² for any non-empty band (Jensen)."""
    r_axis = (grid.radii[4], grid.radii[14], grid.radii[24])
    smeared = lognormal_smear(
        grid,
        r_geom_mean_axis=r_axis,
        sigma_geom_axis=(1.20,),
        on_truncation="mask",
        weighting="number_density",
    )
    e_r = smeared.expected_radius_by_regime
    e_r_sq = smeared.expected_radius_sq_by_regime
    finite = np.isfinite(e_r) & np.isfinite(e_r_sq)
    assert finite.any()
    variance = e_r_sq[finite] - e_r[finite] ** 2
    # Variance is non-negative in exact arithmetic; allow ~1e-10 relative
    # noise from independent finite-precision sums of m1 and m2.
    assert (variance >= -1e-10 * e_r_sq[finite]).all()


def test_number_density_kernel_invalid_weighting_keyword_raises(grid) -> None:
    with pytest.raises(ValueError, match="weighting"):
        lognormal_smear(
            grid,
            r_geom_mean_axis=(grid.radii[14],),
            sigma_geom_axis=(1.20,),
            on_truncation="mask",
            weighting="mass",  # type: ignore[arg-type]
        )
