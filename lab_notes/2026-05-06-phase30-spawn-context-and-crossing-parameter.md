# Phase 30 — tactical bundle: spawn-context (item I) + crossing_parameter (item J)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 29 closed items L (S-slice nomenclature reconciliation) and H
(v0.3 review residue) at commit `3bbdd55`. Phase 30 closes the
remaining tactical bundle from
[`docs/work-plan-v0-4.md` §4](../docs/work-plan-v0-4.md):

- **Item I.** Switch `regime_map.walk_grid`'s `ProcessPoolExecutor`
  to a `multiprocessing.get_context("spawn")` context to remove the
  macOS fork-safety footgun documented in
  [`docs/release-notes/v0.3.md` §H](../docs/release-notes/v0.3.md):
  *"macOS users should note the fork-safety caveat (pre-fork imports
  can hang — use spawn context or stay on serial default)"*. Pre-fork
  imports of NumPy / SciPy under macOS' Accelerate framework can
  deadlock at worker creation; the spawn start method re-imports
  cleanly in each worker.
- **Item J.** Extend `time_evolution`'s root-finding API. The work
  plan's mention of "extending to `top_to_bottom_ratio` crossings"
  was already shipped in v0.3 Phase 22 (`crossing_time(criterion='ratio')`);
  the genuinely new bit is the parameter-sweep counterpart —
  `crossing_parameter(...)` — which fixes `t_obs_s` and root-finds
  on a physical parameter (`delta_shell_m` or `lambda_se`).

## What was done

### Item I — spawn-context for ProcessPoolExecutor

- **Updated [`src/regime_map.py`](../src/regime_map.py).**
  - Added `import multiprocessing`.
  - In `walk_grid`, wrap the executor with
    `mp_context=multiprocessing.get_context("spawn")`. The serial
    path (`n_workers=1`) is unaffected.
  - Added an early guard for non-importable pseudo-main execution
    (`__main__.__file__ == "<stdin>"`, missing file paths). Without
    this guard, `spawn` fails later with `BrokenProcessPool`; the
    guard raises a direct `RuntimeError` telling the caller to run
    from a `.py` / `python -m` module or use `n_workers=1`.
  - Updated the docstring's parallel-walk paragraph to call out
    the spawn switch and reference the v0.3 release note's
    fork-safety caveat.
- **Extended [`tests/test_regime_map.py`](../tests/test_regime_map.py).**
  The existing `test_walk_grid_parallel_byte_identical_to_serial` in
  [`tests/test_regime_map.py`](../tests/test_regime_map.py) walks a
  24-cell slice with `n_workers=2` and confirms equality with the
  serial walk. After the spawn switch, the same test exercises the
  spawn path; passing it now means parallel walks are byte-identical
  under the new start method. A review-fix regression test,
  `test_walk_grid_spawn_rejects_stdin_main_with_clear_error`, pins
  the stdin/heredoc guard.

### Item J — crossing_parameter

- **Extended [`src/time_evolution.py`](../src/time_evolution.py).**
  - Added `crossing_parameter(...)`, the parameter-sweep counterpart
    to `crossing_time`. Given a fixed cell `(r, T, h)` and a fixed
    `t_obs_s`, sweeps `parameter ∈ {"delta_shell_m", "lambda_se"}`
    over `[p_min, p_max]` and returns the parameter value at which
    the chosen criterion (`"bmf"` or `"ratio"`) crosses the target.
    Returns `None` when no crossing exists in the interval.
  - Implementation mirrors `crossing_time`: linearly-spaced
    bracketing sweep, sign-change detection, PCHIP + Brent root-find
    with linear-interpolation fallback if PCHIP fails to bracket
    exactly. (Linear spacing is appropriate for both parameters'
    natural ranges: `lambda_se ∈ (0, 1]` and `delta_shell_m ∈ [0,
    ~50 nm]`.)
  - Added a private `_solve_with_parameter(...)` helper that builds
    the right `solve_cell` call: a `ParticleGeometry` constructor
    for `delta_shell_m`, a direct kwarg for `lambda_se`.
  - Input validation: rejects unknown parameter names, inverted or
    negative intervals, `lambda_se > 1`, non-positive `t_obs_s`,
    `n_points < 4`.
  - The module docstring is updated to describe both Phase 22 and
    Phase 30 surfaces.
