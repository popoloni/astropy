"""Regression tests for azimuth wrap plotting behavior."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pytz

from plots.base import setup_altaz_plot
from plots.utils.common import (
    azimuth_to_display_x,
    circular_mean_degrees,
    format_azimuth_tick_label,
    get_azimuth_window_span,
    get_visible_azimuth_segments,
    split_trajectory_by_azimuth_wrap,
)
from plots.visibility.desktop import plot_visibility_chart


def test_visible_azimuth_segments_wrap_window():
    """Wrap windows must be represented as one centered display segment."""
    segments = get_visible_azimuth_segments(315, 90)
    assert segments == [(0.0, 135.0)]


def test_display_mapping_centered_no_gap():
    """Display mapping must keep W->N->E continuous without central gaps."""
    span = get_azimuth_window_span(270, 90)
    assert span == 180

    display_w = azimuth_to_display_x(270, 270, 90)
    display_n = azimuth_to_display_x(0, 270, 90)
    display_e = azimuth_to_display_x(90, 270, 90)

    assert display_w == 0
    assert display_n == 90
    assert display_e == 180


def test_display_tick_labels_cardinals():
    """Tick labels should expose real azimuth as cardinal points on wrap axes."""
    assert format_azimuth_tick_label(0, 270, 90, use_cardinals=True) == 'W'
    assert format_azimuth_tick_label(90, 270, 90, use_cardinals=True) == 'N'
    assert format_azimuth_tick_label(180, 270, 90, use_cardinals=True) == 'E'


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
    """Wrap configuration should create a centered visible-region rectangle."""
    fig, ax = setup_altaz_plot()
    try:
        visible_rectangles = [p for p in ax.patches if hasattr(p, "get_width") and p.get_width() > 0]
        assert len(visible_rectangles) >= 1

        x_min, x_max = ax.get_xlim()
        assert x_min <= 0
        assert 120 <= x_max <= 200
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
