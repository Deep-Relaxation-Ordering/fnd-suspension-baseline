"""Method B — stochastic Langevin ensemble.

Spec: breakout-note §4.1 Method B.

Vectorised Euler–Maruyama integration of the overdamped Langevin equation::

    dz/dt = -v_sed + sqrt(2 D) ξ(t)

on z ∈ [0, h] with reflecting boundaries, for ensembles of N trajectories.

Adaptive timestep (round-2 fix)::

    dt = min(α · ℓ_g / v_sed, β · ℓ_g² / D)        with α, β ~ 1e-2

falling back to ``β · h² / D`` in the diffusion-dominated regime where
ℓ_g ≫ h. ℓ_g and v_sed are taken from `parameters.diffusivity` /
`analytical.settling_velocity`; the kernel here works on the
already-evaluated (v_sed, D, h) triple so the same simulator can drive
the test cases (`v_sed = 0` for pure Brownian, `D = 0` for pure
sedimentation) without juggling fictitious physical cells.

Feasibility envelope (round-3 fix): for r ≳ 1 µm, ℓ_g becomes
sub-nanometric and the timestep prohibitive. `is_feasible` is the
explicit check; cells outside the envelope are tagged "Method B not
run" and handled by Methods A and C instead.

Boundary handling: a single ``np.mod`` + ``np.where`` fold reflects
arbitrary multi-bounce excursions onto [0, h] in one shot — see
`_reflect_into_box` for the derivation. With reflecting walls the
overdamped equilibrium reduces to the Method A barometric profile (or
to uniform-on-[0,h] when ℓ_g ≫ h); both limits are pinned by the
validation tests in `tests/test_equilibrium.py` and
`tests/test_method_consistency.py`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import NamedTuple

import numpy as np
from numpy.typing import ArrayLike, NDArray

from analytical import settling_velocity
from parameters import RHO_P_DIAMOND, diffusivity

# ---------------------------------------------------------------------------
# Defaults — α and β are the round-2 timestep coefficients.
# ---------------------------------------------------------------------------

ALPHA: float = 1e-2
"""Drift-resolution coefficient: dt_drift = α · length / v_sed."""

BETA: float = 1e-2
"""Diffusion-resolution coefficient: dt_diff = β · length² / D."""

MAX_STEPS_DEFAULT: int = 5_000_000
"""Feasibility cap. A cell needing more than this many Euler–Maruyama
steps for a given t_total is tagged out-of-envelope; Methods A and C
take over for those cells (round-3 fix)."""


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------


@dataclass
class LangevinResult:
    """Output of one Langevin run.

    `snapshots` and `first_passage_times` are populated only when their
    corresponding kwargs were enabled at the call site. Everything else
    is always present.
    """

    final_z: NDArray[np.float64]
    initial_z: NDArray[np.float64]
    dt: float
    n_steps: int
    t_total: float
    v_sed: float
    diffusivity: float
    h: float
    n_trajectories: int
    bounded: bool
    snapshots: NDArray[np.float64] | None = None
    snapshot_times: NDArray[np.float64] | None = None
    first_passage_times: NDArray[np.float64] | None = None


# ---------------------------------------------------------------------------
# Timestep policy and feasibility envelope
# ---------------------------------------------------------------------------


def adaptive_timestep(
    v_sed: float,
    diff: float,
    h: float,
    *,
    alpha: float = ALPHA,
    beta: float = BETA,
) -> float:
    """Round-2 adaptive timestep, in seconds.

    Special-cases:
    - Pure Brownian (v_sed == 0):     dt = β · h² / D.
    - Pure sedimentation (D == 0):    dt = α · h / v_sed.
    - Diffusion-dominated (ℓ_g > h):  dt = β · h² / D (ℓ_g doesn't constrain).
    - General:                        dt = min(α ℓ_g / v_sed, β ℓ_g² / D).

    Both ``v_sed = 0`` and ``D = 0`` is rejected — there is no
    physical timescale to set dt against.
    """
    if v_sed == 0.0 and diff == 0.0:
        raise ValueError("Both v_sed and D are zero; no timescale.")
    if v_sed == 0.0:
        return beta * h**2 / diff
    if diff == 0.0:
        return alpha * h / v_sed
    ell_g = diff / v_sed
    if ell_g > h:
        return beta * h**2 / diff
    return min(alpha * ell_g / v_sed, beta * ell_g**2 / diff)


class FeasibilityCheck(NamedTuple):
    """Result of `is_feasible`. ``dt_policy`` is the *upper bound* on
    the integrator step from the round-2 policy, used here to count
    steps. The dt that `simulate()` actually integrates with may be
    smaller — when ``t_total < dt_policy`` the auto-dt path collapses
    it to ``t_total / n_steps`` so the run covers exactly the
    requested time. Don't use ``dt_policy`` as a provenance record
    of the simulator's actual step.
    """

    feasible: bool
    n_steps: int
    dt_policy: float


def is_feasible(
    v_sed: float,
    diff: float,
    h: float,
    t_total: float,
    *,
    max_steps: int = MAX_STEPS_DEFAULT,
    alpha: float = ALPHA,
    beta: float = BETA,
) -> FeasibilityCheck:
    """Feasibility envelope (round-3): is the (v_sed, D, h, t_total) cell
    cheap enough to integrate with Method B?

    Returns a `FeasibilityCheck` namedtuple. A cell with
    ``feasible = False`` should be classified by Method A / Method C
    instead. ``dt_policy`` is the round-2 timestep upper bound — see
    its field docstring for why it can differ from the dt
    `simulate()` actually uses.
    """
    dt_policy = adaptive_timestep(v_sed, diff, h, alpha=alpha, beta=beta)
    n_steps = max(1, int(math.ceil(t_total / dt_policy)))
    return FeasibilityCheck(
        feasible=(n_steps <= max_steps),
        n_steps=n_steps,
        dt_policy=dt_policy,
    )


# ---------------------------------------------------------------------------
# Reflecting boundary fold
# ---------------------------------------------------------------------------


def _reflect_into_box(z: NDArray[np.float64], h: float) -> NDArray[np.float64]:
    """Fold an arbitrary z-array back onto [0, h] under reflecting walls.

    The reflection at the bottom (z → −z) and at the top (z → 2h − z)
    composed any number of times equals the triangle-wave
    ``f(z mod 2h)`` with f(x) = x on [0, h] and f(x) = 2h − x on [h, 2h].
    `np.mod` already gives a Python-style nonnegative remainder, so this
    handles overshoots in either direction in two vectorised lines.
    """
    folded = np.mod(z, 2.0 * h)
    return np.where(folded > h, 2.0 * h - folded, folded)


# ---------------------------------------------------------------------------
# Initial conditions
# ---------------------------------------------------------------------------


def _resolve_initial_z(
    z0: ArrayLike | str,
    n_trajectories: int,
    h: float,
    rng: np.random.Generator,
) -> NDArray[np.float64]:
    if isinstance(z0, str):
        if z0 == "uniform":
            return rng.uniform(0.0, h, size=n_trajectories)
        if z0 == "delta_top":
            return np.full(n_trajectories, h, dtype=np.float64)
        if z0 == "delta_bottom":
            return np.zeros(n_trajectories, dtype=np.float64)
        raise ValueError(
            f"Unknown z0 string {z0!r}; expected 'uniform', 'delta_top', or 'delta_bottom'."
        )
    arr = np.asarray(z0, dtype=np.float64)
    if arr.ndim == 0:
        return np.full(n_trajectories, float(arr), dtype=np.float64)
    if arr.shape != (n_trajectories,):
        raise ValueError(
            f"z0 array shape {arr.shape} does not match n_trajectories={n_trajectories}."
        )
    return arr.copy()


# ---------------------------------------------------------------------------
# Core simulator
# ---------------------------------------------------------------------------


def simulate(
    *,
    v_sed: float,
    diff: float,
    h: float,
    t_total: float,
    n_trajectories: int,
    z0: ArrayLike | str = "uniform",
    dt: float | None = None,
    n_snapshots: int = 0,
    track_first_passage_to_bottom: bool = False,
    bounded: bool = True,
    seed: int | None = None,
    max_steps: int = MAX_STEPS_DEFAULT,
    alpha: float = ALPHA,
    beta: float = BETA,
) -> LangevinResult:
    """Vectorised Euler–Maruyama integrator on (v_sed, D, h, t_total).

    Parameters
    ----------
    v_sed, diff, h, t_total
        Cell physics. ``h`` is unused when ``bounded=False`` but is
        still recorded on the result for provenance. ``t_total`` must
        be ≥ 0; ``t_total = 0`` short-circuits to the initial condition.
        When ``dt`` is auto-derived from the policy, ``t_total`` is
        honoured exactly — the policy dt is treated as an upper bound
        and the actual dt is collapsed to ``t_total / n_steps`` so that
        the run covers exactly the requested time.
    n_trajectories
        Ensemble size N.
    z0
        Initial-condition spec. ``'uniform'`` (default) draws
        z₀ ~ U(0, h); ``'delta_top'``/``'delta_bottom'`` start every
        trajectory at z = h / z = 0; an array of length N starts
        trajectories at the supplied positions.
    dt
        Override the adaptive timestep policy. Required when
        ``bounded=False`` (no length scale to derive a default from).
        When set explicitly, ``n_steps = ceil(t_total / dt)`` and
        ``result.t_total`` may exceed the requested ``t_total`` by less
        than one ``dt`` — the auto-derived path is preferred when an
        exact duration matters.
    n_snapshots
        If > 0, store *up to* ``n_snapshots`` snapshots of the
        ensemble across the run, approximately evenly spaced and
        always including the final step. The actual count is
        ``min(n_snapshots, n_steps)`` after deduplicating the integer
        step indices generated by `np.linspace`, so for very short
        runs (n_snapshots ≥ n_steps) the number stored is exactly
        n_steps. For an N = 1e5 ensemble at 1000 steps,
        full-trajectory storage would be ~800 MB, which is why this
        defaults to 0.
    track_first_passage_to_bottom
        When True, each trajectory's first time it reaches z ≤ 0 is
        recorded (NaN for trajectories that never reach the bottom).
        First-passage is detected on the unreflected step, before the
        boundary fold — so a particle that crosses below 0 and bounces
        back still has its arrival recorded.
    bounded
        If False, no boundary fold is applied. Required for
        unbounded-MSD checks. ``dt`` must be set explicitly in this
        case because the adaptive policy uses h as its length scale
        when v_sed = 0.
    seed
        RNG seed (`numpy.random.default_rng`).
    max_steps
        Feasibility cap; raises ``ValueError`` if the run would exceed it.
    """
    if not bounded and dt is None:
        raise ValueError("dt must be supplied explicitly when bounded=False.")

    if t_total < 0.0:
        raise ValueError(f"t_total must be non-negative; got {t_total}.")

    rng = np.random.default_rng(seed)
    z_init = _resolve_initial_z(z0, n_trajectories, h, rng)

    # Zero-time short-circuit: return the initial condition without taking a step.
    # Requested by the t_total-honouring contract — a zero-length run advances
    # nothing rather than rounding up to one full dt.
    if t_total == 0.0:
        return LangevinResult(
            final_z=z_init.copy(),
            initial_z=z_init,
            dt=0.0 if dt is None else dt,
            n_steps=0,
            t_total=0.0,
            v_sed=v_sed,
            diffusivity=diff,
            h=h,
            n_trajectories=n_trajectories,
            bounded=bounded,
            snapshots=None,
            snapshot_times=None,
            first_passage_times=(
                np.full(n_trajectories, np.nan, dtype=np.float64)
                if track_first_passage_to_bottom
                else None
            ),
        )

    # Resolve dt and step count.
    #
    # Auto-dt path: the policy gives an *upper bound* dt_policy. We pick
    # n_steps = ceil(t_total / dt_policy) and then collapse dt = t_total / n_steps
    # so the integration covers exactly the requested t_total. This fixes a
    # bug where short t_obs values were rounded *up* to a full policy step
    # (e.g. requested 1 s in a quiet box where dt_policy ≈ 4080 s ran for
    # 4080 s, reported as result.t_total).
    #
    # Explicit-dt path: user wants tight control of the integrator step;
    # we honour their dt and round n_steps up. result.t_total may then
    # exceed the requested t_total by < dt — flagged in the docstring.
    if dt is None:
        dt_policy = adaptive_timestep(v_sed, diff, h, alpha=alpha, beta=beta)
        n_steps = max(1, int(math.ceil(t_total / dt_policy)))
        dt = t_total / n_steps
    else:
        if dt <= 0.0:
            raise ValueError(f"dt must be positive; got {dt}.")
        n_steps = max(1, int(math.ceil(t_total / dt)))

    if n_steps > max_steps:
        raise ValueError(
            f"Cell out of feasibility envelope: needs {n_steps} steps "
            f"(max {max_steps}). Use Methods A/C for this cell."
        )

    z = z_init.copy()

    sigma = math.sqrt(2.0 * diff * dt) if diff > 0.0 else 0.0

    # Snapshots — integer step indices generated by linspace(1, n_steps,
    # n_snapshots) and deduplicated. Approximately evenly spaced and
    # always including the final step. The previous interval-based logic
    # front-loaded snapshots (e.g. for n_steps=10, n_snapshots=6 it
    # recorded steps 1..6 and missed the back half of the trajectory).
    if n_snapshots > 0:
        snapshot_indices_arr = np.unique(
            np.linspace(1, n_steps, n_snapshots, dtype=np.int64)
        )
        snapshot_indices = snapshot_indices_arr.tolist()
        snapshots = np.empty((len(snapshot_indices), n_trajectories), dtype=np.float64)
        snapshot_times = snapshot_indices_arr.astype(np.float64) * dt
    else:
        snapshot_indices = []
        snapshots = None
        snapshot_times = None

    # First-passage tracking
    if track_first_passage_to_bottom:
        first_passage = np.full(n_trajectories, np.nan, dtype=np.float64)
        not_yet_reached = np.ones(n_trajectories, dtype=bool)
    else:
        first_passage = None
        not_yet_reached = None

    # Main Euler–Maruyama loop
    snapshot_cursor = 0
    for step in range(1, n_steps + 1):
        if sigma > 0.0:
            z = z - v_sed * dt + sigma * rng.standard_normal(n_trajectories)
        else:
            z = z - v_sed * dt

        if track_first_passage_to_bottom:
            crossed = not_yet_reached & (z <= 0.0)
            if crossed.any():
                first_passage[crossed] = step * dt
                not_yet_reached[crossed] = False

        if bounded:
            z = _reflect_into_box(z, h)

        if snapshot_indices and snapshot_cursor < len(snapshot_indices):
            if step == snapshot_indices[snapshot_cursor]:
                snapshots[snapshot_cursor] = z
                snapshot_cursor += 1

    return LangevinResult(
        final_z=z,
        initial_z=z_init,
        dt=dt,
        n_steps=n_steps,
        t_total=n_steps * dt,
        v_sed=v_sed,
        diffusivity=diff,
        h=h,
        n_trajectories=n_trajectories,
        bounded=bounded,
        snapshots=snapshots,
        snapshot_times=snapshot_times,
        first_passage_times=first_passage,
    )


# ---------------------------------------------------------------------------
# Physical-cell convenience wrapper
# ---------------------------------------------------------------------------


def simulate_cell(
    radius_m: float,
    temperature_kelvin: float,
    sample_depth_m: float,
    t_total: float,
    n_trajectories: int,
    *,
    rho_particle_kg_per_m3: float = RHO_P_DIAMOND,
    **kwargs,
) -> LangevinResult:
    """Convenience wrapper: take a (r, T, h) cell, derive (v_sed, D), simulate."""
    v = settling_velocity(radius_m, temperature_kelvin, rho_particle_kg_per_m3)
    d = diffusivity(radius_m, temperature_kelvin)
    return simulate(
        v_sed=v,
        diff=d,
        h=sample_depth_m,
        t_total=t_total,
        n_trajectories=n_trajectories,
        **kwargs,
    )
