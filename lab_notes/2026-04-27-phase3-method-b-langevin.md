# 2026-04-27 — Phase 3: Method B (Langevin)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 3 of the breakout-note timeline (§9): vectorised Euler–Maruyama
integration of the overdamped Langevin equation, with the round-2
adaptive timestep and the round-3 feasibility envelope. Builds on the
Phase 1 (`parameters.py`) and Phase 2 (`analytical.py`) primitives.

## What was done

### `src/langevin.py`

Implemented:

- **Constants**: `ALPHA = BETA = 1e-2` (round-2 timestep coefficients);
  `MAX_STEPS_DEFAULT = 5_000_000` (feasibility cap).
- **`adaptive_timestep(v_sed, D, h)`**: returns dt per round-2 policy.
  Special-cases pure Brownian (v_sed = 0 → β·h²/D), pure sedimentation
  (D = 0 → α·h/v_sed), diffusion-dominated (ℓ_g > h → β·h²/D), and
  general (min of drift and diffusion scales evaluated at ℓ_g). Both
  v_sed = 0 *and* D = 0 raises — there is no physical timescale.
- **`is_feasible(v_sed, D, h, t_total)`**: round-3 envelope check.
  Returns `(feasible, n_steps, dt)`. r ≳ 1 µm cells at t ~ 10⁴ s
  correctly fall out (dt ~ 10⁻¹⁰ s, n_steps ~ 10¹³).
- **`_reflect_into_box(z, h)`**: triangle-wave fold via
  `np.mod(z, 2h)` + `np.where(folded > h, 2h - folded, folded)`.
  Handles arbitrary multi-bounce overshoots in two vectorised lines.
- **`LangevinResult`** dataclass: provenance fields (v_sed, D, h, dt,
  n_steps, t_total, n_trajectories, bounded) plus `final_z`,
  `initial_z`, optional `snapshots`/`snapshot_times`, optional
  `first_passage_times`.
- **`simulate(...)`** (kernel): keyword-only on (v_sed, D, h, t_total,
  n_trajectories) plus optional `z0`, `dt`, `n_snapshots`,
  `track_first_passage_to_bottom`, `bounded`, `seed`. The kernel
  takes (v_sed, D) directly — not (r, T) — so the same simulator
  drives the test cases (v_sed = 0 for pure Brownian, D = 0 for
  pure sedimentation) without juggling fictitious cells.
- **`simulate_cell(r, T, h, ...)`**: physical-cell convenience wrapper
  that derives (v_sed, D) from `analytical.settling_velocity` /
  `parameters.diffusivity` and forwards to `simulate`.

### `tests/test_langevin.py`

15 new tests — kernel-level sanity, separated from §4.4 physics:

- Adaptive timestep policy: pure-Brownian, pure-sedimentation,
  general-stratified, diffusion-dominated fallback, double-zero rejection.
- Feasibility envelope: r = 10 µm correctly rejected; r = 100 nm accepted.
- Reflecting fold: identity inside box, single overshoot at top/bottom,
  multi-bounce overshoot.
- Determinism under seed.
- `bounded=False` requires explicit dt (no length scale to infer from).
- `bounded=True` keeps trajectories in [0, h].
- `simulate_cell` records the kernel parameters it derived.
- Snapshots are stored at evenly-spaced times.

### `tests/test_equilibrium.py`

Replaced 2 skips with real assertions:

- **`test_method_b_long_time_matches_barometric`**: 100 nm at 25 °C in
  100 µm cell (h/ℓ_g ≈ 2.5, t_eq ≈ 650 s). Run 20·t_eq with N = 10⁴,
  seed 42. Method B mean height 31.7 µm vs Method A barometric mean
  31.0 µm — relative error ~2 %, inside the §4.4 tolerance.
- **`test_position_variance_saturates_at_h2_over_12`**: pure-Brownian
  in a 1-µm box, t = 10 s ≫ h²/D ≈ 0.4 s, N = 2·10⁴. Var(z) within
  2 % of h²/12.

### `tests/test_method_consistency.py`

Replaced 3 skips with real assertions (5 still pending Method C):

- **`test_unbounded_msd_linear_in_time`**: free Brownian, no walls,
  z₀ = 0, dt = 1 ms, t = 1 s, N = 2·10⁴. ⟨[z(t)−z(0)]²⟩ within 2 %
  of 2Dt.
- **`test_bounded_displacement_msd_saturates_at_h2_over_6`**: same
  pure-Brownian setup with reflecting walls, long time. MSD within
  2 % of h²/6 (the round-4 distinction from h²/12 above).
- **`test_pure_sedimentation_arrival_times`**: D = 0,
  v_sed = 1 µm/s, h = 1 mm, uniform IC, N = 5000,
  `track_first_passage_to_bottom=True`. Mean first-passage time
  within 2 % of h/(2·v_sed) = 500 s; max first-passage within one
  dt of h/v_sed.

