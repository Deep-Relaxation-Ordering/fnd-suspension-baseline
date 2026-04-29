# Work plan — `pilot-v0.2`

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

| Field | Value |
|---|---|
| Status | **Accepted — Phase 11 complete; Phase 11.1 review fixes applied; Phase 12 physics propagation in progress.** Scope, D1–D6 decisions, and risk register accepted. |
| Date | 2026-04-29 (accepted; drafted 2026-04-28) |
| Drafted at | commit `42e819e` (Phase 10 ADR landed) |
| Spec anchor | breakout-note v0.2 commit `3b7b18af` (frozen unless v0.3 lands during the cycle; see [ADR 0001](adr/0001-v0.2-spec-anchoring.md)) |
| Predecessor | `pilot-v0.1` tag at `9a0fc76` |
| Successor tag | `pilot-v0.2` (target — Phase 15) |
| Working tempo | v0.1 baseline: ~1 phase per session; ~7 working days across ~10 sessions; calendar 1.5–2 weeks |

This document is the contract for the v0.2 cycle. Each phase below
declares its goal, concrete deliverables (with file paths), API
sketch, test additions, audit-gap pins, exit criteria, and risks.
The cycle ends when every phase's exit criteria are met and the
`pilot-v0.2` tag conditions in §"Tag acceptance criteria" are
satisfied.

The conversation-level phase table that opened this cycle was the
seed; this document is now the accepted contract for the v0.2 cycle.

---

## 1. Scope

### In scope

Three additions, all forward-compatible with v0.1:

1. **Rayleigh-number convection gate** (Phases 11 / 11.1). Flag
   cells where buoyancy-driven convection at experimentally-
   plausible vertical temperature gradients would dominate
   diffusion / sedimentation. Does not override the §5.1 regime
   label; sits beside it.
2. **Hydrodynamic-vs-material radius split** (Phases 12 / 12.1).
   Separate `r_material` (sets buoyant mass via `ρ_diamond`) from
   `r_hydro = r_material + δ_shell` (sets Stokes drag and
   Stokes-Einstein diffusivity). Default `δ_shell = 0`
   reproduces v0.1.
3. **Log-normal polydispersity post-processing** (Phases 14 /
   14.1). Convolve §5 sharp-radius classification against
   `P(r | r̄, σ_geom)` to produce probabilistic regime labels and
   a deliverable-6 design table. Default `σ_geom → 0` reproduces
   v0.1.

Plus the housekeeping phases:

- **Phase 13** — re-walk the §5 cache so the new
  `convection_flag` column exists in compatibility mode
  (`delta_T_assumed = 0.0 K`, therefore all-False) without forcing
  every consumer to recompute. Experimental convection overlays use
  `DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1 K` and recompute the flag
  from the cache axes / precursors.
- **Phase 15** — release: deliverable index updated, findings
  narratives extended, `docs/experimental-envelope.md` shipped,
  `pilot-v0.2` tag.

### Out of scope (parallel tracks)

- **Aggregation pre-screen** (EC item 4). Owned in
  `Deep-Relaxation-Ordering/diamonds_in_water` or a sibling
  Markdown breakout. Tabulates `τ_agg(ζ, I, pH)` for diamond-
  water from DLVO inputs against the §5 t_obs axis. Effort
  ~3 d. Not blocked by v0.2.
- **Capsule-geometry port** (EC item 5). Separate breakout note
  proposing a 3D-spherical port at d = 10–100 µm. Note ~2 d;
  implementation pilot ~12 d (own cycle).

These are tracked here only so they don't accidentally creep
into v0.2.

### Forward-compatibility contract (non-negotiable)

The forward-compat reference is **the current `main` branch state
at the start of Phase 11** (the post-Phase-9.3 lineage; commit
`94b102a` at the time of writing), not the historical
`pilot-v0.1` tag at `9a0fc76`. The Phase-9.3 cache repair
intentionally changed 8 H→S labels via threshold refinement; that
change is correct and stays. The `pilot-v0.1` tag remains a
historical reference for the v0.1 release moment, but it is
*not* the v0.2 forward-compat target.

v0.2 must satisfy, against the post-9.3 `main` baseline:

1. The post-9.3 baseline suite passes unchanged at the v0.2
   compatibility-mode settings (`δ_shell = 0`,
   `delta_T_assumed = 0.0 K`, `σ_geom = 0`). The current suite
   count increases as v0.2 phases add tests; Phase 12.1 records the
   exact pre-refactor and post-refactor counts. Enforced by Phase
   12.1's regression audit and by CI.
2. The current `main` §5 cache
   `notebooks/data/regime_map_grid.csv` regime label columns
   (`regime`, `top_to_bottom_ratio`, `bottom_mass_fraction`) are
   unchanged after Phase 13's re-walk, modulo the new
   `convection_flag` column added: regime strings exactly equal,
   booleans exactly equal, numeric channels equal to machine
   precision (`rtol <= 1e-15`, `atol = 0` unless a documented
   zero-crossing channel requires absolute tolerance).
3. The current `main` deliverable artefacts (notebook 02–04
   figures, design tables, `cell_summary` outputs) are
   equal to machine precision when generated from v0.2 code at
   compatibility-mode settings. PNG/PDF metadata diffs are allowed
   only when image pixels / plotted data are unchanged.

Any commit that breaks (1)–(3) is reverted before merge. CI
catches violations at PR time.

---

## 2. Phase plan

```
                        ┌────────────────────────────────┐
Phase 10 (DONE) ────────► ADR 0001 + scoping             │
                        └──────────────┬─────────────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                ▼                      ▼                      ▼
        Phase 11 (DONE)       Phase 12 (radius split)
                │                      │
                ▼                      ▼
        Phase 11.1 (DONE)     Phase 12.1 regression audit
                │                      │
                └──────────┬───────────┘
                           ▼
                  Phase 13 (cache regen)
                           │
                           ▼
                  Phase 14 (polydispersity)
                           │
                           ▼
                  Phase 14.1 review
                           │
                           ▼
                  Phase 15 (release + tag)
                           │
                           ▼
                  Phase 15.1 (anticipated post-release)
```

Phase 11 / 11.1 is complete. Phase 12 has started with the explicit
radius schema, three-format CSV parser checkpoint, and radius-split
physics propagation through Method A/B/C wrappers; Phases 13 onward are
strictly sequential.

---

## 3. Phase 11 — Rayleigh-number convection gate

**Goal.** Classify §5 cells as "convection-dominated" via the
dimensionless Rayleigh number, side-channel to the existing §5.1
regime label.

### Physics

```text
Ra = g · α(T) · ΔT · h³ / (ν(T) · κ)
```

