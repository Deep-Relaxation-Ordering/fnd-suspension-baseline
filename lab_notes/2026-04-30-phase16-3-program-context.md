# Phase 16.3 — program-context articulation (long-horizon goal v0.1)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 16.1 deferred the Zenodo DOI mint to `pilot-v1.0` and Phase 16.2
shipped the v0.3 deliberation surfaces ([work plan scaffold](../docs/work-plan-v0-3.md),
[ADR 0002 stub](../docs/adr/0002-v0.3-spec-anchoring.md), [ADR index](../docs/adr/README.md)).
The closeout exposed a structural gap: `pilot-v1.0` was named in
`CITATION.cff` and `codemeta.json` as a deferred milestone but it was
never defined in scientific terms. The implicit roadmap lived only in
[`docs/deliverable-index.md`](../docs/deliverable-index.md) §"What
`pilot-v0.3` would change", which is a tactical punch list — not a
navigation chart.

Without a chart, every prioritisation decision in the v0.3 cycle and
beyond inherits an unstated long-horizon assumption. Phase 16.3 lands
the chart so the v0.3 acceptance ceremony (Phase 17) can anchor
against it.

This phase deliberately does **not** open Phase 17. The acceptance
ceremony for the v0.3 cycle (promote ADR 0002, reshape work-plan-v0-3
§1, fill §4 / §6 / §7) is a separate session, per reviewer 1's "Option
A" framing — separating the goal articulation from the cycle-opening
ceremony preserves git history of *what was decided when*.

## What was done

- **Added [`docs/program-context.md`](../docs/program-context.md) at
  v0.1.** Sail-class document, not a Coastline. Articulates the
  long-horizon goal in three layers (L1 Realism / L2 Thermometry / L3
  Nucleation), each anchored to a falsifiable release (`pilot-v1.0` /
  `pilot-v2.0` / `pilot-v3.0`). §3.1 enumerates seven L1 slices S1–S7
  with a "layer-defining vs housekeeping" gate; §4 spells out the
  release criteria including the v1.0 *provisional observable set*.
  §7 carries eight open programme-level decisions (D-PC-1 … D-PC-8),
  of which D-PC-2 is resolved (S2 ships first) and the rest remain
  open.
- **Recorded the load-bearing prerequisite P-1** (the experimental-
  campaign repository does not yet exist) and the supplier-failure
  fallback P-2 (sibling-repo continuity) in §2 — named at the top so
  they cannot be treated as bookkeeping lower in the document.
- **Added a programme-level falsification clause** (§1.5), distinct
  from layer-level release criteria. This forecloses conflating "v1.0
  missed its tolerance on cell X" with "diamonds-in-water is the
  wrong system."
- **Added the local-spec/synchronisation ADR/test-rerun three-step
  procedure** to §5 for the supplier-failure case, so a stalled
  upstream cannot silently park the programme *and* a catching-up
  upstream cannot silently drift the local copy.
- **Updated [`README.md`](../README.md) phase table** to add the
  Phase 16.3 row with a link to this note and to
  [`docs/program-context.md`](../docs/program-context.md).
- **Updated [`lab_notes/README.md`](README.md)** to prepend the
  Phase 16.3 row.

## Decisions

| Decision | Rationale |
|---|---|
| Land program-context.md at v0.1 (not v1.0) and accept the open D-PC-1 … D-PC-8 list | Follows reviewer 1's "Option A": ship the chart now so v0.3 anchors against a real document; iterate to v0.2 only when an actual event triggers it (S2 implementation reveals a gap, D-PC-1 closes, the campaign exists). Avoids the indefinite-review hold that v0.2 of the chart would otherwise require. |
| Resolve D-PC-2 (S1 vs S2 ordering) inside this phase | Three independent reviews converged on "S2 first as the implementation-ready slice while S1 awaits its sibling breakout." Recording the resolution in program-context §3.1 / §7 means ADR 0002 (Phase 17) can simply cite it rather than re-litigate. |
| Pin S2 outputs as `provisional=True` until S1 lands | Documentation alone is insufficient — the design-tool entry points (`plan_*` helpers) must refuse provisional outputs without an explicit override. The interface-level enforcement is recorded in program-context §3.1 with the API surface deferred to ADR 0002. |
| Keep program-context.md *internal* (not promoted to a Sail in the Open-Science Harbour vocabulary) at v0.1 | D-PC-4 in §7. Premature publication commits to the goal in public; keeping it internal preserves repivot flexibility until S1 lands. |
| Phase 16.3 is documentation-only and ships under `pilot-v0.2.1` | No code, schema, or cache changes; no `pyproject.toml` version bump. Same convention as Phase 16.2. |
| Use 2026-04-30 as the lab-note date | Same calendar day as Phases 16, 16.1, 16.2 — the v0.2.1 cycle has been a single sustained session. |

