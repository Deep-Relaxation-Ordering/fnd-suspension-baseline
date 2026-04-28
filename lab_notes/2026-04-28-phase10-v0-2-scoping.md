# 2026-04-28 — Phase 10: `pilot-v0.2` scoping + spec-anchoring ADR

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Opening session of the `pilot-v0.2` cycle. The v0.1 release at
`9a0fc76` (with post-release polish through `94b102a`) is feature-
complete against breakout-note v0.2 (commit `3b7b18af`). Three
follow-on additions are now in scope for v0.2: the Rayleigh-number
convection gate, the hydrodynamic-vs-material radius split, and
log-normal polydispersity post-processing. Items 4 and 5 of the EC
list (aggregation pre-screen, capsule-geometry port) are out of
scope and live as separate sibling tracks.

The work plan is recorded in the conversation; this note records
the decisions Phase 10 makes — primarily, the spec-anchoring choice
captured in [ADR 0001](../docs/adr/0001-v0.2-spec-anchoring.md).

**Stance** — Integrator with Guardian residue. Work-plan composition
is principally Integrator (process, flow, synthesis); the gate at
this ADR and at the Phase-15 Handbook-completion item is Guardian.

## What was done

### `docs/adr/0001-v0.2-spec-anchoring.md`

First ADR in the repository. Documents the spec-anchoring choice for
the v0.2 cycle:

- **Problem.** Three additions in scope. Do they require a
  breakout-note v0.3 spec drift first, or can they extend v0.1
  within the existing envelope?
- **Decision.** Option B — extend v0.1 within the existing envelope.
  Implementation defaults (`δ_shell = 0`, `delta_T_assumed = 0.0 K`,
  `σ_geom → 0`) reproduce v0.1 arithmetic to machine precision, so
  the v0.1 cache, deliverables, and tag remain bit-for-bit valid.
  The breakout-note pin and cd-rules pin both stay frozen at v0.1
  values unless v0.3 of the breakout note lands during the v0.2
  cycle.
- **Three explicit upstream recommendations** are recorded for the
  breakout-note authors to act on at their tempo:
  1. Convection *should* be promoted to a §5.1 normative inclusion
     (it can flip cells outside the §5.1 classification envelope
     entirely).
  2. `δ_shell` stays implementation-level until experimental
     functionalisation data motivate §3 promotion.
  3. `σ_geom` stays deliverable-only at v0.2 — promotion to a §5
     axis would 5-10× the cache walk cost without proportionate
     scientific yield.

The ADR follows the classic Nygard format (Context / Options / Decision
/ Consequences), with a short trailing "Notes on ADR convention" so
ADR 0002 has a precedent to follow.

### Phase table for v0.2

The full phase table is recorded in the conversation work plan and
mirrored into the README. Summary:

| Phase | Surface | Wall time |
|---|---|---|
| 10 | scope + ADR (this note) | 0.5 d |
| 11 | `src/convection.py` + `regime_map` channel + tests | 1 d |
| 11.1 | review fixes (Ra threshold convention, default ΔT defensibility) | 0.25 d |
| 12 | `r_material` / `r_hydro` split + propagation through Methods A/B/C | 1 d |
| 12.1 | regression audit (full v0.1 suite at `δ_shell = 0`) | 0.25 d |
| 13 | re-walk §5 cache with new channels | 0.5 d compute + 0.25 d review |
| 14 | `src/polydispersity.py` + notebook 05 + deliverable 6 | 2 d |
| 14.1 | review fixes (σ_geom integral discretisation, r-axis edge handling) | 0.25 d |
| 15 | findings updates, deliverable-index extension, README, `pilot-v0.2` tag | 1 d |
| 15.1 | post-release doc fixes (anticipated) | 0.25 d |

Total ~7 working days across ~10 sessions; calendar 1.5–2 weeks at
v0.1 working tempo.

### Forward-compatibility contract

Pinned in the ADR Consequences block and re-stated here as the v0.2
exit-criterion: the entire v0.1 test suite (94 tests) must pass
unchanged at `δ_shell = 0`, `delta_T_assumed = 0.0 K`,
`σ_geom = 0`. The test that enforces this is Phase 12.1's
regression audit; CI catches v0.1 regressions at PR time.

The contract also implies that the existing §5 grid cache
(`notebooks/data/regime_map_grid.csv`) does *not* need to be
re-walked at the new defaults — Phase 13 re-walks because the new
*channels* (`convection_flag`, possibly an `r_hydro` provenance
column) need to be populated, not because the regime labels are
expected to change. Phase 13's diff-against-v0.1 acceptance test
will assert zero changes in the regime label columns.

### Out-of-scope (recorded for future)

- **Aggregation pre-screen dossier** (EC item 4). Owned in
  `Deep-Relaxation-Ordering/diamonds_in_water` or a sibling
  Markdown breakout. Tabulates `τ_agg(ζ, I, pH)` for
  diamond-water from DLVO inputs against the §5 t_obs axis. Effort
  ~3 d. Not blocked by v0.2.
