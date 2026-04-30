# Work plan — `pilot-v0.3`

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

| Field | Value |
|---|---|
| Status | **Accepted contract.** All open decisions (D1–D9) resolved. §1 in-scope list fixed against D1 = Option 2. §4 phase plan, §6 risk register, and §7 schedule filled. Phase 18 (S2 — Stokes-Einstein corrections) is cleared to open. |
| Date | 2026-04-30 (drafted Phase 16.2; opened against ADR 0002 Phase 17) |
| Drafted at | post-Phase 16.1, commit `e2639ff` (FAIR metadata + DOI deferral landed) |
| Predecessor tag | `pilot-v0.2` at `dfbb94d` (also `pilot-v0.2.1` once tagged) |
| Successor tag (proposed) | `pilot-v0.3` |
| Spec anchor | **breakout-note v0.2 commit `3b7b18af`** — Option 2, resolved by [ADR 0002](adr/0002-v0.3-spec-anchoring.md). Same pin as v0.2 / v0.2.1. |
| First implementation slice | **S2 — Stokes-Einstein corrections at sub-150-nm radii** ([program-context §3.1](program-context.md), [ADR 0002 Decision 2](adr/0002-v0.3-spec-anchoring.md)). See §1 item K. |
| Working tempo | v0.2 baseline: ~7 working days across ~10 sessions; calendar 1.5–2 weeks |

The scaffold structure mirrors [`work-plan-v0-2.md`](work-plan-v0-2.md)
so promotion to contract is mechanical. Sections marked `[OPEN]`
require a decision; sections marked `[TBD]` are populated after the
open decisions are made.

---

## 0. Spec anchoring — RESOLVED

**Decision: Option 2.** `pilot-v0.3` stays anchored to breakout-note
v0.2 commit `3b7b18af`. Recorded in
[ADR 0002 Decision 1](adr/0002-v0.3-spec-anchoring.md). Resolves D1
in §5.

The original three options remain readable in the ADR for context:

1. ~~Re-anchor to breakout-note v0.3 if/when it lands~~ — rejected
   for calendar risk.
2. **Stay anchored to breakout-note v0.2 commit `3b7b18af`** —
   chosen.
3. ~~Hybrid~~ — rejected for per-phase bookkeeping cost.

**Consequence for §1.** Items that require a physics-scope expansion
beyond the v0.2 envelope (e.g. item D aggregation, item E wall
hydrodynamics) are *not* in v0.3 scope; they are parallel-breakout
candidates or v0.4-and-later items. §1 reshape (the next step of the
Phase 17 ceremony) marks each item accordingly.

**Re-pin policy** if breakout-note v0.3 lands mid-cycle: ADR 0001's
"release-phase picks up the new pin" clause applies — the v0.3
release phase (proposed Phase 24) re-pins, not earlier phases.

---

## 1. Scope candidates [OPEN — first slice fixed]

Each item below is a **candidate** drawn from existing repo evidence
or from [program-context.md §3.1](program-context.md). Format per
item: motivation, source, rough effort, blast radius, decision
needed.

**First slice fixed: item K (S2 — Stokes-Einstein corrections at
sub-150-nm radii)** per [ADR 0002 Decision 2](adr/0002-v0.3-spec-anchoring.md).
The other items are resolved below.

