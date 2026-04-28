# Physics findings — what the §5 sweep shows

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

This document distils the experimentally-actionable conclusions from
the `pilot-v0.1` §5 sweep cache
([`notebooks/data/regime_map_grid.csv`](../notebooks/data/regime_map_grid.csv),
6300 cells of (r, T, h, t_obs) classified per breakout-note §5.1).
The deliverable index ([`docs/deliverable-index.md`](deliverable-index.md))
maps each finding to the artefact that backs it; this document is
the narrative companion.

## Headline distribution

Across the full §5 grid (30 radii × 7 temperatures × 5 depths × 6
observation times):

| Regime | Cells | Fraction |
|---|---|---|
| homogeneous | 1166 | 18.5 % |
| stratified | 2293 | 36.4 % |
| sedimented | 2841 | 45.1 % |

Roughly half of the parameter space sediments at some observation
time within a week; only one-fifth stays mixed throughout. The
diamond-density / aqueous-suspension regime is dominated by gravity
across most of the (r, h, t_obs) space the breakout note sets out
to scan.

## The homogeneous-edge boundary follows `r ∝ h^{-1/3}`

The "homogeneous" upper-edge radius — the largest particle size that
the suspension keeps mixed at long times — is set analytically by
the §5.1 ratio threshold

```text
exp(-h / ℓ_g) = 0.95   ⇒   h / ℓ_g = -ln 0.95 ≈ 0.0513
                       ⇒   r ≈ ((3 / 4π) · k_B T · |ln 0.95| / (g h Δρ))^(1/3)
```

so `r_max(homog) ∝ (T / Δρ)^{1/3} · h^{-1/3}`. (Note: this is the
ratio-threshold edge `h/ℓ_g ≈ 0.051`, *not* the Péclet-unity
condition `h/ℓ_g = 1`. Pe ≈ 1 corresponds to `c(h)/c(0) = e⁻¹ ≈
0.37`, well inside the stratified band.) At room temperature this
gives:

| h | analytic r_max | §5 grid r_max (1 week) | comment |
|---|---|---|---|
| 0.1 mm | 27.4 nm | 24.1 nm | 1 §5 bin below |
| 0.5 mm | 16.0 nm | 14.3 nm | 1 §5 bin below |
| 1 mm | 12.7 nm | 11.0 nm | 1 §5 bin below |
| 2 mm | 10.1 nm | 8.4 nm | 1 §5 bin below |
| 10 mm | 5.9 nm | 5.0 nm | at the §5 floor |

The cube-root scaling in `h` is the dominant axis: a 100× change in
sample depth shifts the homogeneous edge by exactly the analytic 4.64×
ratio (= `100^{1/3}`). Cuvette depth choice is therefore the strongest
single experimental knob for keeping a given particle size mixed.

## Temperature dependence is sub-bin

Across the breakout-note 5 → 35 °C scan range, `T / Δρ` varies by
about 12 % (T scales linearly; Δρ = ρ_diamond − ρ_water drops a few
percent as water expands). The cube-root in the formula compresses
that to a ~3.4 % shift in `r_max`:

| T | analytic `r_max(homog)` at h = 1 mm | §5 grid r_max |
|---|---|---|
| 5 °C | 12.41 nm | 11.0 nm |
| 25 °C | 12.69 nm | 11.0 nm |
| 35 °C | 12.83 nm | 11.0 nm |

The §5 r-axis is 30 log-spaced points (~10 % bin spacing), so the
~3 % temperature shift falls inside a single bin and the §5 grid
samples cannot resolve it. Notebook 03's
`homogeneous_envelope_vs_T.png` overlays the smooth analytic
boundary on the grid markers to make this honestly visible. **Practical
consequence:** for the diamond-water system, holding the temperature
constant matters less than holding the cell depth constant.

## Time matters more than temperature

Walking the breakout-note t_obs axis at 25 °C, h = 1 mm — slice
shape is the §5 r-axis (30 radii) at fixed (T, h, t_obs):

