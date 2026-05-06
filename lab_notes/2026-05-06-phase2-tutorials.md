# Tutorial phase 2 — Colab launch path + TUT-06 cache explorer

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Tutorial phase 1 (commit `9569f1e`) backfilled the lab note for the
TUT-01…TUT-05 first batch (governance commit `13ac8d7` + implementation
commit `d31783d`). Phase 1's lab note flagged two open questions:
`.ipynb` distribution path, and a "WP data display / manipulation
stage." Phase 2 closes both.

User decision: "Both. Try Colab."

## What was done

### Colab launch path for TUT-01…TUT-05

- **Jupytext header bumped to `formats: ipynb,py:percent`** in all
  five existing tutorials. Pairs `.py` (canonical) with a generated
  `.ipynb` so Colab can open it directly from the repo URL.
- **Colab launch badge** (markdown cell) added at the top of each
  tutorial's front matter, linking to the paired `.ipynb` on `main`.
- **Colab bootstrap cell** added after the front matter:
  `if 'google.colab' in sys.modules:` clones the repo, `chdir`s to
  the root, and prepends `src/` to `sys.path`. No-op locally — the
  if-block short-circuits before any IPython magic; the embedded
  `subprocess.run(["git", "clone", …])` call works in plain Python
  too, so the source file remains valid Python.
- **`__file__` fall-back** in TUT-01 / TUT-03 (the cache loaders):
  `try: cache_path = Path(__file__)... except NameError: cache_path
  = Path("notebooks/data/regime_map_grid.csv")`. `__file__` is
  undefined in Colab and in Jupyter notebook contexts; the
  fall-back catches both, while the bootstrap cell guarantees the
  cwd is the repo root in Colab.

### TUT-06 — Interactive cache explorer (the WP-display surface)

[`notebooks/tutorials/06_cache_explorer.py`](../notebooks/tutorials/06_cache_explorer.py).
Demonstrates the §5 cache as a sliceable, interactive object:

- **Runtime detection.** `_is_interactive_kernel()` returns `True`
  only when `ipywidgets` imports successfully *and* the active
  IPython shell is a `ZMQInteractiveShell` (Jupyter / Colab kernel).
  Plain `python` returns `False` and the static-fallback path runs.
- **Interactive path** (Jupyter / Colab kernel + ipywidgets). Three
  `Dropdown` widgets (T, depth, t_obs) wired to
  `interactive_output(render_slice, …)`. Live regime-count summary
  + `top_to_bottom_ratio` curve as a function of radius for the
  current slice.
- **Static-fallback path** (plain `python` smoke run). Renders the
  representative (T=298.15 K, h=1 mm, t_obs=1 h) slice with
  `draw=False` and exits cleanly. This is the smoke-gate path; the
  convention's <60 s runtime budget is honoured (~0.95 s).
- No new runtime dependencies — `ipywidgets >= 8` and `jupytext >=
  1.16` were already in the `[notebooks]` extra of
  [`pyproject.toml`](../pyproject.toml).

### Paired `.ipynb` generation + sync

`.venv/bin/jupytext --to ipynb notebooks/tutorials/0*.py` produces
six `.ipynb` files committed alongside the `.py` sources. Subsequent
edits to a `.py` source are propagated to the `.ipynb` via
`.venv/bin/jupytext --sync notebooks/tutorials/<stem>.py`.

### Convention + roadmap + Pages updates

- **[`docs/conventions.md`](../docs/conventions.md) §"Tutorial
  notebooks".** Added two bullet items:
  - "Paired `.ipynb` files (tutorial-only carve-out)" — the `.py` is
    canonical; the `.ipynb` is a Colab-launchable mirror; the
    deliverable notebooks under `notebooks/` stay `.py`-only.
  - "Colab bootstrap cell" — describes the no-op-locally git-clone
    + chdir + sys.path pattern that every TUT-* now ships.
- **[`docs/tutorial-roadmap.md`](../docs/tutorial-roadmap.md).**
  Added a Colab column (all six = `yes`); added TUT-06 row; updated
  legend; bumped the *Note* line to "TUT-01 through TUT-06."
- **[`notebooks/tutorials/README.md`](../notebooks/tutorials/README.md).**
  Added Colab-badge column to the table; added "How to launch in
  Colab" and "How to keep `.py` and `.ipynb` in sync" subsections.
- **[`docs/index.html`](../docs/index.html).** "Try the model"
  evidence-grid section gets a sixth card (TUT-06) and an explicit
  "Open in Colab" link in every card.
- **[`README.md`](../README.md) "Learning path".** Reworded the
  table: extra Colab column, TUT-06 row, "paired jupytext `.py` +
  `.ipynb`" framing.

### Ruff disposition

The pre-existing TUT-01…TUT-05 sources had 29 ruff errors that
slipped through the prior release-cycle check. Rather than silently
absorb them, this batch adopts a two-step disposition:

- **Auto-fixed via `ruff check --fix`**: 18 safe issues (`I001`
  unsorted imports, `F401` unused imports, `W291` trailing
  whitespace, `W292` missing trailing newline, `F541` f-strings
  without placeholders). Pure formatting; no behaviour change.
- **`pyproject.toml` carve-outs** for the kinds of issues that are
  legitimate in a tutorial:
  - `extend-exclude = ["notebooks/tutorials/*.ipynb"]` — the
    auto-generated `.ipynb` files mirror their `.py` source; lint
    coverage stays on the canonical surface only.
  - `per-file-ignores = {"notebooks/tutorials/*.py": ["E501"]}` —
    front-matter markdown comment lines naturally exceed 100
    chars (long URLs, citation paths, smoke-command strings),
    and demonstrative `print(...)` lines in tutorials sometimes
    do too. The rest of the lint set still applies.

