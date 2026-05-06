# Phase 28 — S5 number-density polydispersity kernel

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Phase 27 closed item B (S3 — Hydrodynamic-shell calibration) at
commit `3a11dc8`. Phase 28 implements item E (S5 — Concentration-
weighted polydispersity kernel) per
[`docs/work-plan-v0-4.md` §1 item E](../docs/work-plan-v0-4.md) and
[`docs/program-context.md` §3.1 S5](../docs/program-context.md):

> The v0.2 polydispersity layer is classification-weighted: each radius
> bin gets the §5.1 label and a probability. For tracking experiments,
> what matters is the *number-density* distribution within each band.

The v0.3 [`lognormal_smear`](../src/polydispersity.py) returns
*marginal* probabilities and expected channels — it tells you the
chance a randomly drawn particle is in regime H / S / SED, but not
the conditional radius distribution within each band. Phase 28
adds an opt-in kernel mode that returns `E[r | regime=R]` and
`E[r² | regime=R]` for each regime, so a tracking experiment can
predict the radius distribution given an observed regime label.

## What was done

- **Extended [`src/polydispersity.py`](../src/polydispersity.py).**
  - Added a `weighting: Literal["classification", "number_density"]`
    keyword argument to `lognormal_smear(...)`. Default
    `"classification"` reproduces the v0.3 kernel byte-identically
    (Pattern 14 zero-default extension).
  - Added two new fields to `SmearedGrid`:
    `expected_radius_by_regime` and `expected_radius_sq_by_regime`,
    each shape `(3, n_r, n_sigma, n_T, n_h, n_t)`. The first axis
    indexes regime in (H, S, SED) order — accessible via
    `REGIME_INDEX_HOMOGENEOUS / _STRATIFIED / _SEDIMENTED`.
  - Added a `weighting` field on `SmearedGrid` so consumers can
    distinguish v0.3-mode payloads from S5-mode payloads at
    runtime.
  - Number-density mode populates the conditional moments cell by
    cell via `m1 = sum_i w_i · r_i · I[regime_i = R]` and
    `m2 = sum_i w_i · r_i² · I[regime_i = R]`, then divides by
    `p_R` (already computed for the classification kernel). Bands
    with `p_R = 0.0` are marked `NaN`. Classification mode leaves
    the new fields as `None`.
- **Extended [`tests/test_polydispersity.py`](../tests/test_polydispersity.py).**
  Six new tests:
  1. Classification kernel omits the Phase 28 fields (returns
     `None` for both moment arrays; `weighting == "classification"`).
  2. Number-density kernel reproduces the classification marginals
     (`p_homogeneous / p_stratified / p_sedimented /
     expected_top_to_bottom_ratio / expected_bottom_mass_fraction`)
     byte-identically — confirms R-E1 mitigation: the new kernel
     does not flip §5.1 regime labels.
  3. Law of total expectation:
     `sum_R p_R · E[r | regime=R] == E[r]_unconditional`
     to `rtol=1e-12`. Verifies the conditional moments are
     consistent with the kernel's marginal channels.
  4. Empty bands are marked `NaN`: anchored at a homogeneous-only
     cell with `sigma_geom = 1.05`, the sedimented band has
     `p_sed == 0` and `E[r | regime=SED] == NaN`.
  5. Jensen sanity: `E[r² | R] ≥ E[r | R]²` for non-empty bands
     (variance non-negative), with `~1e-10` relative tolerance to
     accommodate independent finite-precision sums of `m1` and
     `m2`.
  6. Invalid `weighting` keyword raises `ValueError`.

## Decisions

