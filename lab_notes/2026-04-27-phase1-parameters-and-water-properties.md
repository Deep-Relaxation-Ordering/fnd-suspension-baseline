# 2026-04-27 — Phase 1: parameters and water-properties

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 1 of the breakout-note timeline (§9): parameters module, water
properties, and the corresponding tests. Pre-requisite for everything
that follows; nothing else can be built or validated without it.

## What was done

### `src/parameters.py`

Implemented:

- **Constants**: `K_B` (CODATA 2019, exact), `G` (BIPM standard gravity),
  `RHO_P_DIAMOND = 3510 kg/m³` (bulk diamond, breakout-note §3 / §7g).
- **Validity ranges**: separate density and viscosity ranges, since
  Tanaka 2001 is calibrated 0–40 °C while the Vogel form for η is good
  across the full liquid range.
- **`rho_water(T)`**: Tanaka et al. (2001), Metrologia 38, 301, Eq. (1).
  ~1 ppm accuracy, traceable to IPTS-90.
- **`eta_water(T)`**: compact Vogel form
  `η(T) = A · 10^(B / (T − C))` with A = 2.414·10⁻⁵ Pa·s, B = 247.8 K,
  C = 140 K. Within ~1 % of IAPWS R12-08 over the liquid range; well
  below the 5 % regime-map threshold.
- **Shared physical primitives** (used by Methods A/B/C in later
  phases): `gamma_stokes(r, T)`, `diffusivity(r, T)`,
  `buoyant_mass(r, T, rho_p=RHO_P_DIAMOND)`. Putting them in
  `parameters.py` rather than `analytical.py` is what lets the
  Einstein–Smoluchowski check live "in the parameter module" as
  breakout-note §4.4 specifies.

### `tests/test_water_properties.py`

Replaced 2 skip stubs with 10 concrete tests:

- ρ(20 °C) ≈ 998.2071 kg/m³ (Tanaka Table 1) within ±0.001.
- ρ(4 °C) ≈ 999.9750 kg/m³ AND ρ(4 °C) > ρ(3 °C), ρ(4 °C) > ρ(5 °C)
  (water density max).
- ρ monotonic decrease across 5–35 °C.
- ρ-range guard: out-of-range raises `ValueError`.
- η at 5 °C, 20 °C, 35 °C against IAPWS R12-08 reference values
  (1 % at 20 °C, 2 % at endpoints — within Vogel-fit accuracy).
- η monotonic decrease across 5–35 °C.
- η(5 °C) / η(35 °C) ∈ (1.9, 2.2): confirms the breakout-note §2c
  "factor of approximately two" framing across the scan.
- η-range guard.

### `tests/test_einstein_relation.py`

Replaced 1 skip with the actual identity test: `D · γ = k_B T` at
machine precision (`rel_tol = 1e-15`) on five representative cells
covering corners and a midpoint of the breakout-note (r, T) grid.

## Verification

```
$ pytest -q
11 passed, 10 skipped in 0.02s
```

Skipped tests are awaiting Methods B and C (Phases 2 and 3).

```
$ ruff check src/ tests/
All checks passed!
```

## Decisions and minor deviations

- **Compact Vogel η-form rather than full IAPWS R12-08**. The full
  formulation has 21 coefficients and a multi-region structure; the
  Vogel form with three constants is good to ~1 % over the liquid
  range, well below the 5 % regime-map threshold. The breakout note
  cites "IAPWS formulation or Kestin–Sengers" — we are within that
  family but explicitly simpler. Documented in the function docstring
  with the IAPWS R12-08 cross-reference.
- **Shared primitives in `parameters.py`** rather than `analytical.py`.
  Reasoning above. The breakout-note §4.4 phrasing
  ("Einstein–Smoluchowski recovered ... in the parameter module")
  pulled the decision in this direction.
- **Scalar functions, not vectorised**. Vectorisation will be added
  when Method B (which evaluates these on trajectory ensembles) lands.
  No premature optimisation.
- **Distinct `T_DENSITY_*` and `T_VISCOSITY_*` ranges**. Honest about
  what each formulation covers; calls outside the calibrated range
  raise rather than silently extrapolate.

## Cross-references

- breakout-note §3 — physical model and material parameters
- breakout-note §4.4 — validation strategy (Einstein–Smoluchowski check)
- breakout-note §5 — parameter-scan ranges (5 nm – 10 µm, 278–308 K)
- cd-rules §0.7 — endorsement marker on this document

## Next session

Phase 2 — Method A (analytical) and notebook 01 (validation report).
This composes the primitives from `parameters.py` into the per-cell
equilibrium quantities (ℓ_g, t_eq, t_settle, v_sed, D), and produces
the first deliverable surface (notebook 01) that demonstrates the
parameter module is wired up correctly. Effort estimate: 1 day.
