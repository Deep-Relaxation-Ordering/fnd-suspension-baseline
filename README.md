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
├── notebooks/                      (deliverables 2–5: validation, regime map, scans, design table)
├── lab_notes/                      (dated session notes — breakout-note §4.5)
├── docs/
│   └── conventions.md              cd-rules pin + per-rule applicability + breakout-note pin
└── archive/                        (cd-rules §0.8 — deprecation, not deletion)
```

## Status

**`pilot-v0.2` cycle open.** v0.1 (tag `pilot-v0.1` at `9a0fc76`)
remains the released reference: all five §6 deliverables shipped,
full §5 grid cached, narrative triad (deliverable index, physics,
process) published. v0.2 adds the Rayleigh-number convection gate,
a hydrodynamic-vs-material radius split (`δ_shell`), and log-normal
polydispersity post-processing — all forward-compatible with v0.1
(defaults reproduce v0.1 arithmetic to machine precision). The
spec-anchoring decision is recorded in
[ADR 0001](docs/adr/0001-v0.2-spec-anchoring.md). Test suite on
the current branch: `115 passed, 0 skipped` (`92 passed` at the
`pilot-v0.1` tag). v0.2 tag will be `pilot-v0.2` at Phase 15.

## Environment

Use Python ≥ 3.11. The project metadata pins NumPy ≥ 2.0 and SciPy ≥
1.12; older system Python environments can import enough to start but
will fail the suite. From a fresh checkout:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -q
ruff check src/ tests/ notebooks/
```

Ad-hoc one-line scripts that import modules directly should either use
the editable install above or set `PYTHONPATH=src`, matching the
notebook regeneration commands.

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
| 8 | `pilot-v0.1` release tag + [`docs/deliverable-index.md`](docs/deliverable-index.md) | done — [phase-8 note](lab_notes/2026-04-28-phase8-pilot-v0-1-release.md) |
| 8.1 | post-release doc fixes (README layout, deliverable-index §4.4 lead-in) | done — [phase-8.1 note](lab_notes/2026-04-28-phase8-1-post-release-doc-fixes.md) |
| 9 | findings narrative — [physics](docs/findings-physics.md) + [process](docs/findings-process.md) | done — [phase-9 note](lab_notes/2026-04-28-phase9-findings-narrative.md) |
| 9.1 | findings corrections (Pe-label, time-evolution table, notebook-03 fallback, section count) | done — [phase-9.1 note](lab_notes/2026-04-28-phase9-1-findings-corrections.md) |
| 9.2 | arithmetic and wording fixes (65 %→67 %, "queries used") | done — [phase-9.2 note](lab_notes/2026-04-28-phase9-2-arithmetic-and-wording-fixes.md) |
| 9.3 | adversarial review fixes (threshold refinement, CI, validity envelope) | done — [phase-9.3 note](lab_notes/2026-04-28-phase9-3-adversarial-review-fixes.md) |
| **`pilot-v0.2` cycle (forward-compatible extensions)** | | |
| 10 | scope + spec-anchoring [ADR 0001](docs/adr/0001-v0.2-spec-anchoring.md) | done — [phase-10 note](lab_notes/2026-04-28-phase10-v0-2-scoping.md) |
| 11 | `src/convection.py` Rayleigh gate + `regime_map` channel | done — [phase-11 note](lab_notes/2026-04-29-phase11-rayleigh-convection-gate.md) |
| 11.1 | review fixes + Phase-12 radius data-model amendment | done — [phase-11.1 note](lab_notes/2026-04-29-phase11-1-review-fixes.md) |
| 12 | `r_material` / `r_hydro` split | in progress — [schema/parser note](lab_notes/2026-04-29-phase12-radius-schema-parser.md) |
| 13 | re-walk §5 cache with new channels | pending |
| 14 | `src/polydispersity.py` + notebook 05 + deliverable 6 | pending |
| 15 | `pilot-v0.2` release tag | pending |

The 12-day effort estimate and phase plan live in breakout-note §9.
A reverse-chronological index of session lab notes is in
[`lab_notes/README.md`](lab_notes/README.md).
