"""Phase 12 — hydrodynamic-vs-material radius data model."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from analytical import (
    barometric_profile_geom,
    cell_summary_geom,
    equilibration_time_geom,
    scale_height_geom,
    settling_velocity_geom,
)
from fokker_planck import solve_cell
from langevin import simulate_cell
from parameters import (
    DELTA_SHELL_CALIBRATIONS,
    ParticleGeometry,
    buoyant_mass_geom,
    canonical_fnd_class,
    delta_shell_calibration_for_fnd_class,
    delta_shell_for_fnd_class,
    diffusivity_geom,
    gamma_stokes_geom,
)
from regime_map import classify_cell, results_from_csv, results_to_csv

_R_MATERIAL = 1e-7
_T = 298.15
_H = 1e-3


def test_default_geometry_reproduces_single_radius() -> None:
    geom = ParticleGeometry(r_material_m=1e-7)

    assert geom.r_material_m == 1e-7
    assert geom.delta_shell_m == 0.0
    assert geom.r_hydro_m == 1e-7
    assert geom.radius_m == geom.r_material_m


def test_from_radius_is_v01_compatibility_constructor() -> None:
    geom = ParticleGeometry.from_radius(5e-9)

    assert geom == ParticleGeometry(r_material_m=5e-9, delta_shell_m=0.0)


def test_delta_shell_calibrations_cover_v04_fnd_classes() -> None:
    assert set(DELTA_SHELL_CALIBRATIONS) == {
        "bare",
        "carboxylated",
        "hydroxylated",
        "peg_functionalised",
    }
    for key, calibration in DELTA_SHELL_CALIBRATIONS.items():
        assert calibration.key == key
        assert calibration.range_m[0] <= calibration.delta_shell_m <= calibration.range_m[1]
        assert calibration.status
        assert calibration.source


@pytest.mark.parametrize(
    "alias, canonical",
    [
        ("bare", "bare"),
        ("oxidized", "bare"),
        ("COOH", "carboxylated"),
        ("hydroxylated", "hydroxylated"),
        ("PEG-functionalized", "peg_functionalised"),
    ],
)
def test_fnd_class_aliases_resolve(alias: str, canonical: str) -> None:
    assert canonical_fnd_class(alias) == canonical
    assert delta_shell_calibration_for_fnd_class(alias).key == canonical


@pytest.mark.parametrize(
    "fnd_class, expected_delta_shell_m",
    [
        ("bare", 0.0),
        ("carboxylated", 5e-9),
        ("hydroxylated", 0.0),
        ("peg_functionalised", 7e-9),
    ],
)
def test_particle_geometry_from_fnd_class_uses_calibrated_default(
    fnd_class: str,
    expected_delta_shell_m: float,
) -> None:
    geom = ParticleGeometry.from_fnd_class(50e-9, fnd_class)

    assert geom.r_material_m == 50e-9
    assert geom.delta_shell_m == expected_delta_shell_m
    assert geom.r_hydro_m == 50e-9 + expected_delta_shell_m
    assert delta_shell_for_fnd_class(fnd_class) == expected_delta_shell_m


def test_user_supplied_delta_shell_overrides_fnd_class_default() -> None:
    geom = ParticleGeometry.from_fnd_class(
        50e-9,
        "peg_functionalised",
        delta_shell_m=0.0,
    )

    assert geom == ParticleGeometry(r_material_m=50e-9, delta_shell_m=0.0)


def test_unknown_fnd_class_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown FND class"):
        ParticleGeometry.from_fnd_class(50e-9, "partially fluorinated")


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


def test_delta_shell_doubles_drag_when_equal_to_material_radius() -> None:
    base = ParticleGeometry(r_material_m=_R_MATERIAL)
    shell = ParticleGeometry(r_material_m=_R_MATERIAL, delta_shell_m=_R_MATERIAL)

    assert math.isclose(
        gamma_stokes_geom(shell, _T) / gamma_stokes_geom(base, _T),
        2.0,
        rel_tol=1e-15,
    )
    assert math.isclose(
        diffusivity_geom(shell, _T) / diffusivity_geom(base, _T),
        0.5,
        rel_tol=1e-15,
    )
    assert math.isclose(
        settling_velocity_geom(shell, _T) / settling_velocity_geom(base, _T),
        0.5,
        rel_tol=1e-15,
    )
    assert scale_height_geom(shell, _T) == scale_height_geom(base, _T)
    assert buoyant_mass_geom(shell, _T) == buoyant_mass_geom(base, _T)


def test_equilibrium_profile_invariant_under_delta_shell() -> None:
    base = ParticleGeometry(r_material_m=_R_MATERIAL)
    shell = ParticleGeometry(r_material_m=_R_MATERIAL, delta_shell_m=10e-9)
    z = np.linspace(0.0, _H, 101)

    assert np.array_equal(
        barometric_profile_geom(z, shell, _T, _H),
        barometric_profile_geom(z, base, _T, _H),
    )


def test_relaxation_time_doubles_when_hydrodynamic_radius_doubles() -> None:
    base = ParticleGeometry(r_material_m=_R_MATERIAL)
    shell = ParticleGeometry(r_material_m=_R_MATERIAL, delta_shell_m=_R_MATERIAL)

    assert math.isclose(
        equilibration_time_geom(shell, _T, _H) / equilibration_time_geom(base, _T, _H),
        2.0,
        rel_tol=1e-15,
    )


def test_cell_summary_reports_explicit_radii_and_consistent_channels() -> None:
    shell = ParticleGeometry(r_material_m=_R_MATERIAL, delta_shell_m=10e-9)

    summary = cell_summary_geom(shell, _T, _H)

    assert summary["r_m"] == shell.r_material_m
    assert summary["r_material_m"] == shell.r_material_m
    assert summary["r_hydro_m"] == shell.r_hydro_m
    assert summary["delta_shell_m"] == shell.delta_shell_m
    assert summary["m_eff_kg"] == buoyant_mass_geom(shell, _T)
    assert summary["gamma_N_s_per_m"] == gamma_stokes_geom(shell, _T)
    assert summary["D_m2_per_s"] == diffusivity_geom(shell, _T)
    assert summary["ell_g_m"] == scale_height_geom(shell, _T)


def test_method_b_c_wrappers_accept_geometry_and_use_hydrodynamic_radius() -> None:
    shell = ParticleGeometry(r_material_m=_R_MATERIAL, delta_shell_m=10e-9)

    method_b = simulate_cell(
        shell,
        _T,
        _H,
        t_total=0.01,
        n_trajectories=5,
        dt=0.01,
        seed=0,
    )
    method_c = solve_cell(shell, _T, _H, t_total=0.01, n_cells=20)

    assert method_b.v_sed == settling_velocity_geom(shell, _T)
    assert method_b.diffusivity == diffusivity_geom(shell, _T)
    assert method_c.v_sed == settling_velocity_geom(shell, _T)
    assert method_c.diffusivity == diffusivity_geom(shell, _T)


def test_classify_cell_accepts_geometry_and_records_shell() -> None:
    shell = ParticleGeometry(r_material_m=5e-9, delta_shell_m=1e-9)

    result = classify_cell(shell, _T, 1e-4, t_obs_s=3600.0)

    assert result.r_material_m == shell.r_material_m
    assert result.r_hydro_m == shell.r_hydro_m
    assert result.delta_shell_m == shell.delta_shell_m
    assert result.radius_m == shell.r_material_m


def test_regime_result_carries_both_radii_through_csv(tmp_path: Path) -> None:
    shell = ParticleGeometry(r_material_m=5e-9, delta_shell_m=1e-9)
    original = classify_cell(shell, _T, 1e-4, t_obs_s=3600.0)
    path = tmp_path / "radius_split.csv"

    results_to_csv([original], path)
    restored = results_from_csv(path)

    assert "r_material_m,r_hydro_m,delta_shell_m" in path.read_text().splitlines()[0]
    assert len(restored) == 1
    assert restored[0].r_material_m == original.r_material_m
    assert restored[0].r_hydro_m == original.r_hydro_m
    assert restored[0].delta_shell_m == original.delta_shell_m
    assert restored[0].r_material_m != restored[0].r_hydro_m
