# Phase 26 (continuation) — v0.4 work-plan contract acceptance

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 26 opening (commit `40e46da`) promoted ADR 0003 to `Accepted`
and resolved D1 (spec anchor = Option 2) and D9 (first slice = item
B / S3 — Hydrodynamic-shell calibration per FND class). This
continuation session reshapes work-plan-v0-4 §1 against the
resolved decisions, resolves the remaining decisions D2 / D3 / D5 /
D6 / D7, fills §3 / §4 / §6 / §7, and removes the SCAFFOLD
qualifier so the v0.4 cycle is under contract. Mirrors
[Phase 17 continuation](2026-04-30-phase17-continuation-contract-acceptance.md)
exactly.

## What was done

- **§1 reshape — every candidate item resolved.** Each item's
  `Decision needed` line was replaced with a concrete `Decision`
  line:
  - **A (S1 — DLVO aggregation):** out-of-scope — defer to v0.5
    (D3). Upstream had not landed; under D1 = Option 2's
    "no calendar gating" stance, S1 waits for its upstream
    breakout note. The `provisional=True` API contract from
    [ADR 0002 §"API surface"](../docs/adr/0002-v0.3-spec-anchoring.md#api-surface--the-provisionaltrue-contract)
    remains in force throughout v0.4 as a consequence.
  - **B (S3 — Hydrodynamic-shell calibration):** in-scope, first
    slice (resolved Phase 26 opening; D4). D2 = Option 1.
  - **C (`lambda_se` → §5 axis):** out-of-scope — defer to v0.5
    (D5). S2 calibration prerequisite has not been run in the FND
    band.
  - **D (S4 — Capsule-geometry port):** out-of-scope — parallel
    pilot cycle. ~12 d effort exceeds v0.4 calendar.
  - **E (S5 — Concentration-weighted polydispersity kernel):**
    in-scope (D6). Phase 28. D2 = Option 1 (kernel-weight refactor
    is opt-in; classification kernel remains default).
  - **F (S6 — Wall hydrodynamics):** out-of-scope — defer to v0.5
    / v1.1.
  - **G (S7 — Thermal control as first-class):** out-of-scope —
    defer to v0.5 / v1.0; gated on D-PC-1 campaign protocol.
  - **H (v0.3 review residue):** in-scope, bundled with item L
    into Phase 29.
  - **I (ProcessPoolExecutor spawn-context on macOS):** in-scope,
    bundled with item J into Phase 30. D2 = Option 1.
  - **J (continuous time-evolution extensions):** in-scope, bundled
    with item I. D2 = Option 1.
  - **K (release-criterion gap audit):** in-scope, bundled into
    Phase 31. D2 = Option 1.
  - **L (doc-fix: reconcile S-slice nomenclature):** in-scope (D7),
    bundled with item H into Phase 29.
- **§2 firm-defer list updated.** Items A and C added (S1 and
  `lambda_se` → §5 axis joining S4 / S6 / S7 in the firm-defer
  list).
- **§3 forward-compat contract — RESOLVED.** D2 = Option 1 for all
  in-scope items. Triple invariant from v0.3 carries forward.
- **§4 phase plan filled.** Concrete phases 27 → 32:
  - 27 — S3 (item B): 1–2 sessions
  - 28 — S5 (item E): 1–2 sessions
  - 29 — Doc-fix + housekeeping bundle (items L + H): 1 session
  - 30 — Tactical bundle (items I + J): 1 session
  - 31 — Integration audit + item K: 1 session
  - 32 — Release `pilot-v0.4`: 1 session
  Total: ~8–10 sessions, ~5–7 working days; calendar ~1.5–2 weeks.
  Slightly faster than v0.3 because no layer-defining slice is in
  v0.4 scope (consistent with D1 = Option 2's "implementation
  tightenings" stance).
- **§5 decisions table — all resolved.** D1 / D4 / D9 (Phase 26
  opening) plus D2 / D3 / D5 / D6 / D7 (this commit). D8 carried
  forward.
- **§6 risk register filled.** Per-item risks for B (R-B1 / R-B2 /
  R-B3), E (R-E1), H (R-H1), I (R-I1), J (R-J1), K (R-K1), L
  (R-L1). Out-of-scope residual risk acknowledged as
  R-A-C-D-F-G.
- **§7 schedule filled.** Concrete calendar from 2026-05-06 (this
  commit) to ~2026-05-18 (release).
- **§8 stale-state checklist updated.** Same-commit doc-fix items
  marked done across Phase 25 / 26 commits. The S-slice
  nomenclature discrepancy (item L) remains unchecked here because
  closing it in Phase 26 would amount to a stealth substantive
  edit of the v0.3 release note; deferred to Phase 29 which owns
  the cleanup explicitly.
- **§9 acceptance — all six steps marked done.** SCAFFOLD qualifier
  removed from the Status line. Status: "Accepted contract."
- **§10 cross-references extended** to add the Phase 25, Phase 26
  opening, and Phase 26 continuation lab notes.
- **Prose: removed the "scaffold structure mirrors..." paragraph**
  that was deliberation-surface text and replaced with a single
  sentence noting the cycle is under contract.

## Decisions

| Decision | Resolution | Rationale |
|---|---|---|
| D2 — Forward-compat baseline | **Option 1 for all in-scope items.** | Every in-scope item (B, E, H, I, J, K, L) is either documentation, a parameter-default change, an opt-in kwarg refactor, or a pure infrastructure tightening — all compatible with Pattern 14 zero-default extension. The v0.3 baseline reproduces at compatibility-mode defaults to machine precision, same triple invariant as v0.2 / v0.3. |
| D3 — S1 in-scope status | **Out-of-scope — defer to v0.5+.** | Upstream `Deep-Relaxation-Ordering/diamonds_in_water` v0.3 breakout note had not landed by Phase 26 opening (2026-05-06). D1 = Option 2's "no calendar gating" stance forecloses Option 1 (re-anchor to upstream); the supplier-failure clause's local-spec fallback is calendar-expensive and reserved for cases where v0.5 cannot wait. v0.4 can wait. |
| D5 — `lambda_se` → §5 axis | **Out-of-scope — defer to v0.5.** | The S2 calibration prerequisite (gold-NP benchmark in the FND band) has not been run; running it inside v0.4 plus shipping the §5 axis promotion would exceed the cycle calendar. The calibration is captured as a pre-Phase-27 prerequisite in the v0.5 candidate list rather than absorbed into v0.4. |
| D6 — S5 polydispersity kernel | **In-scope (Phase 28).** | Small blast radius, no upstream dependency, housekeeping per [program-context summary table](../docs/program-context.md#L222). The default expectation in §5 was "yes"; no contraindication surfaced in the §1 reshape. |
| D7 — Doc-fix scope (item L) | **In-scope (Phase 29, bundled with H).** | The deliverable-index / release-notes-v0.3 S-slice nomenclature discrepancy is a real bug — future readers cannot disambiguate which list is authoritative. Resolved by treating program-context as authoritative. |
| Phase ordering: B → E → L+H → I+J → K+integration → release | **Adopted.** | Mirrors v0.3's "one program-context slice + tactical follow-ups + integration + release" pattern (Phase 18 = K, Phases 19–22 = tactical, Phase 23 = integration, Phase 24 = release). v0.4 closes two program-context slices (B = S3, E = S5) so the implementation phases are split into two slice phases (27, 28) rather than one. |
| Cycle adopts two program-context slices (B + E), not one | **Adopted.** | v0.3 closed one layer-defining slice (S2 = item K) plus six tactical items in 9–12 sessions. v0.4 closing two housekeeping slices (S3 + S5) plus four tactical items is similar effort because each housekeeping slice is smaller than v0.3's S2. The v0.3 working tempo (~7 working days for ~7 items) is reproducible. Justifies "v0.4 is two program-context closures" as a non-trivial cycle worth releasing. |
| Run continuation immediately after opening, not in a separate session | **Adopted.** | Phase 17 ran opening and continuation in the same session (both 2026-04-30). The deliberation surface was already complete in Phase 25; the opening session resolved the load-bearing D1 / D9; the continuation just formalises the rest against the resolved defaults. No new information is needed in between. |

## Verification

```sh
.venv/bin/python -m pytest -q
# expect: 171 passed, 0 skipped (no code changes in this phase)

.venv/bin/python -m ruff check .
# expect: All checks passed!

git diff --check
# expect: clean
```

HEAD before Phase 26 continuation: `40e46da` (Phase 26 opening).

## What was not done

- **No code changes.** Phase 26 is documentation-only; code work
  starts at Phase 27.
- **No `pyproject.toml` version bump.** Phase 26 ships under the
  `pilot-v0.3` tag.
- **No fix to the deliverable-index / release-notes-v0.3 S-slice
  list discrepancy.** That's item L — Phase 29's job. Doing it
  here would either pre-empt the explicit phase that owns the fix
  or amount to a stealth edit of the v0.3 release note.
- **No new ADR for D2 / D3 / D5 / D6 / D7.** These were
  scope-shaping decisions resolvable in the work plan §1 reshape;
  ADR-level treatment is reserved for spec-anchoring and
  layer-defining decisions (see [ADR README §"Conventions"](../docs/adr/README.md)).
- **No new lab note for `delta_shell_calibration` upgrade.** That's
  Phase 27's job (S3 implementation).

## Next step

**Phase 27 — S3: Hydrodynamic-shell calibration per FND class.**
The v0.4 cycle is now under contract. Phase 27 opens with the
following scope, drawn from §1 item B and ADR 0003 Decision 2
"What item B (S3) ships":

1. Survey open-literature DLS measurements for functionalised FND
   classes (bare, carboxylated, hydroxylated, PEG-functionalised).
2. Produce a citation-anchored calibration table replacing the
   provisional [`docs/delta_shell_calibration.md`](../docs/delta_shell_calibration.md)
   table.
3. Wire the calibrated default into the parameters layer such that
   `delta_shell_m=0` continues to reproduce v0.3 byte-identically
   (Pattern 14 zero-default extension).
4. Add tests that pin the calibration against the §5 cache rows at
   the new defaults.
5. Phase 27 lab note explaining the calibration sources, any
   conflicts, and the audit-gap-pin closure.

Effort: 1–2 sessions per §4 / §7. Risk register entries R-B1 / R-B2
/ R-B3 apply.

## Cross-references

- [`docs/work-plan-v0-4.md`](../docs/work-plan-v0-4.md) — promoted
  to `Accepted contract` in this phase.
- [`docs/adr/0003-v0.4-spec-anchoring.md`](../docs/adr/0003-v0.4-spec-anchoring.md)
  — the ADR this contract builds on; D1 / D9 resolved Phase 26
  opening.
- [Phase 25 lab note](2026-05-05-phase25-v0-4-deliberation-surfaces.md)
  — drafted the scaffold this contract promotes.
- [Phase 26 opening lab note](2026-05-06-phase26-opening-adr-0003-and-work-plan-v0-4.md)
  — resolved D1 / D9; this continuation builds on it.
- [Phase 17 continuation lab note](2026-04-30-phase17-continuation-contract-acceptance.md)
  — the precedent this phase mirrors (work-plan-v0-3 contract
  acceptance).
- [Phase 19 lab note](2026-05-01-phase19-audit-gap-pins-and-parallel-walk.md)
  — v0.3's pattern of opening with prior-cycle audit-gap pin
  closure (T_OBS_S / DEPTHS_M); v0.4 Phase 27 mirrors this with
  `delta_shell_m`.
- [Phase 21 lab note](2026-05-01-phase21-mesh-convergence-and-shell-calibration.md)
  — v0.3's provisional `delta_shell_m` calibration that Phase 27
  promotes to a citation-anchored table.
- [`docs/program-context.md` §3.1](../docs/program-context.md) —
  authoritative S1–S7 menu; S3 (item B) is the chosen first slice.
- [Pattern 14 in `findings-process.md`](../docs/findings-process.md#14-forward-compatible-parameter-splits-via-zero-default-extension)
  — forward-compatible parameter splits via zero-default extension
  (the engineering contract D2 = Option 1 inherits).
