# Tutorial phase 1 — TUT-01 … TUT-05 first batch

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

`pilot-v0.4` shipped (commit `a3b6107`, tag `pilot-v0.4`) with seven
implementation items but no visitor-facing tutorial layer. The
post-release work introduces tutorials as an accessibility surface
separate from §6 deliverables, governed by the new
[`docs/conventions.md` §"Tutorial notebooks"](../docs/conventions.md)
ruleset and tracked by [`docs/tutorial-roadmap.md`](../docs/tutorial-roadmap.md).

This is the **first tutorial batch**: governance layer (commit
`13ac8d7`) plus five tutorials (commit `d31783d`), implemented and
smoke-tested against the `pilot-v0.4` tag.

This lab note is a **backfill** — the convention in
[`lab_notes/README.md` §"Tutorial phases"](README.md) (added in the
same governance commit) requires a per-batch lab note that cites the
TUT-* IDs and records the smoke commands. The two implementation
commits had thorough commit messages but no accompanying lab note;
this entry catches up.

## What was done

### Governance layer (commit `13ac8d7`)

- **[`docs/conventions.md`](../docs/conventions.md) §"Tutorial notebooks".**
  Location (`notebooks/tutorials/` as jupytext `.py`), stable `TUT-XX`
  identifiers, runtime budget under 60 s on the reference machine,
  prohibition on `walk_grid()` calls (committed cache only), front
  matter (purpose / runtime / release tag / canonical inputs / smoke
  command / citation hooks), back matter (next-tutorial pointer +
  related deliverable / findings link), FAIR floor (findable through
  the roadmap, accessible without network-only inputs, interoperable
  with the jupytext convention, reusable via citation / licence /
  source-command annotations), smoke-test gate before every release
  tag.
- **[`docs/tutorial-roadmap.md`](../docs/tutorial-roadmap.md).** Stable
  IDs, planned paths, canonical inputs, smoke commands, status legend
  (`proposed → draft → ready → stale`), FAIR tracking checklist, and
  a standing audit prompt for every release.
- **[`README.md`](../README.md) "Learning path" section** linking to
  `notebooks/tutorials/` and the roadmap; coverage table for the v0.5
  cycle.
- **[`docs/index.html`](../docs/index.html) "Try it" nav link +
  `#tutorials` section** with five evidence cards (one per TUT-*).
- **[`docs/deliverable-index.md`](../docs/deliverable-index.md)
  tutorial-accessibility section** explicitly separated from §6
  deliverables; points to the roadmap for inputs and smoke commands.
- **[`notebooks/tutorials/README.md`](../notebooks/tutorials/README.md)**
  initially as placeholder (refreshed in the implementation commit).
- **[`lab_notes/README.md`](README.md) "Tutorial phases" section.**
  Establishes the convention this lab note honours.

### Implementation (commit `d31783d`)

Five jupytext `.py` tutorials shipped under
[`notebooks/tutorials/`](../notebooks/tutorials/), all status `ready`
against `pilot-v0.4`:

| ID | File | Purpose | API surfaces exercised |
|---|---|---|---|
| TUT-01 | [`01_quick_start_regime_map.py`](../notebooks/tutorials/01_quick_start_regime_map.py) | Load the §5 cache and inspect a single (r, h) cell. | `regime_map.results_from_csv` |
| TUT-02 | [`02_geometry_and_shell_calibration.py`](../notebooks/tutorials/02_geometry_and_shell_calibration.py) | Instantiate FND classes; inspect hydrodynamic-radius shifts. | Phase 27: `ParticleGeometry.from_fnd_class`, `delta_shell_for_fnd_class`, four canonical class defaults |
| TUT-03 | [`03_polydispersity_intuition.py`](../notebooks/tutorials/03_polydispersity_intuition.py) | Compare log-normal smearing under classification vs number-density weighting. | Phase 28: `lognormal_smear(weighting=…)`, `expected_radius_by_regime` |
| TUT-04 | [`04_time_and_parameter_crossings.py`](../notebooks/tutorials/04_time_and_parameter_crossings.py) | Demonstrate `crossing_time` and `crossing_parameter` root-finding. | Phase 22: `crossing_time(criterion='ratio')`; Phase 30: `crossing_parameter('delta_shell_m')` |
| TUT-05 | [`05_experimental_envelope.py`](../notebooks/tutorials/05_experimental_envelope.py) | Narrative walkthrough of model validity caveats and open S-slice gates. | Documentation only; cross-references `experimental-envelope.md` and `program-context.md` |

### First-attempt fixes folded into the implementation commit

Recorded in `d31783d`'s commit message and re-stated here for the
convention's audit trail:

- **TUT-01.** Hardcoded 100 nm radius was not on the §5 grid (the
  axis is log-spaced; 100 nm is between two grid points). Replaced
  with a programmatic nearest-grid-point lookup so the cell exists
  irrespective of grid changes.
- **TUT-04.** Original (criterion, target) combination did not
  bracket on the chosen cell. Switched to `criterion='ratio'`,
  `target=0.5` for `crossing_time` (returns ~65.7 s on a 100 nm
  cell) and `criterion='bmf'`, `target=0.5` for `crossing_parameter`
  on a 150 nm cell over the `delta_shell_m` axis (returns ~13.9 nm).
  Both demonstrate successful root-finding with non-`None` results,
  matching the "positive crossing tests are non-skippable" principle
  established in commit `cbcdd33` (Phase 30 review fixes).

## Smoke-test record (run against `pilot-v0.4`, venv Python 3.13)

