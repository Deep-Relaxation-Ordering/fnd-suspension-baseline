# 2026-04-27 — Phase 3.2: architecture polish (barometric mean height, feasibility provenance, snapshot contract)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Second post-merge review pass on the Phase 3 / Phase 3.1 commits.
Three findings — one decentralised analytical helper, one provenance
mismatch, and one over-promised docstring — none load-bearing for
correctness, all worth fixing before Phase 4 starts depending on the
public surfaces.

## What was done

### Architecture — promote `barometric_mean_height` to Method A

`_barometric_mean_height` was a private helper inside
`tests/test_equilibrium.py`. ⟨z⟩ of the barometric profile is a
closed-form Method-A quantity by construction; per the project's own
design rule (`src/analytical.py` owns Method A), it belongs there.

- Added `analytical.barometric_mean_height(sample_depth_m, scale_height_m)`
  with a 700-threshold asymptotic branch (the naive expm1 form
  overflows for h/ℓ_g ≳ 710, which the §5 deeply-sedimented corner
  reaches).
- Added `z_mean_m` to `cell_summary` so it travels with the per-row
  record of the §5 sub-grid output.
- `tests/test_equilibrium.py` now imports the public function instead
  of carrying its own copy.
- Three new tests in `tests/test_analytical.py`:
  - homogeneous-limit recovers h/2 (5 nm at 25 °C in 100 µm cell, h/ℓ_g ≈ 3·10⁻⁴)
  - sedimented-limit recovers ℓ_g (1 µm at 25 °C in 1 mm cell, h/ℓ_g ≈ 2.5·10⁴; exercises the asymptotic branch)
  - h = 0 returns 0
- Plus `test_cell_summary_z_mean_matches_standalone_function` to pin
  cell_summary against the public function as the single source of
  truth.

### Provenance — `is_feasible` returns `dt_policy`, not `dt`

After the Phase 3.1 t_total fix, `simulate()`'s actual integration
step can be smaller than the round-2 policy step (the auto-dt path
collapses dt = t_total / n_steps when t_total < dt_policy). Yet
`is_feasible()` still returned the policy step in a 3-tuple position
named `dt`, which read as if it were the simulator's actual step.

- `is_feasible` now returns a `FeasibilityCheck` NamedTuple with
  fields `(feasible, n_steps, dt_policy)`. The class docstring spells
  out the policy-vs-actual distinction so callers can't misread the
  field as a provenance record.
- `tests/test_langevin.py`: existing tests rewritten to use the named
  fields; new `test_feasibility_dt_policy_matches_adaptive_timestep`
  pins the `dt_policy == adaptive_timestep(...)` contract.

### Documentation — snapshot scheduling contract is "up to N, including final"

The Phase 3.1 fix moved snapshot scheduling to
`np.unique(np.linspace(1, n_steps, n_snapshots, dtype=int))`. That's
not strictly "evenly spaced" — integer rounding plus dedupe means
you get *up to* `n_snapshots` snapshots, approximately spaced,
always including the final step.

- `simulate()` and `LangevinResult.snapshots` docstrings updated.
- New `test_simulate_snapshots_capped_at_n_steps_when_oversubscribed`
  pins the cap behaviour for `n_snapshots > n_steps` (returns
  exactly n_steps snapshots, not n_snapshots).

## Decisions

| Decision | Rationale |
|---|---|
| `barometric_mean_height` lives in `analytical.py`, not `parameters.py` | It's a Method-A composite, not a shared primitive. The Phase-1 rule "shared primitives in parameters.py" was about γ, D, m_eff which are used by every method. |
| 700-threshold asymptotic branch rather than try/except OverflowError | Explicit threshold reads cleaner, doesn't hide the regime distinction in exception flow, and matches the same idiom we'd use if we ever needed an expm1-equivalent in numpy land where exceptions are not raised. |
| `FeasibilityCheck` as a NamedTuple, not a dataclass | NamedTuple gives field access *and* tuple unpacking. Existing call sites that destructure into 3 names keep working. |
| Test file imports public function rather than re-deriving the formula | Lab note's own design rule: "test-first for testable rules". The test-derived helper was the rule's *implementation*; once that exists in production code, the test should consume it, not duplicate it. |
| Snapshot count is "up to N, capped at n_steps" rather than padding to N | Padding to N would either repeat the final step or interpolate; both are user-misleading. Cap is honest. |

## Verification

```
HEAD before this pass:  6d622ec31a3517f2a8a5e2c9d7767baa34f54a40
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
63 passed, 5 skipped in 1.55s
$ ruff check src/ tests/ notebooks/
All checks passed!
```

The +6 passing tests are: 3 limit-case tests for
`barometric_mean_height`, 1 cell_summary parity test, 1 dt_policy
contract test, 1 snapshot-cap regression. Skipped count unchanged
at 5 (Method C).

The five Phase 3 §4.4 physics tests continue to pass with the same
seeded rel_err numbers — promoting the helper didn't shift the
ensemble statistics because the formula was already accurate; the
move was purely architectural.

## What was *not* done

- **Adding `z_mean_m` to the Phase 2 anchor-cell snapshot table** in
  the Phase 2 lab note. Historical record; leave alone.
- **Updating `notebooks/01_baseline_validation.py`** to display
  `z_mean_m` in the anchor cell printout. The notebook iterates the
  whole `cell_summary` dict, so the new key surfaces automatically;
  no edit needed.

## Cross-references

- Phase 3 lab note — table values unchanged; the helper move is
  invisible to the seeded statistics.
- Phase 3.1 lab note — this pass extends the post-merge review
  discipline established there.
- breakout-note §4.1 — Method A inventory now includes ⟨z⟩ as an
  exposed quantity (was always a derivable consequence of the
  barometric profile, just not previously named).

## Next session

Unchanged: Phase 4 — Method C (Smoluchowski PDE). The five
Method-C-dependent tests in `test_method_consistency.py` are still
the punch list.
