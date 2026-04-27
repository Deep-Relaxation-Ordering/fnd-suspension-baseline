# 2026-04-27 — Phase 2: Method A and notebook 01

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 2 of the breakout-note timeline (§9): Method A (analytical layer)
and notebook 01 (baseline validation). Phase 1 (`parameters.py` plus
water properties) landed earlier today; this builds on top of those
primitives.

## What was done

### `src/analytical.py`

Per (r, T, h) cell:

- `scale_height(r, T, ρ_p)` — ℓ_g = k_B T / (m_eff g)
- `settling_velocity(r, T, ρ_p)` — v_sed = m_eff g / γ
- `equilibration_time(r, T, h, ρ_p)` — t_eq ~ min(h, ℓ_g)² / D
  (order-of-magnitude scaling; not a spectral-gap relaxation time)
- `settling_time(r, T, h, ρ_p)` — t_settle = h / v_sed
- `top_to_bottom_ratio(r, T, h, ρ_p)` — c(h)/c(0) = exp(−h / ℓ_g)
- `barometric_profile(z, r, T, h, ρ_p)` — normalised c_eq(z) on [0, h]
  with `expm1`-based normalisation that survives the homogeneous limit
- `cell_summary(r, T, h, ρ_p)` — every Method A quantity plus material
  inputs as a single dict, suitable as the per-row record of the
  1 050-cell §5 sub-grid output.

The barometric profile uses `numpy` for vectorised z-arrays; the scalar
quantities use stdlib `math`. This is the first place arrays appear in
the codebase.

### `tests/test_analytical.py`

16 new tests covering:

- Anchor-cell sanity (100 nm at 25 °C, 1 mm depth) — order-of-magnitude
  bands rather than fragile point values.
- Scaling laws — v_sed ∝ r², D ∝ 1/r, ℓ_g ∝ 1/r³ at fixed T.
- Limit behaviour of the top-to-bottom ratio — homogeneous and
  sedimented asymptotes, plus a check that the §5.1 5 % threshold
  corresponds to h / ℓ_g ≈ ln(20) ≈ 3.
- Barometric profile — mass conservation in both stratified and
  homogeneous limits, profile uniformity at small h / ℓ_g, and
  c(h)/c(0) ≪ 1 in a sedimented cell.
- `cell_summary` — all expected keys, plus the Einstein–Smoluchowski
  identity holds inside the dict (catches a class of stale-value bugs).

Two early failures were intolerance, not in the code: the
"homogeneous limit" tests at r = 5 nm, h = 1 mm asserted < 0.1 %
deviation when the actual cell sits at h / ℓ_g ≈ 3·10⁻³ → ~0.3 %
deviation. Loosened to 1 % to match the §5.1 regime semantics rather
than chase a tighter asymptote.

### `notebooks/01_baseline_validation.py`

Stored as a jupytext `:percent` `.py` file (cell markers `# %%`) so
the canonical source is diff-friendly. New convention captured in
`docs/conventions.md`.

The notebook produces three figures (PNG + PDF, under
`notebooks/figures/01_baseline_validation/`):

1. `vsed_D_ellg_vs_r.png` — deliverable-3 first figure: v_sed, D, ℓ_g
   vs. r at 25 °C, log–log. Reads cleanly: ℓ_g and v_sed cross D's
   horizontal sense at characteristic radii.
2. `regime_preview_ratio_vs_r.png` — c(h)/c(0) vs. r at fixed T for
   four sample depths, with §5.1 thresholds (0.95, 0.05) drawn. Each
   h-curve crosses the homogeneous and sedimented thresholds at
   definite radii; this is the analytical preview of the deliverable-3
   regime map (Method C will turn the equilibrium crossings into
   time-dependent crossings at finite t_obs).
3. `barometric_profile_three_radii.png` — equilibrium profile at three
   illustrative radii (30 nm, 100 nm, 300 nm) for h = 1 mm. Plotted on
   log y because the sedimented spike at z = 0 spans ~280 orders of
   magnitude when extrapolated to z = h, swamping linear scales.

### `docs/conventions.md`

Added the notebook convention: jupytext `:percent` `.py` is the
canonical source, `.ipynb` is generated on demand. Run notebooks with
`PYTHONPATH=src python notebooks/<notebook>.py`. Static figure outputs
under `notebooks/figures/<stem>/` as PNG + PDF.

## Anchor-cell snapshot (for cross-reference)

100 nm diamond, 25 °C, 1 mm sample:

| Quantity | Value |
|---|---|
| ρ_f | 997.05 kg/m³ |
| η | 8.90·10⁻⁴ Pa·s |
| m_eff | 1.05·10⁻¹⁷ kg |
| γ | 1.68·10⁻⁹ N·s/m |
| D | 2.45·10⁻¹² m²/s |
| v_sed | 6.15·10⁻⁸ m/s ≈ 60 nm/s |
| ℓ_g | 39.9 µm |
| t_eq | 648 s ≈ 11 min |
| t_settle | 1.63·10⁴ s ≈ 4.5 h |
| c(h)/c(0) | 1.29·10⁻¹¹ (sedimented at equilibrium) |

These values are the baseline against which Methods B and C will be
cross-checked in Phase 3 / Phase 4.

## Verification

```
$ pytest -q
27 passed, 10 skipped in 0.08s
$ ruff check src/ tests/ notebooks/
All checks passed!
```

10 still-skipped tests are Methods B and C dependencies.

## Decisions

| Decision | Rationale |
|---|---|
| Notebook as jupytext `.py`, not `.ipynb` | Diff-friendly, reviewable, no embedded base64-encoded outputs. Convert on demand. |
| Figures saved as both PNG and PDF | PNG for previews and lab notes; PDF for paper-ready inclusion. |
| `barometric_profile` uses numpy; scalar Method A quantities stay on `math` | Profile is the only function that naturally takes an array; no need to vectorise the rest yet. |
| Tolerances on "homogeneous limit" tests set to 1 %, not 0.1 % | Matches the §5.1 regime semantics. The asymptote is r → 0; we are testing in-regime behaviour, not asymptotic limits. |

## Next session

Phase 3 — Method B (stochastic Langevin ensemble), implementation in
`src/langevin.py` with vectorised Euler–Maruyama and the round-2 / 3
adaptive timestep + feasibility envelope. Includes wiring the
test_method_consistency / test_equilibrium tests for Method B. Effort
estimate: 2–3 days per breakout-note §9.
