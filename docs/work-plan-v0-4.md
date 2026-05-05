# Work plan — `pilot-v0.4`

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

| Field | Value |
|---|---|
| Status | **SCAFFOLD — D1 / D9 resolved (Phase 26 opening); D2–D7 still [OPEN].** §0 reflects the spec-anchor resolution; §1 first-slice fixed against item B (S3). The §1 reshape (in-scope vs out-of-scope), §3 forward-compat baseline (D2), §4 phase plan, §6 risk register, and §7 schedule are filled in the Phase 26 continuation session. |
| Date | 2026-05-05 (drafted Phase 25); 2026-05-06 (Phase 26 opening — D1 / D9 resolved) |
| Drafted at | post-Phase 24, commit `00f2fc7` (`pilot-v0.3` released; Pages landing page adopted) |
| Predecessor tag | `pilot-v0.3` at `ad48b0b` |
| Successor tag (proposed) | `pilot-v0.4` |
| Spec anchor | **breakout-note v0.2 commit `3b7b18af`** — Option 2, resolved by [ADR 0003](adr/0003-v0.4-spec-anchoring.md). Same pin as v0.2 / v0.2.1 / v0.3. |
| First implementation slice | **item B (S3 — Hydrodynamic-shell calibration per FND class)** ([`program-context.md` §3.1](program-context.md), [ADR 0003 Decision 2](adr/0003-v0.4-spec-anchoring.md)). See §1 item B. |
| Working tempo | v0.3 baseline: ~7 working days across ~10 sessions; calendar 1.5–2 weeks |

The scaffold structure mirrors [`work-plan-v0-3.md`](work-plan-v0-3.md)
so promotion to contract is mechanical. Sections marked `[OPEN]`
require a decision; sections marked `[TBD]` are populated after the
open decisions are made.

