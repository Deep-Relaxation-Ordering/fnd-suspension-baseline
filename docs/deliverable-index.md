# Deliverable index — `pilot-v0.3`

This file is the cumulative §6 closeout document. The `pilot-v0.2`
section is preserved below the `pilot-v0.3` delta so readers can see
the full artefact history in one place.

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
| Pilot tag | `pilot-v0.3` |
| FAIR metadata patch | `0.3.0` |
| Spec | breakout-note v0.2, pinned to `Deep-Relaxation-Ordering/diamonds_in_water` commit `3b7b18af7bd1739f3cb7b3360d2b75264dd5ad07` (see [`conventions.md`](conventions.md) §"Pilot-spec pin") |
| cd-rules | pinned to `threehouse-plus-ec/cd-rules` commit `ee01c80352dd8446f189c3159a3d9e347463902c` (see [`conventions.md`](conventions.md) §"Inherited rules") |
| Test suite at metadata patch | `171 passed, 0 skipped` (`pytest -q`) |
| Lint at metadata patch | `ruff check .` clean |

## §6 deliverable mapping — `pilot-v0.3` additions

| # | Deliverable | Artefact | Regen command |
|---|---|---|---|
| 7 | Stokes–Einstein correction audit (`lambda_se` flip rates across sub-150-nm grid slice) | [`notebooks/06_lambda_se_audit.py`](../../notebooks/06_lambda_se_audit.py) | `PYTHONPATH=src python notebooks/06_lambda_se_audit.py` |
| 8 | Mesh-convergence fidelity envelope (30 / 60 / 120 / 240 / 480 cell sweep) | [`notebooks/07_mesh_convergence_audit.py`](../../notebooks/07_mesh_convergence_audit.py) + figures in [`notebooks/figures/07_mesh_convergence/`](../../notebooks/figures/07_mesh_convergence/) | `PYTHONPATH=src python notebooks/07_mesh_convergence_audit.py` |
| 9 | Continuous time-evolution design table (crossing-time entries per cell) | [`notebooks/08_time_evolution_design_table.py`](../../notebooks/08_time_evolution_design_table.py), [`notebooks/data/design_table_crossing_time_room_T.csv`](../../notebooks/data/design_table_crossing_time_room_T.csv) (if generated) | `PYTHONPATH=src python notebooks/08_time_evolution_design_table.py` |
| 10 | Integration audit (cache reproducibility + continuous-threshold smoke + time-evolution smoke) | [`notebooks/09_integration_audit.py`](../../notebooks/09_integration_audit.py) | `PYTHONPATH=src python notebooks/09_integration_audit.py` |

## `pilot-v0.2` §6 deliverable mapping (preserved)