| Decision | Rationale |
|---|---|
| Per-regime conditional radius moments are the right output for "number-density distribution within each band" | Program-context S5 frames the v0.4 deliverable as "for each regime band, what is the radius distribution?" The first two moments (`E[r | R]`, `E[r² | R]`) characterise the band-conditional distribution sufficiently for design-tool consumption (mean radius and variance). Returning a discrete kernel (per-bin conditional density) was considered but adds an entire radius axis to every cell — wasteful when the design-tool consumer only ever wants summary statistics. |
| Pack moments into `(3, ...)` arrays rather than six separate fields | The existing `SmearedGrid` keeps one field per channel (`p_homogeneous` / `p_stratified` / `p_sedimented`), which works for 3 channels. Phase 28 doubles that to 6; six explicit fields is verbose. The packed form matches the natural mathematical shape (regime-indexed) and exposes `REGIME_INDEX_*` constants for callers, keeping the API clean. |
| Default kernel is `classification`, not `number_density` | D2 = Option 1 from [`docs/work-plan-v0-4.md` §3](../docs/work-plan-v0-4.md): every in-scope item must reproduce `pilot-v0.3` byte-identically at compatibility-mode defaults. Switching the default to `number_density` would change the `weighting` field on `SmearedGrid`, which a strict consumer could observe. Keeping the default at `classification` preserves v0.3's `SmearedGrid(weighting="classification", ..., expected_radius_by_regime=None)` shape exactly. |
| Empty bands return `NaN`, not 0.0 | `E[r \| regime=R]` is mathematically undefined when the band is empty (`p_R = 0`). Returning `NaN` makes that explicit; consumers that mask on `p_R > 0` get correct behaviour, and consumers that incorrectly broadcast see a propagated `NaN` rather than a silently-wrong 0.0. |
| No notebook 05 update | Notebook 05 uses the default kernel only and produces v0.3-anchor figures and design tables. Updating it to consume the new kernel would change figures and CSVs that ship under the v0.3 reproduction contract. The number-density payload is exposed for downstream tracking-experiment consumers; surfacing it in a notebook is deferred to a v0.4 release-notes example or a future tracking-pipeline notebook (see "Next step"). |
| No deliverable-index v0.4 mention yet | The deliverable-index "What `pilot-v0.4` would change" section is forward-looking from v0.3's perspective. Recording S5 closure as a release-time event lives in the v0.4 release notes (Phase 32), not here. |

## Verification

```sh
.venv/bin/python -m pytest -q
# 189 passed, 0 skipped (183 → 189: six new Phase 28 tests)

.venv/bin/python -m ruff check .
# All checks passed!

git diff --check
# clean
```

HEAD before Phase 28: `3a11dc8` (Phase 27 — S3 calibration).

## Risk register entries this phase activated

- **R-E1 (concentration-weighted kernel might flip §5.1 regime
  labels).** Mitigation honoured: the new kernel reproduces the
  classification kernel's marginal channels byte-identically; the
  per-regime conditional moments are *additional* output, not a
  replacement. Test
  `test_number_density_kernel_reproduces_classification_marginals`
  pins this with `np.testing.assert_array_equal`.

## What was not done

- **No new design table.** v0.4 has not yet exposed
  number-density-kernel output via a notebook or CSV; that's
  scoped for a possible follow-up notebook (after the tracking
  experiment exists, see [`program-context.md` §3.1 S8](../docs/program-context.md)
  trajectory-level outputs) or for the v0.4 release notes' usage
  example. Phase 28 ships the kernel, not a derived deliverable.
- **No v0.3 cache regen.** The v0.3 §5 cache is untouched;
  number-density moments are computed on the fly from the cache
  per call.
- **No `lambda_se`-axis interaction.** The kernel weights are
  purely radius-based; an `lambda_se` axis (item C, deferred to
  v0.5) would compose orthogonally if/when it lands.
- **No experimental-envelope edit.** The envelope already covers
  log-normal polydispersity at the radius level; the conditional
  moments do not introduce a new assumption.

## Next step

**Phase 29 — Doc-fix + housekeeping bundle** (items L + H per
[`docs/work-plan-v0-4.md` §4](../docs/work-plan-v0-4.md)):

1. Reconcile the S-slice nomenclature in
   [`docs/deliverable-index.md`](../docs/deliverable-index.md) and
   [`docs/release-notes/v0.3.md`](../docs/release-notes/v0.3.md)
   §"What `pilot-v0.4` would change" against
   [`program-context.md` §3.1](../docs/program-context.md).
   Treat program-context as authoritative.
2. Sweep v0.3 review residue.
3. `grep -rn "S[1-9]"` for additional stale references.

Effort: 1 session per §7. No code changes.

## Cross-references

- [`docs/work-plan-v0-4.md`](../docs/work-plan-v0-4.md) — Phase 28
  is item E (S5 polydispersity kernel).
- [`docs/program-context.md` §3.1 S5](../docs/program-context.md) —
  the program-context entry that motivates this phase.
- [`docs/adr/0002-v0.3-spec-anchoring.md`](../docs/adr/0002-v0.3-spec-anchoring.md)
  — the `provisional=True` API contract; Phase 28's outputs sit
  inside that contract because they are downstream of S2's
  `lambda_se` channel and therefore inherit `provisional=True`
  from the regime-grid input.
- [Phase 14 lab note](2026-04-30-phase14-polydispersity-smearing.md)
  — v0.2 polydispersity layer this phase extends.
- [Phase 27 lab note](2026-05-06-phase27-s3-hydrodynamic-shell-calibration.md)
  — predecessor v0.4 phase.
- [Pattern 14 in `findings-process.md`](../docs/findings-process.md#14-forward-compatible-parameter-splits-via-zero-default-extension)
  — zero-default extension contract.
