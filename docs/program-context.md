# Program context — long-horizon goal and roadmap

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg. Sail-class document; not a Coastline. The deliverables
under this programme are governed by their own breakout notes and
endorsement markers; this document only states **why** the deliverables
exist and **in what order** they should be built.*

| Field | Value |
|---|---|
| Status | **v0.1 — draft, second iteration.** First articulation of the long-horizon goal that the `fnd-suspension-baseline` pilot is meant to serve. Iterated against three independent reviews; pending acceptance. |
| Date | 2026-04-30 |
| Drafted in response to | the Phase-16.1 closeout, where `pilot-v1.0` was named in the metadata as a deferred milestone but not defined in scientific terms. |
| Seeded by | breakout-note v0.2 (`Deep-Relaxation-Ordering/diamonds_in_water` commit `3b7b18af`) §8 "Out of scope (explicit deferrals)". This document goes beyond that spec — adding thermometry, nucleation, capsule geometry, and a campaign-anchored release strategy — so "anchored against" would overclaim. The breakout-note pin remains the authority for the v0.2 *implementation*; this document states what the implementation is ultimately for. |
| Spec-anchored authorities | unchanged: cd-rules pin (`ee01c80`), breakout-note pin (`3b7b18af`), ADR 0001. Future S-slices will introduce their own breakout-note pins via ADRs (ADR 0002 and onward). |
| Supersedes | the implicit roadmap previously tracked only in the deliverable-index "What `pilot-v0.3` would change" section. |
| Successor | this document is expected to grow as the programme advances; major scope changes go through ADRs (see §7 below). |

This document is the navigation chart that has been missing. Until now,
the `fnd-suspension-baseline` repository has been governed phase-by-phase
against the v0.2 breakout note, with tactical follow-ups recorded in
`docs/deliverable-index.md`. That has worked for v0.1 — v0.2, but it
does not answer the question that determines every prioritisation
decision from here on: **what experimental programme is this
infrastructure ultimately meant to serve, and how do we know when it
is sufficient?**

The goal stated in §1 is the answer to that question. The dependency
graph in §3 is the order in which the answer must be built. The
release criteria in §4 make each milestone falsifiable.

---

## 1. Long-horizon goal

The `fnd-suspension-baseline` repository, together with its planned
sibling breakouts, exists to support **the most realistic feasible
simulation of nano- to micrometre-sized diamond particles in aqueous
suspension** — and, on a longer arc, of the phase transitions of that
suspension under controlled cooling.

The simulation is the platform; three scientific destinations sit on
top of it.

### 1.1 Realism (what "most realistic" means in scope)

A simulation that an experimentalist can use as a design tool
without re-deriving regime boundaries, accounting for the
experimental knobs that *actually* shift those boundaries on the
timescale and length scale of a diamond-in-water tracking experiment:

- aggregation kinetics on minute-to-hour timescales (DLVO-class);
- hydrodynamic-vs-material radius separation, with the shell scale
  calibrated against measured functionalised-FND batches;
- Stokes-Einstein corrections at sub-150-nm radii where the
  continuum picture begins to fail;
- polydispersity beyond the v0.2 post-processing layer
  (concentration-weighted, not just classification-weighted);
- wall-hydrodynamic corrections near sealed-cell boundaries;
- thermal control as a first-class variable, not just a Rayleigh
  side channel.

### 1.2 Brownian thermometry

The diamonds are not passive tracers. Their Brownian motion *is*
a measurement of local temperature through the Stokes-Einstein
relation `D = k_B T / γ`. The simulator must therefore eventually
support trajectory-level outputs and uncertainty propagation that
let an experimentalist extract `T(x, t)` from observed FND tracks
— and, importantly, do this *consistently* with NV-centre
thermometry on the same particles. A single FND batch reporting
two different temperatures (one from its motion, one from its
fluorescence) is the kind of contradiction that needs to surface
loudly, not be averaged away.

### 1.3 Phase transitions and FNDs as nucleation seeds

The longest arc. Diamond surfaces — depending on functionalisation,
roughness, surface charge, and aggregation state — can act as
heterogeneous nucleation sites for ice. The simulator should
eventually support questions like: *for a given FND batch and
cooling protocol, what is the predicted distribution of
nucleation temperatures and times?* This is the connection point
to the wider relaxation-ordering and Mpemba-effect literature
(see breakout-note §8 deferred items, and the geometric framework
discussions referenced in `docs/findings-physics.md`'s validity
envelope).

