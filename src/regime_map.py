"""High-level orchestration — produces deliverables 3 (regime map) and 5 (design table).

Spec: breakout-note §5 (parameter scan), §5.1 (regime classification), §6 (deliverables).

Parameter grid: 30 × 7 × 5 × 6 = 6300 cells of (r, T, h, t_obs). The
radius / temperature / depth axes are owned by `src/scan_grid.py`; do
not restate them here. The t_obs axis lands with Method B / Method C
and will move to `scan_grid` at that point.

Regime classification (initial condition c(z, 0) = 1/h, uniform after mixing):

- **homogeneous**  c(h)/c(0) ≥ 0.95
- **stratified**   0.05 < c(h)/c(0) < 0.95
- **sedimented**   c(h)/c(0) ≤ 0.05  AND  ∫₀^{0.05·h} c dz ≥ 0.95

The fixed-bottom-layer second criterion (round-4 fix) prevents finite-time
profiles where the top has depleted but the bulk mass is still in transit
from being mis-labelled as sedimented.

Stub only — no functions implemented yet.
"""

from __future__ import annotations