This document is *not* a commitment to ship `pilot-v0.4`. It is the
deliberation surface for that question. Acceptance criteria are in
§9.

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
- **Upstream dependency:** `Deep-Relaxation-Ordering/diamonds_in_water` owes the breakout note. Status: not yet drafted (per [Phase 24 release note](../lab_notes/2026-05-01-phase24-pilot-v0-3-release.md) and [program-context §5](program-context.md#5-coupling-to-sibling-repositories)).
- **Decision needed:** **in-scope first slice if upstream lands**, **in-scope as audit-gap-pin local spec under §5 supplier-failure clause if upstream stalls**, OR **deferred to v0.5** if the cycle wants smaller blast-radius items first.

### B. S3 — Hydrodynamic-shell calibration per FND class
- **Source:** [`program-context.md` §3.1](program-context.md) (S3 — Hydrodynamic-shell calibration); [v0.3 Phase 21 δ_shell calibration](../lab_notes/2026-05-01-phase21-mesh-convergence-and-shell-calibration.md); [`docs/delta_shell_calibration.md`](delta_shell_calibration.md) (provisional table).
- **Why:** v0.3 ships a *provisional* `delta_shell_m` calibration table marked as audit-gap pin. S3 promotes the provisional table to a calibrated default range per FND class (bare, carboxylated, hydroxylated, PEG-functionalised). Housekeeping (closes audit-gap pin) per [`program-context.md` §3.1](program-context.md) summary table.
- **Effort:** ~1–2 d if open-literature DLS is sufficient; longer if manufacturer collaboration is pursued.
- **Blast radius:** documentation + parameter defaults; no API change. The user-supplied knob remains; the default value gets a citation-anchored class identity.
- **Contingency:** manufacturer data may be NDA-bound. Per [`program-context.md` §3.1 S3](program-context.md), fallback is open-literature DLS only with affected batches flagged as "unverified" in metadata. The repo never blocks on proprietary data.
- **Decision needed:** **in-scope** (small blast radius, no upstream dependency, closes a v0.3 audit-gap pin).

### C. Promote `lambda_se` to §5 scan axis
- **Source:** [v0.3 release notes "What v0.4 would change"](release-notes/v0.3.md#what-pilot-v04-would-change) bullet "Promote `lambda_se` to §5 scan axis if calibrated working values are ≤ 0.3"; [`docs/work-plan-v0-3.md` item K](work-plan-v0-3.md#k-stokes-einstein-corrections-at-sub-150-nm-radii-first-slice).
- **Why:** v0.3 ships `lambda_se` as a single axis applied at compute time, with the §5 cache reproducing v0.2 byte-for-byte at `lambda_se = 1.0`. If the gold-NP calibration (Laloyaux z₂) shows working values consistently ≤ 0.3 in the FND-relevant band, a §5 cache schema bump that carries `lambda_se` as an axis is the next tightening — design-tool consumers can then compare across SE-correction strengths without recomputing.
- **Effort:** ~2 d (cache schema bump, dimension expansion, consumer updates) **gated on** the calibration result.
- **Blast radius:** §5 cache schema change (Pattern 14 zero-default extension); notebook consumers that read the cache need updates.
- **Decision needed:** **conditionally in-scope** — only if S2 calibration in the FND band confirms `lambda_se ≤ 0.3`. Otherwise defer to v0.5.

### D. S4 — Capsule-geometry port (1-D radial in spherical coordinates)
- **Source:** [`program-context.md` §3.1 S4](program-context.md); [`work-plan-v0-2.md` §1 "Out of scope (parallel tracks)"](work-plan-v0-2.md#out-of-scope-parallel-tracks).
- **Why:** Layer-defining for L1. The simulator extends from 1-D Cartesian slab to 1-D radial coordinate in spherical geometry, for sealed micro-cells of diameter d = 10–100 µm. *Not* a full 3-D simulator (that is explicitly out of scope at every layer per [`program-context.md` §6](program-context.md#6-out-of-scope-explicit-deferrals--what-this-programme-is-not)).
- **Effort:** ~12 d per the v0.2 plan estimate (its own pilot cycle).
- **Blast radius:** new geometry module + Methods A/B/C ported to spherical Jacobians + sibling-repo breakout note required first.
- **Upstream dependency:** sibling-repo breakout note required.
- **Decision needed:** **out-of-scope — parallel pilot cycle.** Effort exceeds the v0.2/v0.3 working-tempo envelope (~7 working days). S4 deserves its own dedicated cycle.

### E. S5 — Concentration-weighted polydispersity kernel
- **Source:** [`program-context.md` §3.1 S5](program-context.md); v0.2 polydispersity (Phase 14) is classification-weighted.
- **Why:** v0.2 polydispersity layer is classification-weighted (each radius bin gets the §5.1 label and a probability). For tracking experiments, what matters is the *number-density* distribution within each band. Bounded change to `lognormal_smear`'s weighting kernel.
- **Effort:** ~1–2 d (kernel-weight refactor + tests + notebook 05 update).
- **Blast radius:** `polydispersity.py` + notebook 05 + deliverable 6 design table; no §5 cache change at compatibility-mode default.
- **Decision needed:** **in-scope** (small blast radius, no upstream dependency, housekeeping per program-context summary table).

### F. S6 — Wall-hydrodynamic Faxén/Brenner corrections
- **Source:** [`program-context.md` §3.1 S6](program-context.md); [`work-plan-v0-3.md` item E](work-plan-v0-3.md#e-wall-hydrodynamic-correction).
- **Why:** Layer-defining for L1 (with "may defer to v1.1" qualifier). Position-dependent Faxén/Brenner corrections to drag and diffusivity near the sealed-cell boundary.
- **Effort:** ~2 d (correction term + `RegimeResult` channel + Method-C boundary-layer integration).
- **Blast radius:** Method-C cells where the bottom layer matters; introduces a near-wall dimensionless parameter (particle-wall separation / radius) and modifies Method A/B/C kernels.
- **Upstream dependency:** likely needs sibling breakout-note specs for boundary conditions.
- **Decision needed:** **defer to v0.5 or v1.1** unless the cycle wants a layer-defining slice. v0.3 deferred this with the same reasoning; absent new motivation, the deferral persists.

### G. S7 — Thermal control as first-class axis
- **Source:** [`program-context.md` §3.1 S7](program-context.md); [`work-plan-v0-3.md` item G](work-plan-v0-3.md#g-refined-convection-model-t-dependent-κ-gradient-profiles-evaporation).
- **Why:** Promote `delta_T_assumed` from its current side-channel status to a first-class axis where experimentally relevant. Sealed-cell thermal protocols and lateral gradients enter here. (Open-cell evaporation is *out of scope* — see [`program-context.md` §6](program-context.md#6-out-of-scope-explicit-deferrals--what-this-programme-is-not); S7 is sealed-cell only.)
- **Effort:** 1–2 d for κ(T); broader thermal-protocol support is a sub-phase.
- **Blast radius:** convection module + cache schema (extra column or recomputed flag). Even κ(T) alone changes §5 cache numerics by design — this is *not* a Pattern 14 zero-default extension; it is a deliberate cache regen.
- **Upstream dependency:** experimental-campaign repo (P-1 in [`program-context.md` §2](program-context.md#2-programme-prerequisites-and-risks)) for cooling protocol specifications. Not strictly blocking, but the protocol set drives the axis range.
- **Decision needed:** **defer to v0.5 or v1.0** absent campaign-driven requirements. v0.3 deferred this with the same reasoning.

### H. Persisting v0.3 review residue
- **Source:** to be enumerated during the §1 reshape ceremony. v0.3 review surface from [Phase 23 integration audit](../lab_notes/2026-05-01-phase23-integration-audit.md) and [Phase 24 release note](../lab_notes/2026-05-01-phase24-pilot-v0-3-release.md) reports clean state, but v0.4 should sweep for any residue once the cycle opens.
- **Why:** Standard cycle housekeeping. v0.2 → v0.3 followed the same pattern (Phase 16.2 §8 "Stale state" sweep).
- **Effort:** ~0.5 d.
- **Blast radius:** documentation only.
- **Decision needed:** **in-scope** (housekeeping; trivially small).

### I. ProcessPoolExecutor fork-safety hardening on macOS
- **Source:** [v0.3 release notes §H](release-notes/v0.3.md) caveat: "macOS users should note the fork-safety caveat (pre-fork imports can hang — use spawn context or stay on serial default)".
- **Why:** v0.3 ships `n_workers > 1` with a documented fork-safety footgun on macOS. v0.4 candidate: switch to `multiprocessing.get_context("spawn")` for the pool, or detect-and-warn.
- **Effort:** ~0.5 d.
- **Blast radius:** `regime_map.walk_grid` only; deterministic output preserved.
- **Decision needed:** **in-scope** (small, removes a documented sharp edge).

### J. Continuous time-evolution channel — extensions
- **Source:** [v0.3 Phase 22 lab note](../lab_notes/2026-05-01-phase22-continuous-time-evolution.md); design-table generator for crossing times shipped.
- **Why:** v0.3 ships `time_series` and `crossing_time` for `bottom_mass_fraction`. A v0.4 candidate is extending the same root-finding pattern to `top_to_bottom_ratio` crossings and to `δ_shell`/`λ_se` at fixed t_obs (parameter sweeps that the design-tool would consume).
- **Effort:** ~1 d.
- **Blast radius:** `time_evolution.py` only; no cache change.
- **Decision needed:** **deliberation needed** — possibly bundled with B (S3 calibration) into a single "design-tool ergonomics" cycle.

### K. v0.4 → v1.0 release-criterion gap audit
- **Source:** [`program-context.md` §4.1](program-context.md#41-pilot-v10) — `pilot-v1.0` ships when S1–S7 land *and* a named graduate student runs a sealed-cuvette FND tracking experiment whose residuals fit within agreed tolerances.
- **Why:** Track which §4.1 boxes remain unchecked after each tactical release. v0.3 closed S2 and most v0.3 audit-gap pins; v0.4 should land at least one more S-slice (S3 or S5) plus retire as much of the housekeeping list as possible, so the v1.0 punch list is short when D-PC-1 (campaign existence) resolves.
- **Effort:** ~0.5 d (audit lab note, no code).
- **Blast radius:** documentation only.
- **Decision needed:** **in-scope** (housekeeping; defines what "v0.4 done" means in §4.1 terms).

### L. Doc-fix: reconcile S-slice nomenclature
- **Source:** discrepancy between [`program-context.md` §3.1](program-context.md) (authoritative S1–S7 list: aggregation / SE / shell-calibration / radial-port / weighted-polydispersity / wall-hydro / thermal-control) and [`deliverable-index.md` §"What `pilot-v0.4` would change"](deliverable-index.md) + [`release-notes/v0.3.md` §"What `pilot-v0.4` would change"](release-notes/v0.3.md) (which list S3 = "salinity correction", S4 = "pH-dependent surface charge", S5 = "multi-particle interaction", S6 = "viscosity T-dependence", S7 = "full 3-D convection" — these labels do not appear in program-context.md).
- **Why:** The two doc-surfaces give incompatible scope predictions for v0.4. Future readers cannot disambiguate which list is authoritative without cross-checking. Pattern 11 (spec pinning at commit-hash precision) applies in spirit: documents that name future scope must agree on the label set.
- **Effort:** ~0.25 d.
- **Blast radius:** [`deliverable-index.md`](deliverable-index.md) and [`release-notes/v0.3.md`](release-notes/v0.3.md) only. The `release-notes/v0.3.md` edit is a documentation correction (not a substantive change to the v0.3 release contract); record the edit in the v0.4 phase note.
- **Decision needed:** **in-scope** (housekeeping; resolved by treating program-context as authoritative and replacing the deliverable-index / release-notes lists with cross-references).

---

## 2. Out-of-scope candidates (firm-defer to a later cycle)

These are listed so they don't accidentally creep into v0.4:

- **S4 capsule-geometry port** (item D above) — its own ~12 d pilot
  cycle, likely after v1.0 closes L1.
- **S6 wall hydrodynamics** (item F above) — defer to v0.5 or v1.1
  unless the v0.4 cycle adopts one layer-defining slice.
- **S7 thermal control as first-class axis** (item G above) —
  defer to v0.5 or v1.0; gated on D-PC-1 campaign protocol.
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

## 3. Forward-compatibility contract [OPEN — D2]

Two options, paralleling the v0.3 work plan:

1. **Anchor to `pilot-v0.3` (HEAD of `main` after Phase 24).** v0.4
   default-mode outputs reproduce the v0.3 §5 cache and deliverables
   to machine precision at the v0.3 compatibility-mode defaults
   (`lambda_se = 1.0`, `delta_shell_m = 0`, `delta_T_assumed = 0.0 K`,
   `n_workers = 1`). Same triple invariant as v0.2 / v0.3.
2. **Anchor to a v0.4 baseline.** If item C (lambda_se → §5 axis)
   or item G (κ(T)) move numerical channels by design, the v0.3
   baseline cannot be the forward-compat target. Fallback contract:
   "v0.3 outputs reproduce when v0.4 features are at their
   compatibility-mode defaults."

**[OPEN]** Decision per item once §1 is reshaped. Default expectation
based on the candidate menu above: **D2 = Option 1 for B / E / H /
I / J / K / L** (zero-default-extension shape applies); D2 = Option 2
required only if C, F, or G land.

---

## 4. Phase plan [TBD]

v0.3 cycle ran Phases 17–24 with `.1` review-driven follow-ups. v0.4
opens at Phase 26 (Phase 25 is the deliberation-surface phase that
ships *this* scaffold + ADR 0003 stub).

The phase plan is filled after §1 is reshaped against the resolved
D1 / D2 / first-slice decisions. Placeholder structure mirrors v0.3:

| Phase | Slice | Items | Effort estimate | Deliverable |
|---|---|---|---|---|
| 25 | Ceremony | This scaffold + ADR 0003 stub | 1 session | Deliberation surfaces shipped |
| 26 (opening) | Ceremony | ADR 0003 promotion; §0 / §5 D1 / D9 resolved | 1 session | ADR 0003 `Accepted` |
| 26 (continuation) | Ceremony | §1 reshape; D2–D7 resolved; §4 / §6 / §7 filled | 1 session | This contract `Accepted` |
| 27+ | TBD | TBD | TBD | TBD |
| (last) | Release | Tag `pilot-v0.4`; update deliverable-index, release notes, pyproject.toml | 1 session | Release artefacts |

Total (placeholder): ~7–10 sessions, ~5–8 working days at v0.3
tempo. Will tighten after §1 is reshaped.

---

## 5. Open decisions (Dn) [OPEN]

| Id | Question | Status |
|---|---|---|
| D1 | Spec anchoring (§0 options 1 / 2 / 3) | **Resolved — Option 2** ([ADR 0003 Decision 1](adr/0003-v0.4-spec-anchoring.md)). |
| D2 | Forward-compat baseline (§3 option 1 / 2) | **[OPEN]** — resolved per in-scope item once §1 reshape happens (Phase 26 continuation). |
| D3 | S1 in scope as first slice if upstream lands? Or as audit-gap-pin local spec? Or deferred? (item A / program-context S1) | **[OPEN]** — under Option 2, default expectation: deferred to v0.5 (upstream had not landed by Phase 26 opening). Confirmed in §1 reshape. |
| D4 | S3 hydrodynamic-shell calibration in scope? (item B) | **Resolved — first slice** ([ADR 0003 Decision 2](adr/0003-v0.4-spec-anchoring.md)). |
| D5 | `lambda_se` → §5 scan axis (item C) | **[OPEN]** — gated on S2 calibration result in the FND band; default expectation: defer to v0.5. Confirmed in §1 reshape. |
| D6 | S5 concentration-weighted polydispersity kernel in scope? (item E) | **[OPEN]** — strong default expectation: yes. Confirmed in §1 reshape. |
| D7 | Doc-fix scope (item L): correct `deliverable-index.md` and `release-notes/v0.3.md` S-slice lists in v0.4? | **[OPEN]** — strong default expectation: yes. Confirmed in §1 reshape. |
| D8 | DOI mint at v0.4, or hold to v1.0 per Phase 16.1? | **Resolved — hold to v1.0** ([Phase 16.1 lab note](../lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md)). The deferral chain extends through v0.4 by precedent. |
| D9 | First v0.4 implementation slice | **Resolved — item B (S3)** ([ADR 0003 Decision 2](adr/0003-v0.4-spec-anchoring.md)). |

D1, D4, D8, D9 are settled. D2 / D3 / D5 / D6 / D7 remain on the
table for the §1 reshape (Phase 26 continuation), with the strong
default expectations recorded above.

---

## 6. Risk register [TBD]

Carry forward the v0.3-cycle structure. Filled after §1 is reshaped.

Provisional risks visible from the candidate menu:

- **R-A1** (S1, item A). Upstream breakout note may not land in
  cycle-open window. **Mitigation:** §5 supplier-failure clause
  fallback (local spec under audit-gap-pin convention, with
  synchronisation ADR on upstream materialisation).
- **R-B1** (S3, item B). Open-literature DLS values for
  functionalised FNDs may be sparse or contradict each other.
  **Mitigation:** carry forward v0.3 Phase 21 audit-gap pin
  treatment; prefer the most-cited open value and flag conflicts.
- **R-C1** (lambda_se → §5 axis, item C). Calibration may show
  working values *not* uniformly ≤ 0.3, in which case the §5 axis
  promotion is premature. **Mitigation:** decision is conditional
  on the calibration result; defer to v0.5 if criterion fails.
- **R-L1** (doc-fix, item L). The discrepancy between
  `deliverable-index` and `program-context` may indicate other
  S-slice references elsewhere in the repo are also stale.
  **Mitigation:** include a `grep -rn "S[3-7]"` audit during the
  doc-fix.

Filled risks for D / E / F / G / H / I / J / K added during §1
reshape.

---

## 7. Schedule [TBD]

Filled after §4 phase plan is filled. Placeholder calendar (post-
ADR 0003 resolution):

| Milestone | Target sessions | Calendar span (approx.) |
|---|---|---|
| Phase 25 (this scaffold) | Current | 2026-05-05 |
| Phase 26 opening (ADR 0003 promotion) | +1 session | 2026-05-05 – 2026-05-12 |
| Phase 26 continuation (contract acceptance) | +1 session | 2026-05-12 – 2026-05-19 |
| Phases 27+ (in-scope items) | TBD | TBD |
| Release phase (tag `pilot-v0.4`) | TBD | TBD |

Total (placeholder): ~7–10 sessions, ~5–8 working days. Tightened
after §1 reshape.

---

## 8. Stale state to clean up

Doc-fix items flagged when this scaffold was drafted, parallel to
the [v0.3 scaffold §8 list](work-plan-v0-3.md#8-stale-state-swept-in-phase-162):

- [ ] [`docs/deliverable-index.md` §"What `pilot-v0.4` would change"](deliverable-index.md)
  uses an S-slice list incompatible with [`program-context.md` §3.1](program-context.md).
  See item L. Cleanup target: replace the inline list with a
  cross-reference to program-context, or correct the labels to
  match.
- [ ] [`docs/release-notes/v0.3.md` §"What `pilot-v0.4` would change"](release-notes/v0.3.md)
  inherits the same incorrect list. Same fix as deliverable-index.
- [x] [`README.md`](../README.md) phase table — Phase 25 row added
  under a new "v0.4 deliberation cycle" section header in the same
  commit as this scaffold.
- [x] [`docs/adr/README.md`](adr/README.md) — ADR 0003 row added to
  the index in the same commit as this scaffold.
- [x] [`lab_notes/README.md`](../lab_notes/README.md) — Phase 25 row
  prepended in the same commit as this scaffold.

Outstanding pre-v0.4 substantive doc fixes resolve to item L when
§1 is reshaped.

---

## 9. Acceptance / next step

This scaffold is a **deliberation surface**, not a contract. It is
accepted as a contract only when **all** of the following are true,
mirroring [v0.3 Phase 17 acceptance](work-plan-v0-3.md#9-acceptance--next-step):

1. ADR 0003 promoted from `Proposed (stub)` → `Accepted` (Phase 26
   opening).
2. D1, D9 resolved in ADR 0003.
3. D2 / D3 / D4 / D5 / D6 / D7 resolved in §5.
4. §1 reshaped into "in-scope" / "out-of-scope" / "parallel breakout"
   per the resolved decisions.
5. §4 phase plan, §6 risk register, §7 schedule filled.
6. The `SCAFFOLD` qualifier removed from the Status line.

Until step 6, this document is a deliberation surface and the v0.4
cycle has not opened.

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