### 1.4 What this goal is *not*

To keep the goal honest:

- This is **not** an attempt to replace experimental measurements.
  The simulator's job is to make experimental design possible, to
  flag where measurement and theory disagree, and to ground
  uncertainty bounds. It does not produce the physics; it
  encodes the physics we already have.
- This is **not** a quantum simulation. NV-centre dynamics enter
  only through their thermometric output and through their
  fluorescence as an experimental observable. Quantum Mpemba
  questions live in sibling repositories and remain out of scope
  here.
- This is **not** a colloid-science textbook. Where the literature
  has settled answers (DLVO, classical nucleation theory,
  Stokes-Einstein corrections), the simulator imports them as
  external coastlines (per the Open-Science Harbour rule that
  fundamental laws are not replicated locally). Where literature
  is unsettled or contradictory — the most important regions are
  the SE-correction band at sub-150-nm radii and heterogeneous
  nucleation propensity for diamond surfaces — this programme
  treats those regions as part of its honest validity envelope
  (`docs/experimental-envelope.md`) rather than re-deriving
  fundamentals.

### 1.5 What falsifies the *programme* (not just a release)

Programme-level falsification — distinct from the layer-level
release criteria in §4 — is the question of whether
diamonds-in-water remains the right system. Three failure modes
would force a strategic rethink rather than a tactical fix:

- **System-level mismatch.** If experimental campaigns (L1 onward)
  reveal that bare/functionalised FNDs in pure water are too noisy,
  too aggregation-prone, or too vendor-variable for the design-tool
  use case the simulator targets, the simulator can be repurposed
  as a methods-only artefact (Zenodo deposit, methods paper) rather
  than continued as a campaign-supporting tool.
- **Coastline obsolescence.** If a paper supersedes the SE-correction
  or DLVO formulations the simulator imports, the simulator does
  *not* re-derive — it reissues with the new pin. If a whole
  family of imports collapses (e.g. continuum hydrodynamics turns
  out not to apply at the scales targeted), the programme contracts
  to the regime where its imports remain valid.
- **Experimental-campaign collapse** (see D-PC-1). If the downstream
  experimental campaign cannot be staffed or funded within the L1
  cycle, v1.0 cannot be released against an experiment, and the
  programme is paused at the last clean tactical release until a
  campaign exists.

These outcomes are not failures of *engineering*; they are
falsifications of *programme assumptions*, and each has a
respectable exit path.

---

## 2. Programme prerequisites and risks

Before describing the architecture (§3) and release criteria (§4),
two structural facts must be visible.

**P-1. The experimental-campaign repository does not yet exist.**
Every "agreed tolerance" in §4 and the "named graduate student"
clause in §4.1 are conditional on a downstream experimental
programme being staffed, funded, and given a steward and a
sibling repository. This is the load-bearing dependency of the
entire programme. It is also tracked as decision D-PC-1 in §7,
because closing it requires choices that lie outside this
document. Until P-1 is resolved, §4 release criteria remain
*placeholders* — the document is a complete navigation chart, but
the harbour at the end of L1 is still being surveyed.

**P-2. Sibling-repo continuity is assumed but not guaranteed.**
The dependency chain in §5 leans on
`Deep-Relaxation-Ordering/diamonds_in_water` to deliver pinned
breakout notes for each S-slice. If that delivery stalls, this
repository may need to author specs locally under the audit-gap-pin
convention (the same pattern used for `T_OBS_S` and the 5th-depth
value in v0.1, and for `δ_shell` in v0.2), then transfer them
upstream once the sibling catches up. §5 makes this fallback
explicit.

These two prerequisites are *named* here so they cannot be
treated as bookkeeping lower in the document.

---

## 3. Architecture: three layers, three timescales

The goal decomposes into three layers. Each layer requires the
previous layer to be in place; each layer produces a falsifiable
release.

| Layer | Question | Releases | Active-development | Calendar (with upstream waits) |
|---|---|---|---|---|
| **L1 — Realism** | Can a student plan a sealed-cuvette FND tracking experiment from the simulator's deliverables and cited references, with realistic aggregation, hydrodynamics, and polydispersity? | `pilot-v1.0` | ~6–9 months focused implementation | ~12–24 months, dominated by upstream-spec drafting and data procurement |
| **L2 — Thermometry** | Does the simulator, given an FND trajectory, recover the local temperature consistently with NV-centre fluorescence on the same particle? | `pilot-v2.0` | ~6–9 months active | ~12–18 months |
| **L3 — Nucleation** | Given an FND batch in a sealed micro-cell under a cooling protocol, can the simulator predict the distribution of nucleation temperatures and times within the experimental error bars? | `pilot-v3.0` | open horizon, scope sketch only | open horizon, ≥ L2-end |

