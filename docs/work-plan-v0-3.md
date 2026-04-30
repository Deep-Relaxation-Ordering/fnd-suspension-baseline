# Work plan — `pilot-v0.3` (scaffold)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

| Field | Value |
|---|---|
| Status | **SCAFFOLD — decisions [OPEN], not accepted.** This document is a deliberation surface, not a contract. Promote to a v0.2-style contract once §1 / §3 / §5 are resolved. |
| Date | 2026-04-30 (drafted) |
| Drafted at | post-Phase 16.1, commit `e2639ff` (FAIR metadata + DOI deferral landed) |
| Predecessor tag | `pilot-v0.2` at `dfbb94d` (also `pilot-v0.2.1` once tagged) |
| Successor tag (proposed) | `pilot-v0.3` |
| Spec anchor | **[OPEN] — see §0 below** |
| Working tempo | v0.2 baseline: ~7 working days across ~10 sessions; calendar 1.5–2 weeks |

The scaffold structure mirrors [`work-plan-v0-2.md`](work-plan-v0-2.md)
so promotion to contract is mechanical. Sections marked `[OPEN]`
require a decision; sections marked `[TBD]` are populated after the
open decisions are made.

---

## 0. Spec anchoring [OPEN]

Three options, mutually exclusive:

1. **Re-anchor to breakout-note v0.3 if/when it lands.** Wait for the
   upstream breakout-note repository to publish a v0.3 spec, then pin
   to its commit per the [ADR 0001](adr/0001-v0.2-spec-anchoring.md)
   pattern. Risk: indefinite wait.
2. **Stay anchored to breakout-note v0.2 commit `3b7b18af`** (the v0.2
   pin). Treat v0.3 strictly as implementation-side tightenings of an
   already-frozen physics scope. Risk: any item that requires a
   physics-scope expansion is forced out of scope.
3. **Hybrid.** In-scope items that fit the v0.2 spec stay anchored to
   `3b7b18af`; items that require physics-scope expansion (e.g.
   aggregation, wall hydrodynamics) are split into parallel breakout
   tracks per the v0.2 plan §1 convention. Risk: bookkeeping cost.

**Decision needed before §1 can be fixed.** ADR 0002 should record
whichever option is chosen.

---

## 1. Scope candidates [OPEN]

Each item below is a **candidate** drawn from existing repo evidence,
not an in-scope decision. Format per item: motivation, source,
rough effort, blast radius, decision needed.

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

## 3. Forward-compatibility contract [OPEN]

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

**Decision needed.** Option 2 is the v0.2 pattern (which used
zero-default extensions per Pattern 14). Recommend option 2 unless
v0.3 contains zero numerical-channel changes.

---

## 4. Phase plan [TBD]

Populated once §1 is fixed. v0.2 cycle ran Phases 10–15 with `.1`
review-driven follow-ups; Phase 16 / 16.1 were FAIR metadata. v0.3
cycle would presumably start at Phase 17.

A possible shape (assuming items A, B, C, F, H, J go in scope and
D, E, G defer):

```
Phase 17  scope + spec-anchoring ADR 0002
Phase 18  audit-gap pin resolution (item A)
Phase 19  performance parallel walk (item H) — unblocks C
Phase 20  mesh-convergence audit (item C)
Phase 21  continuous regime thresholds (item B)
Phase 22  continuous time-evolution channel (item J)
Phase 23  δ_shell calibration (item F)
Phase 24  release pilot-v0.3
```

Hold the diagram empty until §1 / §3 are accepted.

---

## 5. Open decisions (Dn) [OPEN]

| Id | Question | Status |
|---|---|---|
| D1 | Spec anchoring (§0 options 1 / 2 / 3) | [OPEN] |
| D2 | Forward-compat baseline (§3 option 1 / 2) | [OPEN] |
| D3 | Aggregation: in-scope, parallel breakout, or defer? (item D) | [OPEN] |
| D4 | Wall hydrodynamics: in-scope or defer to v0.4? (item E) | [OPEN] |
| D5 | Convection refinement: full κ(T) + gradients + evaporation, or just κ(T)? (item G) | [OPEN] |
| D6 | `σ_geom` scan-axis promotion: wait on breakout-note authors, or carry as v0.3 candidate? (item I) | [OPEN] |
| D7 | Development Status classifier: keep `3 - Alpha` through v0.3, or promote to `4 - Beta` if all pins resolve? | [OPEN] |
| D8 | DOI mint at v0.3, or hold to v1.0 per Phase 16.1? | Resolved — hold to v1.0. |

D8 is the only one already settled (Phase 16.1).

---

## 6. Risk register [TBD]

Carry forward the v0.2-cycle structure. Concrete entries pending §1.
Likely high-severity rows once scope fixes:

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

1. Resolving D1 / D2 / D3 / D4 / D5 / D6 (D7 can carry forward).
2. Fixing §1 in-scope vs out-of-scope per the resolved decisions.
3. Drafting ADR 0002 (spec anchoring for v0.3, mirroring ADR 0001).
4. Filling §4 phase plan, §6 risk register, §7 schedule.
5. Committing the contract version under the same filename
   (`docs/work-plan-v0-3.md`), removing the `[SCAFFOLD]` status.

Until step 5 lands, this file is informational only and no v0.3 phase
work should start.

---

## 10. Cross-references

- [`work-plan-v0-2.md`](work-plan-v0-2.md) — the v0.2 contract used as
  the structural template.
- [`adr/0001-v0.2-spec-anchoring.md`](adr/0001-v0.2-spec-anchoring.md)
  — spec-anchoring pattern. ADR 0002 will mirror it for v0.3.
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
