# δ_shell calibration — FND-class defaults (v0.4 S3)

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

| Field | Value |
|---|---|
| Status | **Citation-anchored FND-class defaults.** The v0.3 audit-gap pin is closed for generic planning defaults; campaign-specific FND batches remain **unverified** until same-buffer DLS / TEM data exist. |
| Date | 2026-05-06 |
| Phase | 27 (v0.4 item B / S3) |
| Code surface | [`src/parameters.py`](../src/parameters.py) `DeltaShellCalibration`, `DELTA_SHELL_CALIBRATIONS`, and `ParticleGeometry.from_fnd_class(...)` |

## 1. What δ_shell represents

`delta_shell_m = r_hydro_m - r_material_m` is the excess hydrodynamic
radius beyond the diamond core. It captures surface functionalisation
layers, hydration / electric-double-layer effects, adsorbed ions or
protein coronae, and loose organic residue from synthesis.

The compatibility default is unchanged:

```python
from parameters import ParticleGeometry

zero_shell = ParticleGeometry(r_material_m=50e-9)
assert zero_shell.delta_shell_m == 0.0
```

The Phase-27 addition is an opt-in class default for callers that know
the nominal FND surface class but do not have a batch-specific DLS
measurement:

```python
from parameters import ParticleGeometry

peg_fnd = ParticleGeometry.from_fnd_class(
    r_material_m=50e-9,
    fnd_class="peg_functionalised",
)
assert peg_fnd.delta_shell_m == 7e-9
```

Passing `delta_shell_m` explicitly always wins. This preserves the
v0.3 / v0.4 forward-compatibility contract: `delta_shell_m = 0` still
reproduces the committed §5 cache and every scalar-radius path.

## 2. Measurement convention

Most open literature reports a **hydrodynamic diameter** from DLS, often
without a matched TEM / AFM material diameter for the same batch. This
document therefore uses DLS measurements conservatively:

1. If a source reports a coating-induced diameter increment `ΔD`, the
   shell default uses `δ_shell ≈ ΔD / 2`.
2. If DLS and microscopy diameters overlap within reported uncertainty,
   the class default is `δ_shell = 0` and the uncertainty range carries
   the possible shell.
3. If DLS reports aggregates (hundreds of nm to µm), that value is not
   encoded as a class shell. It is a sample-preparation / medium state;
   callers must supply the measured hydrodynamic radius explicitly.
4. HPHT FND shape anisotropy is not corrected into a universal scalar
   here. `ParticleGeometry` remains a scalar Stokes-equivalent model;
   non-spherical batch corrections need campaign-specific metadata.

## 3. Source register

