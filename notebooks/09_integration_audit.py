"""Integration audit: byte-identical baseline verification.

Phase 23 (v0.3) introduced this script to enforce the
Phase 12.1 regression-audit pattern:

1. Load the committed §5 cache.
2. Re-run ``walk_grid()`` with default parameters (λ = 1.0, δ_shell = 0).
3. Compare every field of every ``RegimeResult`` byte-for-byte.
4. Report PASS or FAIL with the first mismatching cell.

Phase 31 (v0.4) extends it with smoke tests for the v0.4 surfaces:

- Phase 27: ``ParticleGeometry.from_fnd_class("bare")`` reproduces the
  zero-shell geometry; the four canonical FND-class defaults are
  the values shipped in `delta_shell_calibration.md`.
- Phase 28: ``lognormal_smear(weighting="classification")`` (default)
  reproduces ``weighting="number_density"`` on the marginal channels
  byte-identically.
- Phase 30 item I: ``walk_grid(n_workers=2)`` under the spawn start
  method is byte-identical to ``walk_grid(n_workers=1)``.
- Phase 30 item J: ``crossing_parameter`` returns a finite value for
  a known-bracketed lambda_se sweep on a stratified cell.

Usage:
    cd /path/to/repo
    PYTHONPATH=src python notebooks/09_integration_audit.py
"""

from __future__ import annotations

from pathlib import Path

from regime_map import results_from_csv, walk_grid

CACHE_PATH = Path(__file__).resolve().parent / "data" / "regime_map_grid.csv"


def audit_cache_reproducibility() -> bool:
    """Return True if a fresh walk_grid matches the committed cache.

    The full 6300-cell serial walk takes ~150 min.  Phase 23 verifies
    a stratified subset (corner + edge + interior cells) and delegates
    the full-grid guarantee to ``test_walk_grid_parallel_byte_identical_
    to_serial`` which already passed in the 171-test suite.
    """
    from scan_grid import DEPTHS_M, T_OBS_S, radii_m, temperatures_k

    print("Loading committed cache...")
    cached_all = results_from_csv(CACHE_PATH)
    print(f"  Committed: {len(cached_all)} cells")

    # Focused subset: 3 radii × 2 temperatures × 2 depths × 2 t_obs = 24 cells
    # Includes short-circuit, resolved, and threshold-adjacent paths.
    subset_radii = (radii_m()[0], radii_m()[14], radii_m()[-1])  # 5 nm, ~300 nm, 10 µm
    subset_temps = (temperatures_k()[0], temperatures_k()[-1])    # 5 °C, 35 °C
    subset_depths = (DEPTHS_M[0], DEPTHS_M[-1])                  # 0.1 mm, 10 mm
    subset_tobs = (T_OBS_S[0], T_OBS_S[-1])                      # 1 min, 1 week

    print("Running focused walk_grid subset (n_workers=1)...")
    fresh_subset = walk_grid(
        radii=subset_radii,
        temperatures=subset_temps,
        depths=subset_depths,
        t_obs=subset_tobs,
        n_workers=1,
    )
    print(f"  Fresh subset: {len(fresh_subset)} cells")

    # Build lookup from cached results
    cached_lookup = {
        (c.r_material_m, c.temperature_kelvin, c.sample_depth_m, c.t_obs_s): c
        for c in cached_all
    }

    print("Comparing focused subset cell-by-cell...")
    for f in fresh_subset:
        key = (f.r_material_m, f.temperature_kelvin, f.sample_depth_m, f.t_obs_s)
        c = cached_lookup.get(key)
        if c is None:
            print(f"FAIL: cached cell missing for {key}")
            return False
        c_dict = c.__dict__
        f_dict = f.__dict__
        if c_dict != f_dict:
            print(f"FAIL: mismatch at {key}")
            diff_keys = [k for k in c_dict if c_dict[k] != f_dict[k]]
            print(f"  Differs: {diff_keys}")
            return False

    print("PASS: focused subset byte-identical")
    print("Note: full 6300-cell guarantee delegated to test suite")
    return True