| # | Deliverable | Artefact | Regen command |
|---|---|---|---|
| 1 | Methods / code (Method A analytical, Method B Langevin, Method C Smoluchowski FV, Rayleigh convection side channel, hydrodynamic/material radius split, log-normal smearing) | [`src/parameters.py`](../src/parameters.py), [`src/analytical.py`](../src/analytical.py), [`src/langevin.py`](../src/langevin.py), [`src/fokker_planck.py`](../src/fokker_planck.py), [`src/convection.py`](../src/convection.py), [`src/regime_map.py`](../src/regime_map.py), [`src/polydispersity.py`](../src/polydispersity.py), [`src/scan_grid.py`](../src/scan_grid.py) | n/a — implementation source |
| 2 | Baseline-validation notebook (Method A primitives, Einstein-Smoluchowski check, radius-split cell summary) | [`notebooks/01_baseline_validation.py`](../notebooks/01_baseline_validation.py) + figures in [`notebooks/figures/01_baseline_validation/`](../notebooks/figures/01_baseline_validation/) | `PYTHONPATH=src python notebooks/01_baseline_validation.py` |
| 3 | Regime-map figure (§5.1 classification across (r, h) at fixed (T, t_obs)) plus experimental Rayleigh overlay | [`notebooks/02_regime_map.py`](../notebooks/02_regime_map.py) + figures in [`notebooks/figures/02_regime_map/`](../notebooks/figures/02_regime_map/) | `PYTHONPATH=src python notebooks/02_regime_map.py` (reads cache) |
| 4 | Parameter-scan supporting figures (Method A primitives across T, regime maps per-T, homogeneous-radius envelope vs T, convection mask) | [`notebooks/03_parameter_scans.py`](../notebooks/03_parameter_scans.py) + figures in [`notebooks/figures/03_parameter_scans/`](../notebooks/figures/03_parameter_scans/) | `PYTHONPATH=src python notebooks/03_parameter_scans.py` (reads cache) |
| 5 | Design table (per (h, t_obs, T): largest tested homogeneous radius, smallest tested sedimented radius) + authoritative §5 cache | [`notebooks/04_design_table.py`](../notebooks/04_design_table.py), [`notebooks/data/regime_map_grid.csv`](../notebooks/data/regime_map_grid.csv), tables in [`notebooks/data/`](../notebooks/data/): `design_table_max_homogeneous_r.csv`, `design_table_min_sedimented_r.csv`, `design_table_room_T.md` | `PYTHONPATH=src python notebooks/04_design_table.py` (reads cache) |
| 6 | Polydispersity design table and figures (`sigma_geom` log-normal smearing over the §5 radius axis) | [`notebooks/05_polydispersity_smearing.py`](../notebooks/05_polydispersity_smearing.py), [`notebooks/data/design_table_polydispersity_room_T.csv`](../notebooks/data/design_table_polydispersity_room_T.csv), [`notebooks/data/design_table_polydispersity_room_T.md`](../notebooks/data/design_table_polydispersity_room_T.md), figures in [`notebooks/figures/05_polydispersity/`](../notebooks/figures/05_polydispersity/) | `PYTHONPATH=src python notebooks/05_polydispersity_smearing.py` (reads cache) |

## Validation surfaces (breakout-note §4.4)

The §4.4 cross-method consistency surface — the five core checks listed
in the spec plus the additional Method-C, cache, convection,
radius-split, and polydispersity surfaces added during implementation —
is pinned end-to-end by the test suite:

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
| Rayleigh convection gate, signed `alpha(T)`, rigid/free thresholds, and `h > 0` guard | `tests/test_convection.py` |
| Convection flag as a §5.1 side channel with cache round-trip support | `tests/test_regime_map.py::test_convection_flag_is_side_channel`, `tests/test_regime_map.py::test_committed_regime_map_cache_uses_v02_zero_shell_schema` |
| v0.1 / Phase-11 / v0.2 CSV compatibility across radius-schema migration | `tests/test_regime_map.py::test_results_from_csv_reads_v01_without_convection_flag`, `test_results_from_csv_reads_phase11_header`, `test_detect_csv_format_accepts_all_known_headers` |
| Hydrodynamic-vs-material radius split with zero-default backward compatibility | `tests/test_hydrodynamic_split.py`, `tests/test_regime_map.py::test_classify_cell_accepts_geometry_and_records_shell` |
| Log-normal smearing conservation, truncation mask/raise behavior, degenerate limit, and anchor regressions | `tests/test_polydispersity.py` |

## Cache as a first-class deliverable

[`notebooks/data/regime_map_grid.csv`](../notebooks/data/regime_map_grid.csv)
(809 958 bytes, 6300 rows) is the full §5 grid sweep, migrated in
Phase 13 to the v0.2 schema:

```text
r_material_m, r_hydro_m, delta_shell_m, temperature_kelvin,
sample_depth_m, t_obs_s, regime, top_to_bottom_ratio,
bottom_mass_fraction, used_homogeneous_short_circuit,
used_equilibrated_short_circuit, used_method_c_fallback,
convection_flag
```

