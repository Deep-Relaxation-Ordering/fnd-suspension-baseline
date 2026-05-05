# Work plan — `pilot-v0.4`

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

| Field | Value |
|---|---|
| Status | **Accepted contract.** All open decisions (D1–D9) resolved. §1 in-scope list fixed against D1 = Option 2 and D9 = item B. §4 phase plan, §6 risk register, and §7 schedule filled. Phase 27 (S3 — Hydrodynamic-shell calibration per FND class) is cleared to open. |
| Date | 2026-05-05 (drafted Phase 25); 2026-05-06 (Phase 26 opening — D1 / D9 resolved; Phase 26 continuation — contract accepted) |
| Drafted at | post-Phase 24, commit `00f2fc7` (`pilot-v0.3` released; Pages landing page adopted) |
| Predecessor tag | `pilot-v0.3` at `ad48b0b` |
| Successor tag (proposed) | `pilot-v0.4` |
| Spec anchor | **breakout-note v0.2 commit `3b7b18af`** — Option 2, resolved by [ADR 0003](adr/0003-v0.4-spec-anchoring.md). Same pin as v0.2 / v0.2.1 / v0.3. |
| First implementation slice | **item B (S3 — Hydrodynamic-shell calibration per FND class)** ([`program-context.md` §3.1](program-context.md), [ADR 0003 Decision 2](adr/0003-v0.4-spec-anchoring.md)). See §1 item B. |
| Working tempo | v0.3 baseline: ~7 working days across ~10 sessions; calendar 1.5–2 weeks |

The structure mirrors [`work-plan-v0-3.md`](work-plan-v0-3.md). All
sections are filled; the v0.4 cycle is under contract and Phase 27
is cleared to open.

---

## 0. Spec anchoring — RESOLVED

**Decision: Option 2.** `pilot-v0.4` stays anchored to breakout-note
v0.2 commit `3b7b18af`. Recorded in
[ADR 0003 Decision 1](adr/0003-v0.4-spec-anchoring.md). Resolves
D1 in §5.

The original three options remain readable in the ADR for context:

1. ~~Re-anchor to breakout-note v0.3 if/when it lands~~ — blocked,
   upstream had not landed by Phase 26 opening (2026-05-06).
2. **Stay anchored to breakout-note v0.2 commit `3b7b18af`** —
   chosen.
3. ~~Hybrid~~ — rejected for per-slice bookkeeping cost.

**Consequence for §1.** Items that require a physics-scope expansion
beyond the v0.2 envelope (S1 aggregation, S6 wall hydrodynamics, S7
thermal control as first-class) are *not* in v0.4 scope; they are
parallel-breakout candidates or v0.5-and-later items. §1 reshape
(Phase 26 continuation) marks each item accordingly.

**Re-pin policy** if breakout-note v0.3 lands mid-cycle: ADR 0001 /
ADR 0002 precedent — the cycle's release phase picks up the new pin,
not earlier phases. Mid-cycle re-pinning would invalidate the
in-flight slices' reviewability anchor.

---

## 1. Scope candidates [OPEN — first slice fixed]

Each item below is a **candidate** drawn from
[`program-context.md` §3.1](program-context.md) (the L1 slice menu)
and from v0.3 audit-gap pins still open after Phase 24. Format per
item: motivation, source, rough effort, blast radius, decision
needed.

**First slice fixed: item B (S3 — Hydrodynamic-shell calibration
per FND class)** per [ADR 0003 Decision 2](adr/0003-v0.4-spec-anchoring.md).
The other items remain `[OPEN]` and are resolved during the §1
reshape (Phase 26 continuation).

The S-slice nomenclature follows [`program-context.md` §3.1](program-context.md)
as the authoritative source. The list in
[`deliverable-index.md`](deliverable-index.md) §"What `pilot-v0.4`
would change" and in [`release-notes/v0.3.md`](release-notes/v0.3.md)
§"What `pilot-v0.4` would change" uses different S-slice labels
inconsistent with program-context §3.1; reconciling those two
documents is item L below (a doc-fix housekeeping item for v0.4).

