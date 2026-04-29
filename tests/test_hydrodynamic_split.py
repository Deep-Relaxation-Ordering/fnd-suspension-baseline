"""Phase 12 — hydrodynamic-vs-material radius data model."""

from __future__ import annotations

import math

import pytest

from parameters import ParticleGeometry


def test_default_geometry_reproduces_single_radius() -> None:
    geom = ParticleGeometry(r_material_m=1e-7)

    assert geom.r_material_m == 1e-7
    assert geom.delta_shell_m == 0.0
    assert geom.r_hydro_m == 1e-7
    assert geom.radius_m == geom.r_material_m


def test_from_radius_is_v01_compatibility_constructor() -> None:
    geom = ParticleGeometry.from_radius(5e-9)

    assert geom == ParticleGeometry(r_material_m=5e-9, delta_shell_m=0.0)


def test_delta_shell_adds_to_hydrodynamic_radius() -> None:
    geom = ParticleGeometry(r_material_m=1e-7, delta_shell_m=1e-8)

    assert math.isclose(geom.r_hydro_m, 1.1e-7, rel_tol=1e-15)


def test_particle_geometry_rejects_invalid_lengths() -> None:
    with pytest.raises(ValueError, match="r_material_m"):
        ParticleGeometry(r_material_m=0.0)
    with pytest.raises(ValueError, match="r_material_m"):
        ParticleGeometry(r_material_m=-1e-9)
    with pytest.raises(ValueError, match="delta_shell_m"):
        ParticleGeometry(r_material_m=1e-7, delta_shell_m=-1e-9)
