# Experimental envelope — `pilot-v0.2`

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

This document makes the pilot's model envelope explicit. The goal is
to separate "the code has a knob for this" from "the experiment must
control this before the model is applicable."

## Model assumptions

| Assumption | What breaks it experimentally | v0.2 status |
|---|---|---|
| Dilute, non-interacting particles | Concentrations high enough for excluded-volume effects, hydrodynamic coupling, or concentration-dependent viscosity | Deferred; use the pilot only as a single-particle / dilute-limit baseline |
| Spherical particles | Faceted, elongated, clustered, or irregular FNDs | Deferred; radius is an effective scalar input |
| Bulk diamond material density | Porosity, coatings, trapped solvent, or composition changes | User-controlled through parameter edits only; no mixture-density model |
| Material radius equals hydrodynamic radius | Functionalisation shells, hydration layers, surface ligands | Addressed as a forward-compatible knob via `ParticleGeometry(r_material_m, delta_shell_m)` |
| Monodisperse sample | Batch size distributions, aggregation tails, filtering cutoffs | Addressed in post-processing via log-normal `sigma_geom` smearing and deliverable 6 |
| Pure-water Stokes drag | Surfactants, buffers, salinity, viscosity modifiers | Partly controlled by temperature-dependent water viscosity; chemistry changes deferred |
| One-dimensional vertical transport | Convection, lateral flows, meniscus effects, tilted cells | Partly addressed by the Rayleigh-number `convection_flag`; flow fields are deferred |
| Reflecting top/bottom boundaries | Adsorption, sticking, bottom roughness, wetting layers | Deferred; Method C uses no-flux boundaries |
| No aggregation or breakup | Salt-triggered aggregation, photo-induced clustering, long storage times | Deferred and experimentally important |
| No wall-hydrodynamic correction | Particle radius not negligible compared with sample depth or near-wall boundary layer | Deferred; most §5 cells have r/h small, but near-bottom transport can still be wall-sensitive |

## Knobs now exposed

### `delta_shell_m`

Use this when the material radius that sets buoyant mass is smaller
than the hydrodynamic radius that sets drag and diffusion:

```python
from parameters import ParticleGeometry

geom = ParticleGeometry(r_material_m=50e-9, delta_shell_m=5e-9)
```

At `delta_shell_m = 0.0`, the v0.2 equations reproduce the scalar
v0.1 physics to machine precision. The committed §5 cache uses this
zero-shell path.

For nominal FND surface classes without batch-specific DLS data, v0.4
adds citation-anchored defaults:

```python
from parameters import ParticleGeometry

geom = ParticleGeometry.from_fnd_class(
    r_material_m=50e-9,
    fnd_class="peg_functionalised",
)
```

The class defaults are documented in
[`docs/delta_shell_calibration.md`](delta_shell_calibration.md). Passing
`delta_shell_m` explicitly remains authoritative; class defaults are
planning aids, not campaign measurements.

### `delta_T_assumed`

Use this when interpreting a real vertical cell with nonzero thermal
hysteresis. The programmatic cache walk defaults to `0.0 K`; notebooks
use `DEFAULT_EXPERIMENTAL_DELTA_T_K = 0.1 K` for overlays. A `True`
`convection_flag` means "do not read the 1-D regime label as a complete
experimental prediction until the thermal gradient is controlled."

### `sigma_geom`

Use this for batch polydispersity after the monodisperse §5 cache is
loaded. v0.2 pins `SIGMA_GEOM_AXIS = (1.05, 1.10, 1.20, 1.40, 1.60)`.
The smearing code reports `truncation_loss` and `accepted`; broad
distributions at the §5 radius-axis edges are diagnostic rows, not
silent extrapolations.

## Deferred experimental variables

The following are outside `pilot-v0.2` and should not be inferred from
the current figures or tables:

- aggregation kinetics and cluster-size evolution;
- adsorption or sticking at cuvette boundaries;
- non-water suspending media or surfactant-dependent viscosity;
- wall-corrected hydrodynamic drag near the bottom plate;
- measured thermal profiles, lateral flows, and evaporation;
- concentration-dependent sedimentation or hindered settling;
- optical readout limits, detection thresholds, and imaging bias.

## Practical use

For a clean, dilute, closed-cell water experiment with known particle
size distribution, use the model in this order:

1. Check the monodisperse regime label in the §5 cache or notebook 02.
2. Check the convection overlay for the actual cell depth and expected
   `delta_T`.
3. If the FND has a coating, rerun the relevant cells with either a
   measured `delta_shell_m` or a class default from
   `ParticleGeometry.from_fnd_class(...)`.
4. If the batch is polydisperse, use notebook 05's probability table
   rather than the single-radius label.
5. Treat aggregation, sticking, wall drag, and chemistry changes as
   out-of-model controls unless a later pilot adds them explicitly.
