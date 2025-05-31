"""
Time and timezone utility functions for astronomical calculations.
"""

import pytz
from datetime import timedelta
import math


def get_local_timezone():
    """Get configured timezone"""
    return pytz.timezone('Europe/Rome')


def local_to_utc(local_time):
    """Convert local time to UTC"""
    milan_tz = get_local_timezone()
    if local_time.tzinfo is None:
        local_time = milan_tz.localize(local_time)
    return local_time.astimezone(pytz.UTC)


def utc_to_local(utc_time):
    """Convert UTC time to local time"""
    milan_tz = get_local_timezone()
    if utc_time.tzinfo is None:
        utc_time = pytz.UTC.localize(utc_time)
    return utc_time.astimezone(milan_tz)


def calculate_julian_date(dt):
    """Calculate Julian Date from datetime (UTC)"""
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
        
    year, month, day = dt.year, dt.month, dt.day
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + (a // 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5
    jd += (dt.hour + dt.minute/60 + dt.second/3600)/24.0
    return jd


def format_time(time):
    """Format time for display"""
    return time.strftime("%H:%M") 