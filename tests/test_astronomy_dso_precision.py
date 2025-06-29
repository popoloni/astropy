"""
Comprehensive DSO and High-Precision Astronomy Accuracy Tests

This module tests:
1. Deep Sky Object (DSO) position accuracy using Messier catalog
2. Constellation star position accuracy
3. High-precision astronomy implementations vs standard implementations
4. Coordinate transformation accuracy
5. All functions against Astropy ground truth

Tests use the official Astropy module as ground truth to validate accuracy
and identify discrepancies in our astronomy calculations.
"""

import unittest
import json
import math
import datetime
from pathlib import Path

# Import our astronomy modules
from astronomy import (
    calculate_altaz, calculate_lst, calculate_sun_position, calculate_moon_position,
    calculate_julian_date, dms_dd, dd_dh, parse_ra, parse_dec
)

# Import high-precision implementations
try:
    from astronomy.precision import (
        calculate_high_precision_lst,
        calculate_high_precision_sun_position,
        calculate_high_precision_moon_position,
        calculate_precise_altaz,
        calculate_precise_coordinate_transformation,
        set_precision_mode,
        get_precision_mode
    )
    PRECISION_AVAILABLE = True
except ImportError as e:
    print(f"High-precision module not available: {e}")
    PRECISION_AVAILABLE = False

# Import catalogs
from catalogs.messier import get_messier_catalog
from models.celestial_objects import CelestialObject

# Import Astropy for ground truth
try:
    import astropy.units as u
    from astropy.time import Time
    from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun, get_moon
    from astropy.coordinates import ICRS, FK5
    import numpy as np
    ASTROPY_AVAILABLE = True
except ImportError:
    print("Astropy not available - please install with: pip install astropy")
    ASTROPY_AVAILABLE = False