where α(T) is the thermal expansion coefficient of water (~2·10⁻⁴
K⁻¹ at 25 °C, sign-flipping at 4 °C — see Phase-11 risk register),
ΔT is the vertical temperature difference, ν(T) = η(T) / ρ(T) is
the kinematic viscosity, κ ≈ 1.4·10⁻⁷ m²/s is the thermal
diffusivity (assumed T-independent at v0.2; promoted to T-dependent
in v0.3 if data warrants).

Critical Rayleigh:
- **Rigid-rigid** (closed cuvette, both walls solid): `Ra_c =
  1707.762` (Chandrasekhar, 1961).
- **Rigid-free** (open-top cuvette, top is air-water interface):
  `Ra_c ≈ 1100.65`.

Default boundary convention for v0.2: rigid-rigid (closed cuvette).
Switch via a kwarg.

### Deliverables

- **`src/convection.py`** (new module):
  ```python
  RAYLEIGH_CRITICAL_RIGID_RIGID: Final[float] = 1707.762
  RAYLEIGH_CRITICAL_RIGID_FREE: Final[float] = 1100.65
  WATER_THERMAL_DIFFUSIVITY_M2_PER_S: Final[float] = 1.4e-7

  # Default ΔT for *experimental*-mode notebooks. Code/cache APIs
  # default to 0.0 K to preserve the forward-compat contract; this
  # constant is what notebook 02 / 03 / 05 explicitly pass when
  # they want the convection_flag populated under realistic
  # laboratory thermostat hysteresis. See ADR 0001 §"Consequences"
  # for the API-vs-experimental-default distinction.
  DEFAULT_EXPERIMENTAL_DELTA_T_K: Final[float] = 0.1

  def thermal_expansion_coefficient(T: float) -> float: ...
      # α(T) for water, K⁻¹. Tanaka-2001-derivable form (D3).

  def rayleigh_number(
      sample_depth_m: float,
      delta_T_kelvin: float,
      temperature_kelvin: float,
  ) -> float: ...
      # rejects sample_depth_m <= 0, matching analytical / Method-C
      # positive-depth conventions.

  def is_convection_dominated(
      Ra: float,
      *,
      boundary: Literal["rigid-rigid", "rigid-free"] = "rigid-rigid",
  ) -> bool: ...
  ```

- **`src/regime_map.py`** changes:
  - `classify_cell(...)` gains optional kwargs
    `delta_T_assumed: float = 0.0` (forward-compat default) and
    `boundary: Literal["rigid-rigid", "rigid-free"] = "rigid-rigid"`.
    With `delta_T_assumed = 0.0`, `Ra ≡ 0`, `convection_flag ≡
    False`, and the cache walk produces a column of all-False —
    exactly matching regime labels against the post-9.3 main cache.
  - `RegimeResult` gains `convection_flag: bool` (default
    `False`).
  - `walk_grid(...)` and `RegimeGrid` channels propagate the new
    field.
  - The §5.1 regime label is unchanged. The flag is a side
    channel.
  - Notebook 02 / 03 explicitly pass
    `delta_T_assumed=DEFAULT_EXPERIMENTAL_DELTA_T_K` when rendering
    the convection-flag overlay so the experimentally-relevant
    figures populate the flag under realistic hysteresis. The
    cache walk itself runs at 0.0 K so the persisted CSV's flag
    column is the analytic "if ΔT were 0" answer (i.e., always
    False); the experimental-overlay figures recompute the flag
    on the fly from the cached `Ra(h, T)` precursors and the
    notebook-supplied ΔT. See Phase 13 below for the cache
    storage choice.

- **`tests/test_convection.py`** (new file). Anchors below were
  recomputed against
  `α(25 °C) = 2.57·10⁻⁴ K⁻¹`, `κ = 1.4·10⁻⁷ m²/s`,
  `ν(25 °C) = η/ρ = 8.93·10⁻⁷ m²/s`:

  | Anchor | h | ΔT | T | Ra | Ra / Ra_c (rigid-rigid) | Flag |
  |---|---|---|---|---|---|---|
  | thin / large ΔT | 0.1 mm | 10 K | 25 °C | ≈ 0.20 | 1.2·10⁻⁴ | False |
  | shallow / lab ΔT | 1 mm | 1 K | 25 °C | ≈ 20 | 1.2·10⁻² | False |
  | deep / lab ΔT | 10 mm | 1 K | 25 °C | ≈ 2.0·10⁴ | 11.8 | True |
  | deep / tight ΔT | 10 mm | 0.1 K | 25 °C | ≈ 2.0·10³ | 1.18 | True (marginal) |
  | deep / sub-mK ΔT | 10 mm | 0.01 K | 25 °C | ≈ 2.0·10² | 0.12 | False |

  Tests:
  - `test_rayleigh_anchor_shallow_lab_dT` — h=1mm, ΔT=1K, T=25°C:
    Ra within 5 % of 20 (hand-derived against the formula and the
    α / κ values pinned in the module).
  - `test_rayleigh_anchor_deep_lab_dT` — h=10mm, ΔT=1K, T=25°C:
    Ra within 5 % of 2.0·10⁴.
  - `test_threshold_round_trip` — Ra exactly at Ra_c is False
    (strict inequality); Ra_c·(1+1e-12) is True.
  - `test_rigid_free_threshold_lower` — same Ra value evaluated
    at `boundary='rigid-free'` flips True at Ra_c_RF ≈ 1100.65
    even though it was False at Ra_c_RR ≈ 1707.76.
  - `test_thin_cell_not_convective_at_any_realistic_dT` — h=0.1mm
    at ΔT=10K stays Ra ≪ Ra_c (Ra ≈ 0.2; flag False).
  - `test_marginal_deep_cell` — h=10mm, ΔT=0.1K, T=25°C: Ra ≈
    2.0·10³, flag True at rigid-rigid (~18 % above threshold) and
    flag True at rigid-free.
  - `test_alpha_handles_4C_inversion` — α(277.15 K) (≈ 4 °C) is
    tiny but positive; α(278.15 K), the v0.2 §5 lower temperature
    boundary (5 °C), is small and positive (~1.6·10⁻⁵ K⁻¹);
    α(275.15 K) is negative. The Phase-11 lab note pins the
    convention: take `Ra > Ra_c` strictly using signed α, so that
    anomalous-density cells with α < 0 cannot flip the flag —
    convection there is not Rayleigh-Bénard in the standard sense.
  - `test_alpha_matches_iapws95_sanity_values` — loose 5 %
    cross-check against IAPWS-95 reference values at 5 / 25 / 35 °C
    and 0.101325 MPa. Tanaka remains the implementation source of
    truth.
  - `test_rejects_nonpositive_depth` — `rayleigh_number` follows
    the rest of the cell APIs and rejects `h <= 0`.