After both: `ruff check .` clean.

## Decisions

| Decision | Rationale |
|---|---|
| Pair `.py` + `.ipynb` for tutorials only, not for deliverable notebooks | Tutorials are accessibility surfaces; the user-acceptance test is "click and run." Deliverable notebooks under `notebooks/` are review-and-regen surfaces; pairing them would double the merge-conflict surface for no external-launch benefit. |
| `subprocess.run(["git", "clone", …])` instead of `!git clone` IPython magic | `!`-magic is a SyntaxError in plain Python. The convention's "smoke gate runs `python script.py`" requires the source to parse outside any IPython shell. `subprocess.run` is identically effective in Colab and runs cleanly under the smoke gate (the if-guard short-circuits the call). |
| TUT-06 single file with both interactive and static paths, not two files | The interactive widget code is small (~25 lines); a fallback file would duplicate the `render_slice` body. The runtime-detect guard is the cleanest way to keep one source of truth and let the smoke gate run unattended. |
| `ipywidgets` not added as a hard dependency | Already in `[project.optional-dependencies].notebooks`. The runtime detection fails cleanly without it, so a default-install consumer who doesn't run notebooks doesn't pull the widget stack. |
| Auto-fix the pre-existing tutorial ruff issues rather than blanket-ignore them | The 18 issues that auto-fix are all formatting (imports, whitespace, f-strings without placeholders). Auto-fixing improves the source without any judgment call about behaviour. The remaining `E501` cases are tolerated via per-file-ignore because the offending lines are markdown comments + demonstrative prints. |
| `formats: ipynb,py:percent` (jupytext metadata) ships in the `.py` header | Tells anyone using `jupytext --sync` (or jupytext-aware editors like JupyterLab with the plugin) that the two surfaces are paired. Without this, `--sync` doesn't know the pair exists. |

## Smoke-test record (run against `pilot-v0.4` HEAD `9569f1e`)

| TUT-* | Command | Wall time | Exit |
|---|---|---:|---|
| TUT-01 | `PYTHONPATH=src python notebooks/tutorials/01_quick_start_regime_map.py` | 0.46 s | 0 |
| TUT-02 | `PYTHONPATH=src python notebooks/tutorials/02_geometry_and_shell_calibration.py` | 0.05 s | 0 |
| TUT-03 | `PYTHONPATH=src python notebooks/tutorials/03_polydispersity_intuition.py` | 0.29 s | 0 |
| TUT-04 | `PYTHONPATH=src python notebooks/tutorials/04_time_and_parameter_crossings.py` | 1.01 s | 0 |
| TUT-05 | `PYTHONPATH=src python notebooks/tutorials/05_experimental_envelope.py` | 0.03 s | 0 |
| TUT-06 | `PYTHONPATH=src python notebooks/tutorials/06_cache_explorer.py` | 0.95 s | 0 |

Sum 2.79 s; well under the 60 s convention budget. None call
`walk_grid()`.

```sh
.venv/bin/python -m pytest -q
# 199 passed, 0 skipped (no test changes in this batch)

.venv/bin/python -m ruff check .
# All checks passed!

git diff --check
# clean
```

## Verification of Colab launch path (manual)

The Colab badges point at URLs of the form
`https://colab.research.google.com/github/Deep-Relaxation-Ordering/fnd-suspension-baseline/blob/main/notebooks/tutorials/<stem>.ipynb`.
These URLs become live once the .ipynb files land on `main` and are
pushed to `origin`. Colab fetches the file from the GitHub raw URL
on click; the bootstrap cell's `git clone` is what makes the
session functional after the .ipynb opens. Until the push, the
badges 404 — manual end-to-end verification under Colab is the
user's call.

## What was not done

- **No Binder configuration.** Binder needs a `binder/` directory
  with `requirements.txt` (or equivalent) and an
  `apt.txt` / `runtime.txt`. Adding it later mirrors what the Colab
  bootstrap cell does and gives a third one-click launch surface.
  Deferred — Colab covers the most common "click and run" path.
- **No `notebooks/09_integration_audit.py` extension for tutorial
  smoke gate.** The smoke gate is currently a manual-loop step
  before each release. Folding it into the audit script would let
  `pytest` exercise it automatically. Deferred to the next
  tutorial-batch phase.
- **No tutorial-level CI workflow.** GitHub Actions could run the
  smoke gate on PRs that touch `notebooks/tutorials/`. Deferred.
- **No update to deliverable-index `pilot-v0.5` candidates list**
  for tutorial-batch follow-ups. The roadmap captures the open
  items; promotion into the v0.5 work-plan candidate menu is a
  v0.5-cycle decision.

## Cross-references

- [Tutorial phase 1 lab note](2026-05-06-phase1-tutorials.md) —
  the predecessor batch.
- [`docs/conventions.md` §"Tutorial notebooks"](../docs/conventions.md)
  — the convention this batch extends.
- [`docs/tutorial-roadmap.md`](../docs/tutorial-roadmap.md) — the
  tracking surface, now showing all six tutorials with Colab=yes.
- [`pyproject.toml`](../pyproject.toml) — ruff carve-outs for
  tutorials documented in the dispositions table.
- Pattern 14 in [`findings-process.md`](../docs/findings-process.md#14-forward-compatible-parameter-splits-via-zero-default-extension)
  — TUT-06's runtime detection is a Pattern-14-shaped extension:
  the static-fallback path is the zero-default that reproduces
  the v0.4 behaviour for plain-`python` callers; the interactive
  path is the opt-in that requires a richer environment.