The cache is both a derived artefact and the authoritative row-level
form of deliverable 5. Regen command:

```sh
PYTHONPATH=src python -c "from regime_map import walk_grid, results_to_csv; \
    results_to_csv(walk_grid(), 'notebooks/data/regime_map_grid.csv')"
```

Wall time remains ~150 min single-threaded on the Phase 6 reference
machine. The Phase 13 migration was by load-and-rewrite after the
Phase 12.1 audit established machine-precision identity to the
post-9.3 baseline at `delta_shell_m = 0`.

## Data schemas and FAIR metadata

The `0.2.1` metadata patch adds citation and data-reuse surfaces
without changing cache values:

| Surface | File |
|---|---|
| CFF citation metadata | [`../CITATION.cff`](../CITATION.cff) |
| CodeMeta JSON-LD | [`../codemeta.json`](../codemeta.json) |
| Data-file index | [`../notebooks/data/README.md`](../notebooks/data/README.md) |
| CSV schemas | [`../notebooks/data/schemas/`](../notebooks/data/schemas/) |
| v0.2 release note | [`release-notes/v0.2.md`](release-notes/v0.2.md) |

Every committed CSV in `notebooks/data/` has a Frictionless Table
Schema:

| CSV | Schema |
|---|---|
| `regime_map_grid.csv` | [`regime_map_grid.schema.json`](../notebooks/data/schemas/regime_map_grid.schema.json) |
| `design_table_max_homogeneous_r.csv` | [`design_table_max_homogeneous_r.schema.json`](../notebooks/data/schemas/design_table_max_homogeneous_r.schema.json) |
| `design_table_min_sedimented_r.csv` | [`design_table_min_sedimented_r.schema.json`](../notebooks/data/schemas/design_table_min_sedimented_r.schema.json) |
| `design_table_polydispersity_room_T.csv` | [`design_table_polydispersity_room_T.schema.json`](../notebooks/data/schemas/design_table_polydispersity_room_T.schema.json) |

`tests/test_data_schemas.py` validates schema coverage, exact headers,
row counts, and scalar type/constraint parsing.

## Provenance trail

The phase-by-phase development is recorded in
[`lab_notes/`](../lab_notes/), reverse-chronological from
[`lab_notes/README.md`](../lab_notes/README.md). Every commit on
`main` is one phase; review-driven fixes appear as `.1` / `.2`
follow-up commits. The complete audit trail from scaffold to this
release runs from `10d1d24` (initial scaffold) through the
`pilot-v0.2` tag, with the `0.2.1` FAIR metadata patch recorded as
Phase 16. The v0.2 scope was anchored in
[`ADR 0001`](adr/0001-v0.2-spec-anchoring.md).

## Known caveats and audit-gap pins

- ~~**`scan_grid.T_OBS_S` audit-gap pin**~~ — **resolved in Phase 19**
  (v0.3 item A). The six observation times are formal v0.3 defaults
  under [ADR 0002 D1](adr/0002-v0.3-spec-anchoring.md).
- ~~**`scan_grid.DEPTHS_M` audit-gap pin**~~ — **resolved in Phase 19**
  (v0.3 item A). Same logic for the 10 mm cuvette.
- **§5 grid-snap in design tables** — the §5 r-axis is 30 log-spaced
  points (~10 % bin spacing), so design-table radius entries are
  grid-snapped, not interpolated thresholds. The continuous-threshold
  channel (v0.3 item B) provides interpolated values alongside.
- **Method-C regime-map fidelity envelope** — resolved transient cells
  use a 120-cell first pass, with 240-cell refinement for cells near
  the `c(h)/c(0)` thresholds. The high-Pe bottom-mass boundary is still
  governed by the 10-nm regime-map fallback policy, not by a full
  1-nm resolved-mesh convergence sweep. The mesh-convergence audit
  (v0.3 item C) documents the drift bounds.