### Audit-gap pin introduced

`DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1 K` becomes the fourth audit-
gap pin in the repo (after `T_OBS_S`, the 5th-depth value, and
the 10-nm regime-map fallback floor). Note this is a *notebook-
side* convention, not the `classify_cell` API default — the API
default stays at 0.0 K (forward-compat). Recorded in
`docs/deliverable-index.md` "Known caveats" and the Phase 11 lab
note.

### Exit criteria

- All new tests in `tests/test_convection.py` pass.
- v0.1 tests still pass: the API default `delta_T_assumed = 0.0 K`
  produces `Ra ≡ 0` and `convection_flag ≡ False`, leaving the
  §5.1 regime label and the cache CSV's regime columns
  equal to the post-9.3 main baseline (exact labels,
  machine-precision numeric channels). Notebook overlays
  that pass `DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1 K` are a separate
  rendering pass and do not affect the cache.
- ruff clean.
- Phase 11 lab note covers the rigid-rigid-vs-rigid-free choice,
  α(T) form, κ value, the 0.0 K vs 0.1 K API-vs-experimental
  default split, and the 4 °C inversion handling.

### Risks

- **α(T) sign flip at 4 °C** (water density max). For the
  breakout-note 5–35 °C scan range, α is positive throughout, but
  the 5 °C grid point is close to the inversion and α there is
  small (~10⁻⁵ K⁻¹ vs ~3·10⁻⁴ at 35 °C). Mitigation: use a
  literature polynomial fit valid for 0–40 °C; pin the value at
  every §5 temperature in the test suite.
- **Choice of κ as T-independent.** At v0.2 this is a documented
  approximation. Promotion to T-dependent costs nothing at runtime
  but adds a calibration pin.
- **ΔT default.** 0.1 K is conservative for a thermostatted
  laboratory bench. Higher values (e.g. 1 K for an unattended
  cell) flip the flag for many more cells. The default is an
  audit-gap pin; *experimental* users override.
- **Failure-surface change.** `classify_cell` computes the
  convection side channel before the homogeneous / equilibrated
  short-circuits return. Temperatures outside the water-property
  calibration range therefore now fail even for cells that would
  previously have short-circuited. This is acceptable because the
  Rayleigh calculation needs the same `ρ(T)` / `η(T)` validity
  envelope, but the Phase 11 lab note records the change.

### Phase 11.1 (review fixes, anticipated)

Review fixes applied after Phase 11: independent IAPWS-95 sanity
values for α(T), non-positive-depth rejection in `rayleigh_number`,
the 4 °C / 5 °C wording fix above, and explicit documentation of
the new convection-side-channel failure surface. ~0.25 d.

---

## 4. Phase 12 — Hydrodynamic-vs-material radius split

**Goal.** Separate the radius that sets buoyant mass from the
radius that sets drag/diffusion, with `δ_shell = 0` reproducing
v0.1 to machine precision.

### Physics

- `m_eff = (4/3) π r_material³ Δρ` — depends on `r_material`.
- `γ = 6 π η r_hydro` — depends on `r_hydro = r_material + δ_shell`.
- `D = k_B T / γ` — depends on `r_hydro`.
- `v_sed = m_eff g / γ` — depends on both.
- `ℓ_g = k_B T / (m_eff g) = D / v_sed` — independent of
  `δ_shell` (the ratio cancels).

The last identity is the key invariant: equilibrium *concentration
profiles* are insensitive to `δ_shell`; only *timescales* (`v_sed`,
`D`, `t_relax`) are affected.

### Data-model decision (accepted before Phase 12)

The cache and public summaries must carry both radii explicitly.
There is no single unqualified "radius" once `δ_shell != 0`.

- `r_material_m` sets buoyant mass, scale height, equilibrium
  profiles, `top_to_bottom_ratio`, and `bottom_mass_fraction`.
- `r_hydro_m` sets Stokes drag, Stokes-Einstein diffusivity,
  `v_sed`, `t_relax`, and `t_settle`.
- `delta_shell_m = r_hydro_m - r_material_m` is recorded wherever
  a row-level summary could otherwise look inconsistent.
- `radius_m` / `r_m` are retained only as v0.2 compatibility aliases
  for `r_material_m` in Python APIs and human-facing tables. New CSV
  columns and new tests use the explicit names.
- `RegimeGrid.radii` remains the field name for notebook
  compatibility and is documented as the material-radius coordinate
  axis. New properties `RegimeGrid.r_material` and
  `RegimeGrid.r_hydro` may be added, but notebooks 02-04 must not be
  forced to rename `grid.radii` during v0.2.
- CSV parsing uses a dedicated `_detect_csv_format(header)` helper
  with explicit handling for all cache formats in the wild:
  1. v0.1: `radius_m`, no `convection_flag`;
  2. Phase 11: `radius_m` plus `convection_flag`;
  3. Phase 12+: `r_material_m`, `r_hydro_m`,
     `delta_shell_m`, plus `convection_flag`.
  Any `radius_m` input maps to
  `r_material_m = r_hydro_m = radius_m` and
  `delta_shell_m = 0.0`; missing `convection_flag` maps to `False`.

### Deliverables

- **`src/parameters.py`** changes:
  ```python
  @dataclass(frozen=True)
  class ParticleGeometry:
      """r_material sets buoyant mass; r_hydro = r_material + δ_shell sets drag/diffusion.

      Default δ_shell = 0 reproduces v0.1 (single-radius) arithmetic.
      """
      r_material_m: float
      delta_shell_m: float = 0.0

      @property
      def r_hydro_m(self) -> float:
          return self.r_material_m + self.delta_shell_m

      @property
      def radius_m(self) -> float:
          """v0.2 compatibility alias for r_material_m."""
          return self.r_material_m

      @classmethod
      def from_radius(cls, r: float) -> "ParticleGeometry":
          """v0.1-compatible single-radius constructor."""
          return cls(r_material_m=r, delta_shell_m=0.0)
  ```

- **`src/parameters.py` primitives** keep the existing public names
  polymorphic, with `@overload` signatures for
  `float | ParticleGeometry`; scalar floats are coerced via
  `ParticleGeometry.from_radius`:
  - `buoyant_mass(radius_or_geom, T, rho_p)` ← uses
    `geom.r_material_m`.
  - `gamma_stokes(radius_or_geom, T)` ← uses `geom.r_hydro_m`.
  - `diffusivity(radius_or_geom, T)` ← uses `geom.r_hydro_m`.

