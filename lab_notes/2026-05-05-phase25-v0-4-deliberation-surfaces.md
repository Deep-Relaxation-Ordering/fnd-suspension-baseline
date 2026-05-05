# Phase 25 — `pilot-v0.4` deliberation surfaces

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 24 closed the `pilot-v0.3` cycle ("v0.4 work-plan scaffold is
deferred to a later session (no open decisions pending)"). Working
tree is clean, tag `pilot-v0.3` at `ad48b0b` is on `main`. Test
suite passes `171 passed, 0 skipped`; `ruff check .` clean.

Before any v0.4 phase work starts, the v0.4 cycle needs a stable
place to deliberate scope and spec anchor — without committing to
decisions that haven't been deliberated. This phase mirrors
[Phase 16.2](2026-04-30-phase16-2-v0-3-deliberation-surfaces.md)
(the v0.3-cycle equivalent), shipping deliberation surfaces in a
deliberately non-committal state so the deliberation itself can
proceed against a committed artefact (reviewers can reference line
numbers; git history shows what was proposed vs what was accepted).

This phase commits two deliberation surfaces, plus the supporting
ADR-index update.

## What was done

- **Added [`docs/work-plan-v0-4.md`](../docs/work-plan-v0-4.md).**
  Scaffold mirroring the [v0.3 work plan](../docs/work-plan-v0-3.md)
  structure. Status field reads "SCAFFOLD — decisions [OPEN], not
  accepted." §1 enumerates twelve candidate scope items A–L drawn
  from [`program-context.md` §3.1](../docs/program-context.md) (the
  authoritative L1 S1–S7 menu) and from v0.3 audit-gap pins still
  open after Phase 24. Each candidate carries motivation, source,
  rough effort, blast radius, and a per-item decision flag. §5 lists
  open decisions D1–D9 with D8 (DOI deferral) carried forward as
  resolved.
- **Added [`docs/adr/0003-v0.4-spec-anchoring.md`](../docs/adr/0003-v0.4-spec-anchoring.md).**
  Status: `Proposed (stub)`. Scopes itself to D1 (spec anchor) and
  D9 (first-slice selection), coupled in the same ADR-0002 pattern.
  Driver-by-option matrix and consequences listed per option.
  Stewardship preferences (Option 2 default with Option 1 as the
  "wait-and-see" path; S3 + housekeeping bundle as default first
  slice with S1 as the "if upstream lands" path) recorded under
  "Working notes during deliberation" but explicitly framed as
  non-binding leanings.
- **Updated [`docs/adr/README.md`](../docs/adr/README.md).** ADR
  index gets an ADR 0003 row; cross-references gain a
  `work-plan-v0-4.md` link parallel to the v0.2 / v0.3 entries.
- **Updated [`README.md`](../README.md) phase table.** Phase 25 row
  added under a new "v0.4 deliberation" section header, mirroring
  the v0.2.1 cycle's "FAIR metadata + v0.3 deliberation" header.
- **Updated [`lab_notes/README.md`](../lab_notes/README.md).** Phase
  25 row prepended.

## Decisions

| Decision | Rationale |
|---|---|
| Commit deliberation surfaces with explicit `SCAFFOLD` / `Proposed (stub)` status | Pattern from Phase 16.2 (v0.3 deliberation surfaces). Preserves deliberation history in git so reviewers can reference line numbers in PRs and `git blame` shows when each decision was raised vs resolved. |
| Frame stewardship preference (Option 2 + S3 first slice) in ADR 0003 as "Working notes" | Non-binding leaning, not the decision. Recording it under a labelled section preserves deliberation context without flipping `Status: Proposed (stub)` to `Accepted`. The user explicitly asked for the v0.4 scaffold, not the contract; this matches that scope. |
| Do **not** bake D1–D7 / D9 recommendations into the work plan §1 in this commit | Acceptance ceremony (mirroring Phase 17 opening + continuation) is a separate session. This commit is the deliberation surface only: ship the scaffold, ship the ADR stub, update the indexes. |
| Use the 2026-05-05 lab-note date | Matches `currentDate` provided in conversation context. Phase 24 (the v0.3 release) was 2026-05-01; the four-day gap is consistent with the calendar pause Phase 24 explicitly took. |
| Treat [`program-context.md` §3.1](../docs/program-context.md) as authoritative for S-slice nomenclature | The v0.4 candidate lists in [`docs/deliverable-index.md`](../docs/deliverable-index.md) §"What `pilot-v0.4` would change" and [`docs/release-notes/v0.3.md`](../docs/release-notes/v0.3.md) §"What `pilot-v0.4` would change" use S-slice labels (S3 = "salinity correction", S4 = "pH-dependent surface charge", etc.) that do not match program-context's S3 = "Hydrodynamic-shell calibration", S4 = "1-D radial port", etc. The discrepancy is recorded as work-plan item L for v0.4 cleanup. Program-context wins because it is the canonical long-horizon goal document and was the upstream source for ADR 0002. |
| Phase number `25`, not `24.1` | Phase 24 was the v0.3 release ceremony (closed); this is the start of v0.4 deliberation, not a v0.3 follow-up. The numbering parallels the v0.2 → v0.3 transition where Phase 16.2 opened v0.3 deliberation as a discrete phase rather than a Phase 15 follow-up. |

## Verification

```sh
.venv/bin/python -m pytest -q
# expect: 171 passed, 0 skipped (no code changes in this phase)

.venv/bin/python -m ruff check .
# expect: All checks passed!

git diff --check
# expect: clean
```

HEAD before Phase 25: `00f2fc7` (Pages: adopt cd-rules visual register).

## What was not done

- **No D1 / D9 acceptance.** ADR 0003 status remains
  `Proposed (stub)`. Promotion to `Accepted` is the Phase 26
  opening session.
- **No §1 scope reshape.** The candidate menu is the drafted
  scaffold; in-scope vs out-of-scope vs parallel-breakout
  classification is the Phase 26 continuation session.
- **No §4 / §6 / §7 fill-in.** Phase plan, risk register, and
  schedule remain `[TBD]` until §1 fixes.
- **No `pyproject.toml` version bump.** Phase 25 is documentation-
  only and ships under the `pilot-v0.3` tag (post-tag, so the
  `0.3.0` package version is not bumped — v0.4 work happens against
  HEAD without retagging v0.3).
- **No fix to the deliverable-index / release-notes-v0.3 S-slice
  list discrepancy.** That fix is item L in the v0.4 work plan;
  doing it in Phase 25 would either pre-empt the §1 reshape decision
  or amount to a stealth substantive edit of the v0.3 release note.
  Deferred to the v0.4 cycle proper.
- **No new ADR for D2 / D3 / D4 / D5 / D6 / D7.** Each gets its own
  surface when the relevant decision becomes ripe inside the v0.4
  cycle.

## Next step

The acceptance ceremony for the v0.4 cycle is on deck, mirroring
the [Phase 17 opening + continuation pattern](2026-04-30-phase17-opening-adr-0002-and-work-plan-v0-3.md):

1. Resolve D1 + D9 in ADR 0003 (promote `Proposed (stub)` →
   `Accepted`). This is Phase 26 opening.
2. Mark D2 / D3 / D4 / D5 / D6 / D7 in
   [`docs/work-plan-v0-4.md`](../docs/work-plan-v0-4.md) §5.
3. Reshape §1 scope per the resolved decisions.
4. Fill §4 phase plan, §6 risk register, §7 schedule.
5. Promote both documents from SCAFFOLD/Proposed to
   Accepted/contract.

The acceptance ceremony is a separate session because the
deliberation itself benefits from the documents existing in
committed form first (reviewers can reference line numbers; git
history shows what was proposed vs what was accepted).

If the upstream `Deep-Relaxation-Ordering/diamonds_in_water` v0.3
breakout note lands before Phase 26 opening, the D1 / D9 path
shifts from "Option 2 + S3 first" to "Option 1 + S1 first." ADR
0003 has both branches surveyed; the choice is made at acceptance
time, not now.

## Cross-references

- [`docs/work-plan-v0-4.md`](../docs/work-plan-v0-4.md) — v0.4
  scaffold this commit ships.
- [`docs/adr/0003-v0.4-spec-anchoring.md`](../docs/adr/0003-v0.4-spec-anchoring.md)
  — D1 + D9 ADR stub.
- [`docs/adr/README.md`](../docs/adr/README.md) — ADR index updated
  in this phase.
- [Phase 16.2 lab note](2026-04-30-phase16-2-v0-3-deliberation-surfaces.md)
  — the precedent this phase mirrors (v0.3 deliberation surfaces).
- [Phase 17 opening lab note](2026-04-30-phase17-opening-adr-0002-and-work-plan-v0-3.md)
  — the precedent for Phase 26 opening (ADR 0002 promotion).
- [Phase 17 continuation lab note](2026-04-30-phase17-continuation-contract-acceptance.md)
  — the precedent for Phase 26 continuation (work-plan acceptance).
- [Phase 24 lab note](2026-05-01-phase24-pilot-v0-3-release.md) —
  v0.3 release ceremony; "v0.4 work-plan scaffold deferred to a
  later session" is the trigger for this phase.
- [Pattern 11 in `findings-process.md`](../docs/findings-process.md#11-spec-pinning-at-commit-hash-precision)
  — spec pinning at commit-hash precision (the convention ADR 0003
  inherits).
- [Pattern 14 in `findings-process.md`](../docs/findings-process.md#14-forward-compatible-parameter-splits-via-zero-default-extension)
  — forward-compatible parameter splits via zero-default extension
  (the engineering contract v0.4 default-mode preserves).
