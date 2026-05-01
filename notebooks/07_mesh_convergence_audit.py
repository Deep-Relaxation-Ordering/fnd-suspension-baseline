"""Phase 21 audit — mesh-convergence sweep on threshold-adjacent cells.

This script runs a focused set of §5 cells through Method C at
increasing mesh resolutions (30 → 960 cells) and records the
convergence of the two classification observables:

- ``top_to_bottom_ratio`` (homogeneous / stratified boundary at 0.95)
- ``bottom_mass_fraction`` (stratified / sedimented boundary at 0.95)

The goal is to document the fidelity envelope of the 120-cell first
pass + 240-cell refinement strategy, and to decide whether the
empirical 10-nm fallback floor is conservative enough.

**Safety guard:** Cells that short-circuit (homogeneous or equilibrated)
are skipped for n_cells > 120, because ``solve_cell`` bypasses the
short-circuit logic and would run an expensive ``expm_multiply`` on a
profile that is already analytically known.

Usage:
    cd /path/to/repo
    PYTHONPATH=src python notebooks/07_mesh_convergence_audit.py

Output:
    ``notebooks/data/mesh_convergence_audit.csv``
"""

from __future__ import annotations

import csv
from pathlib import Path

from fokker_planck import solve_cell
from regime_map import classify_cell

# ---------------------------------------------------------------------------
# Audit configuration
# ---------------------------------------------------------------------------

# Threshold-adjacent cells identified from the §5 cache and prior lab
# notes.  These are cells where the 120-cell first pass sits close to
# a regime boundary and the 240-cell refinement is known to fire.
FOCUS_CELLS = [
    # (r_m, T_K, h_m, t_obs_s, note)
    (2.41e-8, 298.15, 1e-2, 600.0, "Phase-5 resolved-threshold regression"),
    (1e-7, 298.15, 1e-4, 60.0, "High-Pe transient near sedimented boundary"),
    (1e-7, 298.15, 1e-3, 60.0, "Method C resolved, stratified"),
    (5e-9, 298.15, 1e-4, 3600.0, "Homogeneous corner, near threshold"),
    (5e-9, 278.15, 1e-3, 3600.0, "Cold T, small r, near homogeneous boundary"),
]

MESH_RESOLUTIONS = (30, 60, 120, 240, 480, 960)

OUTPUT_CSV = Path(__file__).resolve().parent / "data" / "mesh_convergence_audit.csv"

# ---------------------------------------------------------------------------
# Audit runner
# ---------------------------------------------------------------------------


def _cell_uses_method_c(r: float, T: float, h: float, t_obs: float) -> bool:
    """Return True if classify_cell takes the full Method C path."""
    result = classify_cell(r, T, h, t_obs)
    return not (
        result.used_homogeneous_short_circuit or result.used_equilibrated_short_circuit
    )


def run_audit() -> None:
    rows: list[dict[str, object]] = []

    for r, T, h, t_obs, note in FOCUS_CELLS:
        uses_method_c = _cell_uses_method_c(r, T, h, t_obs)
        print(
            f"Auditing cell: r={r:.0e} m, T={T} K, h={h:.0e} m, t_obs={t_obs} s "
            f"(Method C={uses_method_c})"
        )
        print(f"  Note: {note}")

        baseline = None
        for n_cells in MESH_RESOLUTIONS:
            # Skip expensive resolutions on short-circuit cells
            if not uses_method_c and n_cells > 120:
                print(f"    n={n_cells:4d}: skipped (short-circuit cell)")
                continue

            result = solve_cell(r, T, h, t_total=t_obs, n_cells=n_cells)
            ratio = result.top_to_bottom_ratio()
            bmf = result.bottom_mass_fraction(0.05)
            fallback = result.used_asymptotic_fallback

            row = {
                "r_material_m": r,
                "temperature_kelvin": T,
                "sample_depth_m": h,
                "t_obs_s": t_obs,
                "n_cells": n_cells,
                "top_to_bottom_ratio": ratio,
                "bottom_mass_fraction": bmf,
                "used_asymptotic_fallback": fallback,
                "note": note,
            }
            rows.append(row)

            if baseline is None:
                baseline = (ratio, bmf)
                print(f"    n={n_cells:4d}: ratio={ratio:.6f}, bmf={bmf:.6f} (baseline)")
            else:
                ratio_drift = abs(ratio - baseline[0]) / max(abs(baseline[0]), 1e-15)
                bmf_drift = abs(bmf - baseline[1]) / max(abs(baseline[1]), 1e-15)
                print(
                    f"    n={n_cells:4d}: ratio={ratio:.6f}, bmf={bmf:.6f} "
                    f"(drift vs 30-cell: ratio={ratio_drift:.2e}, bmf={bmf_drift:.2e})"
                )
        print()

    # ------------------------------------------------------------------
    # Convergence summary
    # ------------------------------------------------------------------

    print("## Convergence summary\n")

    # For each cell, compare 120-cell vs 240-cell vs 960-cell
    for r, _T, h, t_obs, _note in FOCUS_CELLS:
        cell_rows = [row for row in rows if row["r_material_m"] == r and row["t_obs_s"] == t_obs]
        by_ncells = {row["n_cells"]: row for row in cell_rows}

        if 120 not in by_ncells or 240 not in by_ncells:
            continue

        r120 = by_ncells[120]["top_to_bottom_ratio"]
        r240 = by_ncells[240]["top_to_bottom_ratio"]

        b120 = by_ncells[120]["bottom_mass_fraction"]
        b240 = by_ncells[240]["bottom_mass_fraction"]

        ratio_refine_drift = abs(r240 - r120) / max(abs(r120), 1e-15)
        bmf_refine_drift = abs(b240 - b120) / max(abs(b120), 1e-15)

        print(f"Cell r={r:.0e}, h={h:.0e}, t_obs={t_obs}:")
        print(f"  ratio: 120→240 drift = {ratio_refine_drift:.2e}")
        print(f"  bmf:   120→240 drift = {bmf_refine_drift:.2e}")

        if 960 in by_ncells:
            r960 = by_ncells[960]["top_to_bottom_ratio"]
            b960 = by_ncells[960]["bottom_mass_fraction"]
            ratio_fine_drift = abs(r960 - r240) / max(abs(r240), 1e-15)
            bmf_fine_drift = abs(b960 - b240) / max(abs(b240), 1e-15)
            print(f"  ratio: 240→960 drift = {ratio_fine_drift:.2e}")
            print(f"  bmf:   240→960 drift = {bmf_fine_drift:.2e}")

    # ------------------------------------------------------------------
    # CSV output
    # ------------------------------------------------------------------

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "r_material_m",
                "temperature_kelvin",
                "sample_depth_m",
                "t_obs_s",
                "n_cells",
                "top_to_bottom_ratio",
                "bottom_mass_fraction",
                "used_asymptotic_fallback",
                "note",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV written: {OUTPUT_CSV}")


if __name__ == "__main__":
    run_audit()
