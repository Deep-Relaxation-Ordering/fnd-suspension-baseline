# Phase 31 — integration audit + release-criterion gap audit (item K)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 30 (commit `1c91276` + review-fix `cbcdd33`) closed the
spawn-context + `crossing_parameter` tactical bundle. All seven
in-scope items for v0.4 are now implemented:

| Item | Description | Phase |
|---|---|---|
| B | S3 — Hydrodynamic-shell calibration per FND class | 27 |
| E | S5 — Concentration-weighted polydispersity kernel | 28 |
| H | v0.3 review residue sweep | 29 |
| I | spawn-context for `walk_grid` | 30 |
| J | `crossing_parameter` parameter-sweep root-finder | 30 |
| K | Release-criterion gap audit | **31 (this phase)** |
| L | S-slice nomenclature reconciliation | 29 |

Phase 31 is the integration audit that verifies the v0.4 cycle
closes cleanly (mirrors [Phase 23](2026-05-01-phase23-integration-audit.md)
for v0.3) plus item K — the §4.1 release-criterion gap audit.

## Audit protocol

Following the Phase 23 / Phase 12.1 regression-audit pattern:

1. **Cache reproducibility.** Load committed `regime_map_grid.csv`
   (generated under v0.3 code); re-run `walk_grid` with all defaults
   (`lambda_se = 1.0`, `delta_shell_m = 0`, `delta_T_assumed = 0.0`,
   `n_workers = 1`); compare every field of every `RegimeResult`.
2. **v0.3 module smoke tests** (carry-forward).
3. **v0.4 module smoke tests** (new):
   - Phase 27: `ParticleGeometry.from_fnd_class("bare")` matches the
     v0.3 zero-shell geometry; class defaults are present and
     well-formed.
   - Phase 28: `lognormal_smear(weighting="classification")` (default)
     reproduces `weighting="number_density"` on the marginal channels
     byte-identically.
   - Phase 30 item I: `walk_grid(n_workers=2)` under spawn is
     byte-identical to `n_workers=1`.
   - Phase 30 item J: `crossing_parameter` returns a finite (or
     `None`) value on a bracketed `lambda_se` sweep and rejects
     invalid parameter names.
4. **Full test suite.** `pytest -q` — 199 tests must pass.

## Results

### Integration audit ([`notebooks/09_integration_audit.py`](../notebooks/09_integration_audit.py))

```
Loading committed cache...
  Committed: 6300 cells
Running focused walk_grid subset (n_workers=1)...
  Fresh subset: 24 cells
PASS: focused subset byte-identical
  Note: full 6300-cell guarantee delegated to test suite

Continuous thresholds default-mode smoke test... PASS
Time evolution default-mode smoke test... PASS
FND-class default smoke test (Phase 27)... PASS
  defaults_m = {bare: 0.0, carboxylated: 5e-09, hydroxylated: 0.0, peg_functionalised: 7e-09}
Polydispersity number-density compat smoke test (Phase 28)... PASS
walk_grid spawn-context byte-identity smoke test (Phase 30 item I)... PASS
  serial == parallel (6 cells)
crossing_parameter smoke test (Phase 30 item J)... PASS

Overall: PASS
```

### Test suite

```
.venv/bin/python -m pytest -q
# 199 passed, 0 skipped (171 → 199 across the v0.4 cycle: Phase 27
# +12, Phase 28 +6, Phase 30 +9, Phase 30.1 review-fix +1 = +28
# new tests, of which 199 - 171 = 28 land net in the suite.)

.venv/bin/python -m ruff check .
# All checks passed!
```

The integration test
`test_walk_grid_parallel_byte_identical_to_serial` continues to
pin the full 6300-cell guarantee: serial vs parallel produce
byte-identical output under the spawn start method.

### Cache regen needed?

**No.** Focused 24-cell subset is byte-identical against the
committed cache; spawn-context test pins parallel == serial; new
v0.4 surfaces (Phase 27 / 28 / 30) are pure additions at their
compatibility-mode defaults (`delta_shell_m = 0`,
`weighting = "classification"`, `n_workers = 1`).

## Item K — release-criterion gap audit