The release numbering is deliberate: each major-version bump
corresponds to closing one scientific layer, not to a tactical
batch of improvements. Tactical work (new tests, refactors,
audit-gap pin closures) ships as `vX.Y` minor or patch releases
inside the layer it serves. **`pilot-v0.3` is a tactical sub-slice
*inside* L1, not the L1 release itself; ADR 0002 and
[`docs/work-plan-v0-3.md`](work-plan-v0-3.md) decide which
S1/S2-adjacent tightenings happen first**, with capsule geometry,
optical readout, multi-particle effects, and the rest of the
S-slices remaining firm v0.3 deferrals.

The "active-development" and "calendar" columns separate
implementation velocity (which v0.1–v0.2 demonstrated at ~7
working days for a contained slice) from calendar time (which is
dominated by upstream breakout-note drafting and experimental-data
procurement, neither under this repo's control). 12–24 months of
calendar time for L1 is realistic if every dependency lands
cleanly and a campaign exists — see P-1 above.

L3's resolution in this document is deliberately lower than L1's.
S12-S15 are scope sketches, not implementation plans; the
breakout notes that would specify them have not been written.
This is honest: by the time L3 starts, the L1 and L2 results will
have reshaped what L3 should look like.

### 3.1 Layer 1 (Realism) — `pilot-v1.0`

Goal-anchored release: see §4.1.

Slices, in dependency order. The S1–S2 ordering is the most
contested; both slices are "must land before v1.0" and the
proposal here resolves the tension noted in review.

**Summary table** (one row per slice; for ADR-level reasoning):

| Slice | Physics content | Needs sibling breakout? | Needs external data? | Layer-defining or housekeeping? |
|---|---|---|---|---|
| S1 | DLVO aggregation timescale → cell trustworthiness flag | Yes — owed by `diamonds_in_water` | No (literature DLVO parameters) | Layer-defining |
| S2 | Stokes-Einstein corrections at sub-150-nm | No (Tier-1 R4 already accepted) | Gold-nanoparticle benchmark (Laloyaux z₂; published) | Layer-defining |
| S3 | Hydrodynamic-shell calibration per FND class | No | Yes — manufacturer data sheets *or* open-literature DLS (contingency) | Housekeeping (closes audit-gap pin) |
| S4 | 1-D radial port for spherical sealed cells | Yes | No | Layer-defining |
| S5 | Concentration-weighted polydispersity kernel | No | No | Housekeeping (kernel-weight refactor) |
| S6 | Wall-hydrodynamic Faxén/Brenner corrections | Probably (boundary-condition specs) | No | Layer-defining; **may defer to v1.1** |
| S7 | Thermal control as first-class axis | No | Yes — sealed-cell cooling protocol from campaign | Layer-defining |

The "layer-defining vs housekeeping" column matters for v1.0 release
gating: housekeeping slices can ship as `vX.Y` patches without
breaking the v1.0 release criterion, but layer-defining slices
cannot. S6's "may defer" status in particular means a v1.0 release
could ship with S1–S5, S7 if the campaign geometry does not put
particles within ~5 radii of the wall.

**S1 — Aggregation pre-screen.** The killer assumption (breakout-
note §7b). Without it, every regime-map cell is dishonest at the
t_obs band the design table sits in. DLVO-class estimate from
Hamaker constant, zeta potential, ionic strength; output is a
characteristic aggregation timescale `τ_agg(ζ, I, pH)` that the
regime classifier consumes as a cell-by-cell *trustworthiness
flag* (cell is "trustworthy" only when `t_obs ≪ τ_agg`).

S1 owns the trustworthiness flag for cells in the §5 cache. Its
breakout note is owed by `Deep-Relaxation-Ordering/diamonds_in_water`
and does not yet exist.

**S2 — Stokes-Einstein corrections at sub-150-nm radii.** Adopted
into Tier-1 from review R4 (see Phase-9.x lab notes). λ-sweep over
{0.1, 0.5, 1.0} of the SE breakdown coefficient. Calibration
against the gold-nanoparticle benchmark (Laloyaux z₂ tabulations).
Forward-compatible: λ = 1.0 reproduces v0.2.

**S2 ships first as the implementation-ready slice while the S1
breakout is being drafted upstream**, because S2 has smaller blast
radius and no upstream dependency. **However: S2 outputs are not
trustworthy in absolute terms until S1 lands** — S2 refines the
diffusivity *given* a trusted radius; S1 establishes when the
radius can be trusted. The combination matters; the order is a
sequencing convenience, not an independence claim.

To enforce this at the interface level rather than rely on
documentation: S2-refined diffusivities are tagged
`provisional=True` in their result objects until the S1 slice
lands, and the design-tool entry points (the planned `plan_*`
helpers) refuse to consume `provisional=True` outputs without an
explicit override. This prevents well-meaning downstream users
from treating an intermediate slice as if L1 were complete. ADR
0002 will pin the exact API surface.

**S3 — Hydrodynamic-shell calibration.** Replace `δ_shell` from
its current "user-supplied geometry knob" status (audit-gap pin
in `docs/deliverable-index.md`) with a calibrated default per
nominal FND class. Three or four classes is enough: bare,
carboxylated, hydroxylated, PEG-functionalised. Source:
manufacturer data sheets cross-checked against literature DLS
measurements.

*Contingency.* Manufacturer data sheets for functionalised FNDs
may be proprietary or NDA-bound. If batch-specific data is not
available without a collaboration agreement, S3 calibrates
against open-literature DLS only and flags affected batches as
"unverified" in the simulator metadata. The repo never blocks on
proprietary data.

**S4 — Capsule-geometry port (radial 1-D approximation).** The
simulator extends from the current 1-D Cartesian slab to a 1-D
radial coordinate in spherical geometry, for sealed micro-cells
of diameter d = 10–100 µm. **S4 is *not* a full 3-D simulator** —
that would be a sub-programme on the scale of the entire L2
layer and is explicitly out of scope here. The radial-1-D port:
Method A retains closed-form equilibrium quantities adapted to
spherical coordinates; Method B simulates radial trajectories
with reflecting boundary at r = R; Method C runs the
Smoluchowski PDE on the radial grid with appropriate Jacobians.
Sibling-repo breakout note required first.

**S5 — Concentration-weighted polydispersity.** The v0.2
polydispersity layer is classification-weighted: each radius bin
gets the §5.1 label and a probability. For tracking experiments,
what matters is the *number-density* distribution within each
band. Bounded change to `lognormal_smear`'s weighting kernel.

**S6 — Wall-hydrodynamic corrections.** Position-dependent
Faxén/Brenner corrections to drag and diffusivity near the sealed-
cell boundary. New physics layer (not just parameter expansion):
introduces a near-wall dimensionless parameter (particle-wall
separation / radius) and modifies Method A/B/C kernels. **S6 is
the largest L1 slice after S4 and may be deferrable to a `v1.1`
patch release** if the L1 campaign's geometry does not put
particles within ~5 radii of the wall on the t_obs timescale.

**S7 — Thermal control as a first-class variable.** Promote
`delta_T_assumed` from its current side-channel status to a
first-class axis where experimentally relevant. Sealed-cell
thermal protocols and lateral gradients enter here. (Open-cell
evaporation is *out of scope* — see §6 deferrals; S7 is
sealed-cell only, consistent with the rest of the programme.)

The L1 punch list from `docs/deliverable-index.md` "What
`pilot-v0.3` would change" — interpolated thresholds, parallel
walks, mesh-convergence audit at the bmf threshold, σ_geom
calibration — folds into the closing tactical work for
`pilot-v1.0` across S5–S7. None of those items are layer-defining;
they are the housekeeping that lets v1.0 ship cleanly.

### 3.2 Layer 2 (Thermometry) — `pilot-v2.0`

Goal-anchored release: see §4.2.

Slices:

**S8 — Trajectory-level output APIs.** Method B (Langevin) already
produces trajectories. What's missing is: a clean `trajectory →
T_estimate(x, t)` pipeline with full uncertainty propagation, and
a notebook that demonstrates it on synthetic ground-truth data.

**S9 — NV-thermometry consistency model.** The "Dual-mode FND
thermometry breakout" listed in breakout-note §8. Encode the
NV-centre temperature dependence (well-established literature)
and provide a checking utility: given simultaneous measurements
of FND motion and fluorescence, do the two thermometers agree?

**S10 — Optical-readout model (PSF-convolved projection).** Forward
model: given a particle distribution and a microscope geometry,
what does the camera see? **Initially scoped to a Gaussian PSF
plus shot-noise approximation** — full vectorial PSF (Gibson-
Lanni etc.) is a sub-programme deferred to L2's tactical
follow-ups. Source for tracking-localization uncertainty, fed
back into S8's uncertainty propagation.

**S11 — Calibration protocol document.** Out-of-repo: a Sail or
Coastline document specifying the calibration sequence that an
experimentalist runs before trusting either thermometer. Lives
in the experimental-campaign sibling repo when that exists.

### 3.3 Layer 3 (Phase transitions) — `pilot-v3.0`

Goal-anchored release: see §4.3. Resolution intentionally lower
than L1; these slices are sketches.

**S12 — Heterogeneous nucleation layer.** Classical nucleation
theory with surface-chemistry-dependent contact angle. Per FND
class, predict heterogeneous nucleation rate `J_het(T, P_b)`
where `P_b` is the per-particle nucleation propensity (treated
as the parameter being learned from experiment, not predicted
ab initio). This is conservative — we are *not* claiming to
predict diamond's surface energy from first principles; we are
encoding that a given batch has a `P_b` that can be measured.

**S13 — Front-dynamics model (sharp-interface or phase-field).**
The "Particle-ice front interaction breakout" from breakout-note
§8. Once nucleation has happened, what does the ice front do, and
what does it do *to* the particles (engulfment vs rejection vs
push)? **The choice between sharp-interface (Stefan problem,
lighter but stiff) and phase-field (Allen-Cahn/Cahn-Hilliard,
heavier but regularising) is itself a decision** — D-PC-7 in §7,
to be resolved before S13 opens.

**S14 — Coupled thermal field.** The advection-diffusion equation
for `T(x, t)` in the sealed cell, coupled to the suspension.
Drives the nucleation rate spatially.

**S15 — Mpemba-relevant comparisons.** The "Connection to the
classical or quantum Mpemba effect" deferred breakout. By this
stage we have enough infrastructure to ask: under what cooling
protocols and FND-batch parameters does a "hot" initial
condition reach nucleation faster than a "cold" one? This is the
question the wider research programme has been pointing at all
along, and it is also the slice that — *honestly* — may turn out
to be a Coastline-level "no, the effect is not robust" result
rather than a positive demonstration. Both outcomes are
publishable.

---

## 4. Release criteria (falsifiable v1.0 / v2.0 / v3.0)

The current deferral text in `CITATION.cff` and `codemeta.json`
("DOI deferred to pilot-v1.0; pre-v1.0 pilots have a moving physics
scope") becomes well-defined under this roadmap, **conditional on
P-1**.

*Programme-level falsification (§1.5) concerns whether
diamonds-in-water remains the right system at all; the layer-level
criteria below concern whether a given layer is scientifically and
experimentally closed. The two are distinct and must not be
conflated — a layer-level miss is a model failure within an
intact programme; a programme-level falsification triggers
strategic rethink, not just the next iteration.*

### 4.1 `pilot-v1.0`

Ships when **all** of the following are true:

- [ ] Slices S1–S7 (aggregation, SE corrections, shell calibration,
      capsule geometry, weighted polydispersity, wall corrections,
      thermal control) have landed, each behind a forward-
      compatibility contract analogous to v0.2's `δ_shell = 0`,
      `delta_T_assumed = 0.0 K`, `σ_geom → 0`. (S6 may be deferred
      to a v1.1 patch — see §3.1.)
- [ ] A named graduate student or collaborator runs a sealed-
      cuvette FND tracking experiment using **this repository's
      deliverables plus its cited breakout-note and external
      coastline references** (no re-derivation of regime
      boundaries from primary sources).
- [ ] Post-experiment fit residuals against the simulator's
      prediction sit within agreed tolerances on the **provisional
      observable set** named below. The set is provisional in the
      sense that D-PC-6 may refine it once the campaign exists;
      naming it now breaks the circularity in which D-PC-6 waits
      on a campaign that waits on this document.

      *Provisional observable set for v1.0 (D-PC-6 to confirm or
      refine):*
      - **Primary:** mean-squared-displacement-derived diffusivity
        `D(r, depth)` averaged over the design-tool's t_obs
        window, compared cell-by-cell against the regime map.
        Tolerance placeholder: ±15 % over trustworthy cells (see
        S1 trustworthiness flag).
      - **Secondary:** one of (i) settling-time distribution to
        a chosen depth, or (ii) near-wall concentration profile
        at t = t_obs. The choice between (i) and (ii) depends on
        whether S6 has landed; D-PC-6 picks.
      - **Falsification condition:** v1.0 is *not* released if the
        primary observable misses by more than the agreed
        tolerance on any trustworthy cell, or if the secondary
        observable disagrees in a way the primary does not capture.

- [ ] An ADR records the calibration data and the experiment's
      identity, so the v1.0 tag is traceable to a real measurement.

The Zenodo DOI is minted at this tag. The repository transitions
from `Development Status :: 3 - Alpha` to `4 - Beta`.

### 4.2 `pilot-v2.0`

Ships when:

- [ ] Slices S8–S11 have landed.
- [ ] A controlled measurement on a calibrated FND batch returns
      consistent temperatures from the two thermometers (Brownian
      and NV) within combined uncertainty across the 5–35 °C range.
- [ ] An **independent L2 anchor** validates the thermometry
      pipeline against external truth — not just internal
      self-consistency. Candidate anchors: a calibrated thermal
      stage with NIST-traceable temperature; a published
      interferometric thermometry result on a comparable FND
      batch. The L1-side gold-nanoparticle benchmark for SE
      corrections is *not* a sufficient L2 anchor because both
      thermometers are then calibrated against overlapping data.
- [ ] The dual-mode-thermometry breakout note has been written and
      published in the sibling repository.

### 4.3 `pilot-v3.0`

Ships when:

- [ ] Slices S12–S15 have landed.
- [ ] A measurement campaign on a sealed FND-loaded micro-cell
      under a specified cooling protocol produces a nucleation-
      temperature distribution within the simulator's predicted
      error bars (or, alternatively, returns a clean falsification
      of the model — also a v3.0 release condition).
- [ ] The sharp-interface vs phase-field choice (D-PC-7) has
      been resolved with a sibling-repo breakout note.
- [ ] The phase-field-or-sharp-interface, heterogeneous-nucleation,
      and Mpemba-connection breakout notes have all been published.

---

## 5. Coupling to sibling repositories

This repository sits in a chain. The chain is currently:

```
[fnd-suspension-experiment — does not yet exist]
        |
        v
[Deep-Relaxation-Ordering/diamonds_in_water]   (breakout notes; specs)
        |
        v
[fnd-suspension-baseline]                       (this repo; numerical pilot)
        |
        v
[downstream consumers]                          (notebook drafts, paper drafts, …)
```

The placeholder name `fnd-suspension-experiment` does not yet
correspond to a real repository — see D-PC-1.

What each link owes the next:

- **`fnd-suspension-experiment`** (when it exists) owes the
  breakout notes a clear statement of *what is being measured*,
  *what the success criterion is*, and *which FND batch is being
  used*. Without this, the breakout notes have no anchor and the
  "physics scope stabilises" deferral remains circular.
- **`Deep-Relaxation-Ordering/diamonds_in_water`** owes this repo
  pinned breakout notes for each S-slice in §3, in the dependency
  order stated there. The current pin (v0.2 commit `3b7b18af`)
  remains valid until S1 (aggregation pre-screen) needs an
  upstream breakout — the next required pin movement.
- **This repo** owes the experimental campaign: deliverable
  artefacts (regime maps, design tables, calibration protocols),
  honest validity envelopes (`docs/experimental-envelope.md`), and
  forward-compatibility (the v0.2 zero-default extension pattern is
  the engineering contract).
- **Downstream consumers** (notebook drafts, paper sections) read
  from this repo's deliverable index and findings documents; they
  do not modify them.

**Supplier-failure clause (P-2).** If
`Deep-Relaxation-Ordering/diamonds_in_water` does not deliver a
required S-slice breakout note on the timeline this programme
needs, this repository may author a *local* spec under the
audit-gap-pin convention (parallel to `T_OBS_S`, the 5th-depth
value, `δ_shell`, and `σ_geom` in v0.1/v0.2). The fallback
follows a three-step procedure to prevent quiet divergence
between local specs and upstream breakouts:

1. **Local spec authored as if upstream.** Any local spec is
   structured with the same sections, assumption-explicitness,
   and validity-envelope language as a `diamonds_in_water`
   breakout note. It is filed in this repo's `docs/local-specs/`
   under the slice name and labelled "audit-gap pending upstream."
2. **Synchronisation ADR on upstream materialisation.** When the
   real upstream breakout appears, an ADR is filed with an
   explicit "diff to local spec" section — what changed, what
   stayed, and which assumptions need re-validation. The local
   spec is then archived (not deleted) with a link to the ADR.
3. **Re-run affected tests.** Any test whose constants came from
   the local spec is re-run against the upstream version; failures
   trigger a slice-level patch release.

This pattern was unblocking in v0.2 (ADR 0001 recommendations to
upstream); making it explicit here means the programme cannot be
silently stalled by upstream delay *and* cannot silently drift
when upstream catches up.

**Coastline drift handling.** External coastlines (DLVO, CNT,
Stokes-Einstein and its corrections) are imported by citation,
not replicated. When a paper supersedes one of these — e.g. a new
SE-correction formulation that supersedes the Laloyaux z₂
tabulations used in S2 — the simulator does *not* re-derive. The
update procedure is: file an ADR naming the new coastline source,
update the citation in the affected slice's documentation, and
re-run the affected tests with the new constants. Coastline
versions are pinned by citation, not by source code.

---

## 6. Out of scope (explicit deferrals — what this programme is *not*)

To prevent scope creep:

- **Quantum-simulation problems.** NV-centre quantum dynamics are
  encoded as input/output couplings (their thermometric reading,
  their fluorescence as a marker), not simulated. Quantum Mpemba
  questions live in `quantum-relaxation-ordering` and similar
  sibling tracks, not here.
- **Colloid-science fundamentals.** DLVO, classical nucleation
  theory, Stokes-Einstein corrections, hydrodynamic interactions
  enter as *external coastlines* with citations. The simulator
  does not re-derive them.
- **Microfluidic device engineering.** The capsule-geometry port
  (S4) treats the cell as a boundary condition; it does not
  simulate the fabrication, surface treatment, or filling
  protocol of the cell.
- **Atmospheric ice nucleation.** A sealed micro-cell with
  controlled FND loading is a different problem from atmospheric
  cloud-droplet freezing; the literature and parameter ranges
  are different. Cross-references will be cited where useful but
  the simulator targets the laboratory geometry only.
- **Open-cell / evaporative geometries.** The simulator targets
  sealed micro-cells throughout. Open-cell evaporation, meniscus
  dynamics, and exposed-surface chemistry are out of scope at
  every layer.
- **Real-time / online operation.** This is a design-and-analysis
  tool, not an experiment-control loop. ARTIQ and similar real-
  time control infrastructure live in other repositories.
- **Replacing the experimental measurement.** The simulator
  predicts; the experiment decides. A v3.0 result that disagrees
  with a careful measurement is a model failure, not a
  measurement failure.
- **Full 3-D Cartesian simulation.** S4's capsule-geometry port is
  1-D radial in spherical coordinates. Full 3-D simulation (with
  asymmetric flows, lateral inhomogeneity, coupled tracking
  pipelines) is a sub-programme outside the L1–L3 scope.
- **Full vectorial PSF / image-formation modelling.** S10's
  optical-readout model is Gaussian-PSF-plus-shot-noise.
  Gibson-Lanni and similar full-vectorial models are deferred
  beyond L2.

---

## 7. Open decisions (where I need to choose)

This document is a v0.1 draft. Several decisions are genuinely
open and the document will only stabilise once they are made.

**D-PC-1.** **The experimental-campaign repository.** Load-
bearing — see §2 P-1. This programme requires a downstream
campaign to be falsifiable. The campaign needs a name, a steward,
an FND batch, a cooling protocol, and a sibling repository.
Until this exists, every "agreed tolerance" in §4 remains a
placeholder. The most defensible candidate hosts:
`AG-Schaetz-internal` (private) or a new public repo
`fnd-suspension-experiment` parallel to this one. **Decision
gates `pilot-v1.0` scope acceptance, not Phase 17.** Phase 17
(v0.3 acceptance ceremony) can proceed because v0.3 is tactical
sub-slice work inside L1 and does not require the campaign to
exist; v1.0 release does.

**D-PC-2.** **The order of S1 and S2.** Resolved in §3.1: **S2
ships first** as the implementation-ready slice (no upstream
dependency, smaller blast radius), with S1 following once the
upstream breakout note lands. S2's outputs are not absolutely
trustworthy until S1 is in place — this is a sequencing
convenience, not an independence claim.

**D-PC-3.** **The v1.0 tolerance threshold.** ±15 % is a
placeholder. The right number depends on the experimental
measurement's own precision, which depends on D-PC-1.

**D-PC-4.** **Whether to publicise this document as a Sail in
the Open-Science Harbour vocabulary**, or to keep it as an
internal `docs/` document until v1.0 ships. Publishing it
commits to the goal in public; keeping it internal preserves
flexibility to repivot. My read: **internal until S1 lands**,
then promote to a Sail with the next ADR. If promoted, the
Sail/Coastline vocabulary in this document will need a one-
sentence gloss for external readers.

**D-PC-5.** **Whether `pilot-v1.0` is followed by a Zenodo DOI
*or* a Zenodo DOI plus a methods journal paper.** A v1.0 methods
paper on the simulator with realistic aggregation and capsule
geometry is plausibly publishable on its own merits, independent
of v2.0's thermometry result. Splitting "DOI for v1.0, paper for
v2.0" might cost a citable methods publication. Two viable
options:
- **(a)** DOI at v1.0, methods paper at v2.0 with thermometry
  as the headline (lower upfront effort, single paper).
- **(b)** DOI + methods paper at v1.0, application paper at v2.0
  (double the writing effort but two citable publications).
My read: lean toward **(b)** if a campaign exists; **(a)** if
not. Tied to D-PC-1.

**D-PC-6.** **The v1.0 acceptance metric set.** §4.1 says "fit
residuals against the simulator's prediction" — but on what
observable? Trajectory MSD curves, concentration profiles vs
depth, settling-time distributions, regime-map labels at
specific t_obs? Each gives a different ±15 % and a different
experimental measurement protocol. The metric set must be named
before D-PC-3's tolerance can be quantified. **Decision needed
alongside D-PC-1**, because the metric depends on what the
campaign measures.

**D-PC-7.** **Sharp-interface vs phase-field for S13.**
Different numerical regimes, different stiffness profiles,
different literature. Decision deferred until L3 opens; flagged
here to prevent the choice being made implicitly at
implementation time.

**D-PC-8.** **Funding cadence and steward continuity.** Out of
scope for a science roadmap, but a 12–24 month L1 followed by
12–18 month L2 is a funding-cycle concern. Explicitly deferred
here: this document does not commit to a funding strategy, but
flags that the timeline is not staff-neutral.

---

## 8. Cross-references

- breakout-note v0.2 §8 "Out of scope (explicit deferrals)" —
  the source list of follow-up breakouts that §3 sequences.
- [`docs/deliverable-index.md`](deliverable-index.md) "What
  `pilot-v0.3` would change" — tactical punch list, now subsumed
  into S5–S7 housekeeping for `pilot-v1.0`.
- [`docs/findings-physics.md`](findings-physics.md) "Model
  validity envelope" — the honest statement of the gaps this
  programme is designed to close.
- [`docs/experimental-envelope.md`](experimental-envelope.md) —
  per-assumption mapping of pilot model to experimental knobs;
  S1–S7 each remove one row from the "deferred" column.
- [`docs/work-plan-v0-3.md`](work-plan-v0-3.md) — the next
  tactical work plan; §3 of this document constrains its scope.
- [`docs/adr/0001-v0.2-spec-anchoring.md`](adr/0001-v0.2-spec-anchoring.md)
  — precedent for ADR-style scoping decisions; ADR 0002 (next)
  picks the first S-slice for v0.3.
- [`docs/release-notes/v0.2.md`](release-notes/v0.2.md) and
  [`lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md`](../lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md)
  — the DOI-deferral chain whose target this document defines.

---

## 9. How this document is maintained

- v0.1 → v1.0 of *this document* (program-context.md) tracks the
  programme's clarity, not the simulator's version. Bumps happen
  when an open decision in §7 is closed, when a new layer is
  added, or when an S-slice is reordered against new evidence.
- Each version bump records its diff in
  [`lab_notes/`](../lab_notes/) under a dated `program-context-bump`
  entry, parallel to the phase-note convention.
- This document is *not* a Coastline. It does not endorse the
  external-coastline content it cites (DLVO, CNT, SE). It only
  states what this repository plans to do with those coastlines
  and in what order.
