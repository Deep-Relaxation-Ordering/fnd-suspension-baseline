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
├── CITATION.cff                    citation metadata (DOI deferred to pilot-v1.0)
├── codemeta.json                   CodeMeta / schema.org software metadata
├── LICENCE                         (MIT — code/tooling layer per cd-rules §0.3)
├── pyproject.toml                  (Python ≥ 3.11; NumPy / SciPy / Matplotlib)
├── src/                            (implementation, per breakout-note §4.3)
│   ├── parameters.py               SI constants, water properties (Method-shared)
│   ├── analytical.py               Method A — closed-form equilibrium quantities
│   ├── langevin.py                 Method B — stochastic Langevin ensemble
│   ├── fokker_planck.py            Method C — Smoluchowski PDE (exp-fitting FV)
│   ├── convection.py               Rayleigh-number convection side channel
│   ├── regime_map.py               Orchestration; produces deliverables 3 and 5
│   └── polydispersity.py           Log-normal smearing; produces deliverable 6
├── tests/                          (validation per breakout-note §4.4)
├── notebooks/                      (deliverables 2–6: validation, maps, scans, design tables)
├── lab_notes/                      (dated session notes — breakout-note §4.5)
├── docs/
│   ├── conventions.md              cd-rules pin + per-rule applicability + breakout-note pin
│   ├── deliverable-index.md        §6 artefact map
│   └── experimental-envelope.md    pilot assumptions and experimental knobs
└── archive/                        (cd-rules §0.8 — deprecation, not deletion)
```

## Status

**`pilot-v0.2` released.** v0.1 (tag `pilot-v0.1` at `9a0fc76`)
shipped the original five §6 deliverables. v0.2 (tag `pilot-v0.2`,
release package version `0.2.0`) adds the Rayleigh-number convection gate, a
hydrodynamic-vs-material radius split (`δ_shell`), log-normal
polydispersity post-processing, deliverable 6, and an explicit
experimental-envelope document — all forward-compatible with v0.1
(zero-default paths reproduce v0.1 arithmetic to machine precision).
The spec-anchoring decision is recorded in
[ADR 0001](docs/adr/0001-v0.2-spec-anchoring.md). Release suite:
`133 passed, 0 skipped` (`92 passed` at the `pilot-v0.1` tag), with
`ruff check .` clean. The current `0.2.1` patch adds FAIR citation,
CodeMeta, and data-schema metadata only; it does not change physics,
cache values, or notebook outputs. Patch suite: `135 passed, 0 skipped`.

## How to cite

Use [`CITATION.cff`](CITATION.cff) for citation metadata. A Zenodo DOI
is intentionally deferred to the `pilot-v1.0` release — the v0.2.x
series is a pre-v1.0 pilot, and minting a citation-grade DOI before
the physics scope stabilises would lock in a moving target. Until v1.0,
cite this repository by its GitHub URL and tag (e.g. `pilot-v0.2.1`).
See the Phase 16.1 lab note for the deferral rationale.

## Environment

Use Python ≥ 3.11. The project metadata pins NumPy ≥ 2.0 and SciPy ≥
1.12; older system Python environments can import enough to start but
will fail the suite. From a fresh checkout:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -q
ruff check .
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
| 12 | `r_material` / `r_hydro` split | done — [schema/parser note](lab_notes/2026-04-29-phase12-radius-schema-parser.md), [physics-propagation note](lab_notes/2026-04-29-phase12-physics-propagation.md) |
| 12.1 | regression audit (`δ_shell = 0` compatibility) | done — [phase-12.1 note](lab_notes/2026-04-30-phase12-1-regression-audit.md) |
| 13 | re-walk §5 cache with new channels | done — [phase-13 note](lab_notes/2026-04-30-phase13-cache-regeneration.md) |
| 14 | `src/polydispersity.py` + notebook 05 + deliverable 6 | done — [phase-14 note](lab_notes/2026-04-30-phase14-polydispersity-smearing.md) |
| 15 | `pilot-v0.2` release tag | done — [phase-15 note](lab_notes/2026-04-30-phase15-pilot-v0-2-release.md) |
| **`pilot-v0.2.1` cycle (FAIR metadata + v0.3 deliberation)** | | |
| 16 | FAIR metadata, data schemas, and v0.2 release note | done — [phase-16 note](lab_notes/2026-04-30-phase16-fair-metadata-and-v0-2-closeout.md) |
| 16.1 | defer Zenodo DOI to `pilot-v1.0` | done — [phase-16.1 note](lab_notes/2026-04-30-phase16-1-defer-doi-to-v1-0.md) |
| 16.2 | v0.3 deliberation surfaces ([work-plan scaffold](docs/work-plan-v0-3.md), [ADR 0002 stub](docs/adr/0002-v0.3-spec-anchoring.md), [ADR index](docs/adr/README.md)) | done — [phase-16.2 note](lab_notes/2026-04-30-phase16-2-v0-3-deliberation-surfaces.md) |
| 16.3 | [program-context articulation](docs/program-context.md) — long-horizon goal v0.1 (L1 / L2 / L3 layers; S1–S7 slices; release criteria for `pilot-v1.0` / `v2.0` / `v3.0`) | done — [phase-16.3 note](lab_notes/2026-04-30-phase16-3-program-context.md) |
| **`pilot-v0.3` cycle (S2 — Stokes-Einstein corrections at sub-150-nm)** | | |
| 17 (opening) | [ADR 0002](docs/adr/0002-v0.3-spec-anchoring.md) promoted to `Accepted` (D1 = Option 2; first slice = S2); [`docs/work-plan-v0-3.md`](docs/work-plan-v0-3.md) opened against it | done — [phase-17 (opening) note](lab_notes/2026-04-30-phase17-opening-adr-0002-and-work-plan-v0-3.md) |
| 17 (continuation) | v0.3 work-plan contract acceptance — §1 reshape; D2–D7 resolved; §4 / §6 / §7 filled; SCAFFOLD → contract | done — [phase-17 (continuation) note](lab_notes/2026-04-30-phase17-continuation-contract-acceptance.md) |
| 18 | S2 — Stokes-Einstein corrections at sub-150-nm radii (`lambda_se` parameter, side-computation module, audit) | done — [phase-18 note](lab_notes/2026-05-01-phase18-s2-stokes-einstein-corrections.md) |
| 19 | items A + H — `T_OBS_S` / `DEPTHS_M` audit-gap pins resolved (no value change); parallel `walk_grid` via `ProcessPoolExecutor` (`n_workers=1` default reproduces v0.2 byte-identical) | done — [phase-19 note](lab_notes/2026-05-01-phase19-audit-gap-pins-and-parallel-walk.md) |
| 20 | item B — continuous regime thresholds via `scipy.optimize.brentq` on the ratio / bmf channels; new room-T continuous CSVs alongside the unchanged grid-snapped tables | done — [phase-20 note](lab_notes/2026-05-01-phase20-continuous-thresholds.md) |

The 12-day effort estimate and phase plan live in breakout-note §9.
A reverse-chronological index of session lab notes is in
[`lab_notes/README.md`](lab_notes/README.md).
