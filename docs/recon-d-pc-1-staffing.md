# Reconnaissance brief — D-PC-1 campaign staffing

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg. Operational artefact, not a Sail; archives once the signal
lands.*

| Field | Value |
|---|---|
| Status | **Draft.** Input to Session 0 (campaign-staffing check). |
| Date | 2026-05-06 |
| Decision horizon | 2 weeks from Session 0, or 1 working session — whichever comes first. Target close-out: 2026-05-20. |
| Owner of the staffing decision | U. Warring |
| Drafted in response to | post-Phase 32.1 v0.5 lead-slice question. D-PC-1 reconnaissance gates whether Phase 33 (deliberation surfaces) opens as a `lambda_se`-led `pilot-v0.5` cycle or as a D-PC-1 readiness checklist. |
| Programme links | [`program-context.md` §2 P-1](program-context.md), [`§7 D-PC-1`](program-context.md), [`work-plan-v0-4.md` §1 firm-defer list](work-plan-v0-4.md). |

This brief is the input to a single ~30-minute reconnaissance session.
It is **not** a work plan and **not** an ADR. It returns one of three
signals — `GREEN` / `AMBER` / `RED` — and the signal selects which
downstream artefact gets drafted next. The brief itself is archived
(per `cd-rules` §0.8) once the signal lands and the downstream artefact
is opened.

---

## The three questions

### Q1. Lab + person + budget — is there a path to start within the next quarter?

Success criterion (all three required for `GREEN`):

- **Lab** — a named space with the required equipment (microscope +
  tracking pipeline + sealed-cuvette mount + temperature stage).
- **Person** — a named graduate student or collaborator with at least
  half-time availability across the experiment's calendar window.
- **Budget** — a budget line (or named funding source) that covers
  consumables, FND batches, and any equipment-time charges.

Signal mapping:

- **GREEN** — all three are named, with no soft maybes.
- **AMBER** — two are named; the third is a soft maybe with an
  identified path to firming up inside the decision horizon.
- **RED** — fewer than two are named, or any one of the three has no
  identifiable path to firming up inside the calendar year.

Earliest realistic start date for a `GREEN` signal: 2026-08-06 (three
months from today). Anything later than 2026-08-06 demotes to `AMBER`.

### Q2 (fires on `GREEN` or `AMBER`). Critical path between now and start.

Order ~5 items by lead time. Examples that have surfaced in v0.4
audit-gap discussions:

- Protocol draft (sealed-cuvette FND tracking; informs the §4.1
  observable set, which is D-PC-6).
- Institutional / ethics approval if the campaign requires it.
- FND-batch procurement — manufacturer + class (informs S3 calibration
  refinement; cross-check `docs/delta_shell_calibration.md`).
- Microscope + tracking-pipeline access window.
- Cooling-stage / thermal-protocol equipment (informs S7 — promotes
  `delta_T_assumed` from side-channel).

Output: an ordered list of items with rough lead times in weeks.

### Q3 (fires on `RED`). Is the blocker resolvable this calendar year?

If `RED` at Q1, identify the binding constraint:

- Funding cycle / grant timing.
- Personnel — no one available to take ownership.
- Lab access — equipment or space contention.
- Institutional — approvals, MOUs, NDAs blocking procurement.

Resolvable before 2026-12-31 — yes / no. If **no**, the answer escalates
to the programme-level falsification clause
([`program-context.md` §1.5](program-context.md), "experimental-campaign
collapse"). That is not a reconnaissance outcome; it is a strategic
rethink trigger.

---

## Signal → downstream artefact

| Signal | Triggers |
|---|---|
| `GREEN` | Draft a lightweight **D-PC-1 readiness checklist** (not a full work plan). Defer Phase 33 deliberation surfaces until critical-path lead times are scoped. v0.5 lead slice becomes "campaign prep + smallest-blast simulator support work" rather than `lambda_se`. |
| `AMBER` | Draft Phase 33 (work-plan-v0-5 + ADR 0004 stub) with `lambda_se` calibration as the lead slice **and** an explicit D-PC-1 merge clause: if the staffing picture firms up to `GREEN` mid-cycle, S7 (or whichever slice the campaign protocol motivates) merges in as a parallel track or becomes the v0.6 lead. |
| `RED` with resolvable blocker | Draft Phase 33 as in `AMBER`. Mark D-PC-1 as v0.7+ at earliest. The `provisional=True` API contract from ADR 0002 stays in force. |
| `RED` with unresolvable blocker | Pause active cycle work at `pilot-v0.4`. Open a programme-level review per `program-context.md` §1.5 to choose between (a) deposit-and-pause as a methods-only artefact (Zenodo + methods paper at the current tag), or (b) repurpose the simulator for a different downstream campaign. |

The `AMBER` and resolvable-`RED` paths converge on the same Phase 33
draft — the difference is in the merge-clause weight.

---

## Output of Session 0 itself

The session produces one short lab note:
`lab_notes/2026-05-XX-recon-d-pc-1-staffing.md`, recording:

- Who was consulted (decision owner + any second-opinion voices).
- Q1 / Q2 / Q3 answers verbatim, with success criterion ticked or not.
- The selected signal and the triggered downstream artefact.
- Target session for the downstream artefact.

The lab note is the only persistent record of Session 0; this brief
itself archives.

---

## Cross-references

- [`program-context.md` §2 P-1](program-context.md) — load-bearing
  prerequisite for the entire programme.
- [`program-context.md` §7 D-PC-1](program-context.md) — the open
  decision this brief reconnoitres.
- [`program-context.md` §7 D-PC-3 / D-PC-6](program-context.md) — both
  unblock when D-PC-1 lands; the metric set and tolerance threshold
  cannot be pinned without a campaign.
- [`program-context.md` §1.5](program-context.md) — programme-level
  falsification, fires on unresolvable `RED`.
- [`work-plan-v0-4.md` §1 items A / F / G](work-plan-v0-4.md) — S1,
  S6, S7 firm-defer rationale; all conditional on D-PC-1 or upstream
  supplier.
- [`release-notes/v0.4.md` "What pilot-v0.5 would change"](release-notes/v0.4.md).