| t_obs | regime distribution along the §5 r-axis (30 radii) |
|---|---|
| 1 min | 8 H / 14 S / 8 s |
| 10 min | 6 H / 12 S / 12 s |
| 1 h | 5 H / 10 S / 15 s |
| 4 h | 4 H / 9 S / 17 s |
| 1 d | 4 H / 9 S / 17 s |
| 1 week | 4 H / 9 S / 17 s |

(H = homogeneous, S = stratified, s = sedimented; each row sums to
30 = number of §5 radii.)

The *long-time* distribution is set by the equilibrium ratio
`exp(-h/ℓ_g)`; the *short-time* distribution drifts toward it. The
sedimented column more than doubles from 1 minute to 1 hour. The
homogeneous corner shrinks but stabilises — beyond `5 · t_relax` the
classifier sees the analytic equilibrium, and t_obs no longer matters
(rows 4 h, 1 d, 1 w are bit-identical at this slice).

## Round-4 second criterion is non-trivial

The §5.1 sedimented rule has an "AND" — `c(h)/c(0) ≤ 0.05` *and*
`∫₀^{0.05·h} c dz ≥ 0.95`. The second criterion (round-4 fix) prevents
finite-time profiles where the top has depleted but the bulk mass is
still in transit from being misclassified.

In the §5 sweep:

- **1085 of 6300 cells (17.2 %)** have ratio ≤ 0.05 but bmf < 0.95.
- All 1085 are classified `stratified` (per the round-4 AND).
- The maximum t_obs in this set is **1 week** — meaning some cells are
  *still in transit* after a week of observation. Equilibrium for
  these cells is sedimented, but the bulk hasn't reached the bottom
  5 % layer yet.

Without the round-4 criterion, those 17 % of cells would have been
labelled "sedimented", and downstream experiments designed against
them would have under-budgeted the time-to-sediment by an
order-of-magnitude factor. The round-4 fix is load-bearing for the
deliverable-5 design table.

## Anchor-cell case study (100 nm in 1 mm at 25 °C)

The breakout-note's canonical reference cell (the one notebook 01's
anchor row is built around) sits in the §5 axis at the nearest grid
radius `89.35 nm` and is **stratified at every t_obs in the §5
grid**, never sedimented:

| t_obs | regime | c(h)/c(0) | bmf(0.05·h) |
|---|---|---|---|
| 1 min | stratified | 0.62 | 0.053 |
| 10 min | stratified | 0.20 | 0.076 |
| 1 h | stratified | 1.7·10⁻² | 0.172 |
| 4 h | stratified | 1.6·10⁻⁴ | 0.466 |
| 1 d | stratified | 1.7·10⁻⁸ | 0.591 |
| 1 week | stratified | 1.7·10⁻⁸ | 0.591 |

The ratio drops from 0.62 to ~10⁻⁸ as the sample equilibrates; the
bottom-mass fraction climbs to **0.591 and asymptotes there** —
*never* reaching the 0.95 sedimented threshold. Why?

For r = 89 nm at 25 °C, ℓ_g ≈ 56 µm. The equilibrium profile is an
exponential of decay length 56 µm in a 1 mm cell. The mass is
concentrated near z = 0 — but the "near z = 0" zone is the ~56 µm
boundary layer, slightly larger than the 50 µm = 5 % cuvette
fraction the round-4 criterion measures against. The boundary
layer has 0.59 of the mass; the §5.1 round-4 criterion wants ≥ 0.95.
Hence the anchor cell asymptotes to "stratified, almost sedimented"
but never crosses the round-4 threshold. The cell *is* observably
non-uniform — c(h)/c(0) is below double precision floor — yet the
classifier calls it stratified.

This is the kind of cell the breakout note's §5.1 round-4
discussion was explicitly designed for: practically-significant
gravitational confinement, mathematically-far-from-flat profile,
but not "all the mass at the bottom" in the strong sense.

