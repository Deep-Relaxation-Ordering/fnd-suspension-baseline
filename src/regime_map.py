"""High-level orchestration — produces deliverables 3 (regime map) and 5 (design table).

Spec: breakout-note §5 (parameter scan), §5.1 (regime classification), §6 (deliverables).

Parameter grid: 30 × 7 × 5 × 6 = 6300 cells of (r, T, h, t_obs). All
four axes are owned by `src/scan_grid.py`; this module composes Method
A (analytical) and Method C (Smoluchowski PDE) per cell to produce the
§5.1 regime label.

Regime classification (initial condition c(z, 0) = 1/h, uniform after mixing):

- **homogeneous**  c(h)/c(0) ≥ 0.95
- **stratified**   0.05 < c(h)/c(0) < 0.95
- **sedimented**   c(h)/c(0) ≤ 0.05  AND  ∫₀^{0.05·h} c dz ≥ 0.95

The fixed-bottom-layer second criterion (round-4 fix) prevents finite-time
profiles where the top has depleted but the bulk mass is still in transit
from being mis-labelled as sedimented.

Method C is the engine:

- ``c(h) / c(0)`` comes from `FokkerPlanckResult.top_to_bottom_ratio`
  (log-linear extrapolation, exact for exponential profiles per Phase 4.1).
- ``∫₀^{0.05·h} c dz`` comes from
  `FokkerPlanckResult.bottom_mass_fraction(0.05)`.

A homogeneous-corner short-circuit avoids the Method C call entirely
when Method A's *equilibrium* ratio ``exp(-h/ℓ_g) ≥ 0.95`` — at finite
t_obs starting from uniform IC, the ratio is bounded between the
equilibrium value and 1, so the cell is always homogeneous regardless
of t_obs. This skip cuts the homogeneous corner of the grid (~half the
6300 cells) out of the expensive expm_multiply path.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from analytical import scale_height, settling_velocity
from fokker_planck import solve_cell
from parameters import RHO_P_DIAMOND, diffusivity
from scan_grid import DEPTHS_M, T_OBS_S, radii_m, temperatures_k

Regime = Literal["homogeneous", "stratified", "sedimented"]
"""§5.1 regime label."""

HOMOGENEOUS_RATIO_THRESHOLD: float = 0.95
"""c(h)/c(0) ≥ this → homogeneous (§5.1)."""

SEDIMENTED_RATIO_THRESHOLD: float = 0.05
"""c(h)/c(0) ≤ this → sedimented candidate; round-4 second criterion still applies."""

SEDIMENTED_BOTTOM_LAYER_FRACTION: float = 0.05
"""Layer thickness for the sedimented bottom-mass criterion (§5.1)."""

SEDIMENTED_BOTTOM_MASS_THRESHOLD: float = 0.95
"""∫₀^{0.05 h} c dz ≥ this → sedimented (round-4 second criterion)."""

EQUILIBRATED_RELAXATION_FACTOR: float = 5.0
"""Multiplier on the diffusive relaxation time at which a cell is treated
as fully equilibrated (the analytic Method-A profile is exact). At
``5 · t_relax`` the residual transient is e⁻⁵ ≈ 0.7 % from equilibrium —
well below the §5.1 threshold sharpness, and well into the corner of
the grid where Method C's refined-mesh expm_multiply becomes ruinously
expensive."""

REGIME_MAP_MIN_RESOLVABLE_DZ_M: float = 1e-8
"""10 nm threshold passed into Method C from `classify_cell`. The
production Method-C default (`fokker_planck.MIN_RESOLVABLE_DZ_M = 1 nm`)
trades runtime for boundary-layer fidelity; for §5.1 *regime
classification* we don't need to resolve sub-10-nm boundary layers
because the fallback's transient + equilibrium answers agree with the
full FV solution on the integrated quantities (top/bottom ratio and
bottom-mass fraction) to well below threshold sharpness. Bumping the
threshold to 10 nm routes the high-r corner of the grid (cells with
ℓ_g ≲ 50 nm and t_obs short of the equilibrated short-circuit) through
the fast asymptotic transient instead of a refined-mesh
expm_multiply that would otherwise cost 10-20 s per cell."""


@dataclass
class RegimeResult:
    """One cell of the §5.1 classification.

    The numerical inputs to the §5.1 thresholds are kept on the result
    so downstream callers (deliverable-5 design table, regime-map
    figures) don't have to re-run Method C to recover them.

    The three short-circuit flags record *which* path produced the
    classification — useful both for debugging the orchestration and
    for the deliverable-3 figure annotations that distinguish
    analytically-determined cells from those that needed the full
    PDE solve.
    """

    radius_m: float
    temperature_kelvin: float
    sample_depth_m: float
    t_obs_s: float
    regime: Regime
    top_to_bottom_ratio: float
    bottom_mass_fraction: float
    used_homogeneous_short_circuit: bool
    used_equilibrated_short_circuit: bool
    used_method_c_fallback: bool


def _equilibrium_bottom_mass_fraction(
    sample_depth_m: float,
    scale_height_m: float,
    layer_fraction: float = SEDIMENTED_BOTTOM_LAYER_FRACTION,
) -> float:
    """Closed-form Method-A bottom-mass fraction of the barometric profile.

    For c_eq(z) ∝ exp(-z/ℓ_g) on [0, h] with reflecting walls::

        ∫₀^{f h} c_eq(z) dz / ∫₀^h c_eq(z) dz = (1 - e^{-f·h/ℓ_g}) / (1 - e^{-h/ℓ_g}).

    The 700-threshold branches keep the formula well-behaved into the
    deeply-sedimented corner (h/ℓ_g ≳ 25 000 in the §5 grid), where
    the naive ``exp(-h/ℓ_g)`` underflows but the layer-fraction term
    may still be representable.
    """
    h_over_ell = sample_depth_m / scale_height_m
    layer_arg = layer_fraction * h_over_ell
    if h_over_ell > 700.0:
        return 1.0 if layer_arg > 700.0 else -math.expm1(-layer_arg)
    return -math.expm1(-layer_arg) / -math.expm1(-h_over_ell)


def _classify_from_ratio_and_bmf(ratio: float, bmf: float) -> Regime:
    """Apply the §5.1 thresholds to a (ratio, bmf) pair."""
    if ratio >= HOMOGENEOUS_RATIO_THRESHOLD:
        return "homogeneous"
    if ratio <= SEDIMENTED_RATIO_THRESHOLD and bmf >= SEDIMENTED_BOTTOM_MASS_THRESHOLD:
        return "sedimented"
    return "stratified"


def classify_cell(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    t_obs_s: float,
    *,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
    n_cells: int = 120,
    min_resolvable_dz_m: float = REGIME_MAP_MIN_RESOLVABLE_DZ_M,
) -> RegimeResult:
    """Classify a single (r, T, h, t_obs) cell per breakout-note §5.1.

    Uses two analytic short-circuits to skip the expensive Method C
    expm_multiply on the corners of the grid where it isn't needed:

    1. **Homogeneous corner**: when the equilibrium ratio
       ``exp(-h/ℓ_g) ≥ 0.95``, the finite-time ratio (decreasing
       monotonically from 1 at uniform IC toward eq_ratio) stays in
       ``[0.95, 1]`` for any t_obs → always homogeneous, no Method C
       needed.

    2. **Equilibrated corner**: when ``t_obs ≥ 5 · t_relax`` *and*
       ``t_obs ≥ 1.01 · h / v_sed``, the system is past the diffusive
       relaxation time and past pure-sedimentation arrival; the
       residual transient is ≲ 0.7 % from the analytic Method-A
       equilibrium. This catches cells like r = 1 µm, h = 1 mm,
       t_obs = 1 min (where ``h / v_sed ≈ 1.6 s``), which would
       otherwise force Method C through a refined-mesh
       expm_multiply with a spectral radius around 10⁵ s⁻¹ and runtimes
       in the tens of seconds per cell.

    Cells that miss both short-circuits go through Method C. For
    sub-5 nm scale heights, Method C's own asymptotic-sedimentation
    fallback engages internally and stays fast.
    """
    ell_g = scale_height(radius_m, temperature_kelvin, rho_particle_kg_per_m3)
    eq_ratio = math.exp(-sample_depth_m / ell_g) if ell_g > 0.0 else 0.0

    # Short-circuit 1: homogeneous corner.
    if eq_ratio >= HOMOGENEOUS_RATIO_THRESHOLD:
        return RegimeResult(
            radius_m=radius_m,
            temperature_kelvin=temperature_kelvin,
            sample_depth_m=sample_depth_m,
            t_obs_s=t_obs_s,
            regime="homogeneous",
            top_to_bottom_ratio=eq_ratio,
            bottom_mass_fraction=SEDIMENTED_BOTTOM_LAYER_FRACTION,
            used_homogeneous_short_circuit=True,
            used_equilibrated_short_circuit=False,
            used_method_c_fallback=False,
        )

    # Short-circuit 2: equilibrated corner.
    v_sed = settling_velocity(radius_m, temperature_kelvin, rho_particle_kg_per_m3)
    d = diffusivity(radius_m, temperature_kelvin)
    t_relax = min(sample_depth_m, ell_g) ** 2 / d
    t_arrival = sample_depth_m / v_sed if v_sed > 0.0 else math.inf
    t_full_eq = max(EQUILIBRATED_RELAXATION_FACTOR * t_relax, 1.01 * t_arrival)

    if t_obs_s >= t_full_eq:
        bmf = _equilibrium_bottom_mass_fraction(sample_depth_m, ell_g)
        return RegimeResult(
            radius_m=radius_m,
            temperature_kelvin=temperature_kelvin,
            sample_depth_m=sample_depth_m,
            t_obs_s=t_obs_s,
            regime=_classify_from_ratio_and_bmf(eq_ratio, bmf),
            top_to_bottom_ratio=eq_ratio,
            bottom_mass_fraction=bmf,
            used_homogeneous_short_circuit=False,
            used_equilibrated_short_circuit=True,
            used_method_c_fallback=False,
        )

    # Otherwise: full Method C, with a regime-classification mesh floor.
    method_c = solve_cell(
        radius_m,
        temperature_kelvin,
        sample_depth_m,
        t_total=t_obs_s,
        rho_particle_kg_per_m3=rho_particle_kg_per_m3,
        n_cells=n_cells,
        min_resolvable_dz_m=min_resolvable_dz_m,
    )
    ratio = method_c.top_to_bottom_ratio()
    bmf = method_c.bottom_mass_fraction(SEDIMENTED_BOTTOM_LAYER_FRACTION)

    return RegimeResult(
        radius_m=radius_m,
        temperature_kelvin=temperature_kelvin,
        sample_depth_m=sample_depth_m,
        t_obs_s=t_obs_s,
        regime=_classify_from_ratio_and_bmf(ratio, bmf),
        top_to_bottom_ratio=ratio,
        bottom_mass_fraction=bmf,
        used_homogeneous_short_circuit=False,
        used_equilibrated_short_circuit=False,
        used_method_c_fallback=method_c.used_asymptotic_fallback,
    )


def walk_grid(
    *,
    radii: tuple[float, ...] | None = None,
    temperatures: tuple[float, ...] | None = None,
    depths: tuple[float, ...] | None = None,
    t_obs: tuple[float, ...] | None = None,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
    n_cells: int = 120,
    min_resolvable_dz_m: float = REGIME_MAP_MIN_RESOLVABLE_DZ_M,
) -> list[RegimeResult]:
    """Walk a (sub-)grid of (r, T, h, t_obs) cells and classify each one.

    With no axes specified, walks the full §5 grid (30 × 7 × 5 × 6 =
    6300 cells). Caller-supplied axes override the defaults — primarily
    used by tests to walk small slices, and by the deliverable-3
    notebook to slice along a single axis (e.g. fixed temperature, vary
    r and h).
    """
    rs = tuple(radii_m()) if radii is None else radii
    ts = tuple(temperatures_k()) if temperatures is None else temperatures
    hs = DEPTHS_M if depths is None else depths
    t_obs_axis = T_OBS_S if t_obs is None else t_obs

    results: list[RegimeResult] = []
    for r in rs:
        for t in ts:
            for h in hs:
                for t_obs_val in t_obs_axis:
                    results.append(
                        classify_cell(
                            r,
                            t,
                            h,
                            t_obs_val,
                            rho_particle_kg_per_m3=rho_particle_kg_per_m3,
                            n_cells=n_cells,
                            min_resolvable_dz_m=min_resolvable_dz_m,
                        )
                    )
    return results
