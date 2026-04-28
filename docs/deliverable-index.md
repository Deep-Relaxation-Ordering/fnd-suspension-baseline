# Deliverable index — `pilot-v0.1`

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

This file maps the breakout-note §6 deliverable list to the shipped
artefacts in this repository. It is the §6 closeout document: when
the principal investigator finalises the breakout note's §6 section
they can paste the rows below directly.

## Pin

| Field | Value |
|---|---|
| Repository | `Deep-Relaxation-Ordering/fnd-suspension-baseline` |
| Pilot tag | `pilot-v0.1` |
| Spec | breakout-note v0.2, pinned to `Deep-Relaxation-Ordering/diamonds_in_water` commit `3b7b18af7bd1739f3cb7b3360d2b75264dd5ad07` (see [`conventions.md`](conventions.md) §"Pilot-spec pin") |
| cd-rules | pinned to `threehouse-plus-ec/cd-rules` commit `ee01c80352dd8446f189c3159a3d9e347463902c` (see [`conventions.md`](conventions.md) §"Inherited rules") |
| Test suite at release | `92 passed, 0 skipped` (`pytest -q`) |
| Lint at release | `ruff check src/ tests/ notebooks/` clean |

## §6 deliverable mapping

| # | Deliverable | Artefact | Regen command |
|---|---|---|---|
| 1 | Methods / code (Method A analytical, Method B Langevin, Method C Smoluchowski FV) | [`src/parameters.py`](../src/parameters.py), [`src/analytical.py`](../src/analytical.py), [`src/langevin.py`](../src/langevin.py), [`src/fokker_planck.py`](../src/fokker_planck.py), [`src/regime_map.py`](../src/regime_map.py), [`src/scan_grid.py`](../src/scan_grid.py) | n/a — implementation source |
| 2 | Baseline-validation notebook (Method A primitives, Einstein–Smoluchowski check) | [`notebooks/01_baseline_validation.py`](../notebooks/01_baseline_validation.py) + figures in [`notebooks/figures/01_baseline_validation/`](../notebooks/figures/01_baseline_validation/) | `PYTHONPATH=src python notebooks/01_baseline_validation.py` |
| 3 | Regime-map figure (§5.1 classification across (r, h) at fixed (T, t_obs)) | [`notebooks/02_regime_map.py`](../notebooks/02_regime_map.py) + figures in [`notebooks/figures/02_regime_map/`](../notebooks/figures/02_regime_map/) | `PYTHONPATH=src python notebooks/02_regime_map.py` (reads cache) |
| 4 | Parameter-scan supporting figures (Method A primitives across T, regime maps per-T, homogeneous-radius envelope vs T) | [`notebooks/03_parameter_scans.py`](../notebooks/03_parameter_scans.py) + figures in [`notebooks/figures/03_parameter_scans/`](../notebooks/figures/03_parameter_scans/) | `PYTHONPATH=src python notebooks/03_parameter_scans.py` (reads cache) |
| 5 | Design table (per (h, t_obs, T): largest tested homogeneous radius, smallest tested sedimented radius) | [`notebooks/04_design_table.py`](../notebooks/04_design_table.py) + tables in [`notebooks/data/`](../notebooks/data/): `design_table_max_homogeneous_r.csv`, `design_table_min_sedimented_r.csv`, `design_table_room_T.md` | `PYTHONPATH=src python notebooks/04_design_table.py` (reads cache) |

## Validation surfaces (breakout-note §4.4)

The five §4.4 cross-method consistency checks all pass:

