# Phase 16.2 — `pilot-v0.3` deliberation surfaces

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phases 16 and 16.1 closed the `pilot-v0.2.1` FAIR metadata work and
deferred DOI minting to `pilot-v1.0`. Before any v0.3 phase work
starts, the v0.3 cycle needs a stable place to deliberate scope and
spec anchor — without committing to decisions that haven't been
deliberated.

This phase commits two deliberation surfaces, plus one supporting
piece of housekeeping and two stale-state fixes flagged in the v0.3
scaffold §8.

## What was done

- **Added [`docs/work-plan-v0-3.md`](../docs/work-plan-v0-3.md).**
  Scaffold mirroring the [v0.2 work plan](../docs/work-plan-v0-2.md)
  structure. Status field reads "SCAFFOLD — decisions [OPEN], not
  accepted." §1 enumerates ten candidate scope items A–J with
  motivation, source, rough effort, blast radius, and per-item
  decision flags. §5 lists open decisions D1–D8 (D8 already resolved
  by Phase 16.1).
- **Added [`docs/adr/0002-v0.3-spec-anchoring.md`](../docs/adr/0002-v0.3-spec-anchoring.md).**
  Status: `Proposed (stub)`. Scopes itself to D1 only (the v0.3
  spec-anchoring question), with a driver-by-option matrix and
  consequences listed per option. Stewardship preference (Option 2,
  stay on v0.2 commit `3b7b18af`) is recorded under "Working notes
  during deliberation" but explicitly framed as a non-decision.
- **Added [`docs/adr/README.md`](../docs/adr/README.md).** ADR index;
  supersedes ADR 0001's "this single document is its own index"
  closing note.
- **Updated [`docs/deliverable-index.md`](../docs/deliverable-index.md)
  "Known caveats".** "DOI pending" bullet rewritten to "DOI deferred
  to `pilot-v1.0`" with a cross-reference to the Phase 16.1 lab note.
- **Updated [`README.md`](../README.md) phase table.** Section header
  for the v0.2.1 cycle broadened to "FAIR metadata + v0.3 deliberation",
  with Phase 16.1 and 16.2 rows added.

## Decisions

| Decision | Rationale |
|---|---|
| Commit deliberation surfaces with explicit `SCAFFOLD` / `Proposed` status | Pattern from `7c5225b` (v0.2 work plan committed as Draft before acceptance). Preserves deliberation history in git so reviewers can reference line numbers in PRs and `git blame` shows when each decision was raised vs resolved. |
| Add `docs/adr/README.md` index in this commit | ADR 0001's "for now this single document is its own index" closing note is now stale. Adding the index alongside ADR 0002 closes the inconsistency in the same commit that creates it. |
| Frame stewardship preference (Option 2 for D1) in ADR 0002 as "Working notes" | The user explicitly asked for ADR 0002 as a stub, not the decision. Recording the leaning under a labelled non-binding section preserves the deliberation context without flipping `Status: Proposed` to `Accepted`. |
| Do **not** bake D1–D7 recommendations into the work plan §1 in this commit | Acceptance ceremony (steps 4–7 of the user's promotion path) is a separate session. This commit is steps 1–3 only: ship the deliberation surfaces, add the ADR index, fix the stale state. |
| Use the 2026-04-30 lab-note date | All Phase 16.x phases are landing on the same day; the date matches `pilot-v0.2` closeout chronology. |

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

HEAD before Phase 16.2: `e2639ff` (Phase 16.1 — DOI deferral).

## What was not done

- **No D1–D7 acceptance.** The work plan §5 still shows them as
  `[OPEN]`. Acceptance is steps 4–7 of the promotion path, separate
  session.
- **No §1 scope reshape.** The candidate menu is unchanged from the
  drafted scaffold.
- **No §4 / §6 / §7 fill-in.** Phase plan, risk register, and schedule
  remain `[TBD]` until §1 fixes.
- **No ADR 0002 promotion.** Status remains `Proposed (stub)`.
- **No `pyproject.toml` version bump.** Phase 16.2 is documentation-
  only and ships under the `pilot-v0.2.1` version.
- **No new ADR for D2 / D3 / D4 / D5 / D6.** Each gets its own surface
  when the relevant decision becomes ripe.

## Next step

The acceptance ceremony for the v0.3 cycle is on deck:

1. Resolve D1 in ADR 0002 (promote `Proposed (stub)` → `Accepted`).
2. Mark D2–D7 in [`docs/work-plan-v0-3.md`](../docs/work-plan-v0-3.md) §5.
3. Reshape §1 scope per the resolved decisions.
4. Fill §4 phase plan, §6 risk register, §7 schedule.
5. Promote both documents from SCAFFOLD/Proposed to Accepted/contract.

The acceptance ceremony is a separate session because the deliberation
itself benefits from the documents existing in committed form first
(reviewers can reference line numbers; git history shows what was
proposed vs what was accepted).

## Cross-references

- [`docs/work-plan-v0-3.md`](../docs/work-plan-v0-3.md) — v0.3
  scaffold this commit ships.
- [`docs/adr/0002-v0.3-spec-anchoring.md`](../docs/adr/0002-v0.3-spec-anchoring.md)
  — D1-only ADR stub.
- [`docs/adr/0001-v0.2-spec-anchoring.md`](../docs/adr/0001-v0.2-spec-anchoring.md)
  — precedent ADR.
- [`docs/adr/README.md`](../docs/adr/README.md) — ADR index added in
  this phase.
- [Phase 16 lab note](2026-04-30-phase16-fair-metadata-and-v0-2-closeout.md)
  — original FAIR metadata phase.
- [Phase 16.1 lab note](2026-04-30-phase16-1-defer-doi-to-v1-0.md)
  — DOI deferral that resolves D8.
- [Pattern 11 in `findings-process.md`](../docs/findings-process.md#11-spec-pinning-at-commit-hash-precision)
  — spec pinning at commit-hash precision (the convention ADR 0002
  inherits).
