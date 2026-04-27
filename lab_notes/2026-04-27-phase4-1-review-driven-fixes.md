# 2026-04-27 — Phase 4.1: review-driven fixes to Method C

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Post-merge review of `fb2a888` (Phase 4) raised three medium findings —
all about the surface area Method C exposes to the upcoming
`regime_map.py` orchestration, none about correctness of the §4.4
checklist that was just un-skipped. Fixing them now is cheaper than
catching the regressions during Phase 5 integration.

## What was done

### Bug 1 — `top_to_bottom_ratio` returned cell-averages, not c(h)/c(0)

The §5.1 regime classification uses the *boundary-value* ratio
`c(h)/c(0)` (homogeneous if ≥ 0.95, sedimented if ≤ 0.05). The
Phase-4 implementation in
[src/fokker_planck.py:91](../src/fokker_planck.py#L91) returned the
cell-average ratio `concentration[-1] / concentration[0]`, which on a
refined high-Pe mesh can differ from the boundary ratio by enough to
cross the threshold in either direction.

Fix: log-linear extrapolation from the two cells nearest each
boundary. This is exact for an exponential profile (the equilibrium
barometric form), reduces to 1 for a uniform profile, and degrades to
the cell-average ratio when interpolation neighbours are non-positive
(rare numerical pathology). The asymptotic-sedimentation fallback
short-circuits with `concentration[-1] == 0 → 0.0` so the existing
fallback test continues to pass with the same semantics.

Verified accuracy: on a stratified resolved-mesh cell (100 nm at 25 °C,
100 µm box, h/ℓ_g ≈ 2.5) the new method matches Method A's
`exp(−h/ℓ_g)` to relative error 1.4·10⁻¹³ at default mesh — essentially
machine precision.

### Bug 2 — only the asymptotic *fallback* path was validated against Method A

The Phase-4 test `test_method_a_c_equilibrium_outside_b_envelope`
deliberately picked `r = 10 µm` to land outside Method B's envelope
and trigger the fallback — so the assertion validated only the
analytic override, not the `expm_multiply` solver. There was no test
that "give Method C a stratified cell, run for many t_eq, the profile
is barometric to better than X %".

Fix: new test `test_method_a_c_equilibrium_inside_b_envelope_resolved_mesh`
on the same 100-nm / 25 °C / 100-µm cell as Bug 1's verification.
Asserts `not used_asymptotic_fallback` (the resolved path is exercised),
then pins three independent equilibrium quantities against Method A:

- `mean_height` within 10⁻³ of `barometric_mean_height(h, ℓ_g)`.
- `top_to_bottom_ratio` within 10⁻⁶ of `exp(−h/ℓ_g)` (essentially
  machine-precision after the Bug-1 fix).
- `bottom_mass_fraction(0.05)` within 10⁻³ of the analytic
  `(1 − e^{−0.05 h/ℓ_g}) / (1 − e^{−h/ℓ_g})`.

The test runs `equilibrium_cell` with `n_cells = 60` and `t_factor = 10`
(rather than the defaults 240 / 50) — these are CI-time settings that
keep the test under 0.5 s while still resolving Method A to better than
2·10⁻⁴ relative error. Production scans should keep the defaults.

### Bug 3 — mass-conservation drift was hidden by `_normalise_density`

`solve()` calls `_normalise_density` after `expm_multiply`, which clips
small negatives to 0 and divides by the running mass. Useful for
floating-point noise; dangerous if it's hiding O(1 %) operator error
from a future regression.

Fix: new test `test_method_c_operator_conserves_mass_to_machine_precision`
calls `make_mesh` + `build_operator` + `expm_multiply` directly (no
normalisation), and asserts the raw output preserves total mass to
relative precision better than 10⁻⁹. Actual measured drift on the
Phase-4 operator with t = 100 s and a 240-cell mesh: 1.6·10⁻¹³.

### Tolerance polish — `test_method_b_c_time_dependent_moments_agree`

The Phase-4 tolerance was keyed to `h` (`abs(mean_b − mean_c) / h < 0.03`),
which for a stratified cell with mean ≈ 30 µm in a 100-µm box was
effectively a 7-10 % relative tolerance — much looser than the actual
seeded agreement.

Fix: tolerance is now keyed to the *value*: `< 0.01` on mean and
`< 0.02` on variance (relative-to-value). Actual measured rel-err at
the committed parameters: 3.8·10⁻³ on mean, 7.3·10⁻³ on variance.

## Decisions

| Decision | Rationale |
|---|---|
| Log-linear extrapolation for `top_to_bottom_ratio`, not linear | Exact for exponential profiles (the equilibrium form); converges to cell-average for short cells; fall-through to cell-average for pathological zero neighbours preserves the API contract. |
| Resolved-mesh equilibrium test runs at `n_cells=60, t_factor=10` | CI runtime budget. The test validates the *solver* logic; the §5 production scan can afford the 240-cell / 50-t_relax defaults. Documented in the test docstring. |
| Mass-conservation test exercises raw operator, not `solve()` | The whole point is to bypass `_normalise_density` — testing the un-normalised invariant. Goes through the public `make_mesh` + `build_operator` API so it doesn't lock down internal renormalisation logic. |
| Phase 4.1 as a separate lab note rather than amending Phase 4 | Mirrors the Phase 2.5 / 3.1 / 3.2 pattern — Phase-4 commit (`fb2a888`) is a session record of the original work; this note is the post-review delta. |
| `import diffusivity from parameters` (not from `analytical`) in the new test code | Phase 2.5 review-fix rule: import primitives from their owning module, not the module that re-exposes them as a side-effect of its own imports. |

## Verification

```
HEAD before this pass:  fb2a888bdec3181cdef5dd843960708aceac1bb5
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
72 passed in 2.37s
$ ruff check src/ tests/ notebooks/
All checks passed!
```

The +2 passing tests are the resolved-mesh equilibrium check and the
raw-operator mass-conservation check. Skipped count remains at 0.

## Validation snapshot

| Quantity | Method A | Method C (resolved mesh) | Rel err |
|---|---|---|---|
| Mean height ⟨z⟩ | 31.0093 µm | 31.0097 µm | 1.2·10⁻⁵ |
| Top-to-bottom ratio | 8.1455·10⁻² | 8.1455·10⁻² | 1.4·10⁻¹³ |
| Bottom-mass fraction (0.05 h) | 0.1283 | 0.1283 | 8.2·10⁻¹⁵ |
| Operator mass drift after t = 100 s | 1.0 (exact) | 1 − 1.6·10⁻¹³ | 1.6·10⁻¹³ |
| Method-B vs Method-C mean (transient) | — | — | 3.8·10⁻³ |
| Method-B vs Method-C variance (transient) | — | — | 7.3·10⁻³ |

## What was *not* done

- **Phase-4 lab-note "What was done" miscount** ("one extra mesh-regression
  check" — actually two) is left as historical record; the Phase 4.1
  count this note pins (5 un-skipped + 2 new + 2 from this pass = 9
  Method-C-related tests) is the current state.
- **`equilibrium_cell` `t_factor = 50` magic constant** still
  undocumented at the function signature. Defer until Phase 5 lands the
  regime-map and shows what convergence margin is actually needed.
- **`make_mesh` returning dead `fallback_edges`** in the unresolved
  branch — minor cleanliness, not load-bearing. Defer.
- **`initial: Literal["uniform"]`** on `solve` — defer until a second
  initial-condition lands.

## Cross-references

- Phase 4 lab note — committed at `fb2a888`; this delta extends it.
- Phase 3.1 / 3.2 lab notes — same review-driven-fix pattern applied
  to Method B's surfaces.
- breakout-note §5.1 — the consumer of `top_to_bottom_ratio` and
  `bottom_mass_fraction`. Bug 1 fixes the former so the regime
  classification matches the spec quantity.

## Next session

Unchanged: Phase 5 — `regime_map.py` orchestration + deliverables 3 / 5.
The corrected Method-C surface (`top_to_bottom_ratio` exact for
exponential profiles, raw-operator mass conservation pinned, resolved-
mesh equilibrium validated) is what Phase 5 will compose against the
§5 grid. The `t_obs` axis in `scan_grid.py` is the first piece.
