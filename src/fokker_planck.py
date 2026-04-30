"""Method C — Smoluchowski (overdamped Fokker-Planck) PDE.

Spec: breakout-note §4.1 Method C.

Solves the 1D Smoluchowski equation on z in [0, h] with no-flux
boundaries:

    partial_t c = D partial_zz c + v_sed partial_z c

with flux J = -D partial_z c - v_sed c and J(0) = J(h) = 0. The
finite-volume discretisation uses Scharfetter-Gummel exponential fitting,
so the interface flux reduces to central differencing at low Peclet number
and to upwind drift at high Peclet number.

The high-Pe end of the scan can have scale heights far below any useful
mesh spacing. Those cells are tagged with an asymptotic-sedimentation
fallback instead of pretending a finite mesh resolved a sub-nanometric
boundary layer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import expm_multiply

from analytical import (
    barometric_mean_height,
    scale_height_geom,
    settling_velocity_geom,
)
from parameters import (
    RHO_P_DIAMOND,
    ParticleGeometry,
    as_particle_geometry,
    diffusivity_geom,
)

DEFAULT_N_CELLS: int = 240
"""Default finite-volume cell count for Method C."""

MAX_N_CELLS: int = 480
"""Upper mesh cap used when bottom refinement is needed."""

MIN_RESOLVABLE_DZ_M: float = 1e-9
"""Smallest cell width Method C attempts to resolve directly."""

@dataclass
class FokkerPlanckResult:
    """Concentration profile returned by Method C.

    `concentration` stores cell-average densities in 1/m. Integrals are
    therefore weighted by `cell_widths`.
    """

    z: NDArray[np.float64]
    cell_edges: NDArray[np.float64]
    cell_widths: NDArray[np.float64]
    concentration: NDArray[np.float64]
    t_total: float
    v_sed: float
    diffusivity: float
    h: float
    method: str
    pe_global: float
    used_asymptotic_fallback: bool = False
    fallback_reason: str | None = None
    mean_override_m: float | None = None
    variance_override_m2: float | None = None

    def mass(self) -> float:
        """Return total probability mass."""
        return float(np.sum(self.concentration * self.cell_widths))

    def probabilities(self) -> NDArray[np.float64]:
        """Return per-cell probability masses normalised to sum to one."""
        mass = self.mass()
        if mass <= 0.0:
            raise ValueError("Concentration has non-positive total mass.")
        return self.concentration * self.cell_widths / mass

    def mean_height(self) -> float:
        """Return mean height <z>, in metres."""
        if self.mean_override_m is not None:
            return self.mean_override_m
        return float(np.sum(self.z * self.probabilities()))

    def variance_height(self) -> float:
        """Return position variance Var(z), in m^2."""
        if self.variance_override_m2 is not None:
            return self.variance_override_m2
        probs = self.probabilities()
        mean = float(np.sum(self.z * probs))
        return float(np.sum((self.z - mean) ** 2 * probs))

    def top_to_bottom_ratio(self) -> float:
        """Return c(h) / c(0), the §5.1 regime-classification quantity.

        Implementation: log-linear extrapolation from the two cells nearest
        each boundary. This is *exact* for an exponential profile (the
        equilibrium barometric form), reduces to 1 for a uniform profile,
        and degrades gracefully for arbitrary cell-centre interpolations
        in between.

        Edge cases:
        - ``concentration[-1] == 0`` (asymptotic-sedimentation fallback):
          returns 0.0 immediately. The fallback equilibrium has all mass
          in the bottom cell, so c(h) is structurally zero.
        - ``concentration[0] <= 0``: returns +inf.
        - Either of the two interpolation neighbours has a non-positive
          concentration (rare numerical pathology): falls back to the
          bare cell-average ratio, which preserves the API contract
          without log-of-zero crashes.
        """
        c_bot_0 = float(self.concentration[0])
        c_bot_1 = float(self.concentration[1])
        c_top_0 = float(self.concentration[-1])
        c_top_1 = float(self.concentration[-2])

        if c_top_0 == 0.0:
            return 0.0
        if c_bot_0 <= 0.0:
            return math.inf

        # Log-linear extrapolation requires positive neighbours; otherwise
        # fall back to the cell-average ratio (still a defined number).
        if c_bot_1 <= 0.0 or c_top_1 <= 0.0:
            return c_top_0 / c_bot_0

        z_bot_0 = float(self.z[0])
        z_bot_1 = float(self.z[1])
        z_top_0 = float(self.z[-1])
        z_top_1 = float(self.z[-2])

        log_c_at_zero = math.log(c_bot_0) + (math.log(c_bot_1) - math.log(c_bot_0)) * (
            0.0 - z_bot_0
        ) / (z_bot_1 - z_bot_0)
        log_c_at_h = math.log(c_top_0) + (math.log(c_top_1) - math.log(c_top_0)) * (
            self.h - z_top_0
        ) / (z_top_1 - z_top_0)

        return math.exp(log_c_at_h - log_c_at_zero)

    def bottom_mass_fraction(self, layer_fraction: float = 0.05) -> float:
        """Return mass in the bottom `layer_fraction` of the sample."""
        if not (0.0 < layer_fraction <= 1.0):
            raise ValueError("layer_fraction must be in (0, 1].")
        cutoff = layer_fraction * self.h
        mass = 0.0
        for left, right, density in zip(
            self.cell_edges[:-1],
            self.cell_edges[1:],
            self.concentration,
            strict=True,
        ):
            overlap = max(0.0, min(float(right), cutoff) - float(left))
            mass += float(density) * overlap
            if right >= cutoff:
                break
        total = self.mass()
        return mass / total if total > 0.0 else math.nan


def bernoulli(x: float) -> float:
    """Scharfetter-Gummel Bernoulli function B(x) = x / (exp(x) - 1)."""
    if abs(x) < 1e-6:
        return 1.0 - 0.5 * x + x * x / 12.0 - x**4 / 720.0
    if x > 50.0:
        return x * math.exp(-x)
    if x < -50.0:
        return -x
    return x / math.expm1(x)


def sg_flux_coefficients(diff: float, v_sed: float, dx: float) -> tuple[float, float]:
    """Return coefficients `(a_left, a_right)` for an interface flux.

    For neighbouring cell concentrations `c_left`, `c_right`::

        J = a_left * c_left + a_right * c_right

    where J is the upward-positive flux. Low Pe gives the central flux
    `-D dc/dz - v c`; high Pe gives the drift-upwind flux `-v c_right`.
    """
    if dx <= 0.0:
        raise ValueError("dx must be positive.")
    if diff < 0.0 or v_sed < 0.0:
        raise ValueError("diff and v_sed must be non-negative.")
    if diff == 0.0:
        return 0.0, -v_sed
    pe = v_sed * dx / diff
    scale = diff / dx
    return scale * bernoulli(pe), -scale * bernoulli(-pe)


def make_mesh(
    h: float,
    *,
    ell_g: float | None = None,
    n_cells: int = DEFAULT_N_CELLS,
    max_cells: int = MAX_N_CELLS,
    min_resolvable_dz_m: float = MIN_RESOLVABLE_DZ_M,
) -> tuple[NDArray[np.float64], bool, str | None]:
    """Build finite-volume cell edges, refined toward z=0 when needed."""
    if h <= 0.0:
        raise ValueError("h must be positive.")
    if n_cells < 2:
        raise ValueError("n_cells must be at least 2.")

    if ell_g is None or ell_g <= 0.0:
        return np.linspace(0.0, h, n_cells + 1, dtype=np.float64), False, None

    target_dz = ell_g / 5.0
    if target_dz < min_resolvable_dz_m:
        if h <= min_resolvable_dz_m:
            fallback_edges = np.array([0.0, h], dtype=np.float64)
        else:
            fallback_edges = np.array([0.0, min_resolvable_dz_m, h], dtype=np.float64)
        return (
            fallback_edges,
            True,
            (
                f"ell_g/5 = {target_dz:.3e} m is below the configured "
                f"minimum dz {min_resolvable_dz_m:.3e} m"
            ),
        )

    required_uniform_n = max(n_cells, int(math.ceil(h / target_dz)))
    if required_uniform_n <= max_cells:
        return np.linspace(0.0, h, required_uniform_n + 1, dtype=np.float64), False, None

    n = max_cells
    # Exponential map z(y) clusters cell edges near the bottom. Increase the
    # stretching parameter until the first cell resolves ell_g/5.
    stretch = 2.0
    y = np.linspace(0.0, 1.0, n + 1, dtype=np.float64)
    edges = np.linspace(0.0, h, n + 1, dtype=np.float64)
    for _ in range(40):
        denom = math.expm1(stretch)
        edges = h * np.expm1(stretch * y) / denom
        if edges[1] - edges[0] <= target_dz:
            edges[0] = 0.0
            edges[-1] = h
            return edges, False, None
        stretch *= 1.25
        if stretch > 700.0:
            break

    return (
        edges,
        True,
        f"unable to resolve ell_g/5 = {target_dz:.3e} m with {max_cells} cells",
    )


def build_operator(
    cell_edges: NDArray[np.float64],
    *,
    diff: float,
    v_sed: float,
) -> csr_matrix:
    """Build the conservative Scharfetter-Gummel finite-volume operator."""
    widths = np.diff(cell_edges)
    if np.any(widths <= 0.0):
        raise ValueError("cell_edges must be strictly increasing.")
    n = widths.size
    centers = 0.5 * (cell_edges[:-1] + cell_edges[1:])

    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []

    for i in range(n - 1):
        dx = float(centers[i + 1] - centers[i])
        a_left, a_right = sg_flux_coefficients(diff, v_sed, dx)

        rows.extend([i, i, i + 1, i + 1])
        cols.extend([i, i + 1, i, i + 1])
        data.extend(
            [
                -a_left / widths[i],
                -a_right / widths[i],
                a_left / widths[i + 1],
                a_right / widths[i + 1],
            ]
        )

    return csr_matrix((data, (rows, cols)), shape=(n, n), dtype=np.float64)


def _normalise_density(
    concentration: NDArray[np.float64],
    widths: NDArray[np.float64],
) -> NDArray[np.float64]:
    c = np.asarray(concentration, dtype=np.float64)
    # Tiny negative entries can appear after Krylov exponentiation; they are
    # numerical noise, not physical probability.
    c = np.maximum(c, 0.0)
    mass = float(np.sum(c * widths))
    if mass <= 0.0:
        raise ValueError("Concentration has non-positive total mass.")
    return c / mass


def _asymptotic_result(
    *,
    h: float,
    t_total: float,
    v_sed: float,
    diff: float,
    ell_g: float,
    reason: str,
    min_resolvable_dz_m: float,
) -> FokkerPlanckResult:
    """Return a tagged high-Pe asymptotic result.

    Before the pure-sedimentation arrival time, use the analytic D -> 0
    map for a uniform initial condition: a bottom delta with mass v*t/h
    plus a translated uniform slab on [0, h - v*t]. After that arrival
    time, return the narrow barometric equilibrium.
    """
    first_edge = min(min_resolvable_dz_m, h)
    if v_sed > 0.0 and t_total < h / v_sed:
        front = h - v_sed * t_total
        raw_edges = [0.0, min(first_edge, front), front, h]
        edges = np.array(sorted({edge for edge in raw_edges if 0.0 <= edge <= h}), dtype=np.float64)
        if edges.size < 2:
            edges = np.array([0.0, h], dtype=np.float64)
        widths = np.diff(edges)
        z = 0.5 * (edges[:-1] + edges[1:])
        concentration = np.zeros_like(z)
        bottom_mass = v_sed * t_total / h
        if bottom_mass > 0.0:
            concentration[0] += bottom_mass / widths[0]
        for idx, (left, right) in enumerate(zip(edges[:-1], edges[1:], strict=True)):
            overlap = max(0.0, min(float(right), front) - float(left))
            concentration[idx] += overlap / (h * widths[idx])
        mean = front**2 / (2.0 * h)
        second_moment = front**3 / (3.0 * h)
        variance = max(0.0, second_moment - mean**2)
        method = "asymptotic-sedimentation-transient"
    else:
        if first_edge == h:
            edges = np.array([0.0, h], dtype=np.float64)
        else:
            edges = np.array([0.0, first_edge, h], dtype=np.float64)
        widths = np.diff(edges)
        z = 0.5 * (edges[:-1] + edges[1:])
        concentration = np.zeros_like(z)
        concentration[0] = 1.0 / widths[0]
        mean = barometric_mean_height(h, ell_g)
        variance = ell_g**2
        method = "asymptotic-sedimentation"

    return FokkerPlanckResult(
        z=z,
        cell_edges=edges,
        cell_widths=widths,
        concentration=concentration,
        t_total=t_total,
        v_sed=v_sed,
        diffusivity=diff,
        h=h,
        method=method,
        pe_global=h / ell_g if ell_g > 0.0 else math.inf,
        used_asymptotic_fallback=True,
        fallback_reason=reason,
        mean_override_m=mean,
        variance_override_m2=variance,
    )


def solve(
    *,
    v_sed: float,
    diff: float,
    h: float,
    t_total: float,
    n_cells: int = DEFAULT_N_CELLS,
    min_resolvable_dz_m: float = MIN_RESOLVABLE_DZ_M,
    initial: str = "uniform",
    allow_asymptotic: bool = True,
) -> FokkerPlanckResult:
    """Solve the Method-C PDE for a `(v_sed, D, h, t_total)` cell."""
    if v_sed < 0.0 or diff < 0.0:
        raise ValueError("v_sed and diff must be non-negative.")
    if h <= 0.0:
        raise ValueError("h must be positive.")
    if t_total < 0.0:
        raise ValueError("t_total must be non-negative.")
    if initial != "uniform":
        raise ValueError("Only the canonical uniform initial condition is implemented.")

    ell_g = diff / v_sed if v_sed > 0.0 and diff > 0.0 else math.inf
    pe_global = h / ell_g if math.isfinite(ell_g) else 0.0
    edges, unresolved, reason = make_mesh(
        h,
        ell_g=ell_g if math.isfinite(ell_g) else None,
        n_cells=n_cells,
        min_resolvable_dz_m=min_resolvable_dz_m,
    )

    if unresolved:
        if not allow_asymptotic:
            raise ValueError(reason or "Method-C mesh unresolved.")
        return _asymptotic_result(
            h=h,
            t_total=t_total,
            v_sed=v_sed,
            diff=diff,
            ell_g=ell_g,
            reason=reason or "unresolved high-Pe boundary layer",
            min_resolvable_dz_m=min_resolvable_dz_m,
        )

    widths = np.diff(edges)
    z = 0.5 * (edges[:-1] + edges[1:])
    c0 = np.full(widths.size, 1.0 / h, dtype=np.float64)

    if t_total == 0.0:
        concentration = c0
    elif diff == 0.0:
        return _asymptotic_result(
            h=h,
            t_total=t_total,
            v_sed=v_sed,
            diff=diff,
            ell_g=min_resolvable_dz_m,
            reason="pure sedimentation is represented by the asymptotic fallback",
            min_resolvable_dz_m=min_resolvable_dz_m,
        )
    else:
        operator = build_operator(edges, diff=diff, v_sed=v_sed)
        concentration = expm_multiply(operator * t_total, c0)
        concentration = _normalise_density(concentration, widths)

    return FokkerPlanckResult(
        z=z,
        cell_edges=edges,
        cell_widths=widths,
        concentration=concentration,
        t_total=t_total,
        v_sed=v_sed,
        diffusivity=diff,
        h=h,
        method="scharfetter-gummel-fv",
        pe_global=pe_global,
    )


def solve_cell(
    radius_m: float | ParticleGeometry,
    temperature_kelvin: float,
    sample_depth_m: float,
    t_total: float,
    *,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
    lambda_se: float = 1.0,
    **kwargs,
) -> FokkerPlanckResult:
    """Convenience wrapper: derive `(v_sed, D)` from a physical cell and solve."""
    geom = as_particle_geometry(radius_m)
    v = settling_velocity_geom(geom, temperature_kelvin, rho_particle_kg_per_m3)
    d = diffusivity_geom(geom, temperature_kelvin, lambda_se=lambda_se)
    return solve(v_sed=v, diff=d, h=sample_depth_m, t_total=t_total, **kwargs)


def equilibrium_cell(
    radius_m: float | ParticleGeometry,
    temperature_kelvin: float,
    sample_depth_m: float,
    *,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
    t_factor: float = 50.0,
    **kwargs,
) -> FokkerPlanckResult:
    """Return a long-time Method-C approximation to the barometric equilibrium."""
    geom = as_particle_geometry(radius_m)
    ell_g = scale_height_geom(geom, temperature_kelvin, rho_particle_kg_per_m3)
    d = diffusivity_geom(geom, temperature_kelvin)
    v = settling_velocity_geom(geom, temperature_kelvin, rho_particle_kg_per_m3)
    t_relax = min(sample_depth_m, ell_g) ** 2 / d
    t_equilibrium = t_factor * t_relax
    if v > 0.0:
        t_equilibrium = max(t_equilibrium, 1.01 * sample_depth_m / v)
    return solve_cell(
        geom,
        temperature_kelvin,
        sample_depth_m,
        t_total=t_equilibrium,
        rho_particle_kg_per_m3=rho_particle_kg_per_m3,
        **kwargs,
    )