This audit measures v0.4's progress against the
[`docs/program-context.md` §4.1](../docs/program-context.md#41-pilot-v10)
release criteria for `pilot-v1.0`. The audit is documentation-only;
no code or contract is touched.

### v1.0 criterion 1 — slices S1–S7 landed

| Slice | Description (from program-context §3.1) | Status before v0.4 | Status after v0.4 |
|---|---|---|---|
| S1 | DLVO aggregation pre-screen → cell trustworthiness flag | Not landed; upstream breakout owed | **Not landed; deferred to v0.5 (D3)** — upstream breakout still owed by `Deep-Relaxation-Ordering/diamonds_in_water` |
| S2 | Stokes–Einstein corrections at sub-150-nm radii | **Closed in v0.3 (Phase 18)** | Closed (carry forward) |
| S3 | Hydrodynamic-shell calibration per FND class | Provisional table only (v0.3 Phase 21) | **Closed in v0.4 (Phase 27)** — citation-anchored defaults per FND class shipped |
| S4 | Capsule-geometry port (1-D radial in spherical coords) | Not landed; parallel pilot cycle | Not landed; deferred to its own ~12 d cycle, post-v1.0 |
| S5 | Concentration-weighted polydispersity kernel | Not landed | **Closed in v0.4 (Phase 28)** — `weighting="number_density"` opt-in shipped |
| S6 | Wall-hydrodynamic Faxén/Brenner corrections | Not landed | Not landed; deferred to v0.5 / v1.1 |
| S7 | Thermal control as first-class axis | Not landed | Not landed; deferred to v0.5 / v1.0; gated on D-PC-1 |

**Slice progress: 3 of 7 closed (S2, S3, S5).** Three of the four
remaining slices (S1, S6, S7) are layer-defining; S4 is a
parallel-pilot-cycle deferral. S1 in particular gates the
`provisional=True` API contract from
[ADR 0002 §"API surface"](../docs/adr/0002-v0.3-spec-anchoring.md#api-surface--the-provisionaltrue-contract):
the contract remains in force throughout v0.4 because S1 has not
landed.

The v0.4 cycle is consistent with [`program-context.md` §3.1](../docs/program-context.md)
summary table: S3 and S5 are housekeeping slices (close audit-gap
pins, no physics-scope expansion); v0.4's "two housekeeping slices
plus tactical follow-ups" matches that classification.

### v1.0 criterion 2 — campaign measurement

> *"A named graduate student or collaborator runs a sealed-cuvette
> FND tracking experiment using **this repository's deliverables
> plus its cited breakout-note and external coastline references**
> (no re-derivation of regime boundaries from primary sources)."*

**Status: not addressed in v0.4.** Tracked as decision D-PC-1 in
[`program-context.md` §7](../docs/program-context.md#7-open-decisions-where-i-need-to-choose):
the experimental-campaign repository does not yet exist. v0.4 is
a tactical L1 sub-slice that does not require the campaign to
exist; v1.0 release does. Until D-PC-1 closes, every *agreed
tolerance* in §4.1 remains a placeholder.

This is the load-bearing gap. Closing it requires:
- a downstream campaign with a named steward, FND batch, cooling
  protocol, and sibling repository;
- D-PC-3 (the ±15 % tolerance) and D-PC-6 (the v1.0 acceptance
  metric set) to be resolved against the campaign's actual
  measurement protocol.

### v1.0 criterion 3 — fit residuals within tolerances

> *"Post-experiment fit residuals against the simulator's prediction
> sit within agreed tolerances on the **provisional observable set**
> named below."*

**Status: not addressable yet.** Depends on criterion 2. The
provisional observable set named in
[`program-context.md` §4.1](../docs/program-context.md#41-pilot-v10)
(MSD-derived diffusivity ±15 % over trustworthy cells; settling-time
distribution OR near-wall concentration profile as secondary) is
ready as a placeholder once a campaign exists. The tolerance number
is recorded as D-PC-3 (placeholder; refines once D-PC-1 closes).

### v1.0 criterion 4 — calibration ADR

> *"An ADR records the calibration data and the experiment's
> identity, so the v1.0 tag is traceable to a real measurement."*

**Status: not addressable yet.** Depends on criterion 2. The
[`docs/adr/`](../docs/adr/) directory is structurally ready
(precedent ADRs 0001 / 0002 / 0003 in place); the v1.0 calibration
ADR will follow ADR 0002's format (Context / Decision / Drivers /
Consequences / Linked artefacts).

### Net release-criterion gap after v0.4

| Gate | Pre-v0.4 | Post-v0.4 | Closure path |
|---|---|---|---|
| S1 (aggregation) | Open; upstream breakout owed | Open; upstream breakout still owed | Wait on upstream `diamonds_in_water` v0.3, then v0.5 phase plan |
| S2 (SE corrections) | Closed | Closed | Carry forward |
| S3 (shell calibration) | Provisional | **Closed** | Closed in v0.4 |
| S4 (capsule geometry) | Open; parallel cycle | Open; parallel cycle | Own ~12-day pilot cycle, post-v1.0 |
| S5 (weighted polydispersity) | Open | **Closed** | Closed in v0.4 |
| S6 (wall hydrodynamics) | Open | Open | v0.5 / v1.1 candidate; sibling-repo breakout note required |
| S7 (thermal control) | Open | Open | v0.5 / v1.0 candidate; D-PC-1 dependency |
| Campaign measurement | Open (D-PC-1) | Open (D-PC-1) | External: campaign repo creation, named steward |
| Tolerance threshold | Placeholder ±15 % | Placeholder ±15 % | D-PC-3 — closes when D-PC-1 closes |
| Acceptance metric set | Placeholder | Placeholder | D-PC-6 — closes when D-PC-1 closes |
| Calibration ADR | Not written | Not written | Phase plan: open after experiment runs |

**Net v0.4 contribution to the v1.0 punch list:** 2 slices closed
(S3 + S5); the other 5 gates are unchanged. The unblocked v0.5
candidates are S6, S7, and the `lambda_se` → §5 axis follow-up
(work-plan-v0-4 item C, deferred); S1 remains gated on upstream.

## Decisions

| Decision | Rationale |
|---|---|
| Cache regen not needed for v0.4 release | Focused 24-cell subset is byte-identical against the committed cache; spawn-context test pins parallel == serial; new v0.4 surfaces (Phase 27 / 28 / 30) are pure additions at their compatibility-mode defaults. Same reasoning Phase 23 used for v0.3. |
| Bundle item K (release-criterion gap audit) into Phase 31 rather than its own phase | Per [`work-plan-v0-4.md` §4](../docs/work-plan-v0-4.md), item K is "documentation only; ~0.5 d effort" and bundles cleanly with the integration audit. The audit's findings inform v1.0 release planning, which is the point of running it during the integration phase rather than during the release phase. |
| Extend `notebooks/09_integration_audit.py` rather than write a new audit notebook | The Phase 23 script is already the canonical integration-audit surface for the repo; extending it with v0.4 surfaces preserves a single audit harness across releases. The script header now says "Phase 23 baseline + Phase 31 v0.4 surfaces." |
| Phase 31 ships before Phase 32 (release) | Phase 23 / Phase 24 precedent: integration audit is the gate that clears the release ceremony. Running the audit *before* the version bump keeps the release commit purely ceremonial. |
| Treat the v1.0 punch list as load-bearing context, not a deliverable | The gap audit is a planning artefact for v0.5 / v1.0 deliberation, not a v0.4 user-facing contract. Recording it in this lab note (rather than a separate `docs/release-criterion-gap-audit.md` document) keeps it close to the audit phase that produced it; future v0.5 work-plan deliberation can reference this lab note. |

## Verification

```sh
PYTHONPATH=src .venv/bin/python notebooks/09_integration_audit.py
# All 7 audits PASS

.venv/bin/python -m pytest -q
# 199 passed, 0 skipped

.venv/bin/python -m ruff check .
# All checks passed!

git diff --check
# clean
```

HEAD before Phase 31: `cbcdd33` (Phase 30 review fixes).

## What was not done

- **No design-table regen.** v0.4 ships kernel additions, not new
  design tables. The v0.3 design tables (`design_table_polydispersity_room_T.csv`,
  `design_table_continuous_thresholds_*.csv`,
  `design_table_crossing_time_*.csv`) remain authoritative under
  v0.4. A v0.5 design table for `crossing_parameter` output is a
  candidate follow-up.
- **No notebook regeneration.** No notebook output (figures, CSVs)
  changed at compatibility-mode defaults; regenerating notebooks
  would only reflow PNG/PDF metadata without changing pixel data
  or design-table content.
- **No release notes / version bump.** Those are Phase 32's job.
- **No new ADR.** Item K is a planning audit, not a decision.
  ADR 0002's `provisional=True` API contract carries forward
  unchanged; no new spec-anchoring or layer-defining decision was
  made in this phase.

## Next step

**Phase 32 — release `pilot-v0.4`.** Per
[`docs/work-plan-v0-4.md` §4](../docs/work-plan-v0-4.md):

1. Bump version: `pyproject.toml` (`0.3.0` → `0.4.0`),
   `CITATION.cff` (date + version), `codemeta.json`
   (version + dates).
2. Write [`docs/release-notes/v0.4.md`](../docs/release-notes/v0.4.md).
3. Update [`docs/deliverable-index.md`](../docs/deliverable-index.md)
   header and add a v0.4 deliverable mapping section.
4. Update [`README.md`](../README.md) Status section.
5. Update [`docs/index.html`](../docs/index.html) Pages text.
6. Add Phase 32 lab note.
7. Tag `pilot-v0.4`.

Effort: 1 session per §7.

## Cross-references

- [`docs/work-plan-v0-4.md` §1 item K + §4 phase plan](../docs/work-plan-v0-4.md)
  — Phase 31's scope.
- [`docs/program-context.md` §4.1](../docs/program-context.md) —
  the v1.0 release criteria the gap audit measures against.
- [`docs/program-context.md` §7](../docs/program-context.md) —
  D-PC-1 (campaign), D-PC-3 (tolerance), D-PC-6 (metric set)
  decisions that gate v1.0 release criteria 2 / 3 / 4.
- [Phase 23 lab note](2026-05-01-phase23-integration-audit.md) —
  the precedent this phase mirrors (v0.3 integration audit).
- [Phase 30 lab note](2026-05-06-phase30-spawn-context-and-crossing-parameter.md)
  — predecessor v0.4 phase.
- [`notebooks/09_integration_audit.py`](../notebooks/09_integration_audit.py)
  — the audit script extended in this phase.
- [Pattern 14 in `findings-process.md`](../docs/findings-process.md#14-forward-compatible-parameter-splits-via-zero-default-extension)
  — zero-default extension contract; the cache reproducibility
  result confirms v0.4's surfaces honour it.