| TUT-* | Command | Wall time | Exit |
|---|---|---:|---|
| TUT-01 | `PYTHONPATH=src python notebooks/tutorials/01_quick_start_regime_map.py` | 0.80 s | 0 |
| TUT-02 | `PYTHONPATH=src python notebooks/tutorials/02_geometry_and_shell_calibration.py` | 0.34 s | 0 |
| TUT-03 | `PYTHONPATH=src python notebooks/tutorials/03_polydispersity_intuition.py` | 0.34 s | 0 |
| TUT-04 | `PYTHONPATH=src python notebooks/tutorials/04_time_and_parameter_crossings.py` | 1.14 s | 0 |
| TUT-05 | `PYTHONPATH=src python notebooks/tutorials/05_experimental_envelope.py` | 0.05 s | 0 |

All five comfortably under the 60 s convention budget; sum 2.67 s.
None call `walk_grid()`; all consume only committed inputs
(`notebooks/data/regime_map_grid.csv` for TUT-01 / TUT-03; `src/`
modules and committed Markdown for TUT-02 / TUT-04 / TUT-05).

## Decisions

| Decision | Rationale |
|---|---|
| Tutorials live under `notebooks/tutorials/` and not `tutorials/` at repo root | Keeps the cd-rules tree intact (no new top-level folder); `notebooks/` is already the home for jupytext `.py` files, so tutorials are a sub-tree under that established convention. |
| Tutorials are accessibility surfaces, not §6 deliverables | A missing tutorial does not block a physics release. A release that *claims* tutorial coverage must have smoke-tested it. The deliverable-index split honours this — §6 row count is unchanged by tutorial work. |
| Stable `TUT-XX` IDs decoupled from filenames | Same shape as the `S1–S15` slice IDs in `program-context.md`. Renames record the path change in the roadmap; links and lab notes survive. |
| FAIR floor as a checklist, not a vague aspiration | Each criterion has a concrete check item: roadmap entry (findable), committed inputs (accessible), jupytext convention (interoperable), citation / licence / source-command hooks (reusable). |
| Backfill this lab note rather than amend the implementation commit | The convention says "create new commits rather than amending"; the lab note arrives in its own commit and the chronology is honest (the work was done 2026-05-06, the lab note was added 2026-05-06 — same day, separate ceremony). |
| TUT-04 demonstrates `criterion='ratio'` on `crossing_time` and `criterion='bmf'` on `crossing_parameter` | The two endpoints differ deliberately: showing both criteria across both functions lets a learner see that the API surfaces are symmetric. The 100 nm cell for `crossing_time` and 150 nm cell for `crossing_parameter` reflect cells where the targets bracket reliably under the chosen radius / depth / target combination. |

## Verification

```sh
# Tutorial smoke gate (per convention, before any release tag is pushed)
for f in notebooks/tutorials/0*.py; do
  PYTHONPATH=src .venv/bin/python "$f" >/dev/null && echo "$f OK"
done
# All five exit 0 within budget.

# Test suite unaffected (tutorials live outside tests/)
.venv/bin/python -m pytest -q
# 199 passed, 0 skipped

# Ruff
.venv/bin/python -m ruff check .
# All checks passed!
```

HEAD at this lab note's authoring: `d31783d` (implementation commit).
The lab note is added in a follow-up commit on top.

## What was not done

- **No `.ipynb` distribution.** The convention pins `.py` as the
  canonical source; `.ipynb` is on-demand via `jupytext --to ipynb`.
  No committed `.ipynb` files. (See "Open question" below.)
- **No Binder / Colab launch badges in the tutorial front matter.**
  External one-click rendering is a future enhancement, scoped
  separately.
- **No notebook 09 update for tutorials.** The integration audit
  script does not exercise the tutorial smoke commands; the
  smoke-test gate is run manually before a release tag rather than
  baked into `pytest`. A future extension could add a
  `notebooks/09_integration_audit.py` audit step that runs each
  `ready` tutorial; deferred.
- **No interactive cache-explorer / dashboard surface.** Out of
  scope for a tutorial batch; flagged as a separate open question
  (see "Open questions" below).

## Open questions (flagged for the user)

- **`.ipynb` distribution path?** Possible options: (a) committed
  `.ipynb` files in parallel with `.py` (not preferred by the
  current convention); (b) a release-time `jupytext --to ipynb`
  step that ships rendered notebooks as a release asset (no
  in-repo churn); (c) Binder / Colab badges in each TUT front
  matter pointing at the public repo URL plus a `binder/`
  configuration directory.
- **WP data display / manipulation stage?** A separate question
  about whether to offer an interactive cache-explorer (ipywidgets,
  streamlit, or panel) as a sixth tutorial or as a release surface.
  Trade-offs: lighter-touch ipywidgets stays inside the existing
  jupytext convention but only renders well in a notebook host;
  streamlit / panel adds runtime dependencies and deployment
  surface but renders in any browser.

## Cross-references

- [`docs/conventions.md` §"Tutorial notebooks"](../docs/conventions.md)
  — the ruleset this batch honours.
- [`docs/tutorial-roadmap.md`](../docs/tutorial-roadmap.md) — the
  tracking surface.
- [`notebooks/tutorials/README.md`](../notebooks/tutorials/README.md)
  — the in-folder index.
- Phase 32 release lab note: [2026-05-06-phase32-pilot-v0-4-release.md](2026-05-06-phase32-pilot-v0-4-release.md)
  — the release this tutorial batch attaches to.
- Pattern 14 in [`findings-process.md`](../docs/findings-process.md#14-forward-compatible-parameter-splits-via-zero-default-extension)
  — TUT-02's `from_fnd_class` example shows the pattern in action.
