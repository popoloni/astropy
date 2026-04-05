"""Tests for wrap-around azimuth visibility logic."""

from datetime import datetime, timedelta

from astronomy.visibility import (
    calculate_visibility_duration,
    find_visibility_window,
)


class DummyObject:
    """Simple object container for visibility tests."""

    def __init__(self, name="Dummy"):
        self.name = name


def test_visibility_window_continuous_across_north_wrap(monkeypatch):
    """Visibility period should stay continuous while azimuth wraps from 359 to 0."""
    start_time = datetime(2026, 1, 10, 19, 0, 0)
    end_time = start_time + timedelta(minutes=6)

    az_values = [350, 355, 359, 1, 5, 10, 20]

    def fake_altaz(_obj, current_time):
        idx = int((current_time - start_time).total_seconds() // 60)
        return 50.0, az_values[idx]

    def fake_sun_position(_current_time):
        return -20.0, 180.0

    monkeypatch.setattr("astronomy.visibility.calculate_altaz", fake_altaz)
    monkeypatch.setattr("astronomy.visibility.calculate_sun_position", fake_sun_position)

    periods = find_visibility_window(DummyObject("IC 1805"), start_time, end_time, use_margins=True)

    assert len(periods) == 1
    assert periods[0][0] == start_time
    assert periods[0][1] == end_time

    duration_hours = calculate_visibility_duration(periods)
    assert abs(duration_hours - (6.0 / 60.0)) < 1e-6