- **Capsule-geometry port** (EC item 5). Separate breakout note in
  `diamonds_in_water` proposing a 3D-spherical port at
  d = 10–100 µm. The note alone is ~2 d; the implementation pilot
  is itself a separate ~12 d effort comparable to v0.1.

## Decisions

| Decision | Rationale |
|---|---|
| Option B (extend v0.1 within envelope), not A or C | Option A serialises v0.2 behind 4–6 weeks of upstream spec work for limited yield; Option C splits v0.2 across two parallel critical paths. Option B opens immediately and preserves v0.1 bit-for-bit. |
| Three upstream recommendations recorded as ADR consequences, not as separate documents | The ADR is the right place for "what we'd ask the spec to do next"; making them separate documents would dilute the audit trail. The breakout-note authors can lift them directly. |
| ADR 0001 becomes the first entry in `docs/adr/` | New convention. The trailing "Notes on ADR convention" section establishes Nygard format and the numbering / index policy (single file is its own index until a second ADR triggers `docs/adr/README.md`). |
| Phase numbering jumps to 10, not "v0.2 Phase 1" | Phase numbers are repo-wide and monotone. The `.0` / `.1` review-fix convention from v0.1 carries over. v0.2's release tag is `pilot-v0.2` (Phase 15); the phase numbers themselves don't restart per release cycle. |
| Forward-compatibility tested at the regression-audit level (Phase 12.1), not by feature-flagging the new code paths | Defaults that reproduce v0.1 arithmetic *are* the feature flag. A separate flag would be redundant and error-prone. The regression audit is the actual contract. |
| Did not bump `pyproject.toml` version yet | Version stays at `0.1.0` until Phase 15 release. Intermediate phases don't bump version metadata; the lab notes and ADR carry the cycle's identity. |

## Verification

```
HEAD before this pass:  94b102aa1838c957bb6189ccdfb622f90423b4b6
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
94 passed
$ ruff check src/ tests/ notebooks/
All checks passed!
```

Phase 10 is documentation-only; no code, no figures, no tests
modified. The 94-test count and ruff-clean state are inherited from
Phase 9.3 / `94b102a`.

## What was *not* done

- **No code changes.** Phase 10 is a scoping pass; Phase 11 begins
  the implementation work.
- **No upstream PR opened** against
  `Deep-Relaxation-Ordering/diamonds_in_water` for the three audit-
  gap footnotes. The ADR records the recommendations; the upstream
  authors decide when and whether to act on them. If they want a
  PR-ready patch, that's a sibling-repo task we can pick up
  separately.
- **No `docs/adr/README.md` index yet.** Single ADR is its own
  index; the index file lands when ADR 0002 is filed.
- **No `pyproject.toml` version bump.** Stays at `0.1.0` through the
  v0.2 implementation phases; bumps to `0.2.0` at Phase 15.

## Cross-references

- [`docs/adr/0001-v0.2-spec-anchoring.md`](../docs/adr/0001-v0.2-spec-anchoring.md)
  — the ADR this note is the lab-note companion to.
- Phase 9 / 9.x lab notes — the v0.1 closeout chain. v0.2 opens
  on top of that closure, not as a fork.
- [`docs/conventions.md`](../docs/conventions.md) — the cd-rules
  and breakout-note pins. Both stay at their v0.1 values.
- [`docs/deliverable-index.md`](../docs/deliverable-index.md) —
  Phase 15 will extend this with deliverable 6 (the polydispersity
  design table) and the new §4.4 test pins.
- Phase 2.5 / Phase 5 lab notes — the audit-gap-pin convention this
  ADR extends. `δ_shell` and `σ_geom` join `T_OBS_S` and the
  5th-depth value as documented audit gaps.

## Next session

**Phase 11 — Rayleigh-number gate.** First implementation work of
the v0.2 cycle.

- New module `src/convection.py` exposing
  `rayleigh_number(h, delta_T, T_kelvin)`,
  `is_convection_dominated(Ra)`, and the Rayleigh-critical
  constants for rigid-rigid (1707.762) and rigid-free (≈ 1100.65)
  Bénard cells.
- `regime_map.classify_cell` gains an optional
  `delta_T_assumed: float = 0.1 K` and an output channel
  `convection_flag: bool` on `RegimeResult`. The flag never
  overrides the §5.1 label; it sits beside it.
- New test file `tests/test_convection.py` covering closed-form
  Ra at the anchor cell, threshold round-trip,
  `convection_flag = False` for h ≤ 0.1 mm at any reasonable ΔT,
  and `convection_flag = True` for h = 10 mm at ΔT = 0.1 K.
- Audit-gap pin: `delta_T_assumed = 0.1 K` becomes the fourth
  documented audit-gap pin in the repo (after `T_OBS_S`,
  5th-depth value, and 10-nm regime-map fallback floor).

Effort estimate: 1 day. Phase 11 also drafts the upstream
recommendation text for the breakout note's §5.1 convection
footnote — the text is sibling-repo material but lives here as a
ready-to-paste snippet in the next lab note.