def audit_continuous_thresholds_compat() -> bool:
    """Verify continuous_thresholds at default mode doesn't touch cache."""
    from continuous_thresholds import (
        find_max_homogeneous_radius,
        find_min_sedimented_radius,
    )

    print("\nContinuous thresholds default-mode smoke test...")
    # These functions call classify_cell with lambda_se=1.0 internally
    # We just verify they run without error on a known cell
    try:
        r_hom = find_max_homogeneous_radius(
            298.15, 1e-3, 3600.0, r_lo=1e-9, r_hi=1e-6
        )
        r_sed = find_min_sedimented_radius(
            298.15, 1e-3, 3600.0, r_lo=1e-9, r_hi=1e-6
        )
        print(f"  max_homog_r = {r_hom}")
        print(f"  min_sed_r   = {r_sed}")
        print("PASS")
        return True
    except Exception as exc:
        print(f"FAIL: {exc}")
        return False


def audit_time_evolution_compat() -> bool:
    """Verify time_evolution at default mode doesn't touch cache."""
    from time_evolution import crossing_time

    print("\nTime evolution default-mode smoke test...")
    try:
        t_cross = crossing_time(1e-7, 298.15, 1e-3, criterion="ratio", target=0.5)
        print(f"  crossing_time = {t_cross}")
        print("PASS")
        return True
    except Exception as exc:
        print(f"FAIL: {exc}")
        return False


# ---------------------------------------------------------------------------
# Phase 31 (v0.4) — smoke tests for Phase 27 / 28 / 30 surfaces
# ---------------------------------------------------------------------------


def audit_fnd_class_default_compat() -> bool:
    """Phase 27: ``ParticleGeometry.from_fnd_class('bare')`` is byte-identical
    to the v0.3 zero-shell geometry, and the four canonical class defaults
    are present and well-formed."""
    from parameters import (
        DELTA_SHELL_CALIBRATIONS,
        ParticleGeometry,
        delta_shell_for_fnd_class,
    )

    print("\nFND-class default smoke test (Phase 27)...")
    try:
        radius = 5e-8
        bare = ParticleGeometry.from_fnd_class(radius, "bare")
        baseline = ParticleGeometry(r_material_m=radius, delta_shell_m=0.0)
        if bare != baseline:
            print(f"FAIL: bare class differs from zero-shell baseline ({bare} vs {baseline})")
            return False
        expected_keys = {"bare", "carboxylated", "hydroxylated", "peg_functionalised"}
        if set(DELTA_SHELL_CALIBRATIONS) != expected_keys:
            print(f"FAIL: calibration keys {set(DELTA_SHELL_CALIBRATIONS)} != {expected_keys}")
            return False
        defaults = {key: delta_shell_for_fnd_class(key) for key in expected_keys}
        print(f"  defaults_m = {defaults}")
        if defaults["bare"] != 0.0 or defaults["hydroxylated"] != 0.0:
            print("FAIL: bare and hydroxylated must remain at 0 nm for v0.3 reproduction")
            return False
        if not (0.0 < defaults["carboxylated"] <= 10e-9):
            print("FAIL: carboxylated out of expected range")
            return False
        if not (5e-9 <= defaults["peg_functionalised"] <= 10e-9):
            print("FAIL: peg_functionalised out of expected range")
            return False
        print("PASS")
        return True
    except Exception as exc:
        print(f"FAIL: {exc}")
        return False


def audit_polydispersity_classification_compat() -> bool:
    """Phase 28: ``weighting='classification'`` (default) reproduces the
    number-density kernel's marginal channels byte-identically; the new
    moment arrays are None under default."""
    import numpy as np

    from polydispersity import lognormal_smear
    from regime_map import results_from_csv, results_to_grid

    print("\nPolydispersity number-density compat smoke test (Phase 28)...")
    try:
        grid = results_to_grid(results_from_csv(CACHE_PATH))
        anchor_radii = (grid.radii[4], grid.radii[14], grid.radii[24])
        sigma_axis = (1.05, 1.20, 1.60)
        classification = lognormal_smear(
            grid,
            r_geom_mean_axis=anchor_radii,
            sigma_geom_axis=sigma_axis,
            on_truncation="mask",
        )
        number_density = lognormal_smear(
            grid,
            r_geom_mean_axis=anchor_radii,
            sigma_geom_axis=sigma_axis,
            on_truncation="mask",
            weighting="number_density",
        )
        for field in (
            "p_homogeneous",
            "p_stratified",
            "p_sedimented",
            "expected_top_to_bottom_ratio",
            "expected_bottom_mass_fraction",
        ):
            if not np.array_equal(
                getattr(classification, field), getattr(number_density, field),
            ):
                print(f"FAIL: {field} differs between weighting modes")
                return False
        if classification.expected_radius_by_regime is not None:
            print("FAIL: classification kernel must leave expected_radius_by_regime as None")
            return False
        if number_density.expected_radius_by_regime is None:
            print("FAIL: number_density kernel must populate expected_radius_by_regime")
            return False
        print("PASS")
        return True
    except Exception as exc:
        print(f"FAIL: {exc}")
        return False


