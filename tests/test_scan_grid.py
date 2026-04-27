"""Sanity tests on the centralised §5 scan grid.

Spec: breakout-note §5. The grid is the single source of truth shared by
notebooks and `regime_map.py`; these tests pin its shape so a silent
edit to one axis does not desynchronise the consumers.
"""

from __future__ import annotations

import math

import numpy as np

from scan_grid import (
    DEPTH_LABELS,
    DEPTHS_M,
    N_RADII,
    N_T_OBS,
    N_TEMPERATURES,
    NOTEBOOK_PREVIEW_DEPTH_INDICES,
    RADIUS_MAX_M,
    RADIUS_MIN_M,
    T_OBS_LABELS,
    T_OBS_S,
    TEMPERATURE_MAX_K,
    TEMPERATURE_MIN_K,
    radii_m,
    temperatures_k,
)


def test_radius_axis_shape_and_endpoints() -> None:
    rs = radii_m()
    assert rs.shape == (N_RADII,)
    assert math.isclose(rs[0], RADIUS_MIN_M, rel_tol=1e-15)
    assert math.isclose(rs[-1], RADIUS_MAX_M, rel_tol=1e-15)


def test_radius_axis_is_log_spaced() -> None:
    rs = radii_m()
    log_diffs = np.diff(np.log(rs))
    assert np.allclose(log_diffs, log_diffs[0], rtol=1e-12)


def test_temperature_axis_shape_and_endpoints() -> None:
    ts = temperatures_k()
    assert ts.shape == (N_TEMPERATURES,)
    assert math.isclose(ts[0], TEMPERATURE_MIN_K, rel_tol=1e-15)
    assert math.isclose(ts[-1], TEMPERATURE_MAX_K, rel_tol=1e-15)


def test_temperature_axis_is_uniform_5K_steps() -> None:
    ts = temperatures_k()
    diffs = np.diff(ts)
    assert np.allclose(diffs, 5.0, rtol=1e-12)


def test_depth_axis_has_five_points_and_labels_align() -> None:
    assert len(DEPTHS_M) == 5
    assert len(DEPTH_LABELS) == 5


def test_notebook_preview_depth_subset_is_well_formed() -> None:
    indices = NOTEBOOK_PREVIEW_DEPTH_INDICES
    assert len(indices) == 4
    assert all(0 <= i < len(DEPTHS_M) for i in indices)
    assert len(set(indices)) == len(indices)


def test_t_obs_axis_has_six_points_strictly_increasing() -> None:
    assert len(T_OBS_S) == N_T_OBS == 6
    assert len(T_OBS_LABELS) == 6
    diffs = [b - a for a, b in zip(T_OBS_S[:-1], T_OBS_S[1:], strict=True)]
    assert all(d > 0 for d in diffs)


def test_t_obs_axis_spans_minutes_to_a_week() -> None:
    """Spec contract: §5 t_obs grid covers fast-microscopy through long-observation."""
    assert T_OBS_S[0] == 60.0  # 1 min
    assert T_OBS_S[-1] == 7 * 24 * 3600.0  # 1 week