- **`delta_shell_m = 0` in the shipped §5 cache** — the v0.2 schema can
  carry distinct material and hydrodynamic radii, but the committed
  §5 cache intentionally preserves the v0.1 physics surface with
  `r_material_m == r_hydro_m`. The `delta_shell_m` calibration table
  was upgraded in Phase 27 (v0.4 item B / S3) to citation-anchored
  FND-class defaults; campaign-specific batches remain unverified until
  same-buffer DLS / TEM measurements exist.
- **`delta_T_assumed` split** — programmatic `classify_cell()` and
  `walk_grid()` default to `0.0 K` so legacy labels and booleans
  reproduce v0.1; notebooks pass
  `DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1 K` explicitly when drawing
  convection overlays.
- **Convection side channel only** — `convection_flag` never changes
  the §5.1 regime label. It warns that the 1-D transport assumption
  may be experimentally invalid under the supplied thermal gradient.
- **`SIGMA_GEOM_AXIS` pin** — deliverable 6 uses
  `{1.05, 1.10, 1.20, 1.40, 1.60}`. Broad distributions at the §5
  radius-axis edges are marked with `truncation_loss` and `accepted`
  diagnostics instead of being silently omitted.
- **`lambda_se` provisional flag** — when `lambda_se != 1.0`,
  `classify_cell_lambda()` returns `provisional = True`. Design-tool
  entry points must require `accept_provisional = True` (contract in
  ADR 0002). No `lambda_se` axis is present in the committed §5 cache.
- **Aggregation, adsorption, surfactants, and wall corrections** —
  not modelled in v0.3. See
  [`experimental-envelope.md`](experimental-envelope.md).
- **DOI deferred to `pilot-v1.0`** — `CITATION.cff` and `codemeta.json`
  carry no DOI; Zenodo minting is intentionally postponed to the v1.0
  release because pre-v1.0 pilots have a moving physics scope. See
  [`../lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md`](../lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md).
- **`equilibrium_cell` `t_factor = 50` magic constant** — works for
  every cell tested; not formally derived.

## What `pilot-v0.4` would change

Candidate tightenings for the next pilot slice (from
[`program-context.md`](program-context.md) §3.1):

- S1 — DLVO aggregation pre-screen (waiting on upstream breakout
  note).
- S3 — Salinity / ionic-strength correction to diffusivity.
- S4 — pH-dependent surface-charge effects on hydrodynamic radius.
- S5 — Multi-particle interaction (concentration-dependent
  sedimentation).
- S6 — Viscosity temperature-dependence beyond the current Tanaka
  fit.
- S7 — Full 3-D convection simulation (beyond Rayleigh threshold).
- Aggregation and wall-hydrodynamic correction models, or at least
  quantified validity limits for them.
- Calibrate `delta_shell_m` against representative functionalised FND
  hydrodynamic measurements instead of leaving it as a user-supplied
  geometry knob.
- Promote `lambda_se` to a §5 scan axis if calibrated working values
  are ≤ 0.3.

None of these are v0.3 correctness fixes; they are the next layer of
experimental realism and consumer convenience.

---

# `pilot-v0.2` deliverable index (preserved for reference)

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
| Pilot tag | `pilot-v0.2` |
| FAIR metadata patch | `0.2.1` |
| Spec | breakout-note v0.2, pinned to `Deep-Relaxation-Ordering/diamonds_in_water` commit `3b7b18af7bd1739f3cb7b3360d2b75264dd5ad07` (see [`conventions.md`](conventions.md) §"Pilot-spec pin") |
| cd-rules | pinned to `threehouse-plus-ec/cd-rules` commit `ee01c80352dd8446f189c3159a3d9e347463902c` (see [`conventions.md`](conventions.md) §"Inherited rules") |
| Test suite at metadata patch | `135 passed, 0 skipped` (`pytest -q`) |
| Lint at metadata patch | `ruff check .` clean |

## §6 deliverable mapping

