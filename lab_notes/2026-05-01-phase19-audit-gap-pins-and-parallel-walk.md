# Phase 19 — audit-gap pin resolution + parallel §5 walk

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 18 (commit `12510d4`) shipped the v0.3 first slice (S2 —
Stokes-Einstein corrections). Phase 19 closes two of the remaining
in-scope items in the [v0.3 work plan](../docs/work-plan-v0-3.md):

- **Item A.** Resolve the `T_OBS_S` and `DEPTHS_M` audit-gap pins.
- **Item H.** Performance — parallel §5 walk via
  `concurrent.futures.ProcessPoolExecutor`.

Both items are "tightenings under the v0.2 envelope" per ADR 0002
D1 (Option 2): no physics-scope expansion, no §5 cache numerical-
channel change, forward-compat baseline = `pilot-v0.2.1`.

## What was done

### Item A — audit-gap pins resolved (no value change)

- **`src/scan_grid.py`.** Removed "audit-gap pin / confirm at next
  spec drift" language from the `DEPTHS_M` and `T_OBS_S` block
  comments. Both axes now carry a Phase 19 resolution note: the v0.2
  spec (`3b7b18af`) is the authority and does not override the
  committed values, so they stand as the formal v0.3 defaults.
- **`docs/deliverable-index.md` Known caveats.** The two
  `scan_grid.*` audit-gap-pin bullets are struck through and
  annotated "resolved in Phase 19", with a cross-reference to
  ADR 0002 D1.
- **`docs/deliverable-index.md` What `pilot-v0.3` would change.**
  The "Resolve the `T_OBS_S` and `DEPTHS_M` audit-gap pins" bullet
  is struck through and annotated "done in Phase 19".

**Numerical impact: zero.** No value moved. The §5 cache reproduces
`pilot-v0.2.1` byte-identical at `λ_se = 1.0` (Phase 18 default).

### Item H — parallel `walk_grid` (byte-identical to serial)

- **`src/regime_map.py`.** `walk_grid()` gains an `n_workers: int = 1`
  kwarg.
  - `n_workers <= 1`: serial path. Same iteration order as v0.2
    (radius → temperature → depth → t_obs); no executor overhead.
  - `n_workers > 1`: cells are flattened into a deterministic list
    in the same iteration order, then dispatched to a
    `ProcessPoolExecutor` via `executor.map`, which preserves input
    order. The picklable top-level helper `_classify_cell_unpack`
    forwards `(cell, kwargs)` to `classify_cell`.
- **`tests/test_regime_map.py`.** New integration test
  `test_walk_grid_parallel_byte_identical_to_serial` walks a
  3 × 2 × 2 × 2 = 24-cell slice including a Method-C-resolved row
  serially and with `n_workers = 2`, asserting `RegimeResult`
  equality for every cell. Byte-identical (not "approximately equal")
  per the ADR 0001 cache contract.

**Forward-compat:** `n_workers = 1` is the default and reproduces
v0.2 line-for-line. The full 6300-cell §5 cache regen path is
unaffected unless the caller opts into parallelism.

**Wall-time benchmark deferred.** A 108-cell test slice
(spanning the slow Method-C-resolved corner) ran for >5 min in
informal timing without completing — the slow tail of the §5
grid dominates wall time, which is exactly what parallelism
buys against, but the timing harness needs its own phase to be
honest. A formal benchmark on the full 6300-cell §5 grid
(serial baseline ~150 min per Phase 6) is deferred to whichever
phase next regenerates the §5 cache; until then, the value of
item H is the *correctness contract* (byte-identical to serial,
pinned by the integration test), not a measured speedup.

## Decisions