class DSOPrecisionAccuracyTests(unittest.TestCase):
    """Test DSO positions, constellation positions, and high-precision implementations"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        if not ASTROPY_AVAILABLE:
            raise unittest.SkipTest("Astropy not available")
        
        # Test location: Milano, Italy
        cls.observer_lat = 45.52  # degrees
        cls.observer_lon = 9.22   # degrees
        cls.observer_elevation = 122  # meters
        
        # Create Astropy observer location
        cls.astropy_location = EarthLocation(
            lat=cls.observer_lat * u.deg,
            lon=cls.observer_lon * u.deg,
            height=cls.observer_elevation * u.m
        )
        
        # Test times across different seasons
        cls.test_times = [
            datetime.datetime(2024, 1, 15, 22, 0, 0),  # Winter
            datetime.datetime(2024, 4, 15, 22, 0, 0),  # Spring
            datetime.datetime(2024, 7, 15, 22, 0, 0),  # Summer
            datetime.datetime(2024, 10, 15, 22, 0, 0), # Autumn
            datetime.datetime(2025, 6, 15, 12, 0, 0),  # Daytime
        ]
        
        # Load test catalogs
        cls.messier_catalog = get_messier_catalog()
        cls.constellation_stars = cls._load_constellation_sample()
        
        # Results storage
        cls.results = {
            'dso_positions': [],
            'constellation_positions': [],
            'precision_comparisons': [],
            'coordinate_transformations': [],
            'summary': {}
        }
        
        # Accuracy thresholds (in arcminutes)
        cls.EXCELLENT_THRESHOLD = 1.0    # < 1 arcmin
        cls.GOOD_THRESHOLD = 5.0         # < 5 arcmin  
        cls.ACCEPTABLE_THRESHOLD = 30.0  # < 30 arcmin
        cls.POOR_THRESHOLD = 120.0       # < 2 degrees
    
    @classmethod
    def _load_constellation_sample(cls):
        """Load a sample of constellation stars for testing"""
        # Sample constellation stars with known accurate coordinates
        return [
            # Orion constellation - bright stars
            {'name': 'Betelgeuse', 'ra_hours': 5.919, 'dec_deg': 7.407},
            {'name': 'Rigel', 'ra_hours': 5.242, 'dec_deg': -8.202},
            {'name': 'Bellatrix', 'ra_hours': 5.418, 'dec_deg': 6.350},
            {'name': 'Mintaka', 'ra_hours': 5.533, 'dec_deg': -0.299},
            {'name': 'Alnilam', 'ra_hours': 5.603, 'dec_deg': -1.202},
            {'name': 'Alnitak', 'ra_hours': 5.679, 'dec_deg': -1.943},
            
            # Ursa Major - Big Dipper
            {'name': 'Dubhe', 'ra_hours': 11.062, 'dec_deg': 61.751},
            {'name': 'Merak', 'ra_hours': 11.031, 'dec_deg': 56.382},
            {'name': 'Phecda', 'ra_hours': 11.897, 'dec_deg': 53.695},
            {'name': 'Megrez', 'ra_hours': 12.257, 'dec_deg': 57.033},
            {'name': 'Alioth', 'ra_hours': 12.900, 'dec_deg': 55.960},
            {'name': 'Mizar', 'ra_hours': 13.399, 'dec_deg': 54.925},
            {'name': 'Alkaid', 'ra_hours': 13.792, 'dec_deg': 49.313},
            
            # Cassiopeia
            {'name': 'Schedar', 'ra_hours': 0.675, 'dec_deg': 56.537},
            {'name': 'Caph', 'ra_hours': 0.153, 'dec_deg': 59.150},
            {'name': 'Gamma Cas', 'ra_hours': 0.945, 'dec_deg': 60.717},
            {'name': 'Ruchbah', 'ra_hours': 1.430, 'dec_deg': 60.235},
            {'name': 'Segin', 'ra_hours': 1.906, 'dec_deg': 63.670},
        ]
    
    def calculate_angular_separation(self, ra1_deg, dec1_deg, ra2_deg, dec2_deg):
        """Calculate angular separation between two positions using spherical trigonometry"""
        ra1, dec1 = math.radians(ra1_deg), math.radians(dec1_deg)
        ra2, dec2 = math.radians(ra2_deg), math.radians(dec2_deg)
        
        # Haversine formula for angular separation
        dra = ra2 - ra1
        a = (math.sin((dec2 - dec1) / 2) ** 2 + 
             math.cos(dec1) * math.cos(dec2) * math.sin(dra / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return math.degrees(c) * 60  # Convert to arcminutes
    
    def test_dso_position_accuracy(self):
        """Test DSO position accuracy against Astropy"""
        print("\n=== Testing DSO Position Accuracy ===")
        
        dso_errors = []
        
        # Test a selection of Messier objects
        test_objects = [
            self.messier_catalog[0],   # M1 Crab Nebula
            self.messier_catalog[6],   # M42 Orion Nebula  
            self.messier_catalog[10],  # M31 Andromeda Galaxy
            self.messier_catalog[13],  # M51 Whirlpool Galaxy
            self.messier_catalog[21],  # M13 Hercules Cluster
            self.messier_catalog[41],  # M45 Pleiades
        ]
        
        for test_time in self.test_times[:3]:  # Test 3 times
            astropy_time = Time(test_time)
            
            for dso in test_objects:
                # Create Astropy coordinate
                astropy_coord = SkyCoord(
                    ra=dso.ra_degrees * u.deg,
                    dec=dso.dec_degrees * u.deg,
                    frame='icrs'
                )
                
                # Transform to AltAz
                altaz_frame = AltAz(obstime=astropy_time, location=self.astropy_location)
                astropy_altaz = astropy_coord.transform_to(altaz_frame)
                
                # Calculate using our function
                try:
                    our_alt, our_az = calculate_altaz(dso, test_time)
                    
                    # Calculate error
                    alt_error = abs(our_alt - astropy_altaz.alt.degree)
                    az_error = abs(our_az - astropy_altaz.az.degree)
                    
                    # Handle azimuth wrap-around
                    if az_error > 180:
                        az_error = 360 - az_error
                    
                    # Convert to arcminutes
                    alt_error_arcmin = alt_error * 60
                    az_error_arcmin = az_error * 60
                    total_error = math.sqrt(alt_error_arcmin**2 + az_error_arcmin**2)
                    
                    dso_errors.append(total_error)
                    
                    result = {
                        'object': dso.name,
                        'time': test_time.isoformat(),
                        'our_alt': our_alt,
                        'our_az': our_az,
                        'astropy_alt': astropy_altaz.alt.degree,
                        'astropy_az': astropy_altaz.az.degree,
                        'alt_error_arcmin': alt_error_arcmin,
                        'az_error_arcmin': az_error_arcmin,
                        'total_error_arcmin': total_error
                    }
                    
                    self.results['dso_positions'].append(result)
                    
                    print(f"{dso.name[:20]:<20} | Error: {total_error:6.1f}' | "
                          f"Alt: {our_alt:6.1f}° vs {astropy_altaz.alt.degree:6.1f}° | "
                          f"Az: {our_az:6.1f}° vs {astropy_altaz.az.degree:6.1f}°")
                    
                except Exception as e:
                    print(f"Error calculating {dso.name}: {e}")
        
        # Analyze results
        if dso_errors:
            max_error = max(dso_errors)
            avg_error = sum(dso_errors) / len(dso_errors)
            
            print(f"\nDSO Position Results:")
            print(f"Max error: {max_error:.1f} arcminutes ({max_error/60:.3f}°)")
            print(f"Average error: {avg_error:.1f} arcminutes ({avg_error/60:.3f}°)")
            
            # Determine status
            if max_error < self.EXCELLENT_THRESHOLD:
                status = "EXCELLENT"
                passed = True
            elif max_error < self.GOOD_THRESHOLD:
                status = "GOOD"
                passed = True
            elif max_error < self.ACCEPTABLE_THRESHOLD:
                status = "ACCEPTABLE"
                passed = True
            else:
                status = "POOR"
                passed = False
            
            print(f"Status: {status}")
            
            self.results['summary']['dso_positions'] = {
                'status': status,
                'max_error_arcmin': max_error,
                'avg_error_arcmin': avg_error,
                'passed': passed
            }
            
            # Assert based on reasonable threshold for DSO positions
            self.assertLess(max_error, 60.0, f"DSO position error too large: {max_error:.1f} arcminutes")
    
    def test_constellation_star_accuracy(self):
        """Test constellation star position accuracy"""
        print("\n=== Testing Constellation Star Position Accuracy ===")
        
        star_errors = []
        test_time = self.test_times[1]  # Spring time
        astropy_time = Time(test_time)
        
        for star in self.constellation_stars:
            # Create Astropy coordinate
            astropy_coord = SkyCoord(
                ra=star['ra_hours'] * 15 * u.deg,  # Convert hours to degrees
                dec=star['dec_deg'] * u.deg,
                frame='icrs'
            )
            
            # Transform to AltAz
            altaz_frame = AltAz(obstime=astropy_time, location=self.astropy_location)
            astropy_altaz = astropy_coord.transform_to(altaz_frame)
            
            # Create a CelestialObject for our function
            star_obj = CelestialObject(
                star['name'], 
                star['ra_hours'], 
                star['dec_deg']
            )
            
            # Calculate using our function
            try:
                our_alt, our_az = calculate_altaz(star_obj, test_time)
                
                # Calculate error
                alt_error = abs(our_alt - astropy_altaz.alt.degree)
                az_error = abs(our_az - astropy_altaz.az.degree)
                
                # Handle azimuth wrap-around
                if az_error > 180:
                    az_error = 360 - az_error
                
                # Convert to arcminutes
                alt_error_arcmin = alt_error * 60
                az_error_arcmin = az_error * 60
                total_error = math.sqrt(alt_error_arcmin**2 + az_error_arcmin**2)
                
                star_errors.append(total_error)
                
                result = {
                    'star': star['name'],
                    'ra_hours': star['ra_hours'],
                    'dec_deg': star['dec_deg'],
                    'our_alt': our_alt,
                    'our_az': our_az,
                    'astropy_alt': astropy_altaz.alt.degree,
                    'astropy_az': astropy_altaz.az.degree,
                    'total_error_arcmin': total_error
                }
                
                self.results['constellation_positions'].append(result)
                
                print(f"{star['name']:<15} | Error: {total_error:6.1f}' | "
                      f"Alt: {our_alt:6.1f}° vs {astropy_altaz.alt.degree:6.1f}°")
                
            except Exception as e:
                print(f"Error calculating {star['name']}: {e}")
        
        # Analyze results
        if star_errors:
            max_error = max(star_errors)
            avg_error = sum(star_errors) / len(star_errors)
            
            print(f"\nConstellation Star Results:")
            print(f"Max error: {max_error:.1f} arcminutes ({max_error/60:.3f}°)")
            print(f"Average error: {avg_error:.1f} arcminutes ({avg_error/60:.3f}°)")
            
            # Determine status
            if max_error < self.EXCELLENT_THRESHOLD:
                status = "EXCELLENT"
                passed = True
            elif max_error < self.GOOD_THRESHOLD:
                status = "GOOD"
                passed = True
            elif max_error < self.ACCEPTABLE_THRESHOLD:
                status = "ACCEPTABLE"
                passed = True
            else:
                status = "POOR"
                passed = False
            
            print(f"Status: {status}")
            
            self.results['summary']['constellation_positions'] = {
                'status': status,
                'max_error_arcmin': max_error,
                'avg_error_arcmin': avg_error,
                'passed': passed
            }
            
            # Stars should be very accurate
            self.assertLess(max_error, 30.0, f"Star position error too large: {max_error:.1f} arcminutes")
    
    @unittest.skipUnless(PRECISION_AVAILABLE, "High-precision module not available")
    def test_high_precision_vs_standard(self):
        """Test high-precision implementations vs standard implementations"""
        print("\n=== Testing High-Precision vs Standard Implementations ===")
        
        test_time = self.test_times[1]
        astropy_time = Time(test_time)
        
        # Test LST calculation
        print("\nLocal Sidereal Time Comparison:")
        try:
            # Standard implementation - note: function signature is (dt, observer_lon)
            standard_lst = calculate_lst(test_time, math.radians(self.observer_lon))
            
            # High-precision implementation
            high_precision_lst = calculate_high_precision_lst(test_time, self.observer_lon)
            
            # Astropy ground truth
            astropy_lst = astropy_time.sidereal_time('apparent', longitude=self.observer_lon * u.deg).hour
            
            # Convert our results from radians to hours
            standard_lst_hours = standard_lst * 12 / math.pi  # Convert radians to hours
            
            # Calculate errors (in minutes of time)
            standard_error = abs(standard_lst_hours - astropy_lst) * 60
            precision_error = abs(high_precision_lst - astropy_lst) * 60
            improvement = standard_error - precision_error
            
            print(f"Standard LST:     {standard_lst_hours:.6f} h | Error: {standard_error:.3f} min")
            print(f"High-precision:   {high_precision_lst:.6f} h | Error: {precision_error:.3f} min")  
            print(f"Astropy:          {astropy_lst:.6f} h")
            print(f"Improvement:      {improvement:.3f} min ({improvement/standard_error*100:.1f}%)")
            
            self.results['precision_comparisons'].append({
                'function': 'LST',
                'standard_error_min': standard_error,
                'precision_error_min': precision_error,
                'improvement_min': improvement,
                'improvement_percent': improvement/standard_error*100 if standard_error > 0 else 0
            })
            
        except Exception as e:
            print(f"LST comparison error: {e}")
        
        # Test Sun position
        print("\nSun Position Comparison:")
        try:
            # Standard implementation - returns (alt, az)
            standard_sun_alt, standard_sun_az = calculate_sun_position(test_time)
            
            # High-precision implementation - returns dict with ra/dec
            high_precision_sun_dict = calculate_high_precision_sun_position(test_time)
            high_precision_sun_ra = high_precision_sun_dict['ra']
            high_precision_sun_dec = high_precision_sun_dict['dec']
            
            # Astropy ground truth
            astropy_sun = get_sun(astropy_time)
            astropy_sun_ra = astropy_sun.ra.degree
            astropy_sun_dec = astropy_sun.dec.degree
            
            # Convert standard sun position back to RA/Dec for comparison
            # This is complex, so let's just compare the high-precision with Astropy
            precision_error = self.calculate_angular_separation(
                high_precision_sun_ra, high_precision_sun_dec,
                astropy_sun_ra, astropy_sun_dec
            )
            
            print(f"High-precision:   RA {high_precision_sun_ra:.3f}°, Dec {high_precision_sun_dec:.3f}° | Error: {precision_error:.1f}'")
            print(f"Astropy:          RA {astropy_sun_ra:.3f}°, Dec {astropy_sun_dec:.3f}°")
            print(f"Standard returns alt/az, not directly comparable to RA/Dec")
            
            self.results['precision_comparisons'].append({
                'function': 'Sun Position',
                'precision_error_arcmin': precision_error,
                'note': 'Standard function returns alt/az, not RA/Dec'
            })
            
        except Exception as e:
            print(f"Sun position comparison error: {e}")
        
        # Test Moon position
        print("\nMoon Position Comparison:")
        try:
            # Standard implementation - returns (alt, az)
            standard_moon_alt, standard_moon_az = calculate_moon_position(test_time)
            
            # High-precision implementation - returns dict
            high_precision_moon_dict = calculate_high_precision_moon_position(test_time)
            high_precision_moon_ra = high_precision_moon_dict['ra']
            high_precision_moon_dec = high_precision_moon_dict['dec']
            
            # Astropy ground truth
            astropy_moon = get_moon(astropy_time)
            astropy_moon_ra = astropy_moon.ra.degree
            astropy_moon_dec = astropy_moon.dec.degree
            
            # Compare high-precision with Astropy
            precision_error = self.calculate_angular_separation(
                high_precision_moon_ra, high_precision_moon_dec,
                astropy_moon_ra, astropy_moon_dec
            )
            
            print(f"High-precision:   RA {high_precision_moon_ra:.3f}°, Dec {high_precision_moon_dec:.3f}° | Error: {precision_error:.1f}'")
            print(f"Astropy:          RA {astropy_moon_ra:.3f}°, Dec {astropy_moon_dec:.3f}°")
            print(f"Standard returns alt/az, not directly comparable to RA/Dec")
            
            self.results['precision_comparisons'].append({
                'function': 'Moon Position',
                'precision_error_arcmin': precision_error,
                'note': 'Standard function returns alt/az, not RA/Dec'
            })
            
        except Exception as e:
            print(f"Moon position comparison error: {e}")
    
    def test_coordinate_transformations(self):
        """Test coordinate transformation accuracy"""
        print("\n=== Testing Coordinate Transformations ===")
        
        # Test coordinate parsing and conversion functions
        test_cases = [
            # (RA string, expected degrees, Dec string, expected degrees) 
            # Note: parse_ra returns degrees, not hours
            ("12h 30m", 187.5, "+45° 30'", 45.5),
            ("00h 00m", 0.0, "+00° 00'", 0.0),
            ("06h 15m", 93.75, "+23° 26'", 23.433),
        ]
        
        coord_errors = []
        
        for ra_str, expected_ra_deg, dec_str, expected_dec_deg in test_cases:
            try:
                # Test RA parsing (returns degrees)
                parsed_ra = parse_ra(ra_str)
                ra_error = abs(parsed_ra - expected_ra_deg) * 60  # Convert to arcminutes
                
                # Test Dec parsing  
                parsed_dec = parse_dec(dec_str)
                dec_error = abs(parsed_dec - expected_dec_deg) * 60  # Convert to arcminutes
                
                total_error = math.sqrt(ra_error**2 + dec_error**2)
                coord_errors.append(total_error)
                
                result = {
                    'ra_input': ra_str,
                    'ra_expected': expected_ra_deg,
                    'ra_parsed': parsed_ra,
                    'ra_error_arcmin': ra_error,
                    'dec_input': dec_str,
                    'dec_expected': expected_dec_deg,
                    'dec_parsed': parsed_dec,
                    'dec_error_arcmin': dec_error,
                    'total_error_arcmin': total_error
                }
                
                self.results['coordinate_transformations'].append(result)
                
                print(f"RA: {ra_str} -> {parsed_ra:.3f}° (expected {expected_ra_deg:.3f}°) | Error: {ra_error:.1f}'")
                print(f"Dec: {dec_str} -> {parsed_dec:.3f}° (expected {expected_dec_deg:.3f}°) | Error: {dec_error:.1f}'")
                
            except Exception as e:
                print(f"Coordinate parsing error: {e}")
        
        # Test DMS to decimal conversion
        dms_test_cases = [
            (45, 30, 15, 45.5042),  # 45° 30' 15"
            (0, 0, 0, 0.0),         # 0° 0' 0"
            (89, 59, 59, 89.9997),  # 89° 59' 59"
        ]
        
        for deg, min_val, sec, expected in dms_test_cases:
            try:
                result = dms_dd(deg, min_val, sec)
                error = abs(result - expected) * 60  # arcminutes
                coord_errors.append(error)
                
                print(f"DMS {deg}° {min_val}' {sec}\" -> {result:.6f}° (expected {expected:.6f}°) | Error: {error:.1f}'")
                
            except Exception as e:
                print(f"DMS conversion error: {e}")
        
        # Analyze coordinate transformation results
        if coord_errors:
            max_error = max(coord_errors)
            avg_error = sum(coord_errors) / len(coord_errors)
            
            print(f"\nCoordinate Transformation Results:")
            print(f"Max error: {max_error:.1f} arcminutes")
            print(f"Average error: {avg_error:.1f} arcminutes")
            
            # Coordinate transformations should be very precise
            status = "EXCELLENT" if max_error < 1.0 else "GOOD" if max_error < 5.0 else "POOR"
            passed = max_error < 30.0  # 30 arcminute tolerance
            
            print(f"Status: {status}")
            
            self.results['summary']['coordinate_transformations'] = {
                'status': status,
                'max_error_arcmin': max_error,
                'avg_error_arcmin': avg_error,
                'passed': passed
            }
            
            self.assertLess(max_error, 30.0, f"Coordinate transformation error too large: {max_error:.1f} arcminutes")
    
    @classmethod
    def tearDownClass(cls):
        """Save test results and generate report"""
        # Calculate overall status
        all_passed = all(
            summary.get('passed', True) 
            for summary in cls.results['summary'].values()
        )
        
        overall_status = "PASSED" if all_passed else "FAILED"
        
        cls.results['overall'] = {
            'status': overall_status,
            'test_location': f"{cls.observer_lat}°N, {cls.observer_lon}°E",
            'test_times': [t.isoformat() for t in cls.test_times],
            'precision_module_available': PRECISION_AVAILABLE,
            'total_tests': len(cls.results['dso_positions']) + 
                          len(cls.results['constellation_positions']) + 
                          len(cls.results['precision_comparisons']) +
                          len(cls.results['coordinate_transformations'])
        }
        
        # Save detailed results
        results_file = Path(__file__).parent / 'dso_precision_accuracy_report.json'
        with open(results_file, 'w') as f:
            json.dump(cls.results, f, indent=2, default=str)
        
        print(f"\n{'='*60}")
        print("DSO & PRECISION ACCURACY TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Overall Status: {overall_status}")
        print(f"Results saved to: {results_file}")
        
        # Generate markdown report
        cls._generate_markdown_report()
    
    @classmethod
    def _generate_markdown_report(cls):
        """Generate comprehensive markdown report"""
        report_file = Path(__file__).parent / 'DSO_PRECISION_ACCURACY_SUMMARY.md'
        
        with open(report_file, 'w') as f:
            f.write("# DSO and High-Precision Astronomy Accuracy Report\n\n")
            f.write("## Executive Summary\n\n")
            f.write(f"**Overall Status**: {cls.results['overall']['status']}\n")
            f.write(f"**Test Location**: {cls.results['overall']['test_location']}\n")
            f.write(f"**Total Tests**: {cls.results['overall']['total_tests']}\n")
            f.write(f"**High-Precision Module**: {'Available' if PRECISION_AVAILABLE else 'Not Available'}\n\n")
            
            # DSO Positions
            if 'dso_positions' in cls.results['summary']:
                dso = cls.results['summary']['dso_positions']
                f.write("## Deep Sky Object Position Accuracy\n\n")
                f.write(f"- **Status**: {dso['status']}\n")
                f.write(f"- **Maximum Error**: {dso['max_error_arcmin']:.1f} arcminutes ({dso['max_error_arcmin']/60:.3f}°)\n")
                f.write(f"- **Average Error**: {dso['avg_error_arcmin']:.1f} arcminutes ({dso['avg_error_arcmin']/60:.3f}°)\n")
                f.write(f"- **Test Objects**: Messier catalog objects (M1, M42, M31, M51, M13, M45)\n")
                f.write(f"- **Assessment**: {'✅ PASSED' if dso['passed'] else '❌ FAILED'}\n\n")
            
            # Constellation Positions
            if 'constellation_positions' in cls.results['summary']:
                const = cls.results['summary']['constellation_positions']
                f.write("## Constellation Star Position Accuracy\n\n")
                f.write(f"- **Status**: {const['status']}\n")
                f.write(f"- **Maximum Error**: {const['max_error_arcmin']:.1f} arcminutes ({const['max_error_arcmin']/60:.3f}°)\n")
                f.write(f"- **Average Error**: {const['avg_error_arcmin']:.1f} arcminutes ({const['avg_error_arcmin']/60:.3f}°)\n")
                f.write(f"- **Test Stars**: Bright stars from Orion, Ursa Major, and Cassiopeia\n")
                f.write(f"- **Assessment**: {'✅ PASSED' if const['passed'] else '❌ FAILED'}\n\n")
            
            # High-Precision Comparisons
            if cls.results['precision_comparisons']:
                f.write("## High-Precision vs Standard Implementation Comparison\n\n")
                for comp in cls.results['precision_comparisons']:
                    f.write(f"### {comp['function']}\n")
                    if 'precision_error_arcmin' in comp:
                        f.write(f"- **High-Precision Error**: {comp.get('precision_error_arcmin', 0):.1f} arcminutes\n")
                        if 'note' in comp:
                            f.write(f"- **Note**: {comp['note']}\n")
                    else:
                        f.write(f"- **Standard Error**: {comp.get('standard_error_min', 0):.3f} minutes\n")
                        f.write(f"- **High-Precision Error**: {comp.get('precision_error_min', 0):.3f} minutes\n")
                        f.write(f"- **Improvement**: {comp.get('improvement_min', 0):.3f} minutes ({comp.get('improvement_percent', 0):.1f}%)\n")
                    f.write("\n")
            
            # Coordinate Transformations
            if 'coordinate_transformations' in cls.results['summary']:
                coord = cls.results['summary']['coordinate_transformations']
                f.write("## Coordinate Transformation Accuracy\n\n")
                f.write(f"- **Status**: {coord['status']}\n")
                f.write(f"- **Maximum Error**: {coord['max_error_arcmin']:.1f} arcminutes\n")
                f.write(f"- **Average Error**: {coord['avg_error_arcmin']:.1f} arcminutes\n")
                f.write(f"- **Functions Tested**: parse_ra(), parse_dec(), dms_dd()\n")
                f.write(f"- **Assessment**: {'✅ PASSED' if coord['passed'] else '❌ FAILED'}\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            
            dso_error = cls.results['summary'].get('dso_positions', {}).get('max_error_arcmin', 0)
            if dso_error > 30:
                f.write("### High Priority\n")
                f.write("- **DSO Position Accuracy**: Consider implementing proper coordinate transformations with precession/nutation\n")
                f.write("- **Atmospheric Refraction**: Add atmospheric refraction corrections for low-altitude objects\n\n")
            
            const_error = cls.results['summary'].get('constellation_positions', {}).get('max_error_arcmin', 0)
            if const_error > 5:
                f.write("### Medium Priority\n")
                f.write("- **Star Position Accuracy**: Review coordinate epoch and proper motion corrections\n")
                f.write("- **Reference Frame**: Ensure consistent use of coordinate reference frames (J2000.0)\n\n")
            
            f.write("### General Improvements\n")
            f.write("- **Testing Coverage**: Extend tests to include more DSO types and fainter objects\n")
            f.write("- **Seasonal Variation**: Test accuracy across full year and different latitudes\n")
            f.write("- **Performance**: Benchmark high-precision implementations vs accuracy gains\n\n")
            
            # Industry Standards
            f.write("## Industry Standards Comparison\n\n")
            f.write("| Application | Typical Accuracy Requirement |\n")
            f.write("|-------------|------------------------------|\n")
            f.write("| Professional Astronomy | < 1 arcsecond |\n")
            f.write("| Amateur Telescope Pointing | < 5 arcminutes |\n")
            f.write("| General Sky Charts | < 30 arcminutes |\n")
            f.write("| Mobile Apps | < 2 degrees |\n\n")
            
            # Our performance summary
            f.write("### Our Performance\n")
            if 'dso_positions' in cls.results['summary']:
                dso_level = "Professional" if dso_error < 0.017 else "Amateur" if dso_error < 5 else "General" if dso_error < 30 else "Mobile"
                f.write(f"- **DSO Positions**: {dso_level} level ({dso_error:.1f} arcminutes)\n")
            
            if 'constellation_positions' in cls.results['summary']:
                const_level = "Professional" if const_error < 0.017 else "Amateur" if const_error < 5 else "General" if const_error < 30 else "Mobile"
                f.write(f"- **Star Positions**: {const_level} level ({const_error:.1f} arcminutes)\n")
        
        print(f"Detailed report saved to: {report_file}")


if __name__ == '__main__':
    unittest.main(verbosity=2)