| # | Deliverable | Artefact | Regen command |
|---|---|---|---|
| 1 | Methods / code (Method A analytical, Method B Langevin, Method C Smoluchowski FV, Rayleigh convection side channel, hydrodynamic/material radius split, log-normal smearing) | [`src/parameters.py`](../src/parameters.py), [`src/analytical.py`](../src/analytical.py), [`src/langevin.py`](../src/langevin.py), [`src/fokker_planck.py`](../src/fokker_planck.py), [`src/convection.py`](../src/convection.py), [`src/regime_map.py`](../src/regime_map.py), [`src/polydispersity.py`](../src/polydispersity.py), [`src/scan_grid.py`](../src/scan_grid.py) | n/a — implementation source |
| 2 | Baseline-validation notebook (Method A primitives, Einstein-Smoluchowski check, radius-split cell summary) | [`notebooks/01_baseline_validation.py`](../notebooks/01_baseline_validation.py) + figures in [`notebooks/figures/01_baseline_validation/`](../notebooks/figures/01_baseline_validation/) | `PYTHONPATH=src python notebooks/01_baseline_validation.py` |
| 3 | Regime-map figure (§5.1 classification across (r, h) at fixed (T, t_obs)) plus experimental Rayleigh overlay | [`notebooks/02_regime_map.py`](../notebooks/02_regime_map.py) + figures in [`notebooks/figures/02_regime_map/`](../notebooks/figures/02_regime_map/) | `PYTHONPATH=src python notebooks/02_regime_map.py` (reads cache) |
| 4 | Parameter-scan supporting figures (Method A primitives across T, regime maps per-T, homogeneous-radius envelope vs T, convection mask) | [`notebooks/03_parameter_scans.py`](../notebooks/03_parameter_scans.py) + figures in [`notebooks/figures/03_parameter_scans/`](../notebooks/figures/03_parameter_scans/) | `PYTHONPATH=src python notebooks/03_parameter_scans.py` (reads cache) |
| 5 | Design table (per (h, t_obs, T): largest tested homogeneous radius, smallest tested sedimented radius) + authoritative §5 cache | [`notebooks/04_design_table.py`](../notebooks/04_design_table.py), [`notebooks/data/regime_map_grid.csv`](../notebooks/data/regime_map_grid.csv), tables in [`notebooks/data/`](../notebooks/data/): `design_table_max_homogeneous_r.csv`, `design_table_min_sedimented_r.csv`, `design_table_room_T.md` | `PYTHONPATH=src python notebooks/04_design_table.py` (reads cache) |
| 6 | Polydispersity design table and figures (`sigma_geom` log-normal smearing over the §5 radius axis) | [`notebooks/05_polydispersity_smearing.py`](../notebooks/05_polydispersity_smearing.py), [`notebooks/data/design_table_polydispersity_room_T.csv`](../notebooks/data/design_table_polydispersity_room_T.csv), [`notebooks/data/design_table_polydispersity_room_T.md`](../notebooks/data/design_table_polydispersity_room_T.md), figures in [`notebooks/figures/05_polydispersity/`](../notebooks/figures/05_polydispersity/) | `PYTHONPATH=src python notebooks/05_polydispersity_smearing.py` (reads cache) |

## Validation surfaces (breakout-note §4.4)

The §4.4 cross-method consistency surface — the five core checks listed
in the spec plus the additional Method-C, cache, convection,
radius-split, and polydispersity surfaces added during implementation —
is pinned end-to-end by the test suite:

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
| Rayleigh convection gate, signed `alpha(T)`, rigid/free thresholds, and `h > 0` guard | `tests/test_convection.py` |
| Convection flag as a §5.1 side channel with cache round-trip support | `tests/test_regime_map.py::test_convection_flag_is_side_channel`, `tests/test_regime_map.py::test_committed_regime_map_cache_uses_v02_zero_shell_schema` |
| v0.1 / Phase-11 / v0.2 CSV compatibility across radius-schema migration | `tests/test_regime_map.py::test_results_from_csv_reads_v01_without_convection_flag`, `test_results_from_csv_reads_phase11_header`, `test_detect_csv_format_accepts_all_known_headers` |
| Hydrodynamic-vs-material radius split with zero-default backward compatibility | `tests/test_hydrodynamic_split.py`, `tests/test_regime_map.py::test_classify_cell_accepts_geometry_and_records_shell` |
| Log-normal smearing conservation, truncation mask/raise behavior, degenerate limit, and anchor regressions | `tests/test_polydispersity.py` |

