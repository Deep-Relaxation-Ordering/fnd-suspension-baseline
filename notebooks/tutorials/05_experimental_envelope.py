# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # TUT-05 — Experimental envelope
#
# **Tutorial ID**: TUT-05
# **Purpose**: Narrative notebook outlining model validity caveats and open S-slice gates.
# **Expected runtime**: < 60 s
# **Release tag**: `pilot-v0.4`
# **Canonical inputs**: `docs/experimental-envelope.md`, `docs/program-context.md`
# **Smoke command**: `PYTHONPATH=src python notebooks/tutorials/05_experimental_envelope.py`
#
# **Links**:
# - Tutorial roadmap
# - Deliverable index
#
# **Citation/reuse**: Please see `CITATION.cff`, `codemeta.json`, `LICENCE`, and `pyproject.toml` in the repository root.

# %%
print("--- Provisional Flags and Audit Gaps ---")
print("\n1. lambda_se (Stokes-Einstein breakdown):")
print("   APIs return provisional=True when lambda_se < 1.0 (sub-continuum behavior).")

print("\n2. delta_shell_m:")
print("   FND class defaults exist (e.g., 'carboxylated' -> 5 nm), but batch-specific DLS remains the gold standard.")

print("\n3. Convection Threshold:")
print("   convection_flag = True if Ra > Ra_c. Stable 1-D transport may be broken by vertical thermal gradients.")

print("\n--- Open S-Slice Gates (for v1.0) ---")
print("   - S1: DLVO aggregation pre-screen")
print("   - S4: Capsule-geometry port (1-D radial in spherical coordinates)")
print("   - S6: Wall-hydrodynamic Faxén/Brenner corrections")
print("   - S7: Thermal control as a first-class axis")

# %% [markdown]
# ## Where to go next
#
# - Related finding: Experimental Envelope
# - Related finding: Program Context