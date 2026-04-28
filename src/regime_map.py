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
of t_obs. This skip cuts the analytically homogeneous corner of the
grid out of the expensive expm_multiply path.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from analytical import scale_height, settling_velocity
from fokker_planck import DEFAULT_N_CELLS, solve_cell
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

REGIME_MAP_N_CELLS: int = 120
"""First-pass finite-volume cell count used by the regime map.

The full §5 sweep is dominated by resolved transient Method-C cells.
A 120-cell first pass keeps the cache walk tractable; cells close to
classification thresholds are rerun with `REGIME_MAP_REFINEMENT_N_CELLS`
before their labels are assigned.
"""

REGIME_MAP_REFINEMENT_N_CELLS: int = DEFAULT_N_CELLS
"""Refined resolved-Method-C cell count for threshold-adjacent cells."""

REGIME_MAP_REFINEMENT_MARGIN: float = 1e-2
"""Rerun resolved transient cells this close to a ratio threshold.

The margin targets numerical classification stability rather than plot
smoothness. It catches the known 120-cell false-homogeneous transient
case while avoiding a full 240-cell sweep through the slow Method-C band.
The bottom-mass threshold is not included here because the high-Pe cells
near that boundary can be pathological under direct 240-cell
`expm_multiply`; those are handled by the 10-nm asymptotic-fallback
policy and documented as part of the fidelity envelope.
"""