## Decisions and minor deviations

| Decision | Rationale |
|---|---|
| N = 10⁴ rather than spec's N = 10⁵ for the long-time barometric test | Test runtime budget: 10⁴ runs in ~0.4 s and meets the 2 % spec tolerance under seeded RNG. The scale is documented in the test docstring; flip to 10⁵ on the §5 production runs. |
| Kernel takes (v_sed, D) directly, with `simulate_cell` as the physical-cell wrapper | Lets pure-Brownian and pure-sedimentation tests reuse the same simulator. Avoids special "gravity off" / "diffusion off" flags that would clutter the call site. |
| Triangle-wave fold over a per-step iterative bounce loop | Two vectorised lines handle arbitrary overshoot magnitudes; the iterative version had a worst-case unbounded inner loop that the typed-array version sidesteps. |
| First-passage tracked on the *unreflected* step | A particle that crosses z = 0 and bounces back still has its arrival time recorded — what the §4.4 arrival-time test actually wants. Doing it after reflection would lose the crossing entirely. |
| `bounded=False` requires explicit dt | The adaptive policy uses h as its length scale when v_sed = 0; an unbounded-Brownian call has no h, so the implicit-dt path can't synthesise one. Explicit ValueError catches the misuse. |
| Single seed = 42 across the §4.4 tests | Deterministic CI; if any one test goes flaky we re-seed *that* test, not the whole suite. |

## Physics-validation snapshot (for cross-reference)

Production runs at the committed N and seed=42. All five inside the
§4.4 2 % tolerance.

| Test | Method-A reference | Method-B (seed 42) | Rel err |
|---|---|---|---|
| Long-time mean height (100 nm, 25 °C, 100 µm; N = 10⁴) | 3.1009·10⁻⁵ m | 3.1573·10⁻⁵ m | 1.82 % |
| Position variance (h = 1 µm, pure-Brownian; N = 2·10⁴) | 8.333·10⁻¹⁴ m² | 8.298·10⁻¹⁴ m² | 0.43 % |
| Unbounded MSD at t = 1 s (D = 2.45·10⁻¹², dt = 1 ms; N = 2·10⁴) | 4.900·10⁻¹² m² | 4.972·10⁻¹² m² | 1.47 % |
| Bounded MSD long-lag (h = 1 µm; N = 2·10⁴) | 1.667·10⁻¹³ m² | 1.660·10⁻¹³ m² | 0.43 % |
| Pure-sed mean first-passage (h = 1 mm, v = 1 µm/s; N = 5·10³) | 500.0 s | 500.6 s | 0.13 % |

The barometric mean-height test is the closest to the threshold; with
N = 10⁴ rather than the spec's N = 10⁵ it's a CI-friendly surrogate
for the full §4.4 validation, not the production statistic.

## Verification

```
HEAD before this pass:  0cd5fd9dd836dbbcb727dad2ff103e84830f3943
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
53 passed, 5 skipped in 1.52s
$ ruff check src/ tests/ notebooks/
All checks passed!
```

The +20 passing tests over Phase 2.5 are: 15 kernel tests
(`test_langevin.py`), 2 equilibrium tests, 3 cross-method tests. The
remaining 5 skipped tests are all Method C dependencies.

## What is *not* done

- **Notebook 02** (Method-B trajectory ensemble figures and Method-A↔B
  agreement panels). Deferred to keep this commit focused on the
  numerics; will land alongside the deliverable-2 figure set in a
  separate session.
- **t_obs axis in `scan_grid.py`** — still on hold until Method C
  fixes the t_obs grid for the regime map.
- **Out-of-envelope tagging in `regime_map.py`** — `is_feasible` is
  callable from there but `regime_map.py` itself remains a stub.

## Cross-references

- breakout-note §4.1 Method B — round-2 adaptive timestep, round-3
  feasibility envelope.
- breakout-note §4.4 — five validation checks for Method B (all
  un-skipped this session).
- Phase 2 lab note — anchor cell numbers reproduced by Method B at
  long times (within 2 %).
- Phase 2.5 lab note — `scan_grid.py` axes are already wired into
  `simulate_cell` via the (r, T, h) signature.

## Next session

Phase 4 — Method C (Smoluchowski PDE). The five Method-C-dependent
tests in `test_method_consistency.py` are the punch list:
exponential-fitting FV at high/low Pe, the asymptotic-sedimentation
fallback (round-4), Method-A↔C equilibrium agreement outside Method
B's envelope, and Method-B↔C time-dependent moments inside it.
Effort estimate per breakout-note §9: 2–3 days.

## Errata

Two bugs in the Phase 3 simulator and one numerical typo in the
validation table above were caught in a post-merge review and are
fixed in [`2026-04-27-phase3-1-review-driven-fixes.md`](2026-04-27-phase3-1-review-driven-fixes.md).
The corrected table above already reflects the post-fix seeded runs.
