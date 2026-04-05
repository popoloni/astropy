"""Regression tests for visibility threshold filtering and label consistency."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pytz

from analysis.filtering import filter_objects_by_criteria
from astronomy.visibility import filter_visible_objects
from plots.trajectory.desktop import plot_object_trajectory
from plots.visibility.desktop import plot_visibility_chart
from plots.utils.common import get_abbreviated_name


class DummyObject:
    """Simple object for filtering and plotting tests."""

    def __init__(self, name="IC 1805", magnitude=6.5, fov="1.0x1.0"):
        self.name = name
        self.magnitude = magnitude
        self.fov = fov


def test_filter_visible_objects_excludes_below_visibility_list_threshold(monkeypatch):
    """Objects below list threshold must be excluded from both output lists."""
    start = datetime(2026, 1, 1, 20, 0, tzinfo=pytz.UTC)
    end = start + timedelta(hours=2)
    obj = DummyObject("IC 1805")

    monkeypatch.setattr("astronomy.visibility.find_visibility_window", lambda *_args, **_kwargs: [(start, end)])
    monkeypatch.setattr("astronomy.visibility.calculate_visibility_duration", lambda _periods: 0.5)
    monkeypatch.setattr("astronomy.visibility.calculate_required_exposure", lambda *_args, **_kwargs: (0.1, 1, 1))
    monkeypatch.setattr("config.settings.VISIBILITY_LIST_THRESHOLD_HOURS", 1.0, raising=False)
    monkeypatch.setattr("config.settings.MIN_VISIBILITY_HOURS", 0.1, raising=False)

    visible, insufficient = filter_visible_objects(
        [obj],
        start,
        end,
        exclude_insufficient=False,
        use_margins=True,
    )

    assert visible == []
    assert insufficient == []


def test_filter_objects_by_criteria_excludes_below_visibility_list_threshold(monkeypatch):
    """Analysis filtering path must apply the same threshold exclusion."""
    start = datetime(2026, 1, 1, 20, 0, tzinfo=pytz.UTC)
    end = start + timedelta(hours=2)
    obj = DummyObject("M42")

    monkeypatch.setattr("analysis.filtering.find_visibility_window", lambda *_args, **_kwargs: [(start, end)])
    monkeypatch.setattr("analysis.filtering.calculate_visibility_duration", lambda _periods: 0.75)
    monkeypatch.setattr("analysis.filtering.calculate_required_exposure", lambda *_args, **_kwargs: (0.1, 1, 1))
    monkeypatch.setattr("config.settings.VISIBILITY_LIST_THRESHOLD_HOURS", 1.0, raising=False)
    monkeypatch.setattr("config.settings.MIN_VISIBILITY_HOURS", 0.1, raising=False)

    visible, insufficient = filter_objects_by_criteria(
        [obj],
        start,
        end,
        exclude_insufficient=False,
        use_margins=True,
    )

    assert visible == []
    assert insufficient == []


def test_desktop_trajectory_legend_uses_shared_abbreviation(monkeypatch):
    """Desktop trajectory legend must use shared abbreviated name formatter."""
    start = datetime(2026, 1, 1, 20, 0, tzinfo=pytz.UTC)
    end = start + timedelta(minutes=3)
    obj = DummyObject("NGC 1499/California Nebula")

    def fake_altaz(_obj, current_time):
        minute_idx = int((current_time - start).total_seconds() // 60)
        return 45.0 + minute_idx, 320.0 + minute_idx

    monkeypatch.setattr("plots.trajectory.desktop.calculate_altaz", fake_altaz)
    monkeypatch.setattr("plots.trajectory.desktop.calculate_moon_position", lambda _t: (-10.0, 180.0))
    monkeypatch.setattr("plots.trajectory.desktop.calculate_sun_position", lambda _t: (-20.0, 180.0))
    monkeypatch.setattr("plots.trajectory.desktop.is_near_moon", lambda *_args, **_kwargs: False)
    monkeypatch.setattr("plots.trajectory.desktop.utc_to_local", lambda t: t)

    fig, ax = plt.subplots()
    try:
        plot_object_trajectory(ax, obj, start, end, color="#00AA00", use_margins=True)
        legend = ax.get_legend()
        assert legend is not None

        labels = [txt.get_text() for txt in legend.get_texts()]
        expected = get_abbreviated_name(obj.name)
        assert expected in labels
    finally:
        plt.close(fig)


def test_integration_threshold_filter_then_visibility_chart_labels(monkeypatch):
    """Integration: threshold filtering must drive chart contents and label naming consistently."""
    start = datetime(2026, 1, 1, 20, 0, tzinfo=pytz.UTC)
    end = start + timedelta(hours=4)

    short_obj = DummyObject("IC 1805")
    long_obj = DummyObject("NGC 1499/California Nebula")

    visibility_periods = {
        short_obj.name: [(start, start + timedelta(minutes=30))],
        long_obj.name: [(start, start + timedelta(hours=2))],
    }

    def fake_find_visibility_window(obj, *_args, **_kwargs):
        return visibility_periods.get(obj.name, [])

    monkeypatch.setattr("astronomy.visibility.find_visibility_window", fake_find_visibility_window)
    monkeypatch.setattr("astronomy.visibility.calculate_required_exposure", lambda *_args, **_kwargs: (0.1, 1, 1))
    monkeypatch.setattr("config.settings.VISIBILITY_LIST_THRESHOLD_HOURS", 1.0, raising=False)
    monkeypatch.setattr("config.settings.MIN_VISIBILITY_HOURS", 0.1, raising=False)

    filtered, insufficient = filter_visible_objects(
        [short_obj, long_obj],
        start,
        end,
        exclude_insufficient=False,
        use_margins=True,
    )

    assert short_obj not in filtered
    assert long_obj in filtered
    assert insufficient == []

    # Chart uses astronomy.find_visibility_window imported in desktop module.
    monkeypatch.setattr("plots.visibility.desktop.find_visibility_window", fake_find_visibility_window)
    monkeypatch.setattr("plots.visibility.desktop.get_local_timezone", lambda: pytz.UTC)

    fig, ax = plot_visibility_chart(filtered, start, end, use_margins=True)
    try:
        ylabels = [tick.get_text() for tick in ax.get_yticklabels()]
        expected_label = get_abbreviated_name(long_obj.name)

        assert expected_label in ylabels
        assert get_abbreviated_name(short_obj.name) not in ylabels
    finally:
        plt.close(fig)
