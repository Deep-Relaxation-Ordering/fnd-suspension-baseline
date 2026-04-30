"""Stokes–Einstein correction side-computation (Phase 18 — S2).

Provides λ-corrected regime classification as a post-processing layer
on top of the §5 cache, following the polydispersity precedent.

The §5 cache itself remains at λ = 1.0 (bare Stokes–Einstein).  This
module lets a caller re-classify cells with a different breakdown
coefficient and compare the resulting labels against the cached
baseline.

Spec: work-plan-v0-3 §1 item K; ADR 0002 §"API surface — the
provisional=True contract".
"""

from __future__ import annotations

from typing import Final

from regime_map import RegimeResult, classify_cell

# ---------------------------------------------------------------------------
# Axis and constants
# ---------------------------------------------------------------------------

LAMBDA_SE_AXIS: Final[tuple[float, ...]] = (0.1, 0.5, 1.0)
"""Sweep values for the SE breakdown coefficient.

λ = 1.0  → bare continuum Stokes–Einstein (v0.2 behaviour).
λ < 1.0  → reduced effective diffusivity, modelling sub-continuum
            breakdown at sub-150-nm radii.
"""

SUB_150_NM_THRESHOLD_M: Final[float] = 1.5e-7
"""Upper bound of the sub-150-nm band where SE corrections matter."""

# ---------------------------------------------------------------------------
# Core wrapper
# ---------------------------------------------------------------------------


def classify_cell_lambda(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    t_obs_s: float,
    *,
    lambda_se: float = 1.0,
    **kwargs,
) -> tuple[RegimeResult, bool]:
    """Classify a cell with λ-corrected diffusivity.

    Returns the ``RegimeResult`` and a ``provisional`` flag.  The flag
    is ``True`` whenever ``lambda_se != 1.0``, signalling that S1
    (aggregation pre-screen) has not yet landed and the radius may not
    be trustworthy on the timescale of the observation.

    Per ADR 0002, downstream design-tool entry points must refuse
    ``provisional=True`` results unless the caller passes an explicit
    ``accept_provisional=True`` override.
    """
    result = classify_cell(
        radius_m,
        temperature_kelvin,
        sample_depth_m,
        t_obs_s,
        lambda_se=lambda_se,
        **kwargs,
    )
    provisional = lambda_se != 1.0
    return result, provisional


# ---------------------------------------------------------------------------
# Audit helpers
# ---------------------------------------------------------------------------


def count_label_flips(
    baseline: RegimeResult,
    corrected: RegimeResult,
) -> bool:
    """Return True if the regime label differs between baseline and corrected."""
    return baseline.regime != corrected.regime


def audit_lambda_impact(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    t_obs_s: float,
    *,
    lambda_axis: tuple[float, ...] = LAMBDA_SE_AXIS,
    **kwargs,
) -> dict[float, RegimeResult]:
    """Re-classify one cell at every λ in ``lambda_axis``.

    Returns a mapping ``λ → RegimeResult`` for direct comparison.
    The caller can use ``count_label_flips`` to detect changes.
    """
    return {
        lambda_se: classify_cell(
            radius_m,
            temperature_kelvin,
            sample_depth_m,
            t_obs_s,
            lambda_se=lambda_se,
            **kwargs,
        )
        for lambda_se in lambda_axis
    }
