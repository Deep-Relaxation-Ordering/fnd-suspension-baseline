"""Log-normal polydispersity post-processing for the §5 regime-map cache.

Phase 14 treats the sharp-radius §5 regime map as a quadrature grid in
material radius and smears it against log-normal preparation statistics.
The convolution uses exact bin masses in log-radius space rather than
pointwise PDF weights.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray

from regime_map import RegimeGrid

SIGMA_GEOM_AXIS: Final[tuple[float, ...]] = (1.05, 1.10, 1.20, 1.40, 1.60)
"""Geometric-standard-deviation axis for the v0.2 deliverable-6 table."""

MIN_COVERED_MASS: Final[float] = 0.95
"""Minimum log-normal probability mass covered by the §5 radius support."""


@dataclass(frozen=True)
class SmearedGrid:
    """Polydispersity-smoothed regime probabilities on cache coordinates."""

    r_geom_mean_axis: tuple[float, ...]
    sigma_geom_axis: tuple[float, ...]
    temperatures: tuple[float, ...]
    depths: tuple[float, ...]
    t_obs: tuple[float, ...]
    p_homogeneous: NDArray[np.float64]
    p_stratified: NDArray[np.float64]
    p_sedimented: NDArray[np.float64]
    expected_top_to_bottom_ratio: NDArray[np.float64]
    expected_bottom_mass_fraction: NDArray[np.float64]
    truncation_loss: NDArray[np.float64]
    accepted: NDArray[np.bool_]


def _validate_lognormal_params(r_geom_mean: float, sigma_geom: float) -> None:
    if r_geom_mean <= 0.0:
        raise ValueError("r_geom_mean must be positive.")
    if sigma_geom < 1.0:
        raise ValueError("sigma_geom must be >= 1.0.")


def lognormal_pdf(r: float, r_geom_mean: float, sigma_geom: float) -> float:
    """Log-normal PDF in radius, parameterised by geometric mean and sigma."""
    _validate_lognormal_params(r_geom_mean, sigma_geom)
    if r <= 0.0:
        return 0.0
    if sigma_geom == 1.0:
        return math.inf if r == r_geom_mean else 0.0
    sigma_ln = math.log(sigma_geom)
    z = (math.log(r) - math.log(r_geom_mean)) / sigma_ln
    return math.exp(-0.5 * z * z) / (r * sigma_ln * math.sqrt(2.0 * math.pi))


def lognormal_cdf(r: float, r_geom_mean: float, sigma_geom: float) -> float:
    """Log-normal CDF in radius, parameterised by geometric mean and sigma."""
    _validate_lognormal_params(r_geom_mean, sigma_geom)
    if r <= 0.0:
        return 0.0
    if sigma_geom == 1.0:
        return 0.0 if r < r_geom_mean else 1.0
    sigma_ln = math.log(sigma_geom)
    z = (math.log(r) - math.log(r_geom_mean)) / (sigma_ln * math.sqrt(2.0))
    return 0.5 * (1.0 + math.erf(z))


def _log_radius_bin_edges(radii: NDArray[np.float64]) -> NDArray[np.float64]:
    if radii.ndim != 1 or radii.size < 2:
        raise ValueError("radii must be a one-dimensional axis with at least two points.")
    if not np.all(radii > 0.0):
        raise ValueError("radii must be positive.")
    if not np.all(np.diff(radii) > 0.0):
        raise ValueError("radii must be strictly increasing.")
    log_r = np.log(radii)
    return np.concatenate([
        [log_r[0] - (log_r[1] - log_r[0]) / 2.0],
        (log_r[:-1] + log_r[1:]) / 2.0,
        [log_r[-1] + (log_r[-1] - log_r[-2]) / 2.0],
    ])


def _bin_weights(
    radii: NDArray[np.float64],
    r_geom_mean: float,
    sigma_geom: float,
) -> tuple[NDArray[np.float64], float]:
    edges = np.exp(_log_radius_bin_edges(radii))
    cdf_values = np.array(
        [lognormal_cdf(float(edge), r_geom_mean, sigma_geom) for edge in edges],
        dtype=np.float64,
    )
    weights = np.diff(cdf_values)
    # Guard against tiny CDF subtraction noise while keeping real negatives visible.
    weights[np.abs(weights) < 1e-18] = 0.0
    covered_mass = float(np.sum(weights))
    return weights, covered_mass


def _as_tuple(axis: ArrayLike, *, name: str) -> tuple[float, ...]:
    arr = np.asarray(axis, dtype=np.float64)
    if arr.ndim != 1 or arr.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional axis.")
    return tuple(float(v) for v in arr)


def lognormal_smear(
    grid: RegimeGrid,
    r_geom_mean_axis: ArrayLike | None = None,
    sigma_geom_axis: ArrayLike = SIGMA_GEOM_AXIS,
    *,
    min_covered_mass: float = MIN_COVERED_MASS,
    on_truncation: Literal["raise", "mask"] = "raise",
) -> SmearedGrid:
    """Smear a sharp-radius `RegimeGrid` against log-normal radius distributions."""
    if not (0.0 < min_covered_mass <= 1.0):
        raise ValueError("min_covered_mass must be in (0, 1].")
    if on_truncation not in {"raise", "mask"}:
        raise ValueError("on_truncation must be 'raise' or 'mask'.")

    radii = np.asarray(grid.r_material, dtype=np.float64)
    r_axis_source = radii if r_geom_mean_axis is None else r_geom_mean_axis
    r_axis = _as_tuple(r_axis_source, name="r_geom_mean_axis")
    sigma_axis = _as_tuple(sigma_geom_axis, name="sigma_geom_axis")
    for r_mean in r_axis:
        if r_mean <= 0.0:
            raise ValueError("r_geom_mean_axis values must be positive.")
    for sigma in sigma_axis:
        if sigma < 1.0:
            raise ValueError("sigma_geom_axis values must be >= 1.0.")

    shape = (
        len(r_axis),
        len(sigma_axis),
        len(grid.temperatures),
        len(grid.depths),
        len(grid.t_obs),
    )
    p_h = np.full(shape, np.nan, dtype=np.float64)
    p_s = np.full(shape, np.nan, dtype=np.float64)
    p_sed = np.full(shape, np.nan, dtype=np.float64)
    expected_ratio = np.full(shape, np.nan, dtype=np.float64)
    expected_bmf = np.full(shape, np.nan, dtype=np.float64)
    truncation_loss = np.full(shape, np.nan, dtype=np.float64)
    accepted = np.full(shape, False, dtype=np.bool_)

    is_h = (grid.regime == 0).astype(np.float64)
    is_s = (grid.regime == 1).astype(np.float64)
    is_sed = (grid.regime == 2).astype(np.float64)

    for ri, r_mean in enumerate(r_axis):
        for si, sigma in enumerate(sigma_axis):
            weights, covered_mass = _bin_weights(radii, r_mean, sigma)
            loss = 1.0 - covered_mass
            cell_accepted = covered_mass >= min_covered_mass
            if on_truncation == "raise" and not cell_accepted:
                raise ValueError(
                    "log-normal distribution loses too much mass outside the §5 "
                    f"radius axis: r_geom_mean={r_mean}, sigma_geom={sigma}, "
                    f"covered_mass={covered_mass:.6g}, truncation_loss={loss:.6g}"
                )
            truncation_loss[ri, si, :, :, :] = loss
            accepted[ri, si, :, :, :] = cell_accepted
            if covered_mass <= 0.0:
                continue

            w = weights[:, None, None, None] / covered_mass
            p_h[ri, si] = np.sum(w * is_h, axis=0)
            p_s[ri, si] = np.sum(w * is_s, axis=0)
            p_sed[ri, si] = np.sum(w * is_sed, axis=0)
            expected_ratio[ri, si] = np.sum(w * grid.ratio, axis=0)
            expected_bmf[ri, si] = np.sum(w * grid.bmf, axis=0)

    return SmearedGrid(
        r_geom_mean_axis=r_axis,
        sigma_geom_axis=sigma_axis,
        temperatures=grid.temperatures,
        depths=grid.depths,
        t_obs=grid.t_obs,
        p_homogeneous=p_h,
        p_stratified=p_s,
        p_sedimented=p_sed,
        expected_top_to_bottom_ratio=expected_ratio,
        expected_bottom_mass_fraction=expected_bmf,
        truncation_loss=truncation_loss,
        accepted=accepted,
    )
