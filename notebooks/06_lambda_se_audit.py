"""Phase 18 audit — regime-label flip prevalence under λ correction.

This script re-classifies a focused slice of the §5 grid at
λ = {0.1, 0.5, 1.0} and counts how many cells change regime labels.
The result determines whether Phase 18.1 should promote λ to a §5
scan axis (label flips are common) or keep it as a side-computation
(flips are rare).

Usage:
    cd /path/to/repo
    python notebooks/06_lambda_se_audit.py

Output:
    Prints a markdown-formatted audit table to stdout and writes
    ``notebooks/data/lambda_se_audit.csv``.
"""

from __future__ import annotations

import csv
from pathlib import Path

from regime_map import classify_cell
from scan_grid import DEPTHS_M, T_OBS_S
from stokes_einstein_correction import (
    LAMBDA_SE_AXIS,
    SUB_150_NM_THRESHOLD_M,
    count_label_flips,
)

# ---------------------------------------------------------------------------
# Audit configuration
# ---------------------------------------------------------------------------

# Focus on sub-150-nm radii where SE breakdown is relevant.
# Use a coarser radius slice than the full 30-point grid for speed.
REPRESENTATIVE_RADII_M = (
    5e-9,
    1e-8,
    2e-8,
    5e-8,
    1e-7,
)

# Single temperature (room T) keeps the audit fast while covering
# the design-table sweet spot.
AUDIT_TEMPERATURE_K = 298.15

# Depths and t_obs: use the full axes since these are the experimental
# knobs that shift regime boundaries.
AUDIT_DEPTHS_M = DEPTHS_M
AUDIT_T_OBS_S = T_OBS_S

OUTPUT_CSV = Path(__file__).resolve().parent / "lambda_se_audit.csv"

# ---------------------------------------------------------------------------
# Audit runner
# ---------------------------------------------------------------------------


def run_audit() -> None:
    """Walk the focused grid, classify each cell at every λ, and report."""
    rows: list[dict[str, object]] = []
    flip_counts: dict[tuple[float, float], int] = {}

    for lambda_se in LAMBDA_SE_AXIS:
        if lambda_se != 1.0:
            flip_counts[(1.0, lambda_se)] = 0

    total_cells = 0

    for r in REPRESENTATIVE_RADII_M:
        for h in AUDIT_DEPTHS_M:
            for t_obs in AUDIT_T_OBS_S:
                total_cells += 1
                baseline = classify_cell(r, AUDIT_TEMPERATURE_K, h, t_obs, lambda_se=1.0)

                for lambda_se in LAMBDA_SE_AXIS:
                    if lambda_se == 1.0:
                        continue

                    corrected = classify_cell(
                        r, AUDIT_TEMPERATURE_K, h, t_obs, lambda_se=lambda_se
                    )
                    flipped = count_label_flips(baseline, corrected)
                    if flipped:
                        flip_counts[(1.0, lambda_se)] += 1

                    rows.append(
                        {
                            "r_material_m": r,
                            "sample_depth_m": h,
                            "t_obs_s": t_obs,
                            "lambda_se": lambda_se,
                            "baseline_regime": baseline.regime,
                            "corrected_regime": corrected.regime,
                            "flipped": flipped,
                        }
                    )

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------

    print("# Phase 18 — λ_SE regime-label flip audit\n")
    threshold_str = f"{SUB_150_NM_THRESHOLD_M:.0e}"
    print(f"- **Radii scanned:** {len(REPRESENTATIVE_RADII_M)} points ≤ {threshold_str} m")
    print(f"- **Temperature:** {AUDIT_TEMPERATURE_K} K")
    print(f"- **Depths:** {len(AUDIT_DEPTHS_M)} points")
    print(f"- **t_obs:** {len(AUDIT_T_OBS_S)} points")
    print(f"- **Total cells:** {total_cells}")
    print(f"- **λ axis:** {LAMBDA_SE_AXIS}\n")

    print("## Flip counts\n")
    print("| Baseline λ | Corrected λ | Flips | Total cells | Prevalence |")
    print("|---|---|---|---|---|")
    for (lam_base, lam_corr), n_flips in flip_counts.items():
        prevalence = n_flips / total_cells
        print(
            f"| {lam_base} | {lam_corr} | {n_flips} | {total_cells} | {prevalence:.1%} |"
        )

    print("\n## Interpretation\n")
    max_prevalence = max(
        (n / total_cells for n in flip_counts.values()), default=0.0
    )
    if max_prevalence == 0.0:
        print(
            "**No regime-label flips detected.**  λ correction can remain a "
            "side-computation; no §5 cache schema bump needed."
        )
    elif max_prevalence < 0.05:
        print(
            f"**Rare flips ({max_prevalence:.1%}).**  Side-computation is still "
            f"the cheap path; consider a §5 axis only if the flipped cells sit "
            f"in the design-table sweet spot."
        )
    elif max_prevalence < 0.25:
        print(
            f"**Moderate flips ({max_prevalence:.1%}).**  A partial §5 cache "
            f"regen for the sub-150-nm band is worth evaluating."
        )
    else:
        print(
            f"**Frequent flips ({max_prevalence:.1%}).**  λ should be promoted to "
            f"a full §5 scan axis; the side-computation path is insufficient."
        )

    # ------------------------------------------------------------------
    # CSV output
    # ------------------------------------------------------------------

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "r_material_m",
                "sample_depth_m",
                "t_obs_s",
                "lambda_se",
                "baseline_regime",
                "corrected_regime",
                "flipped",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV written: {OUTPUT_CSV}")


if __name__ == "__main__":
    run_audit()