### A. S1 — DLVO aggregation pre-screen
- **Source:** [`program-context.md` §3.1](program-context.md), [`work-plan-v0-3.md` §1 item D](work-plan-v0-3.md#d-aggregation-pre-screen-dlvo-τ_aggζ-i-ph), v0.3 release notes "What v0.4 would change".
- **Why:** Layer-defining for L1 ([`program-context.md` §3.1 summary table](program-context.md#L222)). The killer assumption from breakout-note §7b — without a `τ_agg(ζ, I, pH)` channel, every regime-map cell is dishonest at the t_obs band the design table sits in. S1 owns the cell-by-cell trustworthiness flag.
- **Effort (rough):** ~3 d core implementation + ~1 d test scaffolding *if* the upstream breakout note exists at cycle open; indefinite if it does not.
- **Blast radius:** new module + side-channel against §5 cache, OR a separate sibling pilot. Not a §5.1 label override. Touches the `provisional=True` API contract from [ADR 0002 §"API surface"](adr/0002-v0.3-spec-anchoring.md): when S1 lands, the override pathway is removed (or replaced with a separate trustworthiness channel).
- **Upstream dependency:** `Deep-Relaxation-Ordering/diamonds_in_water` owes the breakout note. Status as of Phase 26 (2026-05-06): not yet drafted.
- **Decision:** **out-of-scope — defer to v0.5.** D3 = defer. Upstream had not landed by Phase 26 opening; under D1 = Option 2's "no calendar gating" stance, S1 waits for its upstream breakout rather than entering v0.4 under the supplier-failure clause. The `provisional=True` API contract from [ADR 0002 §"API surface"](adr/0002-v0.3-spec-anchoring.md#api-surface--the-provisionaltrue-contract) remains in force throughout v0.4 as a consequence.

### B. S3 — Hydrodynamic-shell calibration per FND class
- **Source:** [`program-context.md` §3.1](program-context.md) (S3 — Hydrodynamic-shell calibration); [v0.3 Phase 21 δ_shell calibration](../lab_notes/2026-05-01-phase21-mesh-convergence-and-shell-calibration.md); [`docs/delta_shell_calibration.md`](delta_shell_calibration.md) (provisional table).
- **Why:** v0.3 ships a *provisional* `delta_shell_m` calibration table marked as audit-gap pin. S3 promotes the provisional table to a calibrated default range per FND class (bare, carboxylated, hydroxylated, PEG-functionalised). Housekeeping (closes audit-gap pin) per [`program-context.md` §3.1](program-context.md) summary table.
- **Effort:** ~1–2 d if open-literature DLS is sufficient; longer if manufacturer collaboration is pursued.
- **Blast radius:** documentation + parameter defaults; no API change. The user-supplied knob remains; the default value gets a citation-anchored class identity.
- **Contingency:** manufacturer data may be NDA-bound. Per [`program-context.md` §3.1 S3](program-context.md), fallback is open-literature DLS only with affected batches flagged as "unverified" in metadata. The repo never blocks on proprietary data.
- **Decision:** **in-scope, first slice** ([ADR 0003 Decision 2](adr/0003-v0.4-spec-anchoring.md)). D2 = Option 1 — calibrated default per FND class is a documentation + parameter-default change; zero-default reproduction of v0.3 stays intact. D4 resolved.

### C. Promote `lambda_se` to §5 scan axis
- **Source:** [v0.3 release notes "What v0.4 would change"](release-notes/v0.3.md#what-pilot-v04-would-change) bullet "Promote `lambda_se` to §5 scan axis if calibrated working values are ≤ 0.3"; [`docs/work-plan-v0-3.md` item K](work-plan-v0-3.md#k-stokes-einstein-corrections-at-sub-150-nm-radii-first-slice).
- **Why:** v0.3 ships `lambda_se` as a single axis applied at compute time, with the §5 cache reproducing v0.2 byte-for-byte at `lambda_se = 1.0`. If the gold-NP calibration (Laloyaux z₂) shows working values consistently ≤ 0.3 in the FND-relevant band, a §5 cache schema bump that carries `lambda_se` as an axis is the next tightening — design-tool consumers can then compare across SE-correction strengths without recomputing.
- **Effort:** ~2 d (cache schema bump, dimension expansion, consumer updates) **gated on** the calibration result.
- **Blast radius:** §5 cache schema change (Pattern 14 zero-default extension); notebook consumers that read the cache need updates.
- **Decision:** **out-of-scope — defer to v0.5.** D5 = defer. The S2 calibration prerequisite has not been run in the FND band yet; running it inside v0.4 plus shipping the §5 axis promotion would exceed the cycle calendar. The calibration itself is captured as a pre-Phase-27 prerequisite to the eventual v0.5 axis decision.

### D. S4 — Capsule-geometry port (1-D radial in spherical coordinates)
- **Source:** [`program-context.md` §3.1 S4](program-context.md); [`work-plan-v0-2.md` §1 "Out of scope (parallel tracks)"](work-plan-v0-2.md#out-of-scope-parallel-tracks).
- **Why:** Layer-defining for L1. The simulator extends from 1-D Cartesian slab to 1-D radial coordinate in spherical geometry, for sealed micro-cells of diameter d = 10–100 µm. *Not* a full 3-D simulator (that is explicitly out of scope at every layer per [`program-context.md` §6](program-context.md#6-out-of-scope-explicit-deferrals--what-this-programme-is-not)).
- **Effort:** ~12 d per the v0.2 plan estimate (its own pilot cycle).
- **Blast radius:** new geometry module + Methods A/B/C ported to spherical Jacobians + sibling-repo breakout note required first.
- **Upstream dependency:** sibling-repo breakout note required.
- **Decision:** **out-of-scope — parallel pilot cycle.** Effort exceeds the v0.3 working-tempo envelope (~7 working days). S4 deserves its own dedicated cycle, post-v1.0. Recorded in §2.

### E. S5 — Concentration-weighted polydispersity kernel
- **Source:** [`program-context.md` §3.1 S5](program-context.md); v0.2 polydispersity (Phase 14) is classification-weighted.
- **Why:** v0.2 polydispersity layer is classification-weighted (each radius bin gets the §5.1 label and a probability). For tracking experiments, what matters is the *number-density* distribution within each band. Bounded change to `lognormal_smear`'s weighting kernel.
- **Effort:** ~1–2 d (kernel-weight refactor + tests + notebook 05 update).
- **Blast radius:** `polydispersity.py` + notebook 05 + deliverable 6 design table; no §5 cache change at compatibility-mode default.
- **Decision:** **in-scope.** D2 = Option 1 — kernel-weight refactor is additive; zero-default reproduction of v0.3's classification-weighted output stays intact for callers that don't opt into the number-density kernel. D6 resolved.

### F. S6 — Wall-hydrodynamic Faxén/Brenner corrections
- **Source:** [`program-context.md` §3.1 S6](program-context.md); [`work-plan-v0-3.md` item E](work-plan-v0-3.md#e-wall-hydrodynamic-correction).
- **Why:** Layer-defining for L1 (with "may defer to v1.1" qualifier). Position-dependent Faxén/Brenner corrections to drag and diffusivity near the sealed-cell boundary.
- **Effort:** ~2 d (correction term + `RegimeResult` channel + Method-C boundary-layer integration).
- **Blast radius:** Method-C cells where the bottom layer matters; introduces a near-wall dimensionless parameter (particle-wall separation / radius) and modifies Method A/B/C kernels.
- **Upstream dependency:** likely needs sibling breakout-note specs for boundary conditions.
- **Decision:** **out-of-scope — defer to v0.5 / v1.1.** Same reasoning as v0.3 work-plan §1 item E. Wall-hydrodynamic corrections exceed the breakout-note v0.2 envelope; deferral persists absent new motivation. Recorded in §2.

### G. S7 — Thermal control as first-class axis
- **Source:** [`program-context.md` §3.1 S7](program-context.md); [`work-plan-v0-3.md` item G](work-plan-v0-3.md#g-refined-convection-model-t-dependent-κ-gradient-profiles-evaporation).
- **Why:** Promote `delta_T_assumed` from its current side-channel status to a first-class axis where experimentally relevant. Sealed-cell thermal protocols and lateral gradients enter here. (Open-cell evaporation is *out of scope* — see [`program-context.md` §6](program-context.md#6-out-of-scope-explicit-deferrals--what-this-programme-is-not); S7 is sealed-cell only.)
- **Effort:** 1–2 d for κ(T); broader thermal-protocol support is a sub-phase.
- **Blast radius:** convection module + cache schema (extra column or recomputed flag). Even κ(T) alone changes §5 cache numerics by design — this is *not* a Pattern 14 zero-default extension; it is a deliberate cache regen.
- **Upstream dependency:** experimental-campaign repo (P-1 in [`program-context.md` §2](program-context.md#2-programme-prerequisites-and-risks)) for cooling protocol specifications. Not strictly blocking, but the protocol set drives the axis range.
- **Decision:** **out-of-scope — defer to v0.5 / v1.0.** Same reasoning as v0.3 work-plan §1 item G. Even κ(T) alone changes §5 cache numerics by design — this is *not* a Pattern 14 zero-default extension; it is a deliberate cache regen that needs campaign motivation (D-PC-1) before it earns a cycle slot. Recorded in §2.

### H. Persisting v0.3 review residue
- **Source:** to be enumerated during the §1 reshape ceremony. v0.3 review surface from [Phase 23 integration audit](../lab_notes/2026-05-01-phase23-integration-audit.md) and [Phase 24 release note](../lab_notes/2026-05-01-phase24-pilot-v0-3-release.md) reports clean state, but v0.4 should sweep for any residue once the cycle opens.
- **Why:** Standard cycle housekeeping. v0.2 → v0.3 followed the same pattern (Phase 16.2 §8 "Stale state" sweep).
- **Effort:** ~0.5 d.
- **Blast radius:** documentation only.
- **Decision:** **in-scope.** D2 = Option 1 — documentation only. Bundled with item L into a single tactical phase (proposed Phase 29).

### I. ProcessPoolExecutor fork-safety hardening on macOS
- **Source:** [v0.3 release notes §H](release-notes/v0.3.md) caveat: "macOS users should note the fork-safety caveat (pre-fork imports can hang — use spawn context or stay on serial default)".
- **Why:** v0.3 ships `n_workers > 1` with a documented fork-safety footgun on macOS. v0.4 candidate: switch to `multiprocessing.get_context("spawn")` for the pool, or detect-and-warn.
- **Effort:** ~0.5 d.
- **Blast radius:** `regime_map.walk_grid` only; deterministic output preserved.
- **Decision:** **in-scope.** D2 = Option 1 — output bytes unchanged at `n_workers=1`; spawn-context switch is observable only at `n_workers>1`. Bundled into the tactical-bundle phase (proposed Phase 30).

### J. Continuous time-evolution channel — extensions
- **Source:** [v0.3 Phase 22 lab note](../lab_notes/2026-05-01-phase22-continuous-time-evolution.md); design-table generator for crossing times shipped.
- **Why:** v0.3 ships `time_series` and `crossing_time` for `bottom_mass_fraction`. A v0.4 candidate is extending the same root-finding pattern to `top_to_bottom_ratio` crossings and to `δ_shell`/`λ_se` at fixed t_obs (parameter sweeps that the design-tool would consume).
- **Effort:** ~1 d.
- **Blast radius:** `time_evolution.py` only; no cache change.
- **Decision:** **in-scope.** D2 = Option 1 — root-find runs on cached snapshots; v0.3 `crossing_time(bottom_mass_fraction = …)` reproduces byte-identically. Bundled with item I into the tactical-bundle phase (proposed Phase 30).

### K. v0.4 → v1.0 release-criterion gap audit
- **Source:** [`program-context.md` §4.1](program-context.md#41-pilot-v10) — `pilot-v1.0` ships when S1–S7 land *and* a named graduate student runs a sealed-cuvette FND tracking experiment whose residuals fit within agreed tolerances.
- **Why:** Track which §4.1 boxes remain unchecked after each tactical release. v0.3 closed S2 and most v0.3 audit-gap pins; v0.4 should land at least one more S-slice (S3 or S5) plus retire as much of the housekeeping list as possible, so the v1.0 punch list is short when D-PC-1 (campaign existence) resolves.
- **Effort:** ~0.5 d (audit lab note, no code).
- **Blast radius:** documentation only.
- **Decision:** **in-scope.** D2 = Option 1 — documentation only. Bundled into the integration phase (proposed Phase 31).

### L. Doc-fix: reconcile S-slice nomenclature
- **Source:** discrepancy between [`program-context.md` §3.1](program-context.md) (authoritative S1–S7 list: aggregation / SE / shell-calibration / radial-port / weighted-polydispersity / wall-hydro / thermal-control) and [`deliverable-index.md` §"What `pilot-v0.4` would change"](deliverable-index.md) + [`release-notes/v0.3.md` §"What `pilot-v0.4` would change"](release-notes/v0.3.md) (which list S3 = "salinity correction", S4 = "pH-dependent surface charge", S5 = "multi-particle interaction", S6 = "viscosity T-dependence", S7 = "full 3-D convection" — these labels do not appear in program-context.md).
- **Why:** The two doc-surfaces give incompatible scope predictions for v0.4. Future readers cannot disambiguate which list is authoritative without cross-checking. Pattern 11 (spec pinning at commit-hash precision) applies in spirit: documents that name future scope must agree on the label set.
- **Effort:** ~0.25 d.
- **Blast radius:** [`deliverable-index.md`](deliverable-index.md) and [`release-notes/v0.3.md`](release-notes/v0.3.md) only. The `release-notes/v0.3.md` edit is a documentation correction (not a substantive change to the v0.3 release contract); record the edit in the v0.4 phase note.
- **Decision:** **in-scope.** D2 = Option 1 — documentation only. D7 resolved. Bundled with item H into a single tactical phase (proposed Phase 29). Resolved by treating program-context as authoritative and replacing the deliverable-index / release-notes lists with cross-references (or with corrected labels matching program-context §3.1).

---

## 2. Out-of-scope candidates (firm-defer to a later cycle)

These are listed so they don't accidentally creep into v0.4:

- **S1 — DLVO aggregation pre-screen** (item A above) — defer to
  v0.5+ until the upstream `Deep-Relaxation-Ordering/diamonds_in_water`
  v0.3 breakout note lands (D3).
- **`lambda_se` → §5 scan axis** (item C above) — defer to v0.5;
  S2 calibration in the FND band is a prerequisite (D5).
- **S4 capsule-geometry port** (item D above) — its own ~12 d pilot
  cycle, likely after v1.0 closes L1.
- **S6 wall hydrodynamics** (item F above) — defer to v0.5 / v1.1.
- **S7 thermal control as first-class axis** (item G above) —
  defer to v0.5 / v1.0; gated on D-PC-1 campaign protocol.
- **Surfactant / non-water suspending media models.** Experimental-
  envelope deferred row; no upstream spec yet.
- **Optical readout, detection thresholds, imaging bias.** L2
  scope (program-context S10).
- **Open-cell / evaporative geometries.** Programme-level deferral
  per [`program-context.md` §6](program-context.md#6-out-of-scope-explicit-deferrals--what-this-programme-is-not).
- **`σ_geom` scan-axis promotion.** ADR 0001 delegated this to the
  breakout-note authors. Wait on upstream.

Each of these is a candidate for v0.5, v1.0, or a sibling pilot
repository, not v0.4.

---

## 3. Forward-compatibility contract — RESOLVED

**Decision: Option 1 for all in-scope items.** Every in-scope item
(B, E, H, I, J, K, L) reproduces `pilot-v0.3` to machine precision
at compatibility-mode defaults (`lambda_se = 1.0`, `delta_shell_m = 0`,
`delta_T_assumed = 0.0 K`, `n_workers = 1`). Same triple invariant
as v0.2 / v0.3:

1. The post-v0.3 baseline suite passes unchanged at the v0.4
   compatibility-mode settings (`delta_shell_m = 0` retains the
   zero-default reproduction; the calibrated default is consulted
   only when no knob is supplied — see item B Decision line).
2. The current `main` §5 cache regime label columns (`regime`,
   `top_to_bottom_ratio`, `bottom_mass_fraction`,
   `convection_flag`, plus v0.3 channels) are unchanged at
   compatibility-mode settings. Numeric channels equal to machine
   precision (`rtol <= 1e-15`).
3. The current `main` deliverable artefacts (notebook 02–08
   figures, design tables, `cell_summary` outputs) are equal to
   machine precision when generated from v0.4 code at
   compatibility-mode settings.

Out-of-scope items (A, C, D, F, G) are not evaluated against the
forward-compat contract in this cycle.

**Resolves D2.**

---

## 4. Phase plan

v0.3 cycle ran Phases 17–24 with `.1` review-driven follow-ups. v0.4
opens at Phase 25 (deliberation surfaces) and proceeds through
Phase 26 (ceremony) to Phase 32 (release).

| Phase | Slice | Items | Effort estimate | Deliverable |
|---|---|---|---|---|
| 25 | Ceremony | This scaffold + ADR 0003 stub | 1 session | Deliberation surfaces shipped (commit `2bd8ec0`) |
| 26 (opening) | Ceremony | ADR 0003 promotion; §0 / §5 D1 / D9 resolved | 1 session | ADR 0003 `Accepted` (commit `40e46da`) |
| 26 (continuation) | Ceremony | §1 reshape; D2 / D3 / D5 / D6 / D7 resolved; §3 / §4 / §6 / §7 filled | 1 session | This contract `Accepted` |
| 27 | S3 | Item B — Hydrodynamic-shell calibration per FND class. Replace [`docs/delta_shell_calibration.md`](delta_shell_calibration.md) provisional table with a citation-anchored calibration table. | 1–2 sessions | Calibrated `delta_shell_m` defaults per FND class; tests; lab note |
| 28 | S5 | Item E — Concentration-weighted polydispersity kernel. `lognormal_smear` weighting refactor. | 1–2 sessions | Kernel-weight refactor + tests + notebook 05 update |
| 29 | Doc-fix + housekeeping bundle | Item L — reconcile S-slice nomenclature in [`deliverable-index.md`](deliverable-index.md) and [`release-notes/v0.3.md`](release-notes/v0.3.md) against [`program-context.md` §3.1](program-context.md). Item H — sweep v0.3 review residue. | 1 session | Doc-fix lab note; updated indexes |
| 30 | Tactical bundle | Item I — `ProcessPoolExecutor` spawn-context switch on macOS. Item J — extend `time_evolution` root-finding to `top_to_bottom_ratio` crossings and parameter sweeps. | 1 session | `regime_map.walk_grid` hardened + extended `time_evolution` API + tests |
| 31 | Integration audit + release-criterion gap audit | Regression audit across all in-scope items; cache regen if needed; notebook refresh. Item K — release-criterion gap audit against [`program-context.md` §4.1](program-context.md). | 1 session | Phase 23-style byte-identical verification; gap-audit lab note |
| 32 | Release | Tag `pilot-v0.4`; update deliverable-index, release notes, `pyproject.toml`, `CITATION.cff`, `codemeta.json`. | 1 session | Release artefacts |

Total: ~8–10 sessions, ~5–7 working days at v0.3 tempo. Calendar
span: ~1.5–2 weeks (allowing for session gaps).

Items A / C / D / F / G are out of scope for v0.4 (see §1
Decision lines and §2 firm-defer list).

---

## 5. Open decisions (Dn) [OPEN]

| Id | Question | Status |
|---|---|---|
| D1 | Spec anchoring (§0 options 1 / 2 / 3) | **Resolved — Option 2** ([ADR 0003 Decision 1](adr/0003-v0.4-spec-anchoring.md)). |
| D2 | Forward-compat baseline (§3 option 1 / 2) | **Resolved — Option 1 for all in-scope items.** Every in-scope slice (B, E, H, I, J, K, L) reproduces `pilot-v0.3` at compatibility defaults. See §3. |
| D3 | S1 in scope as first slice if upstream lands? Or as audit-gap-pin local spec? Or deferred? (item A / program-context S1) | **Resolved — defer to v0.5.** Under D1 = Option 2's "no calendar gating" stance, S1 waits for its upstream breakout note rather than entering v0.4 under the supplier-failure clause. The `provisional=True` API contract from [ADR 0002 §"API surface"](adr/0002-v0.3-spec-anchoring.md#api-surface--the-provisionaltrue-contract) remains in force throughout v0.4 as a consequence. See §1 item A. |
| D4 | S3 hydrodynamic-shell calibration in scope? (item B) | **Resolved — first slice** ([ADR 0003 Decision 2](adr/0003-v0.4-spec-anchoring.md)). |
| D5 | `lambda_se` → §5 scan axis (item C) | **Resolved — defer to v0.5.** S2 calibration prerequisite has not been run in the FND band; running it inside v0.4 plus shipping the §5 axis promotion would exceed cycle calendar. See §1 item C. |
| D6 | S5 concentration-weighted polydispersity kernel in scope? (item E) | **Resolved — in-scope.** Small blast radius, no upstream dependency, housekeeping per [program-context summary table](program-context.md#L222). Phase 28. |
| D7 | Doc-fix scope (item L): correct `deliverable-index.md` and `release-notes/v0.3.md` S-slice lists in v0.4? | **Resolved — in-scope.** Resolved by treating program-context as authoritative. Bundled with item H into Phase 29. |
| D8 | DOI mint at v0.4, or hold to v1.0 per Phase 16.1? | **Resolved — hold to v1.0** ([Phase 16.1 lab note](../lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md)). The deferral chain extends through v0.4 by precedent. |
| D9 | First v0.4 implementation slice | **Resolved — item B (S3)** ([ADR 0003 Decision 2](adr/0003-v0.4-spec-anchoring.md)). |

All decisions resolved.

---

## 6. Risk register

Carry forward the v0.3-cycle structure. All in-scope items (B, E,
H, I, J, K, L) are listed below; out-of-scope items (A, C, D, F,
G) carry no mitigation in this cycle.

In-scope risks:

- **R-B1.** Open-literature DLS values for functionalised FNDs are
  sparse or contradict each other. **Mitigation:** carry forward
  v0.3 Phase 21 audit-gap pin treatment; prefer the most-cited
  open value, flag conflicts in the calibration table, mark
  unverified batches as such in the simulator metadata.
- **R-B2.** Manufacturer data sheets may be NDA-bound. **Mitigation:**
  fallback to open-literature DLS only ([`program-context.md` §3.1 S3 contingency](program-context.md#31-layer-1-realism--pilot-v10));
  the repo never blocks on proprietary data.
- **R-B3.** The "calibrated default per FND class" may not be
  uniquely defined for borderline batches (e.g. partially
  carboxylated). **Mitigation:** name the four classes (bare,
  carboxylated, hydroxylated, PEG-functionalised) explicitly; if
  a batch does not fit, document as audit-gap pin and treat as
  bare default.
- **R-E1.** Concentration-weighted kernel produces results that
  flip §5.1 regime labels relative to v0.3's classification
  weighting. **Mitigation:** keep the v0.3 classification kernel
  as the default (`weighting='classification'`); the new kernel
  is opt-in (`weighting='number_density'`). Pattern 14 zero-default
  preserves v0.3 byte-identical reproduction.
- **R-H1.** v0.3 review residue sweep surfaces an issue large
  enough to warrant a `.1` follow-up. **Mitigation:** triage at
  Phase 29 open; if a substantive issue lands, escalate to a
  Phase 29.1 fix before Phase 30.
- **R-I1.** Spawn-context switch on macOS reveals existing
  fork-unsafe imports in the regime-map module. **Mitigation:**
  if discovered, document the affected imports in a Phase 30 lab
  note and either move them inside the worker function or escalate
  to a Phase 30.1 fix.
- **R-J1.** Extending the `time_evolution` API surface introduces
  a backward-incompatible signature change. **Mitigation:**
  preserve v0.3's `crossing_time(bottom_mass_fraction = …)` exact
  call signature; new metrics enter as additional kwargs with
  zero-default-extension shape.
- **R-K1.** §4.1 release-criterion gap audit reveals that v0.4
  does not narrow the v1.0 punch list as much as expected.
  **Mitigation:** documentation only; the audit lab note records
  the gap explicitly so v0.5 / v1.0 planning can adjust.
- **R-L1.** The S-slice nomenclature discrepancy in
  `deliverable-index` / `release-notes/v0.3.md` may indicate other
  stale S-slice references elsewhere in the repo. **Mitigation:**
  include a `grep -rn "S[1-9]"` audit during the doc-fix; pin any
  additional stale references in the same Phase 29 commit.

Out-of-scope residual risk (acknowledged, not mitigated in v0.4):

- **R-A-C-D-F-G.** S1 aggregation, `lambda_se` → §5 axis, S4
  capsule-geometry, S6 wall hydrodynamics, and S7 thermal control
  are deferred. The v0.3 validity envelope remains honest but
  narrower than L1 requires. The `provisional=True` API contract
  from [ADR 0002 §"API surface"](adr/0002-v0.3-spec-anchoring.md#api-surface--the-provisionaltrue-contract)
  remains in force throughout v0.4 as a direct consequence of D3.
  **Acceptance:** acknowledged in [`docs/experimental-envelope.md`](experimental-envelope.md)
  carry-forward and in the v0.4 release notes.

---

## 7. Schedule

| Milestone | Target sessions | Calendar span (approx.) |
|---|---|---|
| Phase 25 (deliberation surfaces) | Done | 2026-05-05 |
| Phase 26 opening (ADR 0003 promotion) | Done | 2026-05-06 |
| Phase 26 continuation (contract acceptance) | Current | 2026-05-06 |
| Phase 27 (S3 — Hydrodynamic-shell calibration) | +1–2 sessions | 2026-05-06 – 2026-05-10 |
| Phase 28 (S5 — concentration-weighted polydispersity kernel) | +1–2 sessions | 2026-05-10 – 2026-05-14 |
| Phase 29 (doc-fix + housekeeping bundle: items L, H) | +1 session | 2026-05-14 – 2026-05-15 |
| Phase 30 (tactical bundle: items I, J) | +1 session | 2026-05-15 – 2026-05-16 |
| Phase 31 (integration audit + release-criterion gap audit: item K) | +1 session | 2026-05-16 – 2026-05-17 |
| Phase 32 (release `pilot-v0.4`) | +1 session | 2026-05-17 – 2026-05-18 |

Total: ~8–10 sessions, ~5–7 working days of active development.
Calendar span: ~1.5–2 weeks (allowing for session gaps).

---

## 8. Stale state — cleared during Phase 25 / 26

Doc-fix items flagged when this scaffold was drafted have been
cleared as follows:

- [x] [`README.md`](../README.md) phase table — Phase 25 row added
  under a new "v0.4 deliberation cycle" section header in the
  Phase 25 commit (`2bd8ec0`); Phase 26 opening row added in the
  Phase 26 opening commit (`40e46da`); Phase 26 continuation row
  added in this commit.
- [x] [`docs/adr/README.md`](adr/README.md) — ADR 0003 row added to
  the index in the Phase 25 commit; Status / Date / Phase columns
  updated to Accepted / 2026-05-06 / 26 in the Phase 26 opening
  commit.
- [x] [`lab_notes/README.md`](../lab_notes/README.md) — Phase 25 row
  prepended in the Phase 25 commit; Phase 26 (opening) row in the
  Phase 26 opening commit; Phase 26 (continuation) row in this
  commit.

The S-slice nomenclature discrepancy in [`docs/deliverable-index.md`](deliverable-index.md)
and [`docs/release-notes/v0.3.md`](release-notes/v0.3.md) is item L
(in-scope, Phase 29). Not closed here because doing so in Phase 26
would amount to a stealth substantive edit of the v0.3 release note;
deferred to a phase that owns the cleanup explicitly.

---

## 9. Acceptance / next step

This contract is accepted when all six steps below are complete:

1. ~~ADR 0003 promoted from `Proposed (stub)` → `Accepted`.~~
   **Done** (Phase 26 opening, commit `40e46da`).
2. ~~D1, D9 resolved in ADR 0003.~~ **Done** (Phase 26 opening).
3. ~~D2 / D3 / D5 / D6 / D7 resolved in §5.~~ **Done** (Phase 26
   continuation, this commit). D4 was already resolved in Phase 26
   opening; D8 carried forward from Phase 16.1.
4. ~~§1 reshaped into "in-scope" / "out-of-scope" / "parallel
   breakout" per the resolved decisions.~~ **Done** (Phase 26
   continuation, this commit).
5. ~~§3 / §4 / §6 / §7 filled.~~ **Done** (Phase 26 continuation,
   this commit).
6. ~~The `SCAFFOLD` qualifier removed from the Status line.~~
   **Done** (Phase 26 continuation, this commit).

The v0.4 cycle is now under contract. Phase 27 (S3 — Hydrodynamic-shell
calibration per FND class) is cleared to open.

---

## 10. Cross-references

- [`program-context.md`](program-context.md) — long-horizon goal
  document. The S1–S7 list in §3.1 is the authoritative scope menu
  for L1, of which v0.4 is one tactical slice.
- [`work-plan-v0-3.md`](work-plan-v0-3.md) — the v0.3 contract
  used as the structural template. v0.3 closeout decisions inform
  v0.4 starting state.
- [`adr/0001-v0.2-spec-anchoring.md`](adr/0001-v0.2-spec-anchoring.md)
  and [`adr/0002-v0.3-spec-anchoring.md`](adr/0002-v0.3-spec-anchoring.md)
  — spec-anchoring precedents. ADR 0003 mirrors them for v0.4.
- [`adr/0003-v0.4-spec-anchoring.md`](adr/0003-v0.4-spec-anchoring.md)
  — `Proposed (stub)`; resolves D1 and D9 when promoted.
- [`deliverable-index.md`](deliverable-index.md) §"What `pilot-v0.4`
  would change" — original candidate list this scaffold expands
  (and contradicts; see item L).
- [`release-notes/v0.3.md`](release-notes/v0.3.md) §"What `pilot-v0.4`
  would change" — same.
- [`experimental-envelope.md`](experimental-envelope.md) — deferred
  experimental variables, which seed §1 and §2 of this scaffold.
- [`findings-physics.md`](findings-physics.md) and
  [`findings-process.md`](findings-process.md) — inform which v0.4
  candidates have empirical / methodological motivation.
- [`delta_shell_calibration.md`](delta_shell_calibration.md) —
  v0.3 provisional calibration table; item B (S3) promotes it.
- [`../lab_notes/2026-05-01-phase24-pilot-v0-3-release.md`](../lab_notes/2026-05-01-phase24-pilot-v0-3-release.md)
  — v0.3 release ceremony that closed v0.3 cycle and deferred this
  scaffold. The "no open decisions pending" note motivates Phase 25
  as the deliberate next step.
- [`../lab_notes/2026-05-05-phase25-v0-4-deliberation-surfaces.md`](../lab_notes/2026-05-05-phase25-v0-4-deliberation-surfaces.md)
  — drafted this scaffold as `SCAFFOLD` and ADR 0003 as
  `Proposed (stub)`.
- [`../lab_notes/2026-05-06-phase26-opening-adr-0003-and-work-plan-v0-4.md`](../lab_notes/2026-05-06-phase26-opening-adr-0003-and-work-plan-v0-4.md)
  — promoted ADR 0003 to `Accepted`; resolved D1 + D9.
- [`../lab_notes/2026-05-06-phase26-continuation-contract-acceptance.md`](../lab_notes/2026-05-06-phase26-continuation-contract-acceptance.md)
  — promoted this contract to `Accepted`; resolved D2 / D3 / D5 /
  D6 / D7; reshaped §1 and filled §3 / §4 / §6 / §7.