## Cache as a first-class deliverable

[`notebooks/data/regime_map_grid.csv`](../notebooks/data/regime_map_grid.csv)
(809 958 bytes, 6300 rows) is the full §5 grid sweep, migrated in
Phase 13 to the v0.2 schema:

```text
r_material_m, r_hydro_m, delta_shell_m, temperature_kelvin,
sample_depth_m, t_obs_s, regime, top_to_bottom_ratio,
bottom_mass_fraction, used_homogeneous_short_circuit,
used_equilibrated_short_circuit, used_method_c_fallback,
convection_flag
```

The cache is both a derived artefact and the authoritative row-level
form of deliverable 5. Regen command:

```sh
PYTHONPATH=src python -c "from regime_map import walk_grid, results_to_csv; \
    results_to_csv(walk_grid(), 'notebooks/data/regime_map_grid.csv')"
```

Wall time remains ~150 min single-threaded on the Phase 6 reference
machine. The Phase 13 migration was by load-and-rewrite after the
Phase 12.1 audit established machine-precision identity to the
post-9.3 baseline at `delta_shell_m = 0`.

## Data schemas and FAIR metadata

The `0.2.1` metadata patch adds citation and data-reuse surfaces
without changing cache values:

| Surface | File |
|---|---|
| CFF citation metadata | [`../CITATION.cff`](../CITATION.cff) |
| CodeMeta JSON-LD | [`../codemeta.json`](../codemeta.json) |
| Data-file index | [`../notebooks/data/README.md`](../notebooks/data/README.md) |
| CSV schemas | [`../notebooks/data/schemas/`](../notebooks/data/schemas/) |
| v0.2 release note | [`release-notes/v0.2.md`](release-notes/v0.2.md) |

Every committed CSV in `notebooks/data/` has a Frictionless Table
Schema:

| CSV | Schema |
|---|---|
| `regime_map_grid.csv` | [`regime_map_grid.schema.json`](../notebooks/data/schemas/regime_map_grid.schema.json) |
| `design_table_max_homogeneous_r.csv` | [`design_table_max_homogeneous_r.schema.json`](../notebooks/data/schemas/design_table_max_homogeneous_r.schema.json) |
| `design_table_min_sedimented_r.csv` | [`design_table_min_sedimented_r.schema.json`](../notebooks/data/schemas/design_table_min_sedimented_r.schema.json) |
| `design_table_polydispersity_room_T.csv` | [`design_table_polydispersity_room_T.schema.json`](../notebooks/data/schemas/design_table_polydispersity_room_T.schema.json) |

`tests/test_data_schemas.py` validates schema coverage, exact headers,
row counts, and scalar type/constraint parsing.

## Provenance trail

The phase-by-phase development is recorded in
[`lab_notes/`](../lab_notes/), reverse-chronological from
[`lab_notes/README.md`](../lab_notes/README.md). Every commit on
`main` is one phase; review-driven fixes appear as `.1` / `.2`
follow-up commits. The complete audit trail from scaffold to this
release runs from `10d1d24` (initial scaffold) through the
`pilot-v0.2` tag, with the `0.2.1` FAIR metadata patch recorded as
Phase 16. The v0.2 scope was anchored in
[`ADR 0001`](adr/0001-v0.2-spec-anchoring.md).