- **Extended [`tests/test_time_evolution.py`](../tests/test_time_evolution.py).**
  Nine `crossing_parameter` tests:
  1. `test_crossing_parameter_rejects_unknown_parameter` — input
     validation.
  2. `test_crossing_parameter_validates_interval` — `p_min >= p_max`
     rejected.
  3. `test_crossing_parameter_validates_lambda_se_range` —
     `p_max > 1` rejected for `lambda_se`.
  4. `test_crossing_parameter_validates_t_obs_positive` —
     non-positive `t_obs_s` rejected.
  5. `test_crossing_parameter_validates_n_points` —
     `n_points < 4` rejected.
  6. `test_crossing_parameter_lambda_se_brackets_and_verifies`
     (`@pytest.mark.slow`) — sweep `lambda_se` for a stratified
     cell, then re-run `solve_cell` at the returned value and check
     the bmf criterion is at the target. The target is deliberately
     bracketed and the test is non-skippable.
  7. `test_crossing_parameter_lambda_se_ratio_brackets_and_verifies`
     (`@pytest.mark.slow`) — same positive-path assertion for the
     `criterion="ratio"` surface.
  8. `test_crossing_parameter_delta_shell_returns_none_when_unreachable`
     (`@pytest.mark.slow`) — homogeneous cell never crosses bmf=0.5
     for any `delta_shell_m`, so `crossing_parameter` returns `None`.
  9. `test_crossing_parameter_lambda_se_returns_none_for_unreachable_target`
     (`@pytest.mark.slow`) — target=0.999 above any plausible
     equilibrium bmf returns `None`.

## Decisions

| Decision | Rationale |
|---|---|
| Always-spawn, no kwarg toggle | The work plan §1 item I describes the change as "switch to spawn context," not "make the start method configurable." A kwarg toggle would be feature creep and add a configuration surface to test. The cost of spawn over fork is per-worker startup time (~tens of ms) plus re-import overhead, which is amortised over the 6300-cell `walk_grid` call by orders of magnitude. |
| Test the spawn contract, not the private executor object | `test_walk_grid_parallel_byte_identical_to_serial` pins serial-vs-parallel equality under the spawn path. The review-fix stdin guard test pins the user-facing failure mode for non-importable pseudo-main execution. A test that asserts `mp_context._name == 'spawn'` would test the implementation, not the contract. |
| `crossing_parameter` API: required `p_min` / `p_max`, no parameter-specific defaults | Symmetry with the `crossing_time` API (which requires `t_min` and `t_max`). Parameter-specific defaults (e.g., `lambda_se` defaulting to `[0.1, 1.0]`) leak knowledge that would change as v0.5 calibration data lands. Forcing the caller to be explicit avoids surprise. |
| `crossing_parameter` linear spacing, not log | `crossing_time` uses log-spaced bracketing because `t_obs` spans many decades. The parameters here span at most one decade (`lambda_se ∈ (0, 1]`) or vary near zero (`delta_shell_m ∈ [0, ~50 nm]`); linear spacing is uniformly informative. |
| Positive crossing tests are non-skippable | `crossing_parameter` returns `None` when the target is genuinely unreachable on the interval; those paths are asserted separately. Positive tests use bracketed targets and must return a parameter value that reproduces the target when re-run through `solve_cell`. |
| Ratio-criterion crossings already in v0.3 | The work-plan-v0-4 §1 item J description was slightly imprecise; the ratio criterion was shipped in v0.3 Phase 22's `crossing_time(criterion='ratio')`. Phase 30 reduces to the parameter-sweep extension. Item J's intent is captured by the new `crossing_parameter` function plus the existing `crossing_time(criterion='ratio')`. |