| Decision | Rationale |
|---|---|
| Confirm `T_OBS_S` and `DEPTHS_M` values rather than move them | The v0.2 breakout-note `3b7b18af` is the v0.3 authority (ADR 0002 D1 Option 2) and does not override the committed values. The six durations (1 min → 1 week) are physically-motivated experimental timescales; the five depths cover Ibidi µ-slide through standard cuvette. Moving values without a spec change would create a gratuitous numerical-channel diff. |
| Default `n_workers = 1` (serial) | Pattern 14 zero-default: parallelism is opt-in, the v0.2 §5 cache regen path is unchanged, and serial output remains byte-identical. CI does not need a worker matrix unless future cycles benchmark under load. |
| Use stdlib `ProcessPoolExecutor` rather than `joblib` / `multiprocessing.Pool` | No new dependency. `executor.map` preserves input order natively, which is the deterministic-ordering contract item H requires. The `_classify_cell_unpack` helper is at module scope (picklable) so the parallel path imposes no constraint on `classify_cell`'s signature. |
| Single integration test rather than a worker-count parameter sweep | Byte-identical equality at any `n_workers > 1` follows from `executor.map`'s order guarantee plus the fact that `classify_cell` is deterministic given identical inputs. Pinning `n_workers = 2` is sufficient evidence; sweeping wastes CI time without adding signal. |
| Phase 19 stays under `pilot-v0.2.1` | Documentation + non-default code paths only. No `pyproject.toml` version bump; the v0.3 release tag lands at Phase 24 per the contract. |

## Verification

```sh
.venv/bin/python -m pytest -q
# 152 passed   (151 v0.2/Phase-18 baseline + 1 new parallel-walk integration test)

.venv/bin/python -m ruff check .
# All checks passed!

git diff --check
# clean
```

HEAD before Phase 19: `660b510` (Phase 18.1 — `count_label_flips`
rename).

## What was not done

- **No §5 cache regen.** Pin values did not move. The v0.2.1 cache
  remains the authoritative artefact for v0.3 in-scope items at
  their compatibility-mode defaults.
- **No CI worker-count matrix.** Item H delivers correctness, not a
  benchmarking harness. If future cycles want a regression on
  parallel speedup, that's its own phase.
- **No `joblib` introduction.** Stdlib `ProcessPoolExecutor` is
  sufficient and avoids a dependency bump.
- **No production §5 regen with `n_workers > 1`.** The v0.2.1 cache
  was generated serially and is staying that way until a phase
  explicitly targets a regen.
- **No measured wall-time speedup committed in this phase.** The
  benchmark harness needs its own phase; informal timing on a
  108-cell slice exceeded 5 minutes without completing because
  the slow Method-C-resolved tail dominates. Deferred to whichever
  phase next regenerates the §5 cache.
- **No `pyproject.toml` version bump.** Phase 19 ships under
  `pilot-v0.2.1`.

## Next step

Phase 20 — item B (continuous regime thresholds via root-finding on
`top_to_bottom_ratio = 0.95`, `bottom_mass_fraction = 0.95`, and
`p_stratified` suitability). 1–2 sessions per the contract;
forward-compat baseline = `pilot-v0.2.1` (D2 Option 1) because the
root-finder is additive, not numerical-channel-changing.

## Cross-references

- [`docs/work-plan-v0-3.md`](../docs/work-plan-v0-3.md) §1 items A
  and H — the contract this phase delivers against.
- [ADR 0002](../docs/adr/0002-v0.3-spec-anchoring.md) Decision 1
  (D1 = Option 2) — the spec-anchor under which "confirm existing
  values" is the right resolution for Item A.
- [ADR 0001](../docs/adr/0001-v0.2-spec-anchoring.md) — the byte-
  identical §5 cache contract that the parallel-walk integration
  test pins.
- [Phase 18 lab note](2026-05-01-phase18-s2-stokes-einstein-corrections.md)
  — immediate predecessor (S2 first slice).
- [Phase 17 (continuation) lab note](2026-04-30-phase17-continuation-contract-acceptance.md)
  — work-plan acceptance ceremony where items A and H were tagged
  in-scope.
- [`docs/deliverable-index.md`](../docs/deliverable-index.md)
  "Known caveats" + "What `pilot-v0.3` would change" — the two
  index sections updated to reflect the audit-gap-pin resolution.