## Known caveats and audit-gap pins

- ~~**`scan_grid.T_OBS_S` audit-gap pin**~~ — **resolved in Phase 19.**
  The six observation times (1 min, 10 min, 1 h, 4 h, 1 d, 1 w) are
  formal v0.3 defaults under [ADR 0002 D1](adr/0002-v0.3-spec-anchoring.md)
  (anchored to breakout-note v0.2 commit `3b7b18af`); the v0.2 spec
  does not override these values, so they stand as authoritative.
- ~~**`scan_grid.DEPTHS_M` audit-gap pin**~~ — **resolved in Phase 19.**
  Same logic for the 10 mm cuvette: v0.2 spec is the authority and
  does not override.
- **§5 grid-snap in design tables** — the §5 r-axis is 30 log-spaced
  points (~10 % bin spacing), so design-table radius entries are
  grid-snapped, not interpolated thresholds.
- **Method-C regime-map fidelity envelope** — resolved transient cells
  use a 120-cell first pass, with 240-cell refinement for cells near
  the `c(h)/c(0)` thresholds. The high-Pe bottom-mass boundary is still
  governed by the 10-nm regime-map fallback policy, not by a full
  1-nm resolved-mesh convergence sweep.
- **`delta_shell_m = 0` in the shipped §5 cache** — the v0.2 schema can
  carry distinct material and hydrodynamic radii, but the committed
  §5 cache intentionally preserves the v0.1 physics surface with
  `r_material_m == r_hydro_m`. Phase 27 adds opt-in FND-class defaults
  while keeping this compatibility path unchanged.
- **`delta_T_assumed` split** — programmatic `classify_cell()` and
  `walk_grid()` default to `0.0 K` so legacy labels and booleans
  reproduce v0.1; notebooks pass
  `DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1 K` explicitly when drawing
  convection overlays.
- **Convection side channel only** — `convection_flag` never changes
  the §5.1 regime label. It warns that the 1-D transport assumption
  may be experimentally invalid under the supplied thermal gradient.
- **`SIGMA_GEOM_AXIS` pin** — deliverable 6 uses
  `{1.05, 1.10, 1.20, 1.40, 1.60}`. Broad distributions at the §5
  radius-axis edges are marked with `truncation_loss` and `accepted`
  diagnostics instead of being silently omitted.
- **Aggregation, adsorption, surfactants, and wall corrections** —
  not modelled in v0.2. See
  [`experimental-envelope.md`](experimental-envelope.md).
- **DOI deferred to `pilot-v1.0`** — `CITATION.cff` and `codemeta.json`
  carry no DOI; Zenodo minting is intentionally postponed to the v1.0
  release because pre-v1.0 pilots have a moving physics scope. See
  [`../lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md`](../lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md).
- **`equilibrium_cell` `t_factor = 50` magic constant** — works for
  every cell tested; not formally derived.

## What `pilot-v0.3` would change

Candidate tightenings for the next pilot slice:

- ~~Resolve the `T_OBS_S` and `DEPTHS_M` audit-gap pins against the
  next frozen breakout-note §5 table.~~ — **done in Phase 19**
  (resolved against ADR 0002 D1 / breakout-note v0.2 commit
  `3b7b18af`; values stand as v0.3 defaults).
- Replace grid-snapped design-table entries with continuous
  interpolated thresholds via root-finding on `top_to_bottom_ratio
  = 0.95`, `bottom_mass_fraction = 0.95`, and the smeared
  `p_stratified` suitability criterion.
- Add a formal mesh-convergence audit around the finite-time
  bottom-mass threshold.
- Add aggregation and wall-hydrodynamic correction models, or at
  least quantified validity limits for them.
- Calibrate `delta_shell_m` against representative functionalised FND
  hydrodynamic measurements instead of leaving it as a user-supplied
  geometry knob.