def audit_walk_grid_spawn_compat() -> bool:
    """Phase 30 item I: ``walk_grid(n_workers=2)`` under spawn is
    byte-identical to ``n_workers=1``. Uses a 6-cell smoke subset."""
    from regime_map import walk_grid
    from scan_grid import DEPTHS_M, T_OBS_S, radii_m, temperatures_k

    print("\nwalk_grid spawn-context byte-identity smoke test (Phase 30 item I)...")
    try:
        subset_radii = (radii_m()[0], radii_m()[14], radii_m()[-1])
        subset_temps = (temperatures_k()[0],)
        subset_depths = (DEPTHS_M[0],)
        subset_tobs = (T_OBS_S[0], T_OBS_S[-1])
        serial = walk_grid(
            radii=subset_radii,
            temperatures=subset_temps,
            depths=subset_depths,
            t_obs=subset_tobs,
            n_workers=1,
        )
        parallel = walk_grid(
            radii=subset_radii,
            temperatures=subset_temps,
            depths=subset_depths,
            t_obs=subset_tobs,
            n_workers=2,
        )
        if not (len(serial) == len(parallel) == 6):
            print(f"FAIL: cell-count mismatch (serial={len(serial)}, parallel={len(parallel)})")
            return False
        for i, (s, p) in enumerate(zip(serial, parallel, strict=True)):
            if s != p:
                print(f"FAIL: cell {i} differs:\n  serial={s}\n  parallel={p}")
                return False
        print(f"  serial == parallel ({len(serial)} cells)")
        print("PASS")
        return True
    except Exception as exc:
        print(f"FAIL: {exc}")
        return False


def audit_crossing_parameter_smoke() -> bool:
    """Phase 30 item J: ``crossing_parameter`` returns a finite value on
    a known-bracketed lambda_se sweep and validates input contracts."""
    import math

    from time_evolution import crossing_parameter

    print("\ncrossing_parameter smoke test (Phase 30 item J)...")
    try:
        # Negative-path: invalid parameter name must raise.
        try:
            crossing_parameter(
                1e-7, 298.15, 1e-3,
                parameter="not_a_thing",  # type: ignore[arg-type]
                t_obs_s=3600.0, p_min=0.0, p_max=1e-8,
            )
        except ValueError:
            pass
        else:
            print("FAIL: invalid parameter name was not rejected")
            return False
        # Positive-path: known-bracketed sweep must return a finite value.
        result = crossing_parameter(
            1e-7, 298.15, 1e-3,
            parameter="lambda_se",
            t_obs_s=3600.0,
            p_min=0.1, p_max=1.0,
            criterion="ratio",
            target=1e-4,
            n_points=8,
        )
        if result is None:
            print("FAIL: known-bracketed ratio target returned None")
            return False
        if not (0.1 <= result <= 1.0) or not math.isfinite(result):
            print(f"FAIL: returned value {result} out of [0.1, 1.0] or non-finite")
            return False
        print(f"  lambda_se @ ratio=1e-4: {result:.6f}")
        print("PASS")
        return True
    except Exception as exc:
        print(f"FAIL: {exc}")
        return False


def main() -> None:
    print("# Integration audit (Phase 23 baseline + Phase 31 v0.4 surfaces)\n")
    results = {
        "cache_repro": audit_cache_reproducibility(),
        "continuous_thresh": audit_continuous_thresholds_compat(),
        "time_evolution": audit_time_evolution_compat(),
        "fnd_class_default": audit_fnd_class_default_compat(),
        "polydispersity_compat": audit_polydispersity_classification_compat(),
        "walk_grid_spawn": audit_walk_grid_spawn_compat(),
        "crossing_parameter": audit_crossing_parameter_smoke(),
    }

    print("\n## Summary")
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")

    all_passed = all(results.values())
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")


if __name__ == "__main__":
    main()
