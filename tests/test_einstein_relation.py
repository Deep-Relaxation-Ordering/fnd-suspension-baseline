"""Einstein–Smoluchowski relation: D · γ = k_B · T to machine precision.

Spec: breakout-note §4.4 validation strategy, fifth bullet.
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Awaiting analytical.py implementation.")
def test_einstein_smoluchowski_machine_precision() -> None:
    pass
