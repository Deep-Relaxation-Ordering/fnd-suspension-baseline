# Phase 26 (opening) — ADR 0003 promoted; work-plan-v0-4 D1 / D9 resolved

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 25 shipped the v0.4 deliberation surfaces (work-plan-v0-4
SCAFFOLD + ADR 0003 `Proposed (stub)`) at commit `2bd8ec0`. This
opening session promotes ADR 0003 to `Accepted` and resolves the
two coupled decisions it scopes (D1 — spec anchor; D9 — first
slice). Mirrors [Phase 17 opening](2026-04-30-phase17-opening-adr-0002-and-work-plan-v0-3.md)
exactly.

The session does **not** reshape the work plan §1 candidate menu,
fill §4 / §6 / §7, or remove the SCAFFOLD qualifier. Those are
the Phase 26 continuation session's job, mirroring how
[Phase 17 continuation](2026-04-30-phase17-continuation-contract-acceptance.md)
followed Phase 17 opening.

## What was done

- **Promoted [`docs/adr/0003-v0.4-spec-anchoring.md`](../docs/adr/0003-v0.4-spec-anchoring.md)
  from `Proposed (stub)` to `Accepted`.** Status field updated;
  Date augmented with the promotion date (2026-05-06); Phase field
  updated to "Phase 25 — drafted; Phase 26 opening — promoted."
  The "Working notes during deliberation (non-binding)" sections
  for D1 and D9 were replaced with their accepted counterparts:
  - D1 — "Why Option 2" + "Consequences of Option 2" + re-pin
    policy.
  - D9 — "Why item B (S3) first" + "What item B (S3) ships" +
    "Contingency."
  The "Coupling between Decision 1 and Decision 2" section now
  records which combination was chosen (Option 2 + S3) and why
  the alternatives were rejected. Q1 / Q2 in "Open questions"
  reduced to "moot under Option 2." Linked artefacts gained a
  pointer to this lab note.
- **Updated [`docs/adr/README.md`](../docs/adr/README.md).** ADR
  0003 row: Status `Proposed (stub)` → `Accepted`, Date
  `2026-05-05` → `2026-05-06`, Phase `25` → `26`.
- **Updated [`docs/work-plan-v0-4.md`](../docs/work-plan-v0-4.md)
  §0 and §5.**
  - §0 promoted from "[OPEN — D1]" to "RESOLVED" with the standard
    options-considered struck-through-or-chosen format used in
    [v0.3 §0](../docs/work-plan-v0-3.md#0-spec-anchoring--resolved).
  - §1 header changed from "[OPEN]" to "[OPEN — first slice fixed]"
    with item B (S3) called out as the first slice. Other items
    remain `[OPEN]` pending the Phase 26 continuation reshape.
  - Status line updated to "SCAFFOLD — D1 / D9 resolved (Phase 26
    opening); D2–D7 still [OPEN]."
  - §5 decisions table: D1 → Resolved (Option 2); D4 → Resolved
    (first slice); D9 → Resolved (item B). D3 / D5 carry "default
    expectation" annotations consistent with Option 2's
    consequences. D2 / D6 / D7 unchanged (still [OPEN]).

## Decisions

| Decision | Resolution | Rationale |
|---|---|---|
| D1 — Spec anchor | **Option 2 — stay on `3b7b18af`.** | As of Phase 26 opening (2026-05-06), upstream `Deep-Relaxation-Ordering/diamonds_in_water` v0.3 breakout note has not landed. Option 1 would gate the cycle on an external calendar item; Option 3 multiplies per-item bookkeeping for a single-slice case. Pattern 11 + ADR 0001 / 0002 precedent both favour Option 2 in the default case. |
| D9 — First slice | **Item B (S3 — Hydrodynamic-shell calibration per FND class).** | Smallest blast radius among ready candidates (no upstream dependency, no API change, no §5 cache schema bump). Closes the v0.3 audit-gap pin shipped in [`docs/delta_shell_calibration.md`](../docs/delta_shell_calibration.md), mirroring v0.3's pattern of opening with prior-cycle debt closure (Phase 19 closed v0.2's `T_OBS_S` / `DEPTHS_M` pins). Mirrors v0.3's overall shape: one program-context slice + housekeeping bundle. |
| Apply the documented stewardship leaning rather than re-deliberate | The Phase 25 ADR working notes already recorded "Option 2 by default" and "S3 + housekeeping bundle" with the conditional "unless upstream lands." Upstream has not landed, so the default branch applies. No new information has surfaced in the four-day Phase 25 → Phase 26 gap. | Re-deliberation without new information would be process churn; the deliberation surface from Phase 25 was committed precisely so this promotion would be a mechanical step. |
| Bundle D1 + D9 promotion in one ADR | ADR 0002 set the precedent: the two decisions are coupled (the spec anchor determines which slices are available), and resolving them together prevents the kind of inconsistent combination that would force re-deliberation. | Same reasoning ADR 0002 used. Recorded explicitly in the "Coupling" section of ADR 0003. |
| Defer §1 reshape and §4 / §6 / §7 fill to a separate continuation session | Mirrors [Phase 17 opening + continuation](2026-04-30-phase17-opening-adr-0002-and-work-plan-v0-3.md) split. Each commit is a clean atomic decision; reviewers can reference line numbers; git history shows what the opening session committed vs what the continuation session committed. | Process parity with v0.3 cycle. The continuation session can be run immediately after this commit lands or in a later session. |
| Use 2026-05-06 as the promotion date | Matches today's `currentDate`; the Phase 25 → Phase 26 gap is one day. Phase 17 opening landed on the same day as Phase 16.2 (2026-04-30); a one-day gap here is consistent with the working tempo. | Matches actual session date. |