| Source | Relevant evidence | Used for |
|---|---|---|
| [Adámas functionalized red FND product information](https://www.adamasnano.com/functionalized-red-fnd-information) | Commercial FNDs span 10–300 nm and are sold with carboxylic acid, amine, polymer-coated, and click-chemistry surfaces. | Class menu / commercial-size context. |
| [Modification of nanodiamonds for fluorescence bioimaging](https://pmc.ncbi.nlm.nih.gov/articles/PMC10839752/) | HPHT NDs near 100 nm show DLS diameter `100 ± 30 nm`; the same source identifies hydrogen / hydroxyl termination and carboxylation by zeta / FTIR. Detonation 5–10 nm NDs aggregate to ~µm scale in water. | Bare / hydroxylated defaults; aggregation caveat. |
| [Reduced background autofluorescence for cell imaging using nanodiamonds and lanthanide chelates](https://www.nature.com/articles/s41598-018-22702-1) | PEG22 functionalisation increases DLS diameter by 16.1 nm for 30 nm FNDs and 11.3 nm for 100 nm FNDs. | PEG default (`ΔD / 2 ≈ 6–8 nm`). |
| [Tumor selective uptake of drug-nanodiamond complexes improves therapeutic outcome in pancreatic cancer](https://pmc.ncbi.nlm.nih.gov/articles/PMC6588439/) | ND-PEG is ~50 nm in water but jumps to hundreds of nm in PBS / DMEM; DMEM + 10% FBS returns to ~70 nm. | PEG medium-sensitivity caveat. |
| [Functionalized fluorescent nanodiamonds for simultaneous drug delivery and quantum sensing in HeLa cells](https://pmc.ncbi.nlm.nih.gov/articles/PMC9437893/) | Bare FND DLS diameter is 115.9 nm; diazoxide functionalisation shifts it to 139.2 nm without obvious aggregation. | Functionalisation-increment sanity check. |
| [Carboxylated nanodiamond: aggregation properties in aqueous dispersion system](https://doi.org/10.1166/jnn.2016.10932) | Carboxylated detonation ND aggregation depends on pH; the article is used as a warning that COOH class identity alone does not fix aggregate size. | Carboxylated aggregation caveat. |
| [Fluorescent HPHT nanodiamonds have disk- and rod-like shapes](https://www.sciencedirect.com/science/article/pii/S000862232300088X) | HPHT FNDs in the 50–150 nm range are often disk- or rod-like, with aspect ratio around three; scalar DLS assumes a sphere. | Shape-anisotropy caveat. |
| [Koniakhin et al., arXiv:1609.01535](https://arxiv.org/abs/1609.01535) | Stokes-Einstein DLS conversion is reliable above ~3 nm but needs care below that scale. | Lower-radius caveat for detonation-ND tails. |

## 4. Calibrated defaults

These are shell **thicknesses**, not hydrodynamic radii. They do not
scale with `r_material_m` unless a caller explicitly chooses to do so.

| Code key | Nominal class | Default `δ_shell` (nm) | Plausible range (nm) | Status |
|---|---|---:|---:|---|
| `bare` | Bare / oxidised HPHT FND | 0 | 0–5 | Open-literature default; campaign-unverified. |
| `carboxylated` | Carboxylated FND (`COOH`) | 5 | 0–10 | Open-literature default; aggregation-sensitive. |
| `hydroxylated` | Hydroxylated / hydrogen-terminated HPHT FND | 0 | 0–5 | Open-literature default; sparse direct data. |
| `peg_functionalised` | PEG-functionalised FND | 7 | 5–10 | Open-literature default for dispersed aqueous PEG-FND. |

### 4.1 Bare / oxidised

Default: `δ_shell = 0 nm`, range `0–5 nm`.

The clean HPHT-FND evidence does not require a nonzero shell: DLS and
microscopy sizes overlap within uncertainty for larger HPHT particles.
For the simulator, that means the safest generic default is the v0.3
zero-shell path. Oxidised / air-treated batches may still have surface
charge and hydration layers; the `0–5 nm` range records that uncertainty.

### 4.2 Carboxylated

Default: `δ_shell = 5 nm`, range `0–10 nm`.

Carboxyl groups themselves are not a thick coating, but COOH-enriched
FNDs are the common starting point for biofunctionalisation and can show
medium- and pH-dependent aggregation. The default therefore takes a
small positive shell rather than encoding aggregate diameters as if they
were ligands. If a carboxylated batch has same-buffer DLS / TEM data,
use the measured value instead.

### 4.3 Hydroxylated

Default: `δ_shell = 0 nm`, range `0–5 nm`.

The open HPHT evidence most directly associated with hydrogen /
hydroxyl surface termination has DLS diameter consistent with the
nominal material diameter. Hydroxylation is therefore treated like the
bare class until a batch measurement says otherwise.

### 4.4 PEG-functionalised

Default: `δ_shell = 7 nm`, range `5–10 nm`.

The PEG22 FND study gives the cleanest same-particle coating increment:
diameter increases of roughly 11–16 nm after PEGylation, which maps to
a shell thickness of roughly 6–8 nm. The default is rounded to 7 nm.

This default applies only to dispersed aqueous PEG-FND. High-salt or
cell-culture media can produce apparent hydrodynamic diameters hundreds
of nm larger than water measurements; those states are aggregation /
corona states and must be passed explicitly.

## 5. Code contract

The calibration table lives in `src/parameters.py`:

```python
from parameters import (
    DELTA_SHELL_CALIBRATIONS,
    ParticleGeometry,
    delta_shell_for_fnd_class,
)

assert delta_shell_for_fnd_class("COOH") == 5e-9
geom = ParticleGeometry.from_fnd_class(50e-9, "COOH")
assert geom.r_hydro_m == 55e-9

# Compatibility / explicit-user-knob path:
compat = ParticleGeometry.from_fnd_class(50e-9, "COOH", delta_shell_m=0.0)
assert compat == ParticleGeometry.from_radius(50e-9)
```

Accepted aliases:

| Canonical key | Accepted aliases |
|---|---|
| `bare` | `bare`, `oxidised`, `oxidized`, `unmodified` |
| `carboxylated` | `carboxylated`, `carboxylate`, `COOH` |
| `hydroxylated` | `hydroxylated`, `hydroxyl`, `OH`, `hydrogenated` |
| `peg_functionalised` | `PEG`, `PEGylated`, `peg_functionalised`, `peg_functionalized` |

Unknown classes raise `ValueError`; they are not silently mapped to
bare. If a future campaign batch is only partially functionalised, the
phase note should record it as a campaign-specific audit pin and pass a
measured `delta_shell_m`.

## 6. What this does not close

- It does not validate any named experimental-campaign batch.
- It does not model pH, ionic strength, protein coronae, surfactants, or
  aggregation kinetics.
- It does not change the committed §5 cache, which remains at
  `delta_shell_m = 0`.
- It does not clear ADR 0002's `provisional=True` S2 contract; S1
  aggregation remains deferred to v0.5+.

The v0.3 audit-gap pin is closed only in the sense required by S3:
there is now a citation-anchored class default and a code path that uses
it deliberately. Campaign-grade truth still comes from same-buffer DLS
on the actual FND batch.

## 7. Cross-references

- [`docs/experimental-envelope.md`](experimental-envelope.md) §"Material
  radius equals hydrodynamic radius" — the assumption this document
  relaxes.
- [`src/parameters.py`](../src/parameters.py) `ParticleGeometry` — the
  API that consumes `delta_shell_m`.
- [`docs/work-plan-v0-4.md`](work-plan-v0-4.md) §1 item B — the S3
  scope mandate for this calibration.
- [`docs/program-context.md`](program-context.md) §3.1 S3 — the
  long-horizon shell-calibration slice.
- [`../lab_notes/2026-05-06-phase27-s3-hydrodynamic-shell-calibration.md`](../lab_notes/2026-05-06-phase27-s3-hydrodynamic-shell-calibration.md)
  — implementation note for this upgrade.
