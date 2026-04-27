# 2026-04-27 — Phase 3.1: review-driven fixes to the Langevin simulator

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

A post-merge review of the Phase 3 commit `486b5da` flagged two real
bugs in `simulate()` and one numerical typo in the Phase 3 validation
table. Both bugs would have surfaced once Method C / the regime-map
started feeding `simulate()` short `t_obs` values from the §5 grid, so
they're cheaper to fix now than after Phase 4 starts depending on
them.

## What was done

### Bug 1 — `t_total` not honoured (high)

`simulate()` was rounding the requested `t_total` *up* to a full
policy step:

```python
n_steps = max(1, int(math.ceil(t_total / dt)))   # n_steps ≥ 1
result.t_total = n_steps * dt                    # could massively exceed t_total
```

Concrete reproducer (pre-fix): pure Brownian, `h = 1 mm`,
`D = 2.45·10⁻¹²`. The policy returns `dt ≈ 4080 s` (the diffusion-
dominated `β·h²/D` fallback). Requesting `t_total = 1 s` ran for
**4080 s** and reported `result.t_total = 4080 s`. For Method B's
own Phase 3 tests this never bit because they all picked
`t_total ≫ dt_policy`. For the §5 `t_obs` grid (Method C / regime
map dependency) this would have been a silent factor-of-thousands
overshoot.

Fix in [src/langevin.py](../src/langevin.py): when `dt` is
auto-derived, treat the policy dt as an *upper bound* and collapse
`dt = t_total / n_steps` so that `n_steps · dt ≡ t_total` exactly.
When `dt` is explicit, the user keeps the rounding behaviour but
the docstring now flags that `result.t_total` may exceed the
request by less than one dt.

### Bug 2 — snapshot scheduling front-loaded (medium)

The interval-based scheduler

```python
snapshot_step_interval = max(1, n_steps // n_snapshots)
snapshot_indices = range(snapshot_step_interval, n_steps + 1, snapshot_step_interval)
```

front-loaded snapshots whenever `n_steps` was not cleanly divisible by
`n_snapshots`. Example: `n_steps = 10`, `n_snapshots = 6` →
`interval = 1` → indices `[1, 2, 3, 4, 5, 6]`, missing the back half
of the trajectory.

Fix: snapshot indices are now
`np.unique(np.linspace(1, n_steps, n_snapshots, dtype=int))` — evenly
spaced, including the final step. The existing test only exercised a
friendly divisibility case so the bug slipped through.

### Validation-table typo (low)

The Phase 3 lab-note table reported a `2.2 %` long-time barometric
relative error and a `6.1 %` "smoke-test" footnote on the position
variance. Reviewer correctly noted that (a) the actual current seeded
run gives `1.82 %`, not `2.2 %`, and (b) reporting an out-of-tolerance
smoke-test value alongside the production results was easy to misread
as a validation failure.

Fix: table now reports only the production-config seeded results
(N at the committed value, seed = 42), with rel_err recomputed
post-bug-fix. The barometric row is still the closest to the 2 %
threshold and is now flagged as "CI surrogate, not the full §4.4
N = 10⁵ statistic".

### Regression tests

Four new tests in [tests/test_langevin.py](../tests/test_langevin.py):

- `test_simulate_honours_requested_t_total_when_dt_auto` — pins the
  Bug 1 contract: `result.t_total == requested t_total` when dt is
  auto-derived, and the actual dt stays under the policy upper bound.
- `test_simulate_zero_t_total_returns_initial_condition` — `t_total = 0`
  short-circuits to a zero-step result whose `final_z == initial_z`.
- `test_simulate_negative_t_total_raises` — negative `t_total` raises
  `ValueError`.
- `test_simulate_snapshots_span_full_run_in_awkward_divisibility`
  — exact reproducer for Bug 2 (`n_steps=10`, `n_snapshots=6`,
  explicit `dt=0.1`); asserts the final snapshot lands at `t_total`.

## Decisions

| Decision | Rationale |
|---|---|
| Auto-dt path collapses dt to t_total / n_steps; explicit-dt path keeps the round-up | The user passing `dt` is asking for tight control of the integrator step; honouring their dt and rounding n_steps up is what they expect. The auto-dt path is the ergonomic default and should be ergonomic — exact t_total honoured with the policy as a ceiling. |
| `t_total = 0` short-circuits rather than raises | A zero-length integration *can* be a valid programmatic input (e.g. `simulate_cell(...)` driven by a regime-map walker that scans `t_obs ∈ {0, …}`). Returning the initial condition is the no-op the caller expects; raising would force a call-site special case. |
| `t_total < 0` raises | No physical interpretation. Caller bug. |
| Linspace-based snapshot scheduler | Two lines, no edge cases, always reaches the final step. The interval-based version's branching was the source of the bug and isn't worth keeping. |
| Phase 3.1 as a separate lab note rather than an addendum to Phase 3 | Mirrors the Phase 2.5 pattern; the Phase 3 note remains a session record of *that* session, with an Errata line pointing here. |

## Verification

```
HEAD before this pass:  486b5daaef130b896f753ac7a067b250577700ca
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
57 passed, 5 skipped in 1.46s
$ ruff check src/ tests/ notebooks/
All checks passed!
```

The +4 passing tests are the regression tests above. Skipped count
unchanged at 5 (Method C dependencies). The five Phase 3 §4.4 tests
pass with the corrected dt contract — the rel_err numbers in the
Phase 3 table (now correctly reported) shifted by O(1e-4) relative
to the pre-fix run, well inside the seeded-run reproducibility band.

## What was *not* done

- **Spec-N (10⁵) production run of the long-time barometric test.**
  The CI surrogate at N = 10⁴ stays as-is; the spec's full-N statistic
  belongs in the §5 production sweep, not in the unit suite.
- **Snapshot-scheduling docstring update on `LangevinResult`.** Already
  accurate ("evenly spaced") because the new implementation makes it
  literally true; no text change needed.

## Cross-references

- Phase 3 lab note — table corrected in place; bug-fix audit trail
  lives here.
- breakout-note §4.1 — no spec change; this is implementation polish.

## Next session

Unchanged from Phase 3: Method C (Smoluchowski PDE). The five
Method-C-dependent skipped tests are the punch list.
