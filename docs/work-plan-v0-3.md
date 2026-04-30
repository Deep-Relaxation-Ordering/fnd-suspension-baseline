# Work plan — `pilot-v0.3` (scaffold)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

| Field | Value |
|---|---|
| Status | **OPENED against ADR 0002 (Phase 17 opening, 2026-04-30).** D1 (spec anchor) and the first-slice selection are resolved; D2 / D3 / D4 / D5 / D6 / D7 remain `[OPEN]`. Document remains a SCAFFOLD until §1 candidate menu, §4 phase plan, §6 risk register, and §7 schedule are filled — that promotion happens later in the Phase 17 ceremony, not in this opening commit. |
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
The other items remain candidates pending the §1 reshape step of the
Phase 17 ceremony.

### A. Resolve audit-gap pins `T_OBS_S` and `DEPTHS_M`
- **Source:** [`docs/deliverable-index.md` §"What pilot-v0.3 would change"](deliverable-index.md#what-pilot-v03-would-change), bullet 1.
- **Why:** These are the two scan-grid pins still flagged "physically-motivated defaults; cross-check at next spec drift."
- **Effort (rough):** 0.5–1 d if the breakout-note v0.3 names the values; 2–3 d if a §5 cache regen is required to validate alternatives.
- **Blast radius:** §5 cache invalidation if the values move.
- **Decision needed:** in-scope, gated on §0.

### B. Continuous regime thresholds (interpolated design-table entries)
- **Source:** Deliverable-index "What v0.3 would change" bullet 2.
- **Why:** v0.2 design-table entries are grid-snapped to the §5 r-axis. Root-finding on `top_to_bottom_ratio = 0.95`, `bottom_mass_fraction = 0.95`, and `p_stratified` suitability would replace 30-bin steps with continuous radii.
- **Effort:** ~1 d (root-finder per metric + revised notebooks 04 / 05).
- **Blast radius:** notebooks 04 / 05 + design-table CSV format. New tests pin the interpolation against the §5 cache rows at degenerate inputs.
- **Decision needed:** in-scope.

### C. Mesh-convergence audit on the finite-time bottom-mass threshold
- **Source:** Deliverable-index bullet 3.
- **Why:** Method-C uses 120-cell first pass + 240-cell refinement around thresholds; the 10-nm fallback floor is empirical. v0.3 would document a convergence sweep so the fidelity envelope is formal, not "tested in practice."
- **Effort:** ~1 d (sweep + audit lab note); no model change.
- **Blast radius:** documentation only if the audit confirms current behaviour; cache regen if it surfaces drift.
- **Decision needed:** in-scope.

### D. Aggregation pre-screen (DLVO `τ_agg(ζ, I, pH)`)
- **Source:** [`work-plan-v0-2.md` §1 "Out of scope (parallel tracks)"](work-plan-v0-2.md#out-of-scope-parallel-tracks), [`experimental-envelope.md`](experimental-envelope.md) deferred-variables list.
- **Why:** Aggregation flips many of the dilute-limit assumptions; the v0.2 envelope flags it as experimentally important.
- **Effort:** ~3 d per the v0.2 plan estimate.
- **Blast radius:** new module + side-channel against §5 cache, or a separate sibling pilot. Not a §5.1 label override.
- **Decision needed:** in-scope **or** parallel breakout (v0.2 plan §1 says "parallel"). §0 hybrid would split the difference.

### E. Wall-hydrodynamic correction
- **Source:** Deliverable-index bullet 4, experimental-envelope "no wall-hydrodynamic correction" row.
- **Why:** Most §5 cells have `r/h` small, but near-bottom transport is wall-sensitive. Faxén / Brenner corrections apply a position-dependent λ to the Stokes drag.
- **Effort:** ~2 d (correction term + `RegimeResult` channel + Method-C boundary-layer integration).
- **Blast radius:** Method-C cells where the bottom layer matters; Method-A unchanged.
- **Decision needed:** in-scope. If yes, recommend zero-default (`λ ≡ 1` reproduces v0.2) per Pattern 14.

### F. Calibrate `delta_shell_m` against measured FND hydrodynamic radii
- **Source:** Deliverable-index bullet 5.
- **Why:** v0.2 ships `δ_shell` as a user knob; v0.3 would translate that into a literature-anchored default range for representative functionalised FNDs.
- **Effort:** ~0.5 d if a single literature pin is acceptable; longer if a survey is wanted.
- **Blast radius:** documentation + a new audit-gap pin entry; no API change.
- **Decision needed:** in-scope.

### G. Refined convection model (T-dependent κ, gradient profiles, evaporation)
- **Source:** Deliverable-index bullet 6, [`work-plan-v0-2.md` §3 risk register](work-plan-v0-2.md), Phase 11 lab note.
- **Why:** v0.2 uses a T-independent thermal diffusivity `κ ≈ 1.4·10⁻⁷ m²/s` and a single Rayleigh threshold. v0.3 candidate: promote `κ` to T-dependent (parameters.py), allow non-uniform gradients, and add an open-cell evaporation channel.
- **Effort:** 1–2 d for κ(T); evaporation is a separate sub-phase.
- **Blast radius:** convection module + cache schema (extra column or recomputed flag).
- **Decision needed:** in-scope.

### H. Performance: parallel §5 walk
- **Source:** Deliverable-index bullet 7.
- **Why:** v0.2 walk is ~150 min serial. `walk_grid` is already process-pool friendly; concretising would make cache regen less painful for the audits in items C / G.
- **Effort:** ~0.5 d (joblib / multiprocessing harness + an integration test).
- **Blast radius:** none (deterministic); CI matrix grows.
- **Decision needed:** in-scope.

### I. Promote `σ_geom` to a §5 scan axis
- **Source:** [ADR 0001](adr/0001-v0.2-spec-anchoring.md) §"Consequences"; [`work-plan-v0-2.md` §6 D4](work-plan-v0-2.md).
- **Why:** v0.2 keeps `σ_geom` in `polydispersity.py` as a post-processing axis. Promotion to a §5 axis would let the cache carry per-σ_geom regime channels.
- **Effort:** ~2–3 d (cache schema bump, dimension expansion, CSV size grows).
- **Blast radius:** §5 cache schema change + notebook 02–05 axes.
- **Decision needed:** **breakout-note authors own this per ADR 0001.** Defer until they decide.

### J. Continuous time-evolution channel
- **Source:** [`docs/findings-physics.md` §"Time matters more than temperature"](findings-physics.md#L101), and the t_obs grid being discrete in v0.2.
- **Why:** v0.2 evaluates regimes at six fixed `t_obs` values. v0.3 candidate: solve for the time at which a fixed criterion (e.g. `bottom_mass_fraction = 0.5`) is crossed, per cell.
- **Effort:** ~1 d (root-find on Method-C output) if Method-C cache is reusable.
- **Blast radius:** new design-table; no §5 cache change if the root-find runs on cached snapshots.
- **Decision needed:** in-scope.

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

**For other slices: D2 remains [OPEN].** If items A / G land and
move numerical channels by design, those slices may need Option 2.
Decided per slice as the §1 reshape happens.

---

## 4. Phase plan [PARTIAL]

v0.2 cycle ran Phases 10–15 with `.1` review-driven follow-ups; Phase
16 / 16.1 / 16.2 / 16.3 closed the v0.2.1 cycle and articulated the
program context. v0.3 starts at Phase 17.

Phase 17 is the cycle-opening ceremony; it has two parts:

```
Phase 17 (opening, this commit)  ADR 0002 promoted to Accepted;
                                 work-plan §0 / §5 D1 / D9 resolved.
Phase 17 (continuation, TBD)     §1 candidate menu reshape against
                                 D1 = Option 2; §4 fill below; §6 / §7.
Phase 18  S2 (item K) — Stokes-Einstein corrections at sub-150-nm.
                                 Forward-compat: λ = 1.0 reproduces v0.2.1.
                                 API contract: provisional=True.
Phase 19+ (TBD)                  Additional slices once §1 reshape
                                 picks them — A / B / C / F / H / J
                                 are the most plausible candidates;
                                 D / E / G defer as parallel
                                 breakouts under D1 = Option 2.
Phase Z (release, ~Phase 24)     pilot-v0.3 release; re-pin policy
                                 per ADR 0002.
```

Phase 18 is the first concrete implementation phase; everything
between Phase 18 and the release phase remains [TBD] until the
Phase 17 continuation sets the §1 in-scope list.

---

## 5. Open decisions (Dn) [OPEN]

| Id | Question | Status |
|---|---|---|
| D1 | Spec anchoring (§0 options 1 / 2 / 3) | **Resolved — Option 2** ([ADR 0002 Decision 1](adr/0002-v0.3-spec-anchoring.md)). |
| D2 | Forward-compat baseline (§3 option 1 / 2) | [OPEN] — for item K (S2), `λ = 1.0` reproduces v0.2.1 to machine precision, favouring §3 Option 1 for that slice; other slices may differ. |
| D3 | Aggregation: in-scope, parallel breakout, or defer? (item D / program-context S1) | [OPEN] — under D1 Option 2, S1 needs an upstream breakout note that does not yet exist; v0.3 may prepare scaffolding only. |
| D4 | Wall hydrodynamics: in-scope or defer to v0.4? (item E / program-context S6) | [OPEN] — under D1 Option 2, likely deferred unless its breakout-note specifications fit the v0.2 envelope. |
| D5 | Convection refinement: full κ(T) + gradients + evaporation, or just κ(T)? (item G) | [OPEN] |
| D6 | `σ_geom` scan-axis promotion: wait on breakout-note authors, or carry as v0.3 candidate? (item I) | [OPEN] — ADR 0001 delegated this upstream; status unchanged. |
| D7 | Development Status classifier: keep `3 - Alpha` through v0.3, or promote to `4 - Beta` if all pins resolve? | [OPEN] — program-context §4.1 sets `4 - Beta` at v1.0, so v0.3 likely stays `3 - Alpha`. |
| D8 | DOI mint at v0.3, or hold to v1.0 per Phase 16.1? | Resolved — hold to v1.0. |
| D9 | First v0.3 implementation slice. | **Resolved — S2 (item K)** ([ADR 0002 Decision 2](adr/0002-v0.3-spec-anchoring.md)). |

D1, D8, D9 are settled. The rest get their own deliberation surfaces
inside the Phase 17 ceremony's continuation.

---

## 6. Risk register [PARTIAL]

Carry forward the v0.2-cycle structure. Item K (S2) is in scope as
of this opening; the rest pending §1 reshape.

In-scope (item K / S2):

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

Likely high-severity rows once §1 reshape brings other items in:

- κ(T) promotion (item G) silently drifts §5 cache numerics.
- Continuous-threshold root-finding (item B) introduces non-deterministic
  outputs if tolerances are loose.
- Parallel walk (item H) introduces ordering bugs in the persisted CSV.

---

## 7. Schedule [TBD]

Populate after §1 / §4 fix. Reuse v0.2 working-tempo estimate (1 phase
per session; ~7 working days).

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

This scaffold becomes a contract by:

1. ~~Drafting ADR 0002.~~ **Done — Phase 17 opening commit.** ADR 0002
   is `Accepted`, resolving D1 (= Option 2) and D9 (S2 first slice).
2. ~~Resolving D1.~~ **Done.** D8, D9 also resolved.
3. Resolving D2 / D3 / D4 / D5 / D6 / D7 in their own deliberation
   surfaces (Phase 17 continuation or later).
4. Fixing §1 in-scope vs out-of-scope per the resolved decisions —
   the D1 = Option 2 implication is recorded in §0, but per-item
   in-scope vs out-of-scope tags still need to be applied to §1.
5. Filling §4 phase plan, §6 risk register, §7 schedule (currently
   `[PARTIAL]` / `[TBD]`).
6. Committing the contract version under the same filename
   (`docs/work-plan-v0-3.md`), removing the `SCAFFOLD` qualifier
   from the status field.

Phase 18 (the first concrete implementation phase, S2) is the
*earliest* phase that may start under this opening, because the
slice it implements is unambiguously fixed by ADR 0002. Other
implementation phases must wait for the Phase 17 continuation to
fix §1.

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
