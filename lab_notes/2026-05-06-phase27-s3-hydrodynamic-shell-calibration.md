# Phase 27 — S3 hydrodynamic-shell calibration per FND class

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 26 accepted the v0.4 contract and cleared Phase 27 as the first
implementation slice: item B / S3, hydrodynamic-shell calibration per
FND class. The governing decisions are:

- D1 = Option 2 — stay anchored to breakout-note v0.2 commit `3b7b18af`.
- D2 = Option 1 — `pilot-v0.3` reproduces at compatibility defaults.
- D4 / D9 = item B (S3) in scope and first slice.

S3's job is to replace the v0.3 provisional
[`docs/delta_shell_calibration.md`](../docs/delta_shell_calibration.md)
survey with citation-anchored FND-class defaults while keeping
`delta_shell_m = 0` as the explicit compatibility path.

## What was done

- **Updated [`src/parameters.py`](../src/parameters.py).**
  Added `DeltaShellCalibration`, `DELTA_SHELL_CALIBRATIONS`,
  `FND_CLASS_ALIASES`, `delta_shell_for_fnd_class(...)`, and
  `ParticleGeometry.from_fnd_class(...)`.
- **Extended [`tests/test_hydrodynamic_split.py`](../tests/test_hydrodynamic_split.py).**
  Tests now pin the four canonical FND classes, alias resolution,
  calibrated defaults, explicit `delta_shell_m` override behaviour, and
  rejection of unknown classes.
- **Replaced [`docs/delta_shell_calibration.md`](../docs/delta_shell_calibration.md).**
  The document is now a v0.4 S3 calibration surface with a source
  register, four-class default table, code contract, and campaign-
  unverified caveats.
- **Updated envelope / index surfaces.**
  [`docs/experimental-envelope.md`](../docs/experimental-envelope.md)
  now shows `ParticleGeometry.from_fnd_class(...)`; the deliverable
  index and Pages landing page no longer describe the table as merely
  provisional.
- **Updated phase indexes.**
  [`README.md`](../README.md) gets the Phase 27 row; this lab-note index
  is updated in the same commit.

## Calibrated defaults

| Code key | Nominal class | Default `δ_shell` | Range | Rationale |
|---|---|---:|---:|---|
| `bare` | Bare / oxidised HPHT FND | 0 nm | 0–5 nm | DLS and microscopy sizes overlap for larger HPHT FNDs; preserve zero-shell default. |
| `carboxylated` | Carboxylated FND (`COOH`) | 5 nm | 0–10 nm | Small positive planning shell; aggregate DLS values are not encoded as ligand thickness. |
| `hydroxylated` | Hydroxylated / hydrogen-terminated HPHT FND | 0 nm | 0–5 nm | Direct HPHT evidence is consistent with nominal material diameter. |
| `peg_functionalised` | PEG-functionalised FND | 7 nm | 5–10 nm | PEG22 DLS diameter increments map to roughly 6–8 nm shell thickness. |

## Decisions

| Decision | Rationale |
|---|---|
| Close the v0.3 audit-gap pin for **generic planning defaults**, not for campaign truth | Program-context S3 asks for calibrated defaults per class. Same-buffer DLS on the eventual experiment batch remains the v1.0-grade measurement. |
| Keep `ParticleGeometry(...)` and `ParticleGeometry.from_radius(...)` at `delta_shell_m = 0` | This preserves D2 Option 1: v0.3 cache and scalar-radius paths reproduce byte-identically at compatibility defaults. |
| Add `ParticleGeometry.from_fnd_class(...)` rather than changing constructor defaults | The class default is opt-in and visible at the call site. User-supplied `delta_shell_m` remains authoritative. |
| Treat aggregate DLS values as caveats, not shell defaults | PBS / DMEM and pH-sensitive carboxylated suspensions can report hundreds of nm to µm hydrodynamic diameters. Those values describe aggregation / corona state, not a stable coating thickness. |
| Use four classes, not the v0.3 five-row dense/sparse PEG split | ADR 0003 and program-context S3 name four classes: bare, carboxylated, hydroxylated, PEG-functionalised. PEG density stays in the range / caveat language until a batch measurement exists. |

## Source survey

Primary sources consulted:

- Adámas functionalized red FND product information — commercial FND
  sizes and available surface functionalities.
- "Modification of nanodiamonds for fluorescence bioimaging" — HPHT ND
  DLS / zeta evidence and detonation-ND aggregation caveat.
- "Reduced background autofluorescence for cell imaging using
  nanodiamonds and lanthanide chelates" — PEG22 FND DLS increments.
- "Tumor selective uptake of drug-nanodiamond complexes improves
  therapeutic outcome in pancreatic cancer" — ND-PEG medium sensitivity.
- "Functionalized fluorescent nanodiamonds for simultaneous drug
  delivery and quantum sensing in HeLa cells" — functionalisation
  increment sanity check.
- "Carboxylated nanodiamond: aggregation properties in aqueous
  dispersion system" — COOH pH / aggregation caveat.
- "Fluorescent HPHT nanodiamonds have disk- and rod-like shapes" —
  FND shape-anisotropy caveat.
- Koniakhin et al., arXiv:1609.01535 — DLS / Stokes-Einstein caution
  near the few-nm lower bound.

## Verification

```sh
.venv/bin/python -m pytest -q
# expect: 183 passed, 0 skipped

.venv/bin/python -m ruff check .
# expect: All checks passed!

git diff --check
# expect: clean
```

## What was not done

- **No §5 cache regeneration.** The committed cache remains at
  `delta_shell_m = 0`.
- **No campaign-batch calibration.** No named FND batch exists yet; this
  is an open-literature planning default.
- **No aggregation model.** S1 remains deferred to v0.5+ and ADR 0002's
  `provisional=True` contract remains in force.
- **No S-slice nomenclature cleanup.** The broader
  `deliverable-index.md` / `release-notes/v0.3.md` correction is Phase
  29 item L.

## Next step

Phase 28 — S5 concentration-weighted polydispersity kernel. The
compatibility default remains the v0.3 classification-weighted kernel;
the number-density kernel is opt-in per work-plan-v0-4 R-E1.