- **`src/analytical.py`** primitives propagate `geom` through:
  - Add explicit `_geom` suffixed primaries for the geometry-aware
    implementation: `scale_height_geom`, `settling_velocity_geom`,
    `equilibration_time_geom`, `settling_time_geom`,
    `top_to_bottom_ratio_geom`, `barometric_profile_geom`, and
    `cell_summary_geom`.
  - Keep existing unsuffixed functions (`scale_height`,
    `settling_velocity`, etc.) as scalar-radius wrappers for v0.1
    callers and notebooks. This avoids polymorphic public Method-A
    docstrings and keeps the old hot path readable.
  - Geometry primaries use `r_material_m` for mass / equilibrium
    quantities and `r_hydro_m` for drag / diffusivity / timescales.
  - `cell_summary(...)` gains explicit
    `"r_material_m"`, `"r_hydro_m"`, and `"delta_shell_m"` keys.
    `"r_m"` remains through v0.2 as a compatibility alias equal to
    `"r_material_m"`. The reported `"gamma_N_s_per_m"` and
    `"D_m2_per_s"` must be internally consistent with
    `"r_hydro_m"`, not `"r_m"`.

- **`src/langevin.py` `simulate_cell`** and **`src/fokker_planck.py`
  `solve_cell`** accept `ParticleGeometry` (or scalar r for
  back-compat).

- **`src/regime_map.py` `classify_cell`** accepts
  `float | ParticleGeometry` in its first positional parameter,
  typed with `@overload` and internally coerced once at the top of
  the function. The existing call style
  `classify_cell(radius_m, T, h, t_obs_s=...)` remains valid; no
  separate `classify_cell_geom` public function is introduced.

- **`src/regime_map.py` cache data model**:
  - `RegimeResult` replaces the persisted `radius_m` field with
    `r_material_m` and adds `r_hydro_m`. A Python compatibility
    property `radius_m` returns `r_material_m` for v0.2 callers.
  - `results_from_csv` delegates header interpretation to
    `_detect_csv_format(header)`, then maps legacy rows as described
    in the data-model decision above.
  - `RegimeGrid.radii` stays as the material-radius coordinate axis.
    `RegimeGrid.r_material` may alias it, and `RegimeGrid.r_hydro`
    is an aligned axis / channel. Any downstream calculation that
    needs drag or diffusion must use `r_hydro`.
  - Phase 13's cache diff therefore expects the old `radius_m`
    column to be superseded by `r_material_m` + `r_hydro_m`; label
    equality and numeric-channel equality are still judged against
    the post-9.3 baseline at `δ_shell = 0`.

- **`tests/test_hydrodynamic_split.py`** (new file):
  - `test_default_geometry_reproduces_v01_buoyant_mass` —
    `ParticleGeometry(r_material_m=1e-7).r_hydro_m == 1e-7`.
  - `test_delta_shell_doubles_drag_when_equal_to_r_material` —
    `δ_shell_m = r_material_m` ⇒ `r_hydro_m = 2·r_material_m` ⇒ `γ`
    doubles, `D` halves, `v_sed` halves, `ℓ_g` unchanged
    (within float precision).
  - `test_equilibrium_profile_invariant_under_delta_shell` —
    `barometric_profile` at fixed `r_material_m` is identical for
    `delta_shell_m = 0` and `delta_shell_m = 10 nm`.
  - `test_relaxation_time_doubles_when_r_hydro_doubles` —
    `delta_shell_m = r_material_m` (i.e. `r_hydro_m = 2 r_material_m`)
    halves `D`. With `ℓ_g` unchanged and `t_relax = min(h, ℓ_g)²
    / D`, `t_relax` *doubles* (the squared-length factor is
    `r_hydro`-independent because `ℓ_g` is set by the *material*
    radius). Pin to `2.0` within `1e-12` rel-tol.
  - `test_regime_result_carries_both_radii` — a nonzero shell stores
    `r_material_m` and `r_hydro_m` distinctly in `RegimeResult` and
    in CSV output.
  - `test_cell_summary_reports_explicit_radii` — `gamma` and `D`
    agree with `r_hydro_m`; `m_eff` and `ell_g` agree with
    `r_material_m`; `r_m == r_material_m` only as a compatibility
    alias.
  - `test_detect_csv_format_accepts_v01_phase11_and_v12_headers` —
    pins all three header formats before the parser is used by the
    cache reader.
  - `test_regime_grid_keeps_radii_axis_alias` — `grid.radii` remains
    available and equal to the material-radius axis after the
    Phase-12 schema change.

### Phase 12.1 — regression audit (separate session)

Run the entire post-9.3 main baseline suite at the new API with
default `delta_shell_m = 0`. Every pre-existing test must pass
unchanged. Numerical snapshots from the post-9.3 main baseline
(anchor-cell numbers in notebook 01, the §5 grid cache) must match
to machine precision (`rtol <= 1e-15` for nonzero float channels;
exact equality for labels, booleans, and integer path codes).

This is the forward-compatibility contract enforced.

If any test fails or any snapshot drifts beyond the documented
tolerance, Phase 12.1 is in-progress until the drift is identified
and fixed before Phase 13 starts.

### Audit-gap pin introduced

`δ_shell = 0` is the v0.2 default. Becomes the fifth audit-gap pin
when promoted to a deliberate experimental setting (rather than a
back-compat default). Recorded in the deliverable index.

### Exit criteria

- All pre-existing tests pass at `delta_shell_m = 0` (Phase 12.1
  contract).
- All new tests in `tests/test_hydrodynamic_split.py` pass.
- ruff clean.
- Phase 12 lab note documents the API change strategy
  (`ParticleGeometry` + back-compat constructor).
- Phase 12.1 lab note documents the snapshot-comparison evidence.

### Risks

- **Surface area of refactor.** `ParticleGeometry` propagates through
  3 public primitives in `parameters.py`, 8 Method-A public functions
  in `analytical.py`, `langevin.simulate_cell`,
  `fokker_planck.solve_cell` / `equilibrium_cell`,
  `regime_map.classify_cell` / `walk_grid` / CSV / `RegimeGrid`, four
  notebooks, and multiple test files. High blast radius for typos and
  signature drift. Mitigation: keep the old scalar-r entry points as
  wrappers for the entire v0.2 cycle; test wrappers explicitly; CI
  catches notebook-side breakage.
- **Notebook signature breakage.** Notebooks 01–04 currently call
  `analytical.scale_height(r, T)`. If we change the primary
  signature to `(geom, T)`, every notebook line breaks. Mitigation:
  keep the scalar-r form callable; deprecate the scalar form as
  a separate v0.3 task if at all.
- **Ambiguous cached radius.** A single `radius_m` field is unsafe
  once `delta_shell_m != 0`. Phase 12 is blocked on the explicit
  `r_material_m` / `r_hydro_m` cache schema above; do not implement
  the radius split until that schema is in place.