## Verification

```sh
.venv/bin/python -m pytest -q
# expect: 171 passed, 0 skipped (no code changes in this phase)

.venv/bin/python -m ruff check .
# expect: All checks passed!

git diff --check
# expect: clean
```

HEAD before Phase 26 opening: `2bd8ec0` (Phase 25 — pilot-v0.4
deliberation surfaces).

## What was not done

- **No §1 reshape.** Items A / C / D / E / F / G / H / I / J / K /
  L still carry their Phase 25 candidate annotations; in-scope vs
  out-of-scope vs parallel-breakout classification is the Phase 26
  continuation session.
- **No D2 / D3 / D5 / D6 / D7 resolution.** Default expectations
  recorded in §5; resolution happens in the continuation session.
- **No §3 forward-compat baseline pin.** D2 = Option 1 is the
  default expectation under Option 2 (item B is a documentation +
  parameter-default change with no cache numerics movement); the
  per-item pin happens during the continuation reshape.
- **No §4 phase plan fill.** Placeholder structure unchanged.
- **No §6 risk register fill.** Provisional risks from Phase 25
  remain provisional.
- **No §7 schedule fill.** Placeholder calendar unchanged.
- **No SCAFFOLD → Accepted contract promotion.** Status line still
  reads "SCAFFOLD" because §1 / §3 / §4 / §6 / §7 are not yet
  filled.
- **No `pyproject.toml` version bump.** Phase 26 opening is
  documentation-only and ships under the `pilot-v0.3` tag.

## Next step

The Phase 26 continuation session reshapes §1 and fills §3 / §4 /
§6 / §7. Mirroring [Phase 17 continuation](2026-04-30-phase17-continuation-contract-acceptance.md):

1. Reshape §1 into "in-scope" / "out-of-scope" / "parallel breakout"
   per the resolved D1 / D9 and the strong default expectations
   recorded in §5.
2. Resolve D2 / D3 / D5 / D6 / D7 in §5.
3. Fill §3 forward-compat baseline (Option 1 expected).
4. Fill §4 phase plan with concrete Phases 27–N.
5. Fill §6 risk register for in-scope items.
6. Fill §7 schedule.
7. Promote work-plan-v0-4 from SCAFFOLD to Accepted contract
   (remove the SCAFFOLD qualifier; update Status line).

The continuation session can run in this same session (recommended,
since Phase 17 ran both opening and continuation on 2026-04-30) or
be deferred. No new information is needed between the two sessions;
the deliberation surface from Phase 25 already covered everything
the continuation has to formalise.

## Cross-references

- [`docs/adr/0003-v0.4-spec-anchoring.md`](../docs/adr/0003-v0.4-spec-anchoring.md)
  — promoted to `Accepted` in this phase; D1 / D9 resolved.
- [`docs/work-plan-v0-4.md`](../docs/work-plan-v0-4.md) — §0 / §5
  updated in this phase; §1 / §3 / §4 / §6 / §7 to be reshaped /
  filled in the continuation.
- [`docs/adr/README.md`](../docs/adr/README.md) — ADR 0003 status
  / date / phase columns updated.
- [Phase 25 lab note](2026-05-05-phase25-v0-4-deliberation-surfaces.md)
  — drafted the ADR + work-plan-v0-4 scaffold this session promotes.
- [Phase 17 opening lab note](2026-04-30-phase17-opening-adr-0002-and-work-plan-v0-3.md)
  — the precedent this phase mirrors (ADR 0002 promotion + D1 / D9
  resolution for v0.3).
- [Phase 17 continuation lab note](2026-04-30-phase17-continuation-contract-acceptance.md)
  — the precedent for the next session (work-plan acceptance).
- [`docs/program-context.md` §3.1](../docs/program-context.md) —
  authoritative S1–S7 menu; S3 (item B) is the chosen first slice.
- [`docs/delta_shell_calibration.md`](../docs/delta_shell_calibration.md)
  — v0.3 provisional table; item B replaces it with a
  citation-anchored calibration per FND class.
- [Pattern 11 in `findings-process.md`](../docs/findings-process.md#11-spec-pinning-at-commit-hash-precision)
  — spec pinning at commit-hash precision (the convention ADR 0003
  inherits and Option 2 honours).
