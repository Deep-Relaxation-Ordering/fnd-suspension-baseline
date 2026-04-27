"""Method C — Smoluchowski (overdamped Fokker–Planck) PDE.

Spec: breakout-note §4.1 Method C.

Solves the 1D Smoluchowski equation on z ∈ [0, h] with no-flux boundaries.

High-Pe regime is non-trivial (round-4 fix): equilibrium boundary layer
narrows to ~ ℓ_g, which can be sub-nanometric, far below any uniform mesh.
The implementation uses:

1. Scharfetter–Gummel exponential-fitting finite-volume discretisation,
   reducing to upwind in the high-Pe limit and central in the low-Pe limit.
2. Non-uniform mesh, geometrically refined toward z = 0, with finest
   spacing ≤ ℓ_g / 5.
3. Asymptotic-sedimentation fallback: when ℓ_g drops below the smallest
   representable mesh spacing, the equilibrium is replaced analytically by
   δ(z = 0) plus an exponential approach.

Cross-validates Method B within Method B's feasibility envelope; serves as
the primary engine for time-dependent profiles across the full t_obs grid.

Stub only — no functions implemented yet.
"""

from __future__ import annotations