---

## 5. Phase 13 — §5 cache regeneration

**Goal.** Re-walk the §5 grid so every cell carries the new
`convection_flag` channel, without any change to existing label
columns.

### Deliverables

- **`src/regime_map.py`** CSV writer/reader updated for the new
  column (back-compat: reading a v0.1-format CSV without the
  column is allowed, with `convection_flag = False` filled in).
- **`notebooks/data/regime_map_grid.csv`** regenerated. File size
  grows with `convection_flag` and, after Phase 12, the explicit
  `r_material_m` / `r_hydro_m` schema. Tests pin the before/after
  diff:
  - regime label columns are exactly equal
  - top_to_bottom_ratio columns match to machine precision
  - bottom_mass_fraction columns match to machine precision
  - `convection_flag` column is new and all-False in
    compatibility-mode cache generation
  - `r_material_m == r_hydro_m == old radius_m` at
    `delta_shell_m = 0`

- **`tests/test_regime_map.py`** additions:
  - `test_csv_back_compat_reads_pre_v02_format` — a CSV without
    the `convection_flag` column (e.g. the post-9.3 main cache
    or the historical `pilot-v0.1` cache) still loads, with the
    flag column synthesised as all-False.
  - `test_v02_label_columns_match_post_9_3_main` —
    snapshot test that the new cache's `regime`,
    `top_to_bottom_ratio`, and `bottom_mass_fraction` columns are
    equal to the post-9.3 main cache (the forward-compat target:
    exact labels, machine-precision floats). Hard-fails on any
    drift beyond tolerance.

### Compute

~150 min wall-time on the Phase 6 reference machine. Roughly the
same as v0.1's walk; the convection check itself is sub-microsecond
per cell.

### Cache-derived artefact regeneration (notebook 02–04, design
tables, etc.)

All cache-derived artefacts must be regenerated after the cache
walk and committed. This phase is not merely a re-run: notebooks
02 / 03 need explicit code edits for the experimental convection
overlay using `DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1 K`, while
notebook 04 must remain compatibility-mode for design-table
semantics. After those edits, the compatibility-mode plotted data
and design-table CSV/Markdown should produce zero semantic diffs
apart from the intentional overlay / schema additions — if not,
it's a Phase 13 bug to investigate before merging.

### Exit criteria

- New cache committed; diff against the post-9.3 main cache is
  empty for regime labels, and machine-precision equal for ratio /
  bmf columns. Intentional additions: `convection_flag`, explicit
  radius schema columns, and any documented overlay artefacts.
- Cache-derived notebook outputs regenerated; semantic diffs limited
  to intentional overlay / schema additions.
- Phase 13 lab note records the wall time and confirms the diff
  invariants.

### Risks

- **Convection flag changes the §5.1 regime label.** Should not —
  the flag is a side channel. But a coding bug that wires it into
  the label is the most likely failure mode. The
  `test_v02_label_columns_match_post_9_3_main`
  snapshot test is the guard.
- **New pathological Method-C cells surface during the re-walk
  (Phase 9.3 lesson).** Phase 9.3 found 8 false-homogeneous
  boundary cells that the 240-cell refinement corrected. v0.2's
  re-walk inherits that refinement, but if the convection-channel
  plumbing accidentally changes a Method-C parameter or short-
  circuit boundary, similar flips could appear. Mitigation:
  same snapshot test as above (labels exact; numeric channels
  machine-precision equal to
  post-9.3 main); if it fails, treat as a Phase 13 bug, not a
  legitimate update. A targeted-repair path that re-runs only
  the flipped cells at higher mesh fidelity is available as a
  fallback (the Phase-9.3 refinement code is the prototype).
- **Wall time blowout.** Low-likelihood (the convection check is
  sub-µs per cell), but if it happens the walk_grid is already
  process-pool friendly via the `radii / temperatures / depths /
  t_obs` axis subsetting; a manual split into per-temperature
  slices would let an 8-core machine finish in ~20 min instead
  of ~150.

---

## 6. Phase 14 — Polydispersity post-processing

**Goal.** Convolve the §5 sharp-radius classification against
`P(r | r̄, σ_geom)` to produce probabilistic regime labels and a
deliverable-6 design table for realistic experimental ensembles.

### Physics

A real particle preparation has a distribution of radii. For a
log-normal distribution with geometric mean `r̄` and geometric
standard deviation `σ_geom`:

```text
P(ln r | r̄, σ_geom) = Normal(ln r; mean=ln r̄, std=ln σ_geom)
```

The probabilistic classification at `(r̄, σ_geom, T, h, t_obs)` is
the integral of `regime_label(r, T, h, t_obs)` against
`P(r | r̄, σ_geom)`. The §5 grid cache supplies the regime label
at the discrete §5 r-axis points; the smear is computed by
**bin-mass quadrature** — CDF differences over geometric bin
edges — *not* PDF-times-Δr at grid points:

1. Build §5 r-axis bin edges in log-space: the geometric mid-
   points between consecutive §5 r values, with end-bins
   extended by half a §5 log-bin so the outer edges sit at
   `[r_min · √(r₂/r₁) ⁻¹, r_max · √(r_N/r_{N-1})]`.
2. For each §5 r-axis bin `i`, compute
   `wᵢ = lognormal_cdf(r_edge_{i+1}; r̄, σ_geom)
       − lognormal_cdf(r_edge_i; r̄, σ_geom)`.
   This is exact in log-space for a log-normal — no quadrature
   error from the §5 grid spacing.
3. Compute the truncation diagnostic
   `w_total = lognormal_cdf(r_edge_N; r̄, σ_geom)
            − lognormal_cdf(r_edge_0; r̄, σ_geom)`.
   `1 − w_total` is the fraction of probability mass outside the
   §5 r-axis. Strict single-cell calls reject inputs (raise
   `ValueError`) when `w_total < 0.95` — the v0.2 acceptance is
   "no more than 5 % of the distribution falls outside §5". Grid /
   table calls carry `truncation_loss = 1 - w_total` and an
   `accepted` mask so deliverables can mark rejected cells rather
   than silently omitting rows.
4. Look up the regime at each §5 r-bin from the cache and
   accumulate the bin masses into the three regime buckets
   `p_homogeneous`, `p_stratified`, `p_sedimented`.
5. Renormalise the buckets by `w_total` so they sum to 1
   exactly. This is the conservation invariant: `p_H + p_S +
   p_s ≡ 1` to machine precision at every accepted cell.
