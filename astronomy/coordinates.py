"""
Coordinate conversion and parsing functions for astronomical calculations.
"""

import math
import re


def dms_dd(degrees, minutes, seconds):
    """Convert Degrees Minutes Seconds to Decimal Degrees"""
    A = abs(seconds) / 60
    B = (abs(minutes) + A) / 60
    C = abs(degrees) + B
    return -C if degrees < 0 or minutes < 0 or seconds < 0 else C


def dd_dh(decimal_degrees):
    """Convert Decimal Degrees to Degree-Hours"""
    return decimal_degrees / 15


def dh_dd(degree_hours):
    """Convert Degree-Hours to Decimal Degrees"""
    return degree_hours * 15


def hms_dh(hours, minutes, seconds):
    """Convert Hours Minutes Seconds to Decimal Hours"""
    A = abs(seconds) / 60
    B = (abs(minutes) + A) / 60
    C = abs(hours) + B
    return -C if hours < 0 or minutes < 0 or seconds < 0 else C


def dh_hour(decimal_hours):
    """Return hour part of Decimal Hours"""
    A = abs(decimal_hours)
    B = A * 3600
    C = round(B - 60 * math.floor(B / 60), 2)
    D = 0 if C == 60 else C
    E = B + 60 if C == 60 else B
    return -(math.floor(E / 3600)) if decimal_hours < 0 else math.floor(E / 3600)


def dh_min(decimal_hours):
    """Return minutes part of Decimal Hours"""
    A = abs(decimal_hours)
    B = A * 3600
    C = round(B - 60 * math.floor(B / 60), 2)
    D = 0 if C == 60 else C
    E = B + 60 if C == 60 else B
    return math.floor(E / 60) % 60


def dh_sec(decimal_hours):
    """Return seconds part of Decimal Hours"""
    A = abs(decimal_hours)
    B = A * 3600
    C = round(B - 60 * math.floor(B / 60), 2)
    return 0 if C == 60 else C


def parse_ra(ra_str):
    """Convert RA from HH:MM format to decimal degrees"""
    match = re.match(r'(\d+)h\s*(\d+)m', ra_str)
    if match:
        hours = float(match.group(1))
        minutes = float(match.group(2))
        return (hours + minutes/60) * 15
    return 0


def parse_dec(dec_str):
    """Convert Dec from DD:MM format to decimal degrees"""
    match = re.match(r'([+-]?\d+)°?\s*(\d+)?\'?', dec_str)
    if match:
        degrees = float(match.group(1))
        minutes = float(match.group(2)) if match.group(2) else 0
        return degrees + minutes/60 * (1 if degrees >= 0 else -1)
    match = re.match(r'([+-]?\d+)°?', dec_str)
    if match:
        return float(match.group(1))
    return 0


def parse_fov(fov_str):
    """Parse FOV string and return list of areas in square arcminutes"""
    if not fov_str:
        return []
    
    fov_list = fov_str.split(',')
    areas = []
    
    for fov in fov_list:
        fov = fov.strip()
        match = re.match(r'([\d.]+)(?:°|\')?x([\d.]+)(?:°|\')?', fov)
        if match:
            width = float(match.group(1))
            height = float(match.group(2))
            
            if '°' in fov:
                width *= 60
                height *= 60
                
            areas.append(width * height)
    
    return areas


def calculate_total_area(fov_str):
    """Calculate total area from FOV string"""
    areas = parse_fov(fov_str)
    return sum(areas) if areas else 0 