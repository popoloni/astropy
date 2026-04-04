"""Regression tests for azimuth wrap plotting behavior."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pytz

from plots.base import setup_altaz_plot
from plots.utils.common import (
    circular_mean_degrees,
    get_visible_azimuth_segments,
    split_trajectory_by_azimuth_wrap,
)
from plots.visibility.desktop import plot_visibility_chart


def test_visible_azimuth_segments_wrap_window():
    """Wrap windows must be represented as two segments around North."""
    segments = get_visible_azimuth_segments(315, 90)
    assert segments == [(315, 360.0), (0.0, 90)]


def test_split_trajectory_by_azimuth_wrap():
    """Trajectories crossing 359->0 should be split to avoid long artifacts."""
    azimuths = [350, 355, 359, 1, 5, 10]
    altitudes = [20, 21, 22, 23, 24, 25]

    segments = split_trajectory_by_azimuth_wrap(azimuths, altitudes)

    assert len(segments) == 2
    assert segments[0][0] == [350, 355, 359]
    assert segments[1][0] == [1, 5, 10]


def test_circular_mean_degrees_wrap_safe():
    """Circular mean should stay near North for values around 0/360."""
    mean_az = circular_mean_degrees([350, 355, 5, 10])
    assert mean_az is not None
    assert mean_az >= 350 or mean_az <= 10


def test_setup_altaz_plot_wrap_region_rectangles():
    """Wrap configuration should create two visible-region rectangles."""
    fig, ax = setup_altaz_plot()
    try:
        visible_rectangles = [p for p in ax.patches if hasattr(p, "get_width") and p.get_width() > 0]
        assert len(visible_rectangles) >= 2

        x_min, x_max = ax.get_xlim()
        assert x_min <= 0
        assert x_max >= 360
    finally:
        plt.close(fig)


def test_visibility_chart_does_not_close_existing_figures():
    """Creating visibility chart must not close figures that already exist."""
    fig_existing = plt.figure()
    try:
        tz = pytz.UTC
        start_time = datetime(2026, 1, 15, 19, 0, tzinfo=tz)
        end_time = start_time + timedelta(hours=8)

        fig_new, _ = plot_visibility_chart([], start_time, end_time)
        try:
            assert plt.fignum_exists(fig_existing.number)
            assert fig_new is not None
        finally:
            plt.close(fig_new)
    finally:
        plt.close(fig_existing)
