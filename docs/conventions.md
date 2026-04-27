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

The pinned commit hash will be added once the breakout note's v0.2 PR
chain merges.

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
  `notebooks/figures/<notebook-stem>/` as both PNG (preview) and PDF
  (paper-ready). Run a notebook directly with
  `PYTHONPATH=src python notebooks/<notebook>.py` from the repo root,
  or open the `.py` in VS Code / PyCharm / Jupyter for cell-by-cell
  execution.