6. The expected-value channels
   `expected_top_to_bottom_ratio = Σᵢ wᵢ · ratioᵢ / w_total` and
   `expected_bottom_mass_fraction = Σᵢ wᵢ · bmfᵢ / w_total` are
   weighted means over the §5 r-axis at fixed (T, h, t_obs).

The CDF-based form is exact in log-space; the §5 r-axis does not
need to be finer for any σ_geom in the planned axis (1.05–1.60).
The truncation diagnostic is a hard gate at the 5 % loss boundary
for strict calls; deliverable tables must expose the same diagnostic
as data so users can see which `(r̄, σ_geom)` cells sit outside the
§5 cache support.

### Deliverables

- **`src/polydispersity.py`** (new module):
  ```python
  def lognormal_pdf(r: float, r_geom_mean: float, sigma_geom: float) -> float: ...
  def lognormal_cdf(r: float, ...) -> float: ...

  @dataclass(frozen=True)
  class SmearedGrid:
      r_geom_mean_axis: tuple[float, ...]
      sigma_geom_axis: tuple[float, ...]
      temperatures: tuple[float, ...]
      depths: tuple[float, ...]
      t_obs: tuple[float, ...]
      p_homogeneous: NDArray[np.float64]   # shape (n_r̄, n_σ, n_T, n_h, n_t)
      p_stratified: NDArray[np.float64]
      p_sedimented: NDArray[np.float64]
      expected_top_to_bottom_ratio: NDArray[np.float64]
      expected_bottom_mass_fraction: NDArray[np.float64]
      truncation_loss: NDArray[np.float64]
      accepted: NDArray[np.bool_]

  def lognormal_smear(
      grid: RegimeGrid,
      r_geom_mean_axis: NDArray[np.float64] | None = None,
      sigma_geom_axis: NDArray[np.float64] = SIGMA_GEOM_AXIS,
      *,
      min_covered_mass: float = 0.95,
      on_truncation: Literal["raise", "mask"] = "raise",
  ) -> SmearedGrid: ...
  ```

  `r_geom_mean_axis=None` means `np.asarray(grid.r_material)` (the
  §5 material-radius axis). `SIGMA_GEOM_AXIS` lives in
  `src/polydispersity.py`, not `scan_grid.py`, because
  polydispersity is post-processing and not a §5 scan axis.

- **`notebooks/05_polydispersity_smearing.py`** (new):
  - **Figure 1** — probabilistic regime triptych (RGB) at room T,
    h = 1 mm, t_obs = 1 h: a 2-D grid in (r̄, σ_geom) with
    `(p_H, p_S, p_s)` mapped to (R, G, B).
  - **Figure 2** — σ_geom sensitivity strip at the §5 anchor cell
    (r̄ = 100 nm, T = 25 °C, h = 1 mm). σ_geom from 1.0 (delta) to
    1.5 (broad). Shows the three regime probabilities as functions
    of σ_geom.
  - **Figure 3** — experimental-suitability map: `(r̄, σ_geom)` grid
    coloured by `p_stratified` at fixed t_obs = 1 h. Identifies the
    "useful preparation" envelope.

- **`notebooks/data/design_table_polydispersity_room_T.md`**
  (deliverable 6): for target `p_stratified ≥ 0.8` at t_obs = 1 h,
  the admissible `(r̄, σ_geom)` envelope per `(T, h)`. Rows whose
  log-normal tails lose more than 5 % outside the §5 r-axis are not
  omitted; they are marked `rejected_truncation` and include a
  `truncation_loss` diagnostic.

- **`tests/test_polydispersity.py`** (new):
  - `test_degenerate_limit_recovers_sharp_labels` — `σ_geom = 1.001`
    (essentially delta) at an `r̄` placed exactly on a §5 r-axis
    point gives `(p_H, p_S, p_s)` matching the cached sharp
    label vector to within 1 %.
  - `test_conservation_at_every_cell` — `p_H + p_S + p_s = 1` at
    every accepted `(r̄, σ_geom, T, h, t_obs)` to machine
    precision.
  - `test_truncation_rejection` — strict mode with `r̄ = 1 nm,
    σ_geom = 1.05` (well below the §5 r-axis floor of 5 nm) raises
    `ValueError` because `w_total < 0.95`.
  - `test_truncation_mask_mode_marks_rejected_cells` — table mode
    returns `accepted=False` and a finite `truncation_loss`, so
    deliverables can show rejected cells explicitly.
  - **Anchored regression tests** (replacing the abstract
    monotonicity claim — the regime map is discrete and not
    globally monotone in σ_geom across all cells):
    - `test_smear_at_homog_anchor_broadens_into_stratified` —
      anchor at `r̄ = 5 nm, T = 25 °C, h = 1 mm, t_obs = 1 h`
      (homogeneous in v0.1). Expect `p_stratified` to rise
      strictly from `σ_geom = 1.05` to `σ_geom = 1.40`
      because the upper tail of the broader distribution
      crosses the homogeneous→stratified §5 boundary.
    - `test_smear_at_sedim_anchor_broadens_into_stratified` —
      anchor at `r̄ = 1 µm, T = 25 °C, h = 1 mm, t_obs = 1 d`
      (sedimented in v0.1). Expect `p_stratified` to rise
      strictly across the same σ_geom sweep because the lower
      tail crosses the stratified→sedimented boundary.
    - `test_smear_at_strat_anchor_dilutes_at_high_sigma` —
      anchor at `r̄ = 100 nm, T = 25 °C, h = 1 mm, t_obs = 1 h`
      (stratified in v0.1). Expect `p_stratified` to *fall*
      from `σ_geom = 1.05` to `σ_geom = 1.60` because both
      tails leak into the H and sed bands.
    Each test pins specific numerical values; we don't claim a
    universal "increases until it dominates, then decreases"
    invariant.
  - `test_smear_axis_extension_outside_§5_r_axis` — `r̄ < 5 nm` or
    `r̄ > 10 µm` (with non-trivial σ_geom) is rejected with a
    clear error via the truncation gate above. The §5 cache has
    no support outside its axis; extrapolation is out of scope.

### Audit-gap pin introduced

