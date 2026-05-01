"""Phase 22 — Design table: crossing times for continuous time evolution.

Generates ``notebooks/data/design_table_crossing_times.csv``, which
lists the observation time at which a given cell crosses a fixed
threshold (e.g. ``bottom_mass_fraction = 0.5``).  This replaces the
discrete t_obs grid with a continuous answer to the question: *how long
does it take for this cell to reach state X?*

Usage:
    cd /path/to/repo
    PYTHONPATH=src python notebooks/08_time_evolution_design_table.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from time_evolution import crossing_time

OUTPUT_CSV = Path(__file__).resolve().parent / "data" / "design_table_crossing_times.csv"

# Representative cells: radius (m), temperature (K), depth (m)
REPRESENTATIVE_CELLS = [
    (5e-9, 298.15, 1e-4, "homogeneous, small r"),
    (1e-7, 298.15, 1e-4, "stratified, shallow"),
    (1e-7, 298.15, 1e-3, "stratified, mid-depth"),
    (1e-6, 298.15, 1e-4, "sedimented, large r"),
    (1e-6, 298.15, 1e-3, "sedimented, mid-depth"),
]

THRESHOLDS = [
    ("bmf", 0.1, "bmf reaches 0.10"),
    ("bmf", 0.5, "bmf reaches 0.50"),
    ("bmf", 0.9, "bmf reaches 0.90"),
    ("ratio", 0.5, "ratio drops to 0.50"),
]


def main() -> None:
    rows: list[dict[str, object]] = []

    for r, T, h, desc in REPRESENTATIVE_CELLS:
        print(f"Cell: r={r:.0e} m, T={T} K, h={h:.0e} m ({desc})")
        for criterion, target, label in THRESHOLDS:
            t_cross = crossing_time(
                r, T, h,
                criterion=criterion,  # type: ignore[arg-type]
                target=target,
                n_points=20,
            )
            status = "reached" if t_cross is not None else "unreachable"
            print(f"  {label}: {t_cross if t_cross is not None else '—'} s ({status})")
            rows.append(
                {
                    "r_material_m": r,
                    "temperature_kelvin": T,
                    "sample_depth_m": h,
                    "cell_description": desc,
                    "criterion": criterion,
                    "target": target,
                    "crossing_time_s": t_cross,
                    "status": status,
                }
            )
        print()

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "r_material_m",
                "temperature_kelvin",
                "sample_depth_m",
                "cell_description",
                "criterion",
                "target",
                "crossing_time_s",
                "status",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV written: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
