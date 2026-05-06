# Conventions

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg. Inherits cd-rules.*

This document pins the project-wide rules this repo follows, plus per-rule
applicability notes for the numerical-pilot context.

## Inherited rules

This repo inherits the project-wide rules from
[`threehouse-plus-ec/cd-rules`](https://github.com/threehouse-plus-ec/cd-rules)
(Corporate Design blueprint).

### Pinned version

| Field | Value |
|---|---|
| Source repo | `threehouse-plus-ec/cd-rules` |
| Pinned commit | `ee01c80352dd8446f189c3159a3d9e347463902c` |
| Pinned date | 2026-04-17 |
| Pinned blueprint | `blueprint-threehouse-CD.md` at the commit above |

When `cd-rules` tags a new release, this pin should update within one
release cycle (cd-rules §0.10 propagation rule). Drift is logged as a lab
note before the pin is moved.

## Per-rule applicability

The cd-rules blueprint covers Corporate Design — typography, emblem
construction, colour, web rendering, accessibility, and folder structure.
Many of those rules apply only to documents and assets that have a
visual-specimen surface. This repo is a numerical-method package; the
applicability is therefore selective.

| cd-rules section | Applies here? | Notes |
|---|---|---|
| §0.1 Open-source materials only | Yes | All dependencies in `pyproject.toml` are OSI-approved. |
| §0.2 No licence misuse | Yes | LICENCE clear; per-folder declarations added when sub-folders diverge. |
| §0.3 Split licence architecture | Yes (code/tooling layer) | This repo is the *Infrastructure* layer → MIT. |
| §0.4 Consistent folder structure | Partial | Standard cd-rules tree is web-asset-oriented. Deviations (no `index.html`, no `assets/`; added `src/`, `tests/`, `notebooks/`, `lab_notes/`) are documented in [`../README.md`](../README.md). |
| §0.5 Markdown first | Yes | All authored documents (README, this file, lab notes, breakout note) are Markdown-canonical. |
| §0.6 No version numbers in filenames | Yes | Version lives in `pyproject.toml` and git tags, not filenames. |
| §0.7 Endorsement marker on all documents | Yes | Markers added to README, this file, and each lab note. |
| §0.8 Deprecation, not deletion | Yes | `archive/` exists; deprecation protocol §15 applies. |
| §0.9 Testable rules vs adaptive guidance | Yes | The breakout-note validation strategy (§4.4) is the pilot's testable-rules layer. |
| §0.10 Asset propagation Model B | Conditionally | Engaged only when this repo first consumes a cd-rules visual asset. Not currently. |
| §0.11 Cross-repo reference pattern | Yes | This file is the cross-repo reference; downstream documents link to it rather than paraphrasing rules. |
| §0.12 Single source of truth | Yes | cd-rules is authoritative on conflict. |
| §2 – §10 (visual design) | Not yet | Engaged only if/when a web-rendered specimen of this repo is added. |
| §11 Heritage and Register | N/A here | Sail-level guidance for authored visual works. |
| §12 / §12A Web rendering and accessibility | Not yet | Engaged only with a web-rendered specimen. |
| §13 Asset inventory | Conditionally | Becomes relevant if `assets/` is added. |
| §14 Folder structure | Partial — see §0.4 row | Deviations documented in README. |
| §15 Deprecation protocol | Yes | Applies to anything that moves to `archive/`. |

## Pilot-spec pin

The methodological spec for this repo is the breakout note in the
sibling repo. Pinned reference:

| Field | Value |
|---|---|
| Source repo | `Deep-Relaxation-Ordering/diamonds_in_water` |
| Document | `breakout-note-brownian-sedimentation.md` |
| Status at scaffold | v0.2 (round-3 + round-4 follow-ups, plus cd-rules cross-reference) |
| Pinned commit | `3b7b18af7bd1739f3cb7b3360d2b75264dd5ad07` |
| Pinned date | 2026-04-27 (PR #2 merge into `main`) |

When the breakout note moves forward, this pin updates within one
working session and the bump is logged as a lab note (parallel to the
cd-rules drift rule above).

## Authoring conventions for this repo

A short, pilot-specific layer on top of cd-rules:

- **Endorsement marker** at the top of every authored Markdown document
  (README, lab notes, conventions, future docs/).
- **Lab notes** named `YYYY-MM-DD-<topic>.md` in `lab_notes/`. One per
  working session. Free-form within: parameters explored, what was run,
  decisions, deviations from spec, cross-references.
- **Issue-tracker discipline**: bugs and design questions go to the GitHub
  issues of this repo; lab notes may reference issue numbers.
- **Test-first for testable rules**: each rule in breakout-note §4.4 has
  a corresponding `tests/test_*.py` module before the implementation
  lands; the test starts skipped and is un-skipped when the implementation
  is in place.
- **Notebooks as jupytext `.py` (percent format)**: the canonical source
  of every notebook in `notebooks/` is a `.py` file with `# %%` cell
  markers (jupytext "percent" format). This keeps git diffs human-readable
  and avoids the pickled-output noise of raw `.ipynb` files. The breakout
  note's §4.3 sketch lists `.ipynb` filenames; in this repo those names
  refer to the paired `.py` files of the same stem, and conversion to
  `.ipynb` is on demand via `jupytext --to ipynb 01_baseline_validation.py`.
  Static figure outputs from each notebook are saved under
  `notebooks/figures/<notebook-stem>/`. PNG previews are tracked in
  git as the canonical reviewable artefact; PDFs (paper-ready) are
  written by the notebook on every run but are gitignored, because
  matplotlib embeds `/CreationDate` and the bytes churn on every
  re-run even when the plotted data is identical. Regenerate PDFs on
  demand by re-running the notebook. Run a notebook directly with
  `PYTHONPATH=src python notebooks/<notebook>.py` from the repo root,
  or open the `.py` in VS Code / PyCharm / Jupyter for cell-by-cell
  execution.

## Tutorial notebooks

Tutorials are a tracked documentation layer — visitor-facing notebooks that
teach the API by example. They are **not** release artefacts; a missing
tutorial does not block a physics release, but a release that claims tutorial
coverage must have smoke-tested it.

- **Location and identifiers.** Tutorials live under
  `notebooks/tutorials/` as jupytext `.py` files. Each tutorial has a
  stable roadmap identifier (`TUT-01`, `TUT-02`, ...); renames keep the
  identifier and record the path change in `docs/tutorial-roadmap.md`.
- **Paired `.ipynb` files (tutorial-only carve-out).** Tutorials may
  ship a paired `.ipynb` alongside the `.py` (jupytext format
  `ipynb,py:percent`) so external readers can launch them in
  Colab / Binder via a one-click badge. The `.py` remains canonical
  for review and merge-conflict resolution; the `.ipynb` is
  regenerated via `jupytext --sync` whenever the `.py` changes. This
  carve-out applies *only* to `notebooks/tutorials/`; deliverable
  notebooks under `notebooks/` stay `.py`-only per the rule above.
- **Colab bootstrap cell.** Every tutorial begins (after the front
  matter) with a no-op-locally bootstrap that clones the repo when
  `'google.colab' in sys.modules`, sets `cwd` to the repo root, and
  prepends `src/` to `sys.path`. This gives Colab readers cache + src
  access without any per-tutorial setup; running the `.py` under
  plain `python` skips the block entirely.
- **Data policy.** Tutorials must use committed cache or data files
  (`notebooks/data/`) unless the notebook is explicitly marked
  `<!-- EXPENSIVE -->` in its opening docstring and in the roadmap.
- **Runtime budget.** Under 60 seconds on the reference machine when run
  with `PYTHONPATH=src python notebooks/tutorials/<stem>.py`.
- **No full grid walks.** Tutorials must not call `walk_grid()`;
  they load the committed cache via `results_from_csv()` or use small
  synthetic parameter sets.
- **Generated files.** PNG figure outputs may be committed as reviewable
  artefacts under `notebooks/figures/<stem>/`. PDFs and ad-hoc CSVs are
  gitignored; commit them only after intentional review.
- **Front matter.** Every tutorial starts with a docstring / markdown cell
  containing:
  - Tutorial ID (matching `docs/tutorial-roadmap.md`)
  - Purpose (one sentence)
  - Expected runtime
  - Release tag it reflects
  - Canonical input files used
  - Smoke-test command
  - Links to canonical docs (breakout note, API docs, findings)
  - Citation / reuse note pointing to `CITATION.cff`, `codemeta.json`,
    `LICENCE`, and the license metadata in `pyproject.toml`
- **Back matter.** Every tutorial ends with a "Where to go next" cell that
  links to the next tutorial in the learning path and to the relevant
  deliverable / findings surface.
- **FAIR floor.** Ready tutorials must be findable via
  `docs/tutorial-roadmap.md`, accessible without network-only inputs,
  interoperable with the repo's jupytext `.py` notebook convention, and
  reusable by naming the release tag, canonical inputs, citation metadata,
  `LICENCE`, and license metadata. Any generated output committed with
  a tutorial must state its source command and input data in the
  tutorial front matter.
- **Smoke test.** Before a release tag is pushed, every tutorial in the
  roadmap with status `ready` is executed once and must exit 0.