`σ_geom` axis values are an audit-gap pin (the breakout-note v0.2
spec doesn't list a polydispersity axis). The pinned values for
the deliverable-6 table are recorded in `src/polydispersity.py` as
`SIGMA_GEOM_AXIS = (1.05, 1.10, 1.20, 1.40, 1.60)`. Do not put this
axis in `src/scan_grid.py`: `scan_grid.py` remains the single source
of truth for the breakout-note §5 axes only. Per ADR 0001 the
breakout-note authors decide if and when `σ_geom` gets promoted to a
§5 axis.

### Exit criteria

- All new tests in `tests/test_polydispersity.py` pass.
- Notebook 05 renders cleanly headless; figures committed.
- Deliverable-6 design table committed.
- Phase 14 lab note documents the discretisation choice (sum over
  §5 r-axis vs. finer interpolation), the σ_geom axis, truncation
  handling / table markers, and the conservation evidence.

### Phase 14.1 (review fixes, anticipated)

Likely review hits: the truncation-acceptance threshold
(95 % vs 99 %?), the deliverable-6 `p_stratified` target
(0.8 vs 0.95?), σ_geom axis spacing (5 vs 7 points), and any
edge-case behaviour at the §5 r-axis end-bins. ~0.25 d.

### Risks

- **Discretisation error.** Summing over the 30-point §5 r-axis
  may underestimate the integral for small σ_geom (delta-like
  distribution that misses §5 grid points) or overestimate at the
  large-σ tails. Mitigation: in the Phase 14 lab note, document the
  expected error bound; if tests at small σ_geom show > 5 % drift
  from the sharp v0.1 labels, switch to finer interpolation.
- **Boundary effects.** A log-normal distribution has support on
  `(0, ∞)`, but the §5 r-axis covers only [5 nm, 10 µm]. Tail
  truncation matters for very broad σ_geom and near the 5 nm /
  10 µm edges. Mitigation: report `truncation_loss` as a
  diagnostic; strict APIs reject inputs where truncation loses more
  than 5 % of probability, while deliverable-table mode marks
  rejected cells explicitly instead of leaving gaps.

---

## 7. Phase 15 — Release `pilot-v0.2`

**Goal.** Tag the v0.2 cycle complete and ship.

### Deliverables

- **`docs/findings-physics.md`** gains:
  - §"Convection caveat at h ≥ 1 mm" — analyse where the
    convection_flag fires across the §5 grid; flag the
    h ≥ 1 mm corner as needing experimental ΔT control.
  - §"Polydispersity broadens regime boundaries" — quantify how
    σ_geom shifts the homogeneous-edge and sedimented-edge §5
    radii.

- **`docs/findings-process.md`** gains a Pattern 14:
  "Forward-compatible parameter splits via zero-default extension"
  (the `ParticleGeometry` and `σ_geom` patterns generalise).

- **`docs/deliverable-index.md`** updates:
  - Pin block: tag → `pilot-v0.2`; suite count → new value.
  - §6 deliverable mapping: deliverable 6 row added.
  - §4.4 validation surfaces: convection round-trip, smear
    conservation, smear monotonicity tests added.
  - "Known caveats" section: add `δ_shell = 0`,
    `delta_T_assumed = 0.1 K`, `σ_geom` axis pin.
  - "What `pilot-v0.3` would change" section (parallel to v0.1's
    "What `pilot-v1.0` would change").

- **`docs/experimental-envelope.md`** (new — Veto-2 closeout from
  the work-plan stance line). Distinguishes pilot assumptions
  (dilute, monodisperse, non-interacting, Stokes, no aggregation)
  from experimental regime variables (aggregation, polydispersity,
  wall hydrodynamics, adsorption, surfactants, T-control). Maps
  each pilot assumption to the experimental knob that, when
  perturbed, breaks the assumption — with a pointer to whether v0.2
  addresses the perturbation (polydispersity, δ_shell) or defers
  it (aggregation, wall corrections).

- **`README.md`** phase table extended through Phase 15;
  status block bumped to "`pilot-v0.2` released".

- **`pyproject.toml`**: `0.1.0` → `0.2.0`, Development Status
  classifier reviewed (probably stays `3 - Alpha`; if all v0.1
  audit-gap pins resolve in v0.2, consider `4 - Beta`).

- **Annotated tag `pilot-v0.2`** with release notes pointing to
  the deliverable index, the findings narrative, and the new
  `experimental-envelope.md`.

### Tag acceptance criteria

The `pilot-v0.2` tag is created when *all* of these hold on `main`:

- [ ] Forward-compatibility contract satisfied (Phase 12.1 evidence
      committed).
- [ ] All new Phase 11 / 12 / 13 / 14 tests pass.
- [ ] All v0.1 tests still pass (CI green).
- [ ] ruff clean.
- [ ] §5 cache re-walked; cache-derived artefacts regenerated.
- [ ] Deliverable index updated; §6 deliverable 6 row populated.
- [ ] Findings narratives extended; the two new §sections exist.
- [ ] `docs/experimental-envelope.md` shipped (Veto-2 closeout).
- [ ] ADR 0001 cross-referenced from Phase 15 lab note.
- [ ] Phase 15 lab note records HEAD SHA before tagging,
      dependency versions, and the suite-count delta vs v0.1.
- [ ] `pyproject.toml` version bumped.

### Phase 15.1 (anticipated post-release doc fixes)

Pattern from every prior release. Reserved 0.25 d. Likely hits:
typos in the new findings sections, broken cross-references after
the doc additions, README phase-table-row format consistency.

---

## 8. Accepted decisions (D1-D6)

Review accepted the six design recommendations below. D1 is
intentionally split: the experimental default is informative
(`0.1 K`), while the programmatic API and cache-generation default
remain in compatibility mode (`0.0 K`) so v0.1 outputs reproduce
exactly.

### D1. `delta_T_assumed` convention

Decision: **`DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1 K`** for
notebooks, figures, and experimental-facing overlays;
**`classify_cell(..., delta_T_assumed=0.0 K)`** remains the API
default and the cache-generation setting.

Reasoning: 0.1 K is the practically useful laboratory hysteresis
scale, so experimental consumers see an informative side-channel
flag without needing to discover an opt-in. The forward-
compatibility contract protects the §5.1 regime labels and the
compatibility-mode cache, which remain unchanged at
`delta_T_assumed = 0.0 K`.

### D2. `boundary` default — `"rigid-rigid"` or `"rigid-free"`?

Closed (capped) cuvettes are rigid-rigid; open (uncovered)
cuvettes are rigid-free. The breakout note (v0.2 §3) does not
specify cuvette closure.

Decision: **`"rigid-rigid"`** as the default — closed cuvettes
are the more controlled experimental mode and the more
conservative threshold (1707.762 vs 1100.65, requiring more ΔT to
flip). Document both constants; let users override via kwarg.

### D3. `α(T)` polynomial fit — which reference?

Standard references for water thermal expansion include Kell
(1975), the IAPWS R6-95 formulation, and various engineering
handbooks. Pick one. v0.1 used Tanaka (2001) for ρ(T); a
Tanaka-derivable α(T) is the most consistent choice (differentiate
the Tanaka form once).

Decision: **derive α(T) by differentiating Tanaka 2001**,
consistent with `parameters.rho_water`. Validate against IAPWS
R6-95 at 5 / 25 / 35 °C as a sanity check; if the discrepancy is
larger than ~5 %, treat that as a Phase-11 review item rather than
silently switching references.

### D4. `σ_geom` axis values — five points or seven?

The deliverable-6 design table needs a small sweep. Five points
(`{1.05, 1.10, 1.20, 1.40, 1.60}`) span "narrow" to "very broad".
Seven points (`{1.05, 1.10, 1.15, 1.20, 1.30, 1.45, 1.60}`)
resolve the small-σ corner better.

Decision: **five points**: `{1.05, 1.10, 1.20, 1.40, 1.60}`. The
deliverable-6 figure 2 (`σ_geom` sensitivity at the anchor cell)
covers the small-σ corner with its own axis; the table should stay
readable and experimental-facing. The axis is owned by
`src/polydispersity.py`, not `src/scan_grid.py`, because it is a
post-processing parameter rather than a §5 scan-grid axis.

### D5. `r̄` axis for polydispersity smearing — same as §5 r-axis or finer?

The §5 r-axis is 30 log-spaced points. For the smearing integral
the §5 r-axis is the *innermost* discretisation; the `r̄` axis is
where we *evaluate* the smeared classification. They can be the
same or different.

Decision: **`r̄` axis matches the §5 r-axis** (30 log-spaced
points, 5 nm to 10 µm). This reuses the existing infrastructure,
avoids interpolation logic, and gives the design table the same
row count as v0.1's homogeneous-edge table.

### D6. Convection flag in the design table?

Should deliverable 6 (the polydispersity design table) report
`convection_flag` per cell? The table is already in `(r̄, σ_geom,
T, h, t_obs)` space; adding a sixth dimension would explode the
table.

Decision: **no — convection flag stays in the regime-map cache**
(deliverable 5 / `regime_map_grid.csv`), separate from the
polydispersity design table. Cross-reference the convection-flag
column in the deliverable-6 prose so consumers know to consult
both outputs.

---

## 9. Risk register (cross-phase)

| Risk | Phase | Severity | Mitigation |
|---|---|---|---|
| Phase 12 refactor regresses v0.1 outputs | 12 / 12.1 | High | Phase 12.1 regression audit; CI; back-compat scalar-r entry points retained for the cycle |
| Phase 12 cache / summary rows carry ambiguous radius semantics | 12 / 13 | High | Explicit `r_material_m` / `r_hydro_m` / `delta_shell_m` schema accepted before implementation; old `radius_m` / `r_m` only compatibility aliases |
| Convection module silently changes §5.1 labels | 11 / 13 | High | Snapshot test against post-9.3 main cache (Phase 13 exit criterion: labels exact; numeric channels machine-precision equal) |
| Cache regen surfaces new pathological Method-C cells (Phase 9.3 precedent: 8 false-homogeneous boundary cells flipped under refinement) | 13 | **Medium** | Snapshot test against post-9.3 main labels is the first guard. If new flips appear: (a) confirm they reproduce locally, (b) confirm they're driven by the new convection-flag code path or by an unintended Method-C parameter change, not by the legitimate refinement already in place. Mitigation toolkit: process-pool-friendly walk_grid signature (already in regime_map.py), explicit per-cell timeout, and a targeted-repair path that re-runs only the flipped cells at higher mesh fidelity. |
| Phase 13 notebook work underestimated as pure regeneration | 13 | Medium | Notebook 02 / 03 overlay code edits are explicit Phase 13 deliverables; regenerated artefact diffs must be explained as overlay / schema changes |
| Cache regen wall time blows out beyond ~150 min | 13 | Low | Convection check is sub-µs; if walk slows by > 10 % investigate before merge. Note Phase 9.3 already added the 240-cell threshold-adjacent refinement, so the v0.2 walk inherits the post-9.3 wall-time profile, not an unrefined v0.1 baseline. |
| Polydispersity discretisation error > 5 % at small σ_geom | 14 | Medium | Phase 14 test pins degenerate-limit error at 1 %; switch to finer interpolation if it fails |
| Polydispersity log-normal tail truncation > 5 % | 14 | Medium | Diagnostic + reject in `lognormal_smear` when truncation lossy |
| α(T) sign at 4 °C anomaly | 11 | Low | Test pins α(5 °C) sign; lab note explicit on convention |
| Breakout-note v0.3 lands during cycle, requiring re-anchoring | any | Low | ADR 0001 explicitly covers; treat as opportunity not blocker |
| Notebook signature breakage from `geom` propagation | 12 | Medium | Back-compat scalar-r entry points; CI runs notebooks headless |
| Phase 15 release misses an exit criterion | 15 | Low | Tag-acceptance checklist gated explicitly; Phase 15.1 buffers post-release fixes |

---

## 10. Schedule summary

| Phase | Wall time | Sequenceable with |
|---|---|---|
| 11 | 1 d | (parallel-safe with 12) |
| 11.1 | 0.25 d | after 11 |
| 12 | 1 d | (parallel-safe with 11) |
| 12.1 | 0.25 d | after 12 (and 11 if testing flag interactions) |
| 13 | 0.5 d compute + 0.25 d review | after 11 *and* 12 |
| 14 | 2 d | after 13 |
| 14.1 | 0.25 d | after 14 |
| 15 | 1 d | after 14.1 |
| 15.1 | 0.25 d | after 15 |
| **Total** | **~7 working days across ~10 sessions** | |

Calendar: 1.5–2 weeks at v0.1 working tempo.

---

## 11. Cross-references

- [`adr/0001-v0.2-spec-anchoring.md`](adr/0001-v0.2-spec-anchoring.md)
  — the spec-anchoring decision this work plan executes against.
- [`../lab_notes/2026-04-28-phase10-v0-2-scoping.md`](../lab_notes/2026-04-28-phase10-v0-2-scoping.md)
  — Phase 10 lab-note companion to the ADR.
- [`deliverable-index.md`](deliverable-index.md) — to be extended
  in Phase 15 with deliverable 6 + new §4.4 test pins + new
  audit-gap pins.
- [`findings-physics.md`](findings-physics.md) and
  [`findings-process.md`](findings-process.md) — to be extended in
  Phase 15.
- v0.1 release tag `pilot-v0.1` at commit `9a0fc76` — historical
  release reference. The forward-compatibility reference is the
  post-Phase-9.3 `main` baseline named in §1.

---

## 12. Acceptance / next step

This document is accepted as the v0.2-cycle contract. Phase 11 and
the Phase 11.1 review fixes are complete; Phase 12 is next. Changes
to scope, D1–D6, the Phase-12 radius schema, or the risk register
after this point require an explicit work-plan amendment before
implementation continues.
