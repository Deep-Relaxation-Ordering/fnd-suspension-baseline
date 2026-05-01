# Phase 24 — `pilot-v0.3` release

## What was done

Release ceremony for `pilot-v0.3`. All seven in-scope items (A, B, C,
F, H, J, K) were implemented and verified during Phases 17–23. This
phase is mechanical: version bumps, metadata updates, release-note
authorship, deliverable-index refresh, and the git tag.

## Checklist

| Step | File / Action | Detail |
|---|---|---|
| 1 | `pyproject.toml` | version `0.2.1` → `0.3.0`; release-notes URL → v0.3 |
| 2 | `CITATION.cff` | version `0.2.1` → `0.3.0`; date `2026-04-30` → `2026-05-01`; abstract updated for v0.3 scope |
| 3 | `codemeta.json` | version `0.3.0`; dates `2026-05-01`; description expanded; downloadUrl → `pilot-v0.3.zip`; tag identifier → `pilot-v0.3`; release-notes link → v0.3 |
| 4 | `docs/release-notes/v0.3.md` | New file. Release pin, scope delta (K/A/B/C/F/H/J), forward-compat contract, narrative closeout, DOI deferral, v0.4 candidates. |
| 5 | `docs/deliverable-index.md` | Header updated to v0.3. Added v0.3 deliverable mapping (items 7–10). Preserved full v0.2 section below as reference. Updated known caveats and "What v0.4 would change". |
| 6 | `README.md` | Status section rewritten: v0.3 paragraph first, then v0.2 / v0.1 retrospective. Phase table extended with v0.3 cycle entries. |
| 7 | `lab_notes/README.md` | Added Phase 24 entry. |

## Verification

```text
$ pytest -q
171 passed in 105.95s

$ ruff check .
All checks passed!

$ git diff --check
(clean)
```

## Release pin

| Field | Value |
|---|---|
| Tag | `pilot-v0.3` |
| Commit | `TBD` |
| Package version | `0.3.0` |
| Test suite | `171 passed, 0 skipped` |
| Lint | `ruff check .` clean |
| Spec anchor | breakout-note v0.2 commit `3b7b18af` ([ADR 0002](../docs/adr/0002-v0.3-spec-anchoring.md)) |
| Predecessor | `pilot-v0.2` / `pilot-v0.2.1` |

## Forward-compat reminder

Zero-default paths (`lambda_se = 1.0`, `delta_shell_m = 0`,
`delta_T_assumed = 0.0 K`, `n_workers = 1`) reproduce the v0.2 §5
cache to machine precision. This was verified in Phase 23 on a
24-cell focused subset.

## v0.3 scope summary

| Item | Phase | Module / Notebook | What it does |
|---|---|---|---|
| K (S2) | 18 | `src/stokes_einstein_correction.py` | `lambda_se` breakdown coefficient at sub-150 nm |
| A | 19 | `src/scan_grid.py` (docs only) | `T_OBS_S` and `DEPTHS_M` pins resolved against ADR 0002 D1 |
| H | 19 | `src/regime_map.py` | Parallel `walk_grid` via `ProcessPoolExecutor` (serial default) |
| B | 20 | `src/continuous_thresholds.py` | Root-find continuous regime thresholds (`brentq`) |
| C | 21 | `notebooks/07_mesh_convergence_audit.py` | Mesh-convergence fidelity envelope documented |
| F | 21 | `docs/delta_shell_calibration.md` | Provisional literature calibration table |
| J | 22 | `src/time_evolution.py` | `time_series()` + `crossing_time()` with PCHIP + Brent |

## Post-release

The [`docs/work-plan-v0-3.md`](../docs/work-plan-v0-3.md) contract
remains in `docs/` as a release artefact. A v0.4 work-plan scaffold
is deferred to a later session (no open decisions pending).