- Refine thermal-convection modelling beyond a single Rayleigh
  threshold: measured gradients, boundary-condition uncertainty,
  water thermal diffusivity vs T, and optional open-cell evaporation.
- Reduce the §5 grid walk wall time via parallel walks or a stronger
  analytic short-circuit on the remaining Method-C-resolved cells.

None of these are v0.2 correctness fixes; they are the next layer of
experimental realism and consumer convenience.
- **§5 grid-snap in design tables** — the §5 r-axis is 30 log-spaced
  points (~10 % bin spacing), so design-table radius entries are
  grid-snapped, not interpolated thresholds.
- **Method-C regime-map fidelity envelope** — resolved transient cells
  use a 120-cell first pass, with 240-cell refinement for cells near
  the `c(h)/c(0)` thresholds. The high-Pe bottom-mass boundary is still
  governed by the 10-nm regime-map fallback policy, not by a full
  1-nm resolved-mesh convergence sweep.
- **`delta_shell_m = 0` in the shipped §5 cache** — the v0.2 schema can
  carry distinct material and hydrodynamic radii, but the committed
  §5 cache intentionally preserves the v0.1 physics surface with
  `r_material_m == r_hydro_m`. Phase 27 adds opt-in FND-class defaults
  while keeping this compatibility path unchanged.
- **`delta_T_assumed` split** — programmatic `classify_cell()` and
  `walk_grid()` default to `0.0 K` so legacy labels and booleans
  reproduce v0.1; notebooks pass
  `DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1 K` explicitly when drawing
  convection overlays.
- **Convection side channel only** — `convection_flag` never changes
  the §5.1 regime label. It warns that the 1-D transport assumption
  may be experimentally invalid under the supplied thermal gradient.
- **`SIGMA_GEOM_AXIS` pin** — deliverable 6 uses
  `{1.05, 1.10, 1.20, 1.40, 1.60}`. Broad distributions at the §5
  radius-axis edges are marked with `truncation_loss` and `accepted`
  diagnostics instead of being silently omitted.
- **Aggregation, adsorption, surfactants, and wall corrections** —
  not modelled in v0.2. See
  [`experimental-envelope.md`](experimental-envelope.md).
- **DOI deferred to `pilot-v1.0`** — `CITATION.cff` and `codemeta.json`
  carry no DOI; Zenodo minting is intentionally postponed to the v1.0
  release because pre-v1.0 pilots have a moving physics scope. See
  [`../lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md`](../lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md).
- **`equilibrium_cell` `t_factor = 50` magic constant** — works for
  every cell tested; not formally derived.

## What `pilot-v0.3` would change

Candidate tightenings for the next pilot slice:

- ~~Resolve the `T_OBS_S` and `DEPTHS_M` audit-gap pins against the
  next frozen breakout-note §5 table.~~ — **done in Phase 19**
  (resolved against ADR 0002 D1 / breakout-note v0.2 commit
  `3b7b18af`; values stand as v0.3 defaults).
- Replace grid-snapped design-table entries with continuous
  interpolated thresholds via root-finding on `top_to_bottom_ratio
  = 0.95`, `bottom_mass_fraction = 0.95`, and the smeared
  `p_stratified` suitability criterion.
- Add a formal mesh-convergence audit around the finite-time
  bottom-mass threshold.
- Add aggregation and wall-hydrodynamic correction models, or at
  least quantified validity limits for them.
- Calibrate `delta_shell_m` against representative functionalised FND
  hydrodynamic measurements instead of leaving it as a user-supplied
  geometry knob.
- Refine thermal-convection modelling beyond a single Rayleigh
  threshold: measured gradients, boundary-condition uncertainty,
  water thermal diffusivity vs T, and optional open-cell evaporation.
- Reduce the §5 grid walk wall time via parallel walks or a stronger
  analytic short-circuit on the remaining Method-C-resolved cells.

None of these are v0.2 correctness fixes; they are the next layer of
experimental realism and consumer convenience.
