# δ_shell calibration — literature survey (v0.3)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

| Field | Value |
|---|---|
| Status | **Best-effort calibration table.** Open-literature values cross-checked where possible; manufacturer data sheets not yet accessed. Marked as **audit-gap pin** pending proprietary DLS measurements. |
| Date | 2026-05-01 |
| Phase | 21 (item F) |

## 1. What δ_shell represents

`delta_shell_m = r_hydro_m - r_material_m` is the excess hydrodynamic radius
beyond the diamond core. It captures:

- Surface functionalisation layers (carboxyl, amine, PEG, etc.)
- Hydration shells and electric double layers
- Adsorbed ions / surfactants
- Any loose organic residue from synthesis

The v0.2 parameterisation treats `delta_shell_m` as a user knob. This
document provides literature-anchored defaults so that an experimentalist
can pick a representative value without running their own DLS.

## 2. Literature values

### 2.1 Bare / oxidised nanodiamond

| Source | Batch description | r_material (nm) | r_hydro (nm) | δ_shell (nm) | Notes |
|---|---|---|---|---|---|
| Kansas (DLS, 10 mM KCl pH 4) | unmodified ND (uND) | — | 37 | — | Single measurement; no TEM cross-check |
| Kansas (DLS, 10 mM KCl pH 4) | oxidised ND (oND) | — | 51 | — | Oxidation increases hydrodynamic size |
| Kansas (DLS, 10 mM KCl pH 4) | acidified ND (aND) | — | 36 | — | Similar to bare |
| Lysine-functionalisation study | pristine carboxylated ND | — | 40–80 (aggregate) | — | DLS in water; aggregates |
| Neugart et al. (FCS, buffer) | carboxylated ND | — | ~24 | — | Fluorescence correlation spectroscopy |
| Finas et al. (DLS, aqueous) | hydrogenated ND | — | 14, 18.5, 23 | — | Three fractions from density gradient |

**Interpretation:** Bare ND hydrodynamic radii scatter between ~15 nm and
~50 nm depending on oxidation state, solvent, and degree of aggregation.
Without a TEM-measured material radius for the same batch, δ_shell cannot
be computed directly.

### 2.2 PEG-functionalised nanodiamond

| Source | Batch description | r_material (nm) | r_hydro (nm) | δ_shell (nm) | Notes |
|---|---|---|---|---|---|
| PlasmaChem (DLS, water) | ND-PEG | 20–50 (mfr) | 25 | ~0–5 | Monodisperse in water; PDI 0.25 |
| PlasmaChem (DLS, PBS) | ND-PEG | 20–50 (mfr) | 415 | ~395 | Heavy aggregation in high-salt |
| PlasmaChem (DLS, DMEM+10%FBS) | ND-PEG | 20–50 (mfr) | ~481 | ~431 | Protein corona stabilises but still large |
| Adámas (DLS, aqueous) | PEG-coated FND | — | 35–50 (nominal) | — | Commercial product line |

**Interpretation:** PEGylation reduces aggregation in water but the
hydrodynamic radius is very sensitive to ionic strength. The δ_shell
for a dense PEG brush can be 5–20 nm; for a sparse PEG layer it may be
< 5 nm.

### 2.3 Commercial fluorescent nanodiamond (Adámas)

| Nominal size (mfr) | Hydrodynamic diameter (DLS) | Approx. r_hydro | Shape caveat |
|---|---|---|---|
| 70 nm | 70 nm | 35 nm | Major axis only; height ~23 nm |
| 100 nm | 100 nm | 50 nm | Major axis only; height ~33 nm |
| 140 nm | 140 nm | 70 nm | Major axis only; height ~47 nm |
| 750 nm | 750 nm | 375 nm | Major axis only; height ~250 nm |

The Adámas data sheet reports **hydrodynamic diameter** (not radius) from
DLS. Because the particles are highly non-spherical, the DLS value
corresponds to the major axis. For a prolate ellipsoid with aspect ratio
~3:1, the Stokes-equivalent spherical radius is roughly the geometric
mean of the semi-axes, i.e. `r_hydro ≈ (a · b²)^(1/3)` where `a` is the
half-major axis and `b` the half-minor axis.

If `a = D/2` (major semi-axis) and `b = a/3` (minor semi-axis), then:

```
r_hydro ≈ (a · (a/3)²)^(1/3) = a / 3^(2/3) ≈ 0.48 · a = 0.24 · D
```

So the effective Stokes radius for drag is ~24% of the reported DLS
diameter, not 50%. This is a **significant correction** for settling-
velocity and diffusivity calculations.

## 3. Proposed default values (conservative)

| FND class | r_material (nm) | r_hydro (nm) | δ_shell (nm) | Confidence |
|---|---|---|---|---|
| Bare / oxidised | 25 (TEM typical) | 35 | 10 | Low — high batch-to-batch variance |
| Carboxylated | 25 | 40 | 15 | Low — depends on COOH density |
| Hydroxylated | 25 | 30 | 5 | Very low — sparse data |
| PEG-functionalised (dense brush) | 25 | 50 | 25 | Moderate — PEG2000 chain length ~8 nm |
| PEG-functionalised (sparse) | 25 | 35 | 10 | Low — depends on grafting density |

**Caveat:** The `r_material = 25 nm` placeholder is a mid-range TEM
value for detonation nanodiamond. HPHT FNDs can be 50–150 nm. The
δ_shell values above should be **re-scaled linearly with r_material**
only if the shell thickness is independent of core size — which is
likely for a covalently grafted monolayer but not for a physisorbed
polymer layer.

## 4. Audit-gap pin

This calibration table is **provisional** because:

1. **No manufacturer data sheets** were accessed. Proprietary DLS
   measurements on the actual FND batches used in the experimental
   campaign would override every value above.
2. **Aggregation-state sensitivity** dominates the DLS signal. The
   same batch can report 50 nm in water and 800 nm in PBS.
3. **Shape anisotropy** (non-spherical diamonds) means DLS
   hydrodynamic diameter is not the Stokes-equivalent spherical
   diameter. A geometric-mean correction is needed.
4. **No direct δ_shell measurement** exists in the open literature
   for the same batch with both TEM material radius and DLS
   hydrodynamic radius.

**Resolution path:** When the experimental campaign identifies its
FND batch, run DLS on that batch in the same buffer as the tracking
experiment. Compare TEM material radius (from manufacturer) with DLS
hydrodynamic radius. The difference is the calibrated δ_shell.

## 5. Cross-references

- [`docs/experimental-envelope.md`](experimental-envelope.md) §"Material
  radius equals hydrodynamic radius" — the assumption this document
  relaxes.
- [`src/parameters.py`](../src/parameters.py) `ParticleGeometry` — the
  API that consumes `delta_shell_m`.
- [`docs/work-plan-v0-3.md`](work-plan-v0-3.md) §1 item F — the scope
  mandate for this calibration.
- [`docs/program-context.md`](program-context.md) §3.1 S3 — the full
  shell-calibration slice planned for v1.0.
