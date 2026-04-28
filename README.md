# fnd-suspension-baseline

Numerical pilot: Brownian motion and gravitational sedimentation of diamond
particles in aqueous suspension as a function of particle size.

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg. Pilot implementation, not a Coastline.*

## What this repo is

The implementation of the breakout note
[*Numerical Pilot: Brownian Motion and Sedimentation of Diamond Particles in
Aqueous Suspension as a Function of Particle Size* (v0.2)](https://github.com/Deep-Relaxation-Ordering/diamonds_in_water/blob/main/breakout-note-brownian-sedimentation.md).

The breakout note is the spec; this repo is the artefact. Read the spec first:
it states scope, methods (analytical / Langevin / Smoluchowski), validation
strategy, parameter scan, regime classification, deliverables, and
acknowledged limitations. Do not paraphrase the note here.

## What this repo is not

- Not an experimental data repository (no measurements live here).
- Not a phase-transition or ice-nucleation study (deferred to a separate breakout).
- Not a comparison against the Mpemba literature (deferred).

## Project rules (inherited)

This repo follows the project-wide rules in
[`threehouse-plus-ec/cd-rules`](https://github.com/threehouse-plus-ec/cd-rules)
(Corporate Design blueprint). The pinned version and per-rule applicability
table are recorded in [`docs/conventions.md`](docs/conventions.md).

Where this repo and `cd-rules` disagree, `cd-rules` is authoritative and this
repo is amended.

### Documented deviations from the standard cd-rules folder structure (§14)

| Rule (cd-rules §14) | Standard | This repo | Justification |
|---|---|---|---|
| `index.html` at root | Required for web-rendered specimen | Omitted | Numerical pilot — no web specimen layer is intended. README + lab notes are the authored surfaces. If a rendered specimen is needed later, it will be added under `docs/` rather than at root. |
| `assets/` with `LICENCE` + `SOURCE.md` | Required for repos consuming cd-rules visual assets | Omitted | This pilot does not consume cd-rules visual assets (emblem, tokens.css). The folder will be added under Model B (§0.10) only when assets are first needed. |
| `src/`, `tests/`, `notebooks/`, `lab_notes/` | Not in the cd-rules standard tree | Added | Required by the breakout-note spec §4.3 (the implementation surfaces of a numerical pilot). These extend, not replace, the cd-rules tree. |

## Layout

```
fnd-suspension-baseline/
├── README.md                       (this file)
├── LICENCE                         (MIT — code/tooling layer per cd-rules §0.3)
├── pyproject.toml                  (Python ≥ 3.11; NumPy / SciPy / Matplotlib)
├── src/                            (implementation, per breakout-note §4.3)
│   ├── parameters.py               SI constants, water properties (Method-shared)
│   ├── analytical.py               Method A — closed-form equilibrium quantities
│   ├── langevin.py                 Method B — stochastic Langevin ensemble
│   ├── fokker_planck.py            Method C — Smoluchowski PDE (exp-fitting FV)
│   └── regime_map.py               Orchestration; produces deliverables 3 and 5
├── tests/                          (validation per breakout-note §4.4)
├── notebooks/                      (deliverables 2–4: validation, scans, regime map)
├── lab_notes/                      (dated session notes — breakout-note §4.5)
├── docs/
│   └── conventions.md              cd-rules pin + per-rule applicability + breakout-note pin
└── archive/                        (cd-rules §0.8 — deprecation, not deletion)
```

## Status

Phase 7 in — all five §6 deliverables exist. Notebook 02 produces
deliverable 3 (regime map), notebook 03 produces the parameter-scan
support figures (Method-A primitives across temperature, regime maps
per-temperature, homogeneous-radius envelope vs T), and notebook 04
produces deliverable 5 (the design table at room T as Markdown plus
multi-T full-precision CSVs). All driven from the §5 grid cache
(`notebooks/data/regime_map_grid.csv`) via the new coordinate-indexed
`regime_map.results_to_grid` helper. Methods A and C are composed by
`regime_map.classify_cell` and `walk_grid` per the §5.1 rules; Method
B remains in place as the cross-validation harness for Method C inside
its feasibility envelope. Test suite: `92 passed`.

| Phase | Surface | State |
|---|---|---|
| 0 | scaffold (repo, conventions, skipped test stubs) | done — [scaffold note](lab_notes/2026-04-27-scaffold.md) |
| 1 | `parameters.py`, water properties, Einstein–Smoluchowski check | done — [phase-1 note](lab_notes/2026-04-27-phase1-parameters-and-water-properties.md) |
| 2 | `analytical.py`, notebook 01 baseline-validation | done — [phase-2 note](lab_notes/2026-04-27-phase2-method-a-and-notebook-01.md) |
| 2.5 | review fixes (pyproject, scan grid, test polish) | done — [review-fixes note](lab_notes/2026-04-27-review-fixes.md) |
| 3 | `langevin.py` (Method B) + §4.4 stochastic checks | done — [phase-3 note](lab_notes/2026-04-27-phase3-method-b-langevin.md) |
| 3.1 | review-driven fixes (t_total honouring, snapshot scheduling) | done — [phase-3.1 note](lab_notes/2026-04-27-phase3-1-review-driven-fixes.md) |
| 3.2 | architecture polish (mean-height promotion, feasibility provenance) | done — [phase-3.2 note](lab_notes/2026-04-27-phase3-2-architecture-polish.md) |
| 4 | `fokker_planck.py` (Method C) + §4.4 PDE checks | done — [phase-4 note](lab_notes/2026-04-27-phase4-method-c-smoluchowski.md) |
| 4.1 | review-driven fixes (boundary top/bottom ratio, resolved-mesh A↔C, raw-operator mass conservation) | done — [phase-4.1 note](lab_notes/2026-04-27-phase4-1-review-driven-fixes.md) |
| 5 | `regime_map.py` orchestration (t_obs axis, classify_cell, walk_grid) | done — [phase-5 note](lab_notes/2026-04-27-phase5-regime-map-orchestration.md) |
| 5.1 | review fixes (t_obs wording, homogeneous-bmf semantics, A/B/C scope) | done — [phase-5.1 note](lab_notes/2026-04-27-phase5-1-review-driven-fixes.md) |
| 6 | grid cache + notebook 02 (deliverable-3 regime map) | done — [phase-6 note](lab_notes/2026-04-27-phase6-grid-cache-and-notebook-02.md) |
| 7 | results_to_grid + notebooks 03/04 (parameter scans + deliverable-5 design table) | done — [phase-7 note](lab_notes/2026-04-27-phase7-parameter-scans-and-design-table.md) |
| 7.1 | review fixes (envelope figure, table semantics, stale comments) | done — [phase-7.1 note](lab_notes/2026-04-28-phase7-1-review-driven-fixes.md) |
| 8 | release tag, paper-draft hooks (breakout-note §9 wrap) | next |

The 12-day effort estimate and phase plan live in breakout-note §9.
A reverse-chronological index of session lab notes is in
[`lab_notes/README.md`](lab_notes/README.md).
