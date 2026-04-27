"""Method A — closed-form equilibrium quantities and characteristic timescales.

Spec: breakout-note §4.1 Method A.

Per (r, T, h) cell delivers:

- ℓ_g  = k_B T / (m_eff g)              gravitational scale height
- v_sed = m_eff g / γ                    settling velocity
- D    = k_B T / γ                       Stokes-Einstein diffusivity
- t_eq ~ min(h, ℓ_g)² / D                order-of-magnitude relaxation time
- t_settle ~ h / v_sed                   experimentally meaningful sedimentation time

t_eq is a scaling estimate, **not** a spectral-gap relaxation time. For
strongly-sedimenting cells, t_settle is the operative timescale (breakout
§4.1 Method A, round-3 follow-up).

Stub only — no functions implemented yet.
"""

from __future__ import annotations
