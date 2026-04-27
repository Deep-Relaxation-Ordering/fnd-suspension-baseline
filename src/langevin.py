"""Method B — stochastic Langevin ensemble.

Spec: breakout-note §4.1 Method B.

Vectorised Euler–Maruyama integration of the overdamped Langevin equation::

    dz/dt = -v_sed + sqrt(2 D) ξ(t)

on z ∈ [0, h] with reflecting boundaries, for N = 1e4–1e5 trajectories.

Adaptive timestep (round-2 fix)::

    dt = min(α · ℓ_g / v_sed, β · ℓ_g² / D)        with α, β ~ 1e-2

falling back to ``β · h² / D`` in the diffusion-dominated regime where
ℓ_g ≫ h.

Feasibility envelope (round-3 fix): for r ≳ 1 µm, ℓ_g becomes
sub-nanometric and dt prohibitive. Cells outside the envelope are tagged
"Method B not run" and handled by Methods A and C instead.

Stub only — no functions implemented yet.
"""

from __future__ import annotations