## Verification

```sh
.venv/bin/python -m pytest -q
# 199 passed, 0 skipped (189 → 199: nine crossing_parameter tests
# plus one spawn stdin-guard test).

.venv/bin/python -m ruff check .
# All checks passed!

git diff --check
# clean
```

HEAD before Phase 30: `3bbdd55` (Phase 29).

## Risk register entries this phase activated

- **R-I1 (spawn-context switch reveals fork-unsafe imports in
  regime_map module).** Mitigation: the integration test
  `test_walk_grid_parallel_byte_identical_to_serial` exercises the
  spawn path against the serial path; equality holds → no
  fork-unsafe behaviour was being relied upon. The stdin/heredoc
  review finding is handled by an early importability guard, not by
  falling back to fork.
- **R-J1 (extending time_evolution introduces a backward-
  incompatible signature change).** Mitigation: `crossing_time`'s
  v0.3 signature is unchanged. `crossing_parameter` is a new
  function; existing v0.3 callers see no API surface change. The
  `time_evolution` module's existing tests pass byte-for-byte after
  the additions.

## What was not done

- **No new design table for parameter-sweep crossings.** A v0.4
  design-table notebook for `crossing_parameter` output (e.g., "for
  what `delta_shell_m` does this cell flip from stratified to
  sedimented at t = 1 hr?") would be reasonable but is deferred
  to a possible v0.5 follow-up. Phase 30 ships the kernel.
- **No `lambda_se`-axis promotion to §5.** That's item C from the
  work plan, deferred to v0.5 (D5). The parameter sweep here is
  on-the-fly per call, not a pre-computed axis on the §5 cache.
- **No spawn-context audit beyond `walk_grid`.** The polydispersity
  smear and Method-A/B/C kernels are all single-process; the only
  ProcessPoolExecutor in the repo is in `walk_grid`. No further
  fork-safety surface to address.
- **No notebook 09 (integration audit) update for the spawn switch.**
  The integration audit notebook does not currently exercise
  `n_workers > 1`; adding a parallel-vs-serial-cache comparison is
  Phase 31's integration-audit job.

## Next step

**Phase 31 — integration audit + item K (release-criterion gap audit).**
Per [`docs/work-plan-v0-4.md` §4](../docs/work-plan-v0-4.md):

1. Phase 23-style byte-identical verification across all v0.4
   in-scope items (B / E / I / J at compatibility-mode defaults
   reproduce the v0.3 `pilot-v0.3` cache).
2. Module smoke tests for the new Phase 27 / 28 / 30 surfaces.
3. Item K — release-criterion gap audit against
   [`docs/program-context.md` §4.1](../docs/program-context.md):
   what fraction of the v1.0 release criteria does v0.4 close?

Effort: 1 session per §7. No code changes expected; documentation +
audit lab note.

## Cross-references

- [`docs/work-plan-v0-4.md` §1 items I and J](../docs/work-plan-v0-4.md)
  — the in-scope decisions this phase implements.
- [`docs/release-notes/v0.3.md` §H — Parallel `walk_grid`](../docs/release-notes/v0.3.md)
  — the fork-safety caveat this phase removes.
- [Phase 22 lab note](2026-05-01-phase22-continuous-time-evolution.md)
  — v0.3's `time_evolution` module that Phase 30 extends.
- [Phase 19 lab note](2026-05-01-phase19-audit-gap-pins-and-parallel-walk.md)
  — v0.3's `walk_grid` parallelism that Phase 30 hardens.
- [Phase 29 lab note](2026-05-06-phase29-doc-fix-and-review-residue.md)
  — predecessor v0.4 phase.
- [Pattern 14 in `findings-process.md`](../docs/findings-process.md#14-forward-compatible-parameter-splits-via-zero-default-extension)
  — zero-default extension contract; the spawn switch is invisible
  at `n_workers=1`, the new `crossing_parameter` function is purely
  additive.