## Smallest sedimented radius at 1 hour

Inverse perspective — for sedimentation experiments, the smallest
particle that the §5 axis classifies "sedimented" at room temperature
and t_obs = 1 hour:

| h | smallest tested sedimented r at 1 h | analytic homog-edge r at h | ratio |
|---|---|---|---|
| 0.1 mm | 331 nm | 27 nm | 12× |
| 0.5 mm | 196 nm | 16 nm | 12× |
| 1 mm | 255 nm | 13 nm | 20× |
| 2 mm | 331 nm | 10 nm | 33× |
| 10 mm | 727 nm | 6 nm | 121× |

The ratio of "smallest radius that is *sedimented* in 1 h" to the
analytic homogeneous-edge radius (the ratio-threshold boundary
`exp(-h/ℓ_g) = 0.95` from the section above) is large (10× to
100×) and grows with `h`. The interpretation: at deep cells,
equilibrium sedimentation is slow because the diffusive relaxation
timescale grows as `h²`, so much larger particles are needed to
*finish* sedimenting in an hour. This bracket — homogeneous-edge
boundary on the small side, in-transit boundary on the large side,
with the stratified band between — is the deliverable-5 design
table's central narrative.

## Practical guidance bracket

For a typical room-temperature experiment in a 1 mm cuvette:

- **Stay-mixed**: r ≲ 11 nm at any t_obs up to a week.
- **Visibly stratified at minutes**: r ≈ 50 – 250 nm.
- **Visibly stratified at hours**: r ≈ 30 – 250 nm.
- **Sedimented within 1 h**: r ≳ 255 nm.
- **Sedimented within 1 minute**: r ≳ 1.6 µm.

Doubling the cell depth roughly halves each radius bracket; halving
it doubles. Temperature is a secondary knob within the
breakout-note's 5 → 35 °C range.

## Where the orchestration leans

For each cell, the regime classifier picks one of four execution
paths in cost order. Across the §5 grid:

| Path | Cells | Fraction | Compute cost |
|---|---|---|---|
| Homogeneous short-circuit | 840 | 13.3 % | < 1 ms each |
| Equilibrated short-circuit | 3266 | 51.8 % | < 1 ms each |
| Method C asymptotic fallback | 133 | 2.1 % | < 1 ms each |
| Method C resolved mesh | 2061 | 32.7 % | ~0.9 s each |

**Two-thirds of the §5 grid (4239 / 6300 cells) is determined
analytically** — by the homogeneous-corner and equilibrated-corner
short-circuits or by the asymptotic-sedimentation fallback. Only the
remaining one-third needs the Scharfetter-Gummel finite-volume
solver. The 147-min wall-time observed for the cache walk is set
almost entirely by these 2061 Method-C-resolved cells.

The implication for any future tightening of the §5 axis: doubling
the radius axis from 30 → 60 points roughly doubles the
Method-C-resolved cell count (the slow zone is mid-radius); doubling
the t_obs axis adds proportionally fewer slow cells (most additional
t_obs values would equilibrate via the short-circuit). Cost scales
with the radius and depth axes far more than with temperature or
t_obs.

## Cross-references

- [`docs/deliverable-index.md`](deliverable-index.md) — the §6
  artefact map; this document gives the narrative behind those
  artefacts.
- [`notebooks/02_regime_map.py`](../notebooks/02_regime_map.py) —
  visual companion to the headline distribution.
- [`notebooks/03_parameter_scans.py`](../notebooks/03_parameter_scans.py)
  — visual companion to the temperature-dependence and
  homogeneous-edge scaling findings (specifically the
  analytic-vs-grid envelope).
- [`notebooks/04_design_table.py`](../notebooks/04_design_table.py)
  — the design-table CSVs are the row-level data the headline
  brackets summarise.
- breakout-note §5.1 round-4 discussion — the "in-transit not
  sedimented" cells are the round-4 fix's raison d'être.