@dataclass
class RegimeResult:
    """One cell of the §5.1 classification.

    The two numerical inputs to the §5.1 thresholds —
    `top_to_bottom_ratio` and `bottom_mass_fraction` — are kept on the
    result so downstream callers can rebuild the design table and the
    regime figure without re-running Method C. Their *interpretation*
    depends on which path produced them:

    - `used_homogeneous_short_circuit = True`:
      `top_to_bottom_ratio` is the analytic equilibrium value
      ``exp(-h/ℓ_g)`` — a lower bound on the finite-time ratio,
      which lives in ``[eq_ratio, 1.0]`` from uniform IC.
      `bottom_mass_fraction` is the analytic equilibrium bmf — an
      upper bound on the finite-time bmf, which rises monotonically
      from 0.05 (uniform IC) toward equilibrium.
    - `used_equilibrated_short_circuit = True`:
      both quantities are analytic equilibrium values; the residual
      finite-time transient is within e⁻⁵ ≈ 0.7 % of these.
    - `used_method_c_fallback = True`:
      finite-time values from the asymptotic-sedimentation transient
      branch (pre-arrival) or the analytic equilibrium fallback
      (post-arrival).
    - none of the above (full Method C):
      finite-time values from the resolved-mesh `expm_multiply`.

    Plot consumers that want the *exact* finite-time ratio for the
    homogeneous corner should re-run Method C with `min_resolvable_dz_m`
    matching their fidelity needs; the regime label itself is correct
    in all four cases.
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


def _needs_refined_method_c(ratio: float) -> bool:
    """Return True when a resolved Method-C ratio is threshold-adjacent."""
    return (
        abs(ratio - HOMOGENEOUS_RATIO_THRESHOLD) < REGIME_MAP_REFINEMENT_MARGIN
        or abs(ratio - SEDIMENTED_RATIO_THRESHOLD) < REGIME_MAP_REFINEMENT_MARGIN
    )


def classify_cell(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    t_obs_s: float,
    *,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
    n_cells: int = REGIME_MAP_N_CELLS,
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

    Cells that miss both short-circuits go through Method C. Resolved
    Method-C cells close to a §5.1 threshold are rerun at
    `REGIME_MAP_REFINEMENT_N_CELLS` before classification. For sub-5 nm
    scale heights, Method C's own asymptotic-sedimentation fallback
    engages internally and stays fast.
    """
    ell_g = scale_height(radius_m, temperature_kelvin, rho_particle_kg_per_m3)
    eq_ratio = math.exp(-sample_depth_m / ell_g) if ell_g > 0.0 else 0.0

    # Short-circuit 1: homogeneous corner.
    #
    # Reported ratio and bmf are the analytic equilibrium values — the
    # *bound*, not the finite-time value. For the homogeneous corner
    # (eq_ratio ≥ 0.95) the equilibrium bmf is ≈ 0.05 + (small h/ℓ_g
    # correction); the finite-time bmf at uniform IC starts at exactly
    # 0.05 and rises monotonically toward the equilibrium value. The
    # regime label is correct regardless. See `RegimeResult` for the
    # full interpretation table of the four execution paths.
    if eq_ratio >= HOMOGENEOUS_RATIO_THRESHOLD:
        eq_bmf = _equilibrium_bottom_mass_fraction(sample_depth_m, ell_g)
        return RegimeResult(
            radius_m=radius_m,
            temperature_kelvin=temperature_kelvin,
            sample_depth_m=sample_depth_m,
            t_obs_s=t_obs_s,
            regime="homogeneous",
            top_to_bottom_ratio=eq_ratio,
            bottom_mass_fraction=eq_bmf,
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
    if (
        not method_c.used_asymptotic_fallback
        and n_cells < REGIME_MAP_REFINEMENT_N_CELLS
        and _needs_refined_method_c(ratio)
    ):
        method_c = solve_cell(
            radius_m,
            temperature_kelvin,
            sample_depth_m,
            t_total=t_obs_s,
            rho_particle_kg_per_m3=rho_particle_kg_per_m3,
            n_cells=REGIME_MAP_REFINEMENT_N_CELLS,
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
    n_cells: int = REGIME_MAP_N_CELLS,
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


# ---------------------------------------------------------------------------
# CSV round-trip — cache for the deliverable notebooks
# ---------------------------------------------------------------------------
#
# The full §5 grid walk takes ~150 min single-threaded (8836 s measured
# on the Phase 6 commit; the Phase 5 extrapolation of 18 min was off by
# ~8× because the timing slice missed the slow Method-C-resolved corner).
# Running it once and pickling the results to disk lets the deliverable-3
# / deliverable-5 notebooks rebuild figures in O(seconds) without
# re-walking. CSV (not pickle) for human-readability and portability —
# the file is the authoritative form of the design table.

_CSV_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(RegimeResult))


def results_to_csv(results: list[RegimeResult], path: str | Path) -> None:
    """Write a list of `RegimeResult` to CSV at `path`.

    Columns are exactly the `RegimeResult` field names, in declaration
    order. Booleans are written as ``True``/``False`` strings; floats
    are written via Python's repr to preserve round-trip precision.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Force Unix line endings: Python's csv default of `\r\n` triggers
    # ``git diff --check`` "trailing whitespace" warnings on every row.
    with path.open("w", newline="\n") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(_CSV_FIELDS)
        for r in results:
            writer.writerow([_format_csv_value(getattr(r, name)) for name in _CSV_FIELDS])


def results_from_csv(path: str | Path) -> list[RegimeResult]:
    """Read a CSV written by `results_to_csv` back into RegimeResult objects."""
    path = Path(path)
    with path.open(newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        if tuple(header) != _CSV_FIELDS:
            raise ValueError(
                f"CSV header {header} does not match RegimeResult fields {_CSV_FIELDS}"
            )
        out: list[RegimeResult] = []
        for row in reader:
            kwargs: dict[str, object] = {}
            for field, raw in zip(_CSV_FIELDS, row, strict=True):
                kwargs[field] = _parse_csv_value(field, raw)
            out.append(RegimeResult(**kwargs))  # type: ignore[arg-type]
    return out


def _format_csv_value(value: object) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    # numpy scalars are not Python `bool`/`float` in isinstance terms; coerce.
    # `radii_m()` and similar return NDArrays whose elements are numpy scalars,
    # and `repr(np.float64(5e-9))` is the string ``'np.float64(5e-09)'`` —
    # not round-trippable through `float()`. Map to a Python float first.
    if hasattr(value, "item") and callable(value.item):  # numpy scalar
        value = value.item()
        if isinstance(value, bool):
            return "True" if value else "False"
    if isinstance(value, float):
        # repr() preserves bit-exact float round-trip (Python 3 guarantee).
        return repr(value)
    return str(value)


_BOOL_FIELDS: frozenset[str] = frozenset(
    f.name for f in fields(RegimeResult) if f.type is bool or f.type == "bool"
)
_STR_FIELDS: frozenset[str] = frozenset({"regime"})


def _parse_csv_value(field: str, raw: str) -> object:
    if field in _BOOL_FIELDS:
        if raw == "True":
            return True
        if raw == "False":
            return False
        raise ValueError(f"Unparseable bool {raw!r} in field {field}")
    if field in _STR_FIELDS:
        return raw
    # Tolerate legacy CSVs where numpy scalars were repr'd as
    # ``'np.float64(5e-09)'`` before the writer learned to coerce.
    if raw.startswith("np.float64(") and raw.endswith(")"):
        raw = raw[len("np.float64(") : -1]
    return float(raw)


# ---------------------------------------------------------------------------
# Coordinate-indexed reshape — for notebook consumption
# ---------------------------------------------------------------------------


_REGIME_INT: dict[Regime, int] = {"homogeneous": 0, "stratified": 1, "sedimented": 2}
"""Integer encoding for regime labels; used as `regime` channel in `results_to_grid`."""

_PATH_HOMOGENEOUS_SC: int = 0
_PATH_EQUILIBRATED_SC: int = 1
_PATH_METHOD_C_FALLBACK: int = 2
_PATH_METHOD_C_RESOLVED: int = 3


@dataclass(frozen=True)
class RegimeGrid:
    """Coordinate-indexed reshape of a list of `RegimeResult`.

    Each ``(ri, ti, hi, oi)`` index in the four channel arrays
    corresponds to ``(radii[ri], temperatures[ti], depths[hi],
    t_obs[oi])`` — *not* to the position in the original results list.
    Built by `results_to_grid`, which raises if any cell in the
    Cartesian product is missing or duplicated.

    Channels:

    - ``regime``: int8 with 0 = homogeneous, 1 = stratified, 2 = sedimented.
    - ``ratio``: float64 c(h)/c(0).
    - ``bmf``: float64 ∫₀^{0.05 h} c dz.
    - ``path``: int8 with 0 = homogeneous SC, 1 = equilibrated SC,
      2 = Method C fallback, 3 = Method C resolved mesh.
    """

    radii: tuple[float, ...]
    temperatures: tuple[float, ...]
    depths: tuple[float, ...]
    t_obs: tuple[float, ...]
    regime: NDArray[np.int8]
    ratio: NDArray[np.float64]
    bmf: NDArray[np.float64]
    path: NDArray[np.int8]


def results_to_grid(results: list[RegimeResult]) -> RegimeGrid:
    """Reshape a flat results list into a coordinate-indexed 4-D grid.

    The reshape is by *coordinate value*, not by row position, so a
    sorted or shuffled CSV produces the same result as the original
    walk_grid order. Raises ValueError if the cells don't form a
    rectangular Cartesian product (any cell missing or duplicated).
    """
    rs = sorted({r.radius_m for r in results})
    ts = sorted({r.temperature_kelvin for r in results})
    hs = sorted({r.sample_depth_m for r in results})
    os = sorted({r.t_obs_s for r in results})

    expected = len(rs) * len(ts) * len(hs) * len(os)
    if len(results) != expected:
        raise ValueError(
            f"results length {len(results)} does not match Cartesian product "
            f"{len(rs)}×{len(ts)}×{len(hs)}×{len(os)} = {expected}; "
            "the cells do not form a rectangular grid."
        )

    r_idx = {v: i for i, v in enumerate(rs)}
    t_idx = {v: i for i, v in enumerate(ts)}
    h_idx = {v: i for i, v in enumerate(hs)}
    o_idx = {v: i for i, v in enumerate(os)}

    shape = (len(rs), len(ts), len(hs), len(os))
    regime = np.full(shape, -1, dtype=np.int8)
    ratio = np.full(shape, np.nan, dtype=np.float64)
    bmf = np.full(shape, np.nan, dtype=np.float64)
    path = np.full(shape, -1, dtype=np.int8)

    for r in results:
        ri = r_idx[r.radius_m]
        ti = t_idx[r.temperature_kelvin]
        hi = h_idx[r.sample_depth_m]
        oi = o_idx[r.t_obs_s]
        if regime[ri, ti, hi, oi] != -1:
            raise ValueError(
                f"duplicate cell at (r={r.radius_m}, T={r.temperature_kelvin}, "
                f"h={r.sample_depth_m}, t_obs={r.t_obs_s})"
            )
        regime[ri, ti, hi, oi] = _REGIME_INT[r.regime]
        ratio[ri, ti, hi, oi] = r.top_to_bottom_ratio
        bmf[ri, ti, hi, oi] = r.bottom_mass_fraction
        if r.used_homogeneous_short_circuit:
            path[ri, ti, hi, oi] = _PATH_HOMOGENEOUS_SC
        elif r.used_equilibrated_short_circuit:
            path[ri, ti, hi, oi] = _PATH_EQUILIBRATED_SC
        elif r.used_method_c_fallback:
            path[ri, ti, hi, oi] = _PATH_METHOD_C_FALLBACK
        else:
            path[ri, ti, hi, oi] = _PATH_METHOD_C_RESOLVED

    if (regime == -1).any():
        raise ValueError("incomplete grid: some cells of the Cartesian product are missing")

    return RegimeGrid(
        radii=tuple(rs),
        temperatures=tuple(ts),
        depths=tuple(hs),
        t_obs=tuple(os),
        regime=regime,
        ratio=ratio,
        bmf=bmf,
        path=path,
    )