| §4.4 check | Pinning test |
|---|---|
| Method-B long-time barometric agreement (mean-height ≤ 2 % at N ≥ 10⁴) | `tests/test_equilibrium.py::test_method_b_long_time_matches_barometric` |
| Position-variance saturation at h²/12 | `tests/test_equilibrium.py::test_position_variance_saturates_at_h2_over_12` |
| Unbounded MSD = 2 D t | `tests/test_method_consistency.py::test_unbounded_msd_linear_in_time` |
| Bounded displacement-MSD saturation at h²/6 | `tests/test_method_consistency.py::test_bounded_displacement_msd_saturates_at_h2_over_6` |
| Pure-sedimentation arrival-time mean = h/(2 v_sed) | `tests/test_method_consistency.py::test_pure_sedimentation_arrival_times` |
| Method-B ↔ Method-C time-dependent moments inside B's envelope | `tests/test_method_consistency.py::test_method_b_c_time_dependent_moments_agree` |
| Method-A ↔ Method-C resolved-mesh equilibrium (Phase 4.1 addition) | `tests/test_method_consistency.py::test_method_a_c_equilibrium_inside_b_envelope_resolved_mesh` |
| Method-A ↔ Method-C asymptotic-fallback equilibrium | `tests/test_method_consistency.py::test_method_a_c_equilibrium_outside_b_envelope` |
| Scharfetter-Gummel high-Pe drift-upwind / low-Pe central limits | `tests/test_method_consistency.py::test_method_c_high_pe_upwind_limit`, `test_method_c_low_pe_central_limit` |
| Asymptotic-sedimentation fallback engagement + finite-time transient | `tests/test_method_consistency.py::test_method_c_asymptotic_sedimentation_fallback`, `test_method_c_asymptotic_fallback_keeps_finite_time_transient` |
| Raw-operator mass conservation (Phase 4.1 addition) | `tests/test_method_consistency.py::test_method_c_operator_conserves_mass_to_machine_precision` |

## Cache as a first-class deliverable

[`notebooks/data/regime_map_grid.csv`](../notebooks/data/regime_map_grid.csv)
(612 530 bytes, 6300 rows) is the full §5 grid sweep, computed once
in Phase 6. It is *both* a derived artefact and the authoritative
form of deliverable 5. Regen command:

```sh
PYTHONPATH=src python -c "from regime_map import walk_grid, results_to_csv; \
    results_to_csv(walk_grid(), 'notebooks/data/regime_map_grid.csv')"
```

Wall time: ~150 min single-threaded on the Phase 6 reference machine.

## Provenance trail

The phase-by-phase development is recorded in
[`lab_notes/`](../lab_notes/), reverse-chronological from
[`lab_notes/README.md`](../lab_notes/README.md). Every commit on
`main` is one phase; review-driven fixes appear as `.1` / `.2`
follow-up commits. The complete audit trail from scaffold to
release runs from `10d1d24` (initial scaffold) through to the
`pilot-v0.1` tag.

## Known caveats (not blocking v0.1)

These are documented in their respective lab notes and intentionally
not addressed at v0.1:

- **`scan_grid.T_OBS_S` audit-gap pin** — the six observation times
  (1 min, 10 min, 1 h, 4 h, 1 d, 1 w) are physically-motivated
  defaults; the breakout-note §5 table's specific values should be
  cross-checked at the next spec drift (Phase 5 lab note).
- **`scan_grid.DEPTHS_M` audit-gap pin** — same for the 5th depth
  value (Phase 2.5 lab note).
- **§5 grid-snap in design tables** — the §5 r-axis is 30 log-spaced
  points (~10 % bin spacing), so the design-table radius entries are
  grid-snapped, not interpolated thresholds. Continuous analytic
  equilibrium boundaries are in notebook 03's overlay (Phase 7.1
  lab note).
- **`equilibrium_cell` `t_factor = 50` magic constant** — works for
  every cell tested; not formally derived (Phase 4.1 lab note).

## What `pilot-v1.0` would change

If the pilot is promoted to a paper-grade artefact, the candidate
tightenings are:

- Resolve the two audit-gap pins above against the breakout-note §5
  table.
- Replace the §5 grid-snapped design-table entries with continuous
  interpolated thresholds via root-finding on `top_to_bottom_ratio
  = 0.95` and `bottom_mass_fraction = 0.95`.
- Reduce the §5 grid walk wall time via either parallel walks
  (joblib / multiprocessing) or an analytic short-circuit on the
  remaining ~33 % of cells that go through Method C resolved-mesh.
- Cite-grade prose pass on each of the four notebooks for paper
  inclusion.

None of these are correctness fixes; they are quality-of-life
improvements for downstream consumers.