### A. Resolve audit-gap pins `T_OBS_S` and `DEPTHS_M`
- **Source:** [`docs/deliverable-index.md` §"What pilot-v0.3 would change"](deliverable-index.md#what-pilot-v03-would-change), bullet 1.
- **Why:** These are the two scan-grid pins still flagged "physically-motivated defaults; cross-check at next spec drift."
- **Effort (rough):** 0.5–1 d if the breakout-note v0.3 names the values; 2–3 d if a §5 cache regen is required to validate alternatives.
- **Blast radius:** §5 cache invalidation if the values move.
- **Decision:** **in-scope.** D2 = Option 1 (anchor to `pilot-v0.2.1`) — no numerical-channel change; pin values get named and documented.

### B. Continuous regime thresholds (interpolated design-table entries)
- **Source:** Deliverable-index "What v0.3 would change" bullet 2.
- **Why:** v0.2 design-table entries are grid-snapped to the §5 r-axis. Root-finding on `top_to_bottom_ratio = 0.95`, `bottom_mass_fraction = 0.95`, and `p_stratified` suitability would replace 30-bin steps with continuous radii.
- **Effort:** ~1 d (root-finder per metric + revised notebooks 04 / 05).
- **Blast radius:** notebooks 04 / 05 + design-table CSV format. New tests pin the interpolation against the §5 cache rows at degenerate inputs.
- **Decision:** **in-scope.** D2 = Option 1 — root-finding is additive; §5 cache unchanged at compatibility defaults.

### C. Mesh-convergence audit on the finite-time bottom-mass threshold
- **Source:** Deliverable-index bullet 3.
- **Why:** Method-C uses 120-cell first pass + 240-cell refinement around thresholds; the 10-nm fallback floor is empirical. v0.3 would document a convergence sweep so the fidelity envelope is formal, not "tested in practice."
- **Effort:** ~1 d (sweep + audit lab note); no model change.
- **Blast radius:** documentation only if the audit confirms current behaviour; cache regen if it surfaces drift.
- **Decision:** **in-scope.** D2 = Option 1 — audit-only; no model change expected.

### D. Aggregation pre-screen (DLVO `τ_agg(ζ, I, pH)`)
- **Source:** [`work-plan-v0-2.md` §1 "Out of scope (parallel tracks)"](work-plan-v0-2.md#out-of-scope-parallel-tracks), [`experimental-envelope.md`](experimental-envelope.md) deferred-variables list.
- **Why:** Aggregation flips many of the dilute-limit assumptions; the v0.2 envelope flags it as experimentally important.
- **Effort:** ~3 d per the v0.2 plan estimate.
- **Blast radius:** new module + side-channel against §5 cache, or a separate sibling pilot. Not a §5.1 label override.
- **Decision:** **out-of-scope — parallel breakout.** D3 = parallel breakout. S1 (DLVO aggregation) requires an upstream breakout note from `Deep-Relaxation-Ordering/diamonds_in_water` that does not yet exist. v0.3 may prepare parameter stubs but not the trustworthiness flag.

### E. Wall-hydrodynamic correction
- **Source:** Deliverable-index bullet 4, experimental-envelope "no wall-hydrodynamic correction" row.
- **Why:** Most §5 cells have `r/h` small, but near-bottom transport is wall-sensitive. Faxén / Brenner corrections apply a position-dependent λ to the Stokes drag.
- **Effort:** ~2 d (correction term + `RegimeResult` channel + Method-C boundary-layer integration).
- **Blast radius:** Method-C cells where the bottom layer matters; Method-A unchanged.
- **Decision:** **out-of-scope — defer to v0.4.** D4 = defer. Wall-hydrodynamic corrections exceed the breakout-note v0.2 envelope. The λ ≡ 1 zero-default pattern is preserved for a future cycle.

### F. Calibrate `delta_shell_m` against measured FND hydrodynamic radii
- **Source:** Deliverable-index bullet 5.
- **Why:** v0.2 ships `δ_shell` as a user knob; v0.3 would translate that into a literature-anchored default range for representative functionalised FNDs.
- **Effort:** ~0.5 d if a single literature pin is acceptable; longer if a survey is wanted.
- **Blast radius:** documentation + a new audit-gap pin entry; no API change.
- **Decision:** **in-scope.** D2 = Option 1 — documentation-only change; no API or numerical-channel change.

### G. Refined convection model (T-dependent κ, gradient profiles, evaporation)
- **Source:** Deliverable-index bullet 6, [`work-plan-v0-2.md` §3 risk register](work-plan-v0-2.md), Phase 11 lab note.
- **Why:** v0.2 uses a T-independent thermal diffusivity `κ ≈ 1.4·10⁻⁷ m²/s` and a single Rayleigh threshold. v0.3 candidate: promote `κ` to T-dependent (parameters.py), allow non-uniform gradients, and add an open-cell evaporation channel.
- **Effort:** 1–2 d for κ(T); evaporation is a separate sub-phase.
- **Blast radius:** convection module + cache schema (extra column or recomputed flag).
- **Decision:** **out-of-scope — defer to v0.4.** D5 = defer. Even κ(T) alone changes §5 cache numerics by design; the full model (gradients + evaporation) is a physics-scope expansion beyond the v0.2 envelope.

### H. Performance: parallel §5 walk
- **Source:** Deliverable-index bullet 7.
- **Why:** v0.2 walk is ~150 min serial. `walk_grid` is already process-pool friendly; concretising would make cache regen less painful for the audits in items C / G.
- **Effort:** ~0.5 d (joblib / multiprocessing harness + an integration test).
- **Blast radius:** none (deterministic); CI matrix grows.
- **Decision:** **in-scope.** D2 = Option 1 — no numerical change; deterministic output.

### I. Promote `σ_geom` to a §5 scan axis
- **Source:** [ADR 0001](adr/0001-v0.2-spec-anchoring.md) §"Consequences"; [`work-plan-v0-2.md` §6 D4](work-plan-v0-2.md).
- **Why:** v0.2 keeps `σ_geom` in `polydispersity.py` as a post-processing axis. Promotion to a §5 axis would let the cache carry per-σ_geom regime channels.
- **Effort:** ~2–3 d (cache schema bump, dimension expansion, CSV size grows).
- **Blast radius:** §5 cache schema change + notebook 02–05 axes.
- **Decision:** **out-of-scope — wait on breakout-note authors.** D6 = wait. ADR 0001 delegated σ_geom promotion upstream; v0.3 does not pre-empt that decision.

### J. Continuous time-evolution channel
- **Source:** [`docs/findings-physics.md` §"Time matters more than temperature"](findings-physics.md#L101), and the t_obs grid being discrete in v0.2.
- **Why:** v0.2 evaluates regimes at six fixed `t_obs` values. v0.3 candidate: solve for the time at which a fixed criterion (e.g. `bottom_mass_fraction = 0.5`) is crossed, per cell.
- **Effort:** ~1 d (root-find on Method-C output) if Method-C cache is reusable.
- **Blast radius:** new design-table; no §5 cache change if the root-find runs on cached snapshots.
- **Decision:** **in-scope.** D2 = Option 1 — root-find runs on cached §5 snapshots; no cache schema change.

### K. Stokes-Einstein corrections at sub-150-nm radii — **FIRST SLICE**
- **Source:** [program-context §3.1, slice S2](program-context.md); [ADR 0002 Decision 2](adr/0002-v0.3-spec-anchoring.md). Adopted into Tier-1 from review R4 (see Phase-9.x lab notes).
- **Why:** Continuum Stokes-Einstein begins to fail below ~150 nm radius. v0.2's diffusivity is bare SE everywhere; for the design-tool to be usable in the sub-150-nm band where FND vendors actually live, the SE breakdown coefficient must be a tunable axis.
- **Spec content:** λ-sweep over `{0.1, 0.5, 1.0}` of the SE breakdown coefficient. Calibration against the gold-nanoparticle benchmark (Laloyaux z₂ tabulations).
- **Forward-compat:** `λ = 1.0` reproduces v0.2 to machine precision (Pattern 14 zero-default extension, same shape v0.2 used for `δ_shell` / `delta_T_assumed` / `σ_geom`).
- **Effort:** ~2–3 d (parameters wiring, λ-axis on Methods A/B/C, calibration test against the gold-NP benchmark, cache regen for the new λ axis if it ships as a §5 channel rather than a side computation).
- **Blast radius:** diffusivity computation in `parameters.py`; potential §5 cache schema bump if λ becomes a scan axis; new test against the Laloyaux benchmark.
- **API contract:** S2-refined diffusivities ship with `provisional=True` metadata; the design-tool entry points refuse provisional outputs without an explicit `accept_provisional=True` override (per [ADR 0002](adr/0002-v0.3-spec-anchoring.md) §"API surface — the `provisional=True` contract"). The flag clears when S1 (DLVO aggregation) lands in a later cycle.
- **Decision:** **in-scope, first slice.** Dependency — none upstream; smaller blast radius than S1.

---

## 2. Out-of-scope candidates (firm-defer to a later cycle)

These are listed so they don't accidentally creep into v0.3:

- **Capsule-geometry port** (3D-spherical at d = 10–100 µm). v0.2 plan
  §1 keeps this as its own pilot cycle (~12 d). Confirm decision still
  holds.
- **Surfactant / non-water suspending media models.** Experimental-
  envelope deferred row; no upstream spec yet.
- **Optical readout, detection thresholds, imaging bias.** Experimental-
  envelope deferred row; not a §5 physics question.
- **Multi-particle / hindered settling / concentration-dependent
  viscosity.** Experimental-envelope dilute-limit assumption — would
  require a different transport model entirely.
- **Adsorption / wetting at boundaries.** Method-C still uses no-flux
  reflecting walls; sticky boundaries are a separate model.

Each of these is a candidate for v0.4 or a sibling pilot repository,
not v0.3.

---

## 3. Forward-compatibility contract [OPEN — first slice covered]

Two options:

1. **Anchor to `pilot-v0.2.1` (HEAD of `main` after Phase 16.1).**
   v0.3 default-mode outputs reproduce the v0.2.1 §5 cache and
   deliverables to machine precision. Same triple invariant as the
   [v0.2 plan §1](work-plan-v0-2.md): regime labels exact, ratio /
   bmf channels machine-precision, intentional schema additions
   permitted.
2. **Anchor to a v0.3 baseline.** If items A (audit-gap pin
   resolution) or G (κ(T)) move numerical channels by design, the
   v0.2.1 baseline cannot be the forward-compat target. In that
   case the contract is "v0.2 outputs reproduce when v0.3 features
   are at their compatibility-mode defaults."

**For item K (S2) specifically: Option 1.** `λ = 1.0` reproduces
v0.2.1 to machine precision (Pattern 14 zero-default extension).
The S2 slice ships under the v0.2.1 forward-compat target.

**For all in-scope slices: D2 = Option 1.** Every in-scope item
(A, B, C, F, H, J, K) reproduces `pilot-v0.2.1` at compatibility-mode
defaults. Out-of-scope items (D, E, G, I) are not evaluated against
the forward-compat contract in this cycle.

---

## 4. Phase plan

v0.2 cycle ran Phases 10–15 with `.1` review-driven follow-ups; Phase
16 / 16.1 / 16.2 / 16.3 closed the v0.2.1 cycle and articulated the
program context. v0.3 opens at Phase 17 and closes at Phase 24.

| Phase | Slice | Items | Effort estimate | Deliverable |
|---|---|---|---|---|
| 17 (opening) | Ceremony | ADR 0002 promoted; §0 / §5 D1 / D9 resolved. | 1 session | ADR 0002 `Accepted` |
| 17 (continuation) | Ceremony | §1 reshape; D2–D7 resolved; §4 / §6 / §7 filled. | 1 session | This contract |
| 18 | S2 | Item K — Stokes-Einstein corrections at sub-150-nm radii. λ-axis, Laloyaux calibration, `provisional=True` contract. | 2–3 sessions | `src/parameters.py` λ-aware diffusivity; tests; lab note |
| 19 | Tightening | Item A — resolve audit-gap pins `T_OBS_S` / `DEPTHS_M`. Item H — parallel §5 walk. | 1 session | Updated scan grid + tests; CI matrix entry |
| 20 | Tightening | Item B — continuous regime thresholds (interpolated design-table entries). | 1–2 sessions | Root-finder + revised notebooks 04/05 |
| 21 | Audit + docs | Item C — mesh-convergence audit on bmf threshold. Item F — δ_shell calibration against literature. | 1 session | Audit lab note; calibration table |
| 22 | Tightening | Item J — continuous time-evolution channel. | 1–2 sessions | `t_cross` root-finder on cached snapshots |
| 23 | Integration | Regression audit across all in-scope items; cache regen if needed; notebook refresh. | 1 session | Phase 12.1-style byte-identical verification |
| 24 | Release | Tag `pilot-v0.3`; update deliverable-index, release notes, pyproject.toml. | 1 session | Release artefacts |

Total: ~9–12 sessions, ~7–10 working days at v0.2 tempo.

Items D / E / G / I are out of scope for v0.3; they follow their own
parallel breakout tracks (program-context §3.1 S1, S6, S7, and ADR 0001
σ_geom delegation respectively).

---

## 5. Open decisions (Dn) [OPEN]

| Id | Question | Status |
|---|---|---|
| D1 | Spec anchoring (§0 options 1 / 2 / 3) | **Resolved — Option 2** ([ADR 0002 Decision 1](adr/0002-v0.3-spec-anchoring.md)). |
| D2 | Forward-compat baseline (§3 option 1 / 2) | **Resolved — Option 1 for all in-scope items.** Every in-scope slice reproduces `pilot-v0.2.1` at compatibility defaults. |
| D3 | Aggregation: in-scope, parallel breakout, or defer? (item D / program-context S1) | **Resolved — parallel breakout.** S1 requires an upstream breakout note that does not yet exist. |
| D4 | Wall hydrodynamics: in-scope or defer to v0.4? (item E / program-context S6) | **Resolved — defer to v0.4.** Exceeds the breakout-note v0.2 envelope. |
| D5 | Convection refinement: full κ(T) + gradients + evaporation, or just κ(T)? (item G) | **Resolved — defer to v0.4.** Even κ(T) alone changes §5 cache numerics by design. |
| D6 | `σ_geom` scan-axis promotion: wait on breakout-note authors, or carry as v0.3 candidate? (item I) | **Resolved — wait on breakout-note authors.** ADR 0001 delegation stands. |
| D7 | Development Status classifier: keep `3 - Alpha` through v0.3, or promote to `4 - Beta` if all pins resolve? | **Resolved — keep `3 - Alpha`.** program-context §4.1 sets `4 - Beta` at v1.0; v0.3 is a tactical tightening cycle. |
| D8 | DOI mint at v0.3, or hold to v1.0 per Phase 16.1? | Resolved — hold to v1.0. |
| D9 | First v0.3 implementation slice. | **Resolved — S2 (item K)** ([ADR 0002 Decision 2](adr/0002-v0.3-spec-anchoring.md)). |

D1, D8, D9 are settled. The rest get their own deliberation surfaces
inside the Phase 17 ceremony's continuation.

---

## 6. Risk register [PARTIAL]

Carry forward the v0.2-cycle structure. All in-scope items (A, B, C,
F, H, J, K) are listed below; out-of-scope items (D, E, G, I) carry
no mitigation in this cycle.

In-scope risks:

- **R-A1.** Pin values (`T_OBS_S`, `DEPTHS_M`) chosen without direct
  experimental validation. **Mitigation:** document as "best-estimate
  pending campaign"; no API or cache change if values are confirmed
  current.
- **R-B1.** Root-finder for continuous thresholds fails or oscillates
  at degenerate inputs (exactly on a regime boundary). **Mitigation:**
  test at degenerate §5 cache rows; fall back to grid-snapped value
  with a warning flag.
- **R-C1.** Mesh-convergence audit reveals drift larger than empirical
  tolerance. **Mitigation:** if drift is < 1 %, document as known
  limitation; if > 1 %, escalate to a Phase 21.1 fix before release.
- **R-F1.** Literature DLS measurements for functionalised FNDs
  conflict. **Mitigation:** pick the most-cited open-literature value,
  flag as audit-gap pin, note the conflict in the calibration table.
- **R-H1.** Parallel walk produces non-deterministic CSV row ordering.
  **Mitigation:** sort by `(r, T, h, t)` before write; verify
  byte-identical against serial walk at same inputs.
- **R-J1.** Continuous time-evolution root-find requires finer time
  mesh than the §5 cache holds. **Mitigation:** reuse cached snapshots
  with local interpolation; if insufficient, document as requiring a
  denser `t_obs` grid.
- **R-K1.** SE-correction λ-axis silently changes diffusivity in
  cells where v0.2 was already trustworthy. **Mitigation:** `λ = 1.0`
  default reproduces v0.2.1 to machine precision (Pattern 14
  zero-default extension); regression test pinning the v0.2.1 cache.
- **R-K2.** Downstream user trusts `provisional=True` outputs as if
  L1 were complete. **Mitigation:** the `accept_provisional=True`
  override is required at every design-tool entry point, no default,
  no env-var, no config file (per ADR 0002 §"API surface").
- **R-K3.** Laloyaux z₂ tabulations (the calibration source) prove
  insufficient for the FND radius range. **Mitigation:** name the
  fallback in the slice's lab note — likely an open-literature DLS
  cross-check on bare FNDs at 100 nm — and treat it as an audit-gap
  pin if no replacement is found.

Out-of-scope residual risk (acknowledged, not mitigated in v0.3):

- **R-D-E-G-I.** Aggregation, wall hydrodynamics, refined convection,
  and σ_geom scan-axis promotion are deferred. The v0.2 validity
  envelope remains honest but narrower than L1 requires.
  **Acceptance:** acknowledged in `docs/experimental-envelope.md`.

---

## 7. Schedule

| Milestone | Target sessions | Calendar span (approx.) |
|---|---|---|
| Phase 17 continuation (contract) | Current | 2026-04-30 |
| Phase 18 (S2 — SE corrections) | +2–3 sessions | 2026-05-01 – 2026-05-05 |
| Phase 19 (A + H) | +1 session | 2026-05-05 – 2026-05-06 |
| Phase 20 (B) | +1–2 sessions | 2026-05-06 – 2026-05-08 |
| Phase 21 (C + F) | +1 session | 2026-05-08 – 2026-05-09 |
| Phase 22 (J) | +1–2 sessions | 2026-05-09 – 2026-05-12 |
| Phase 23 (integration) | +1 session | 2026-05-12 – 2026-05-13 |
| Phase 24 (release) | +1 session | 2026-05-13 – 2026-05-14 |

Total: ~9–12 sessions, ~7–10 working days of active development.
Calendar span: ~2 weeks (allowing for session gaps).

---

## 8. Stale state swept in Phase 16.2

The doc-fix items flagged when this scaffold was drafted have been
cleared in Phase 16.2 (see
[`../lab_notes/2026-04-30-phase16-2-v0-3-deliberation-surfaces.md`](../lab_notes/2026-04-30-phase16-2-v0-3-deliberation-surfaces.md)):

- [x] [`docs/deliverable-index.md` §"Known caveats"](deliverable-index.md#known-caveats-and-audit-gap-pins)
  — "DOI pending" caveat reworded to "DOI deferred to `pilot-v1.0`",
  cross-linked to the Phase 16.1 lab note.
- [x] [`README.md`](../README.md) phase table — Phase 16.1 and 16.2
  rows added; v0.2.1 cycle header broadened to "FAIR metadata + v0.3
  deliberation".
- [x] [`docs/adr/README.md`](adr/README.md) — ADR index added,
  superseding ADR 0001's "this single document is its own index"
  closing note.
- [x] `lab_notes/README.md` — Phase 16.2 row added (16 / 16.1 were
  already present).

No outstanding pre-v0.3 doc fixes remain.

---

## 9. Acceptance / next step

This contract is accepted when all six steps below are complete:

1. ~~Drafting ADR 0002.~~ **Done.**
2. ~~Resolving D1.~~ **Done.**
3. ~~Resolving D2 / D3 / D4 / D5 / D6 / D7.~~ **Done.**
4. ~~Fixing §1 in-scope vs out-of-scope.~~ **Done.**
5. ~~Filling §4 phase plan, §6 risk register, §7 schedule.~~ **Done.**
6. ~~Removing the `SCAFFOLD` qualifier.~~ **Done.**

The v0.3 cycle is now under contract. Phase 18 (S2 — Stokes-Einstein
corrections at sub-150-nm radii) is cleared to open.

---

## 10. Cross-references

- [`program-context.md`](program-context.md) — the long-horizon goal
  document (Phase 16.3) that anchors what `pilot-v0.3` is for. v0.3
  is a tactical sub-slice inside L1; this work plan implements the
  S2 slice as the first concrete step.
- [`work-plan-v0-2.md`](work-plan-v0-2.md) — the v0.2 contract used as
  the structural template.
- [`adr/0001-v0.2-spec-anchoring.md`](adr/0001-v0.2-spec-anchoring.md)
  — spec-anchoring precedent. ADR 0002 mirrors it for v0.3.
- [`adr/0002-v0.3-spec-anchoring.md`](adr/0002-v0.3-spec-anchoring.md)
  — Accepted; resolves D1 (= Option 2) and D9 (S2 first slice).
- [`deliverable-index.md`](deliverable-index.md) §"What `pilot-v0.3`
  would change" — original candidate list this scaffold expands.
- [`experimental-envelope.md`](experimental-envelope.md) — deferred
  experimental variables, which seed §1 and §2 of this scaffold.
- [`findings-physics.md`](findings-physics.md) and
  [`findings-process.md`](findings-process.md) — inform which v0.3
  candidates have empirical / methodological motivation.
- [`release-notes/v0.2.md`](release-notes/v0.2.md) — the v0.2 release
  narrative this scaffold builds on.
- [`../lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md`](../lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md)
  — DOI deferral that resolves D8.