## Verification

```sh
.venv/bin/python -m pytest -q
# 135 passed

.venv/bin/python -m ruff check .
# All checks passed!

.venv/bin/cffconvert --validate -i CITATION.cff
# Citation metadata are valid according to schema version 1.2.0.

git diff --check
# clean
```

HEAD before Phase 16.3: `de36d8f` (Phase 16.2 — v0.3 deliberation
surfaces).

## What was not done

- **No ADR 0002 promotion.** ADR 0002 remains `Proposed (stub)`. The
  Phase 17 ceremony will promote it to `Accepted` with D1 = Option 2
  and the explicit S2-first selection that program-context §3.1 /
  D-PC-2 already record.
- **No `docs/work-plan-v0-3.md` reshape.** D1 / D2 / D3 / D4 / D5 /
  D6 / D7 in work-plan-v0-3 §5 remain `[OPEN]`; §1 candidate menu and
  §4 / §6 / §7 stay as scaffolded. The Phase 17 ceremony will mark D1
  resolved against ADR 0002 and add the S2 candidate to §1 (the
  current A–J list does not yet contain Stokes-Einstein corrections
  as a discrete slice).
- **No new Phase 17 commit.** Phase 17 is the next session.
- **No external publication of program-context.md.** D-PC-4 keeps it
  internal until S1 lands; "Sail" status in the Open-Science Harbour
  vocabulary is deferred.
- **No `docs/local-specs/` directory created.** §5's three-step
  supplier-failure procedure references `docs/local-specs/` as the
  fallback location, but no local spec is owed yet — the directory
  is created on first use, not pre-emptively.
- **No DOI minting.** Confirmed deferred to `pilot-v1.0` per Phase
  16.1; D-PC-5 in program-context §7 records the DOI-vs-DOI-plus-paper
  decision as still open.

## Next step

The acceptance ceremony for the v0.3 cycle is on deck (Phase 17),
now able to anchor against program-context.md:

1. Promote [`docs/adr/0002-v0.3-spec-anchoring.md`](../docs/adr/0002-v0.3-spec-anchoring.md)
   from `Proposed (stub)` → `Accepted`, recording D1 = Option 2 and
   the S2-first selection per program-context §3.1 / D-PC-2. Pin the
   `provisional=True` API surface for S2-refined diffusivities.
2. Update [`docs/work-plan-v0-3.md`](../docs/work-plan-v0-3.md) §0
   and §5: D1 = Resolved (Option 2). Add a new §1 candidate K
   "Stokes-Einstein corrections at sub-150-nm radii" mapped to
   program-context S2; mark it as the first phase. Promote SCAFFOLD
   → contract once §1 / §4 / §6 / §7 fix.
3. Subsequent v0.3 phase work (Phase 18 onward) implements S2.

## Cross-references

- [`docs/program-context.md`](../docs/program-context.md) — the
  document this phase lands.
- [`docs/work-plan-v0-3.md`](../docs/work-plan-v0-3.md) — v0.3
  scaffold whose Phase 17 acceptance ceremony anchors against
  program-context §3.1.
- [`docs/adr/0002-v0.3-spec-anchoring.md`](../docs/adr/0002-v0.3-spec-anchoring.md)
  — D1 stub, to be promoted in Phase 17.
- [`docs/adr/0001-v0.2-spec-anchoring.md`](../docs/adr/0001-v0.2-spec-anchoring.md)
  — precedent ADR.
- [Phase 16.2 lab note](2026-04-30-phase16-2-v0-3-deliberation-surfaces.md)
  — deliberation surfaces this phase builds on.
- [Phase 16.1 lab note](2026-04-30-phase16-1-defer-doi-to-v1-0.md)
  — DOI deferral that motivated the goal-articulation gap.
- [`docs/deliverable-index.md` §"What pilot-v0.3 would change"](../docs/deliverable-index.md)
  — tactical punch list now subsumed into program-context S5–S7
  housekeeping for `pilot-v1.0`.
- [`docs/findings-physics.md`](../docs/findings-physics.md) "Model
  validity envelope" — honest statement of the gaps program-context
  S1–S7 are designed to close.
- [`docs/experimental-envelope.md`](../docs/experimental-envelope.md)
  — per-assumption mapping; program-context S1–S7 each remove one
  row from the "deferred" column over the L1 cycle.
