"""SI constants, water properties, and shared physical primitives.

Spec: breakout-note §3 (Physical model) and §4.4 (Einstein–Smoluchowski check).

Provides:

- Physical constants (CODATA 2019; SI).
- T-dependent water density (Tanaka 2001) and dynamic viscosity
  (IAPWS-derived Vogel form, after Korson 1969).
- Stokes drag γ, Stokes–Einstein diffusivity D, and buoyancy-corrected
  mass m_eff as scalar primitives shared across Methods A/B/C, with
  explicit `ParticleGeometry` variants for the v0.2 material/hydrodynamic
  radius split.

Functions are scalar in the input temperature and radius/geometry.
Vectorisation is deferred to the call sites that actually need it
(Method B trajectory arrays, Method C grids).

References
----------
Tanaka, M., Girard, G., Davis, R., Peuto, A., Bignell, N. (2001).
"Recommended table for the density of water between 0 °C and 40 °C
based on recent experimental reports", Metrologia 38, 301–309.

International Association for the Properties of Water and Steam (2008).
"IAPWS R12-08, Release on the IAPWS Formulation 2008 for the Viscosity
of Ordinary Water Substance". Compact Vogel form used here is consistent
with Korson, L., Drost-Hansen, W., Millero, F.J. (1969). "Viscosity of
water at various temperatures", J. Phys. Chem. 73, 34–39.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

# ---------------------------------------------------------------------------
# Physical constants (CODATA 2019, SI)
# ---------------------------------------------------------------------------

K_B: float = 1.380_649e-23
"""Boltzmann constant, J/K (exact, CODATA 2019)."""

G: float = 9.806_65
"""Standard gravity, m/s² (BIPM convention)."""

# ---------------------------------------------------------------------------
# Material parameters
# ---------------------------------------------------------------------------

RHO_P_DIAMOND: float = 3510.0
"""Bulk-diamond density, kg/m³ (breakout-note §3, §7g caveat for HPHT FNDs)."""


@dataclass(frozen=True)
class DeltaShellCalibration:
    """Citation-anchored default for one nominal FND surface class."""

    key: str
    label: str
    delta_shell_m: float
    range_m: tuple[float, float]
    status: str
    source: str


@dataclass(frozen=True)
class ParticleGeometry:
    """Material and hydrodynamic radii for one particle preparation.

    ``r_material_m`` sets buoyant mass. ``r_hydro_m`` sets Stokes drag
    and Stokes-Einstein diffusivity. The zero-shell default preserves
    the v0.1 single-radius interpretation.
    """

    r_material_m: float
    delta_shell_m: float = 0.0

    def __post_init__(self) -> None:
        if self.r_material_m <= 0.0:
            raise ValueError("r_material_m must be positive.")
        if self.delta_shell_m < 0.0:
            raise ValueError("delta_shell_m must be non-negative.")

    @property
    def r_hydro_m(self) -> float:
        return self.r_material_m + self.delta_shell_m

    @property
    def radius_m(self) -> float:
        """v0.2 compatibility alias for the material radius."""
        return self.r_material_m

    @classmethod
    def from_radius(cls, radius_m: float) -> ParticleGeometry:
        """Construct the v0.1-compatible zero-shell geometry."""
        return cls(r_material_m=radius_m, delta_shell_m=0.0)

    @classmethod
    def from_fnd_class(
        cls,
        r_material_m: float,
        fnd_class: str,
        *,
        delta_shell_m: float | None = None,
    ) -> ParticleGeometry:
        """Construct a geometry using the Phase-27 FND-class shell default.

        Passing ``delta_shell_m`` explicitly keeps the user-supplied knob
        authoritative.  Omitting it applies the citation-anchored default for
        the nominal FND class.
        """
        shell_m = (
            delta_shell_for_fnd_class(fnd_class)
            if delta_shell_m is None
            else delta_shell_m
        )
        return cls(r_material_m=r_material_m, delta_shell_m=shell_m)


DELTA_SHELL_CALIBRATIONS: Final[dict[str, DeltaShellCalibration]] = {
    "bare": DeltaShellCalibration(
        key="bare",
        label="Bare / oxidised HPHT FND",
        delta_shell_m=0.0,
        range_m=(0.0, 5e-9),
        status="open-literature default; campaign-unverified",
        source="Adamas FND product data + HPHT ND DLS survey",
    ),
    "carboxylated": DeltaShellCalibration(
        key="carboxylated",
        label="Carboxylated FND",
        delta_shell_m=5e-9,
        range_m=(0.0, 10e-9),
        status="open-literature default; aggregation-sensitive",
        source="FND-COOH DLS / zeta-potential studies",
    ),
    "hydroxylated": DeltaShellCalibration(
        key="hydroxylated",
        label="Hydroxylated / hydrogen-terminated HPHT FND",
        delta_shell_m=0.0,
        range_m=(0.0, 5e-9),
        status="open-literature default; sparse direct data",
        source="hydrogen/hydroxyl HPHT ND DLS survey",
    ),
    "peg_functionalised": DeltaShellCalibration(
        key="peg_functionalised",
        label="PEG-functionalised FND",
        delta_shell_m=7e-9,
        range_m=(5e-9, 10e-9),
        status="open-literature default for dispersed aqueous PEG-FND",
        source="PEG22 FND DLS increment + ND-PEG stability data",
    ),
}
"""Phase-27 calibrated ``delta_shell_m`` defaults by nominal FND class."""

FND_CLASS_ALIASES: Final[dict[str, str]] = {
    "bare": "bare",
    "oxidised": "bare",
    "oxidized": "bare",
    "unmodified": "bare",
    "carboxylated": "carboxylated",
    "carboxylate": "carboxylated",
    "cooh": "carboxylated",
    "hydroxylated": "hydroxylated",
    "hydroxyl": "hydroxylated",
    "oh": "hydroxylated",
    "hydrogenated": "hydroxylated",
    "peg": "peg_functionalised",
    "pegylated": "peg_functionalised",
    "peg_functionalised": "peg_functionalised",
    "peg_functionalized": "peg_functionalised",
}
"""Accepted aliases for the four Phase-27 FND-class defaults."""


def _normalise_fnd_class(fnd_class: str) -> str:
    return fnd_class.strip().lower().replace("-", "_").replace(" ", "_")


def canonical_fnd_class(fnd_class: str) -> str:
    """Return the canonical key for a nominal FND surface class."""
    key = _normalise_fnd_class(fnd_class)
    try:
        return FND_CLASS_ALIASES[key]
    except KeyError as exc:
        valid = ", ".join(DELTA_SHELL_CALIBRATIONS)
        raise ValueError(
            f"Unknown FND class {fnd_class!r}; expected one of {valid}."
        ) from exc


def delta_shell_calibration_for_fnd_class(fnd_class: str) -> DeltaShellCalibration:
    """Return the Phase-27 calibration record for a nominal FND class."""
    return DELTA_SHELL_CALIBRATIONS[canonical_fnd_class(fnd_class)]


def delta_shell_for_fnd_class(fnd_class: str) -> float:
    """Return the calibrated default ``delta_shell_m`` for an FND class."""
    return delta_shell_calibration_for_fnd_class(fnd_class).delta_shell_m


def as_particle_geometry(radius_or_geom: float | ParticleGeometry) -> ParticleGeometry:
    """Coerce scalar-radius inputs to the v0.1-compatible geometry object."""
    if isinstance(radius_or_geom, ParticleGeometry):
        return radius_or_geom
    return ParticleGeometry.from_radius(radius_or_geom)

# ---------------------------------------------------------------------------
# Validity ranges
# ---------------------------------------------------------------------------

T_DENSITY_MIN_K: float = 273.15
T_DENSITY_MAX_K: float = 313.15
"""Tanaka (2001) is calibrated for 0 °C ≤ T ≤ 40 °C."""

T_VISCOSITY_MIN_K: float = 273.15
T_VISCOSITY_MAX_K: float = 373.15
"""Vogel form remains within ~1 % of IAPWS R12-08 across the liquid range."""


# ---------------------------------------------------------------------------
# Water properties
# ---------------------------------------------------------------------------


def rho_water(temperature_kelvin: float) -> float:
    """Water density ρ(T) at 1 atm, in kg/m³.

    Tanaka et al. (2001), Metrologia 38, 301, Eq. (1). Quoted accuracy
    ~1 ppm over 0 °C – 40 °C, traceable to IPTS-90.

    Raises
    ------
    ValueError
        If the temperature is outside the Tanaka calibration range
        [273.15 K, 313.15 K].
    """
    if not (T_DENSITY_MIN_K <= temperature_kelvin <= T_DENSITY_MAX_K):
        raise ValueError(
            f"Temperature {temperature_kelvin} K outside the Tanaka (2001) "
            f"calibration range [{T_DENSITY_MIN_K}, {T_DENSITY_MAX_K}] K."
        )
    t_c = temperature_kelvin - 273.15
    a1 = -3.983_035
    a2 = 301.797
    a3 = 522_528.9
    a4 = 69.348_81
    a5 = 999.974_950
    return a5 * (1.0 - (t_c + a1) ** 2 * (t_c + a2) / (a3 * (t_c + a4)))


def eta_water(temperature_kelvin: float) -> float:
    """Water dynamic viscosity η(T) at 1 atm, in Pa·s.

    Compact Vogel form η(T) = A · 10^(B / (T − C)) with
    A = 2.414·10⁻⁵ Pa·s, B = 247.8 K, C = 140 K. Within ~1 % of IAPWS
    R12-08 over the full liquid range, well below the 5 % regime-map
    threshold (breakout-note §5.1).

    Raises
    ------
    ValueError
        If the temperature is outside [273.15 K, 373.15 K].
    """
    if not (T_VISCOSITY_MIN_K <= temperature_kelvin <= T_VISCOSITY_MAX_K):
        raise ValueError(
            f"Temperature {temperature_kelvin} K outside the liquid-water "
            f"range [{T_VISCOSITY_MIN_K}, {T_VISCOSITY_MAX_K}] K."
        )
    a = 2.414e-5
    b = 247.8
    c = 140.0
    return a * 10.0 ** (b / (temperature_kelvin - c))


# ---------------------------------------------------------------------------
# Shared physical primitives
# ---------------------------------------------------------------------------


def gamma_stokes_geom(geom: ParticleGeometry, temperature_kelvin: float) -> float:
    """Stokes drag coefficient γ = 6 π η(T) r_hydro, in N·s/m.

    Low-Reynolds-number, no-slip sphere. Breakout-note §3, §11 (Lock 1).
    """
    return 6.0 * math.pi * eta_water(temperature_kelvin) * geom.r_hydro_m


def gamma_stokes(
    radius_or_geom: float | ParticleGeometry,
    temperature_kelvin: float,
) -> float:
    """Stokes drag wrapper accepting a scalar radius or `ParticleGeometry`."""
    return gamma_stokes_geom(as_particle_geometry(radius_or_geom), temperature_kelvin)


def diffusivity_geom(
    geom: ParticleGeometry,
    temperature_kelvin: float,
    *,
    lambda_se: float = 1.0,
) -> float:
    """Stokes–Einstein diffusivity D = λ · k_B T / γ, in m²/s.

    Breakout-note §3, §11 (Lock 2). The Einstein–Smoluchowski relation
    D · γ = λ · k_B T must hold to machine precision; this is the test in
    `tests/test_einstein_relation.py`.

    ``lambda_se`` is the Stokes–Einstein breakdown coefficient.
    ``lambda_se = 1.0`` reproduces the bare continuum SE relation
    (v0.2 behaviour). ``lambda_se < 1.0`` reduces the effective
    diffusivity, modelling sub-continuum breakdown at sub-150-nm
    radii. The parameter is deliberately dimensionless and
    phenomenological — calibration against the Laloyaux z₂ gold-
    nanoparticle benchmark is a Phase-18 follow-up.
    """
    return lambda_se * K_B * temperature_kelvin / gamma_stokes_geom(geom, temperature_kelvin)


def diffusivity(
    radius_or_geom: float | ParticleGeometry,
    temperature_kelvin: float,
    *,
    lambda_se: float = 1.0,
) -> float:
    """Diffusivity wrapper accepting a scalar radius or `ParticleGeometry`."""
    return diffusivity_geom(
        as_particle_geometry(radius_or_geom), temperature_kelvin, lambda_se=lambda_se
    )


def buoyant_mass_geom(
    geom: ParticleGeometry,
    temperature_kelvin: float,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
) -> float:
    """Buoyancy-corrected mass m_eff = (4/3) π r_material³ (ρ_p − ρ_f), in kg.

    Breakout-note §3. The particle radius r used here is the *material*
    radius r_c (breakout-note §7h); for r ≲ 20 nm, r_c may differ from
    the hydrodynamic radius r_H used in `gamma_stokes` and `diffusivity`.
    """
    delta_rho = rho_particle_kg_per_m3 - rho_water(temperature_kelvin)
    return (4.0 / 3.0) * math.pi * geom.r_material_m**3 * delta_rho


def buoyant_mass(
    radius_or_geom: float | ParticleGeometry,
    temperature_kelvin: float,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
) -> float:
    """Buoyant-mass wrapper accepting a scalar radius or `ParticleGeometry`."""
    return buoyant_mass_geom(
        as_particle_geometry(radius_or_geom),
        temperature_kelvin,
        rho_particle_kg_per_m3,
    )
