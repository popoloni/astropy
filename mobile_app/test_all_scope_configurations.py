#!/usr/bin/env python3
"""
Comprehensive Smart Scope Configuration Testing Script
Tests all scope types, configurations, and integration scenarios
"""

import sys
import os
import json
from typing import Dict, List, Tuple, Any
from dataclasses import asdict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all smart scope modules
from mobile_app.utils.smart_scopes import (
    ScopeSpecifications, SmartScopeManager, ScopeType,
    get_scope_manager, get_all_scope_names, get_selected_scope,
    set_selected_scope, calculate_target_fov_compatibility
)
from mobile_app.utils.advanced_filter import AdvancedFilter


class ScopeConfigurationTester:
    """Comprehensive tester for all scope configurations"""
    
    def __init__(self):
        self.manager = get_scope_manager()
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
    def log_result(self, test_name: str, passed: bool, message: str = "", details: Any = None):
        """Log test result"""
        if passed:
            self.test_results['passed'] += 1
            status = "✅ PASS"
        else:
            self.test_results['failed'] += 1
            status = "❌ FAIL"
            self.test_results['errors'].append(f"{test_name}: {message}")
        
        self.test_results['details'][test_name] = {
            'status': status,
            'message': message,
            'details': details
        }
        
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        if details and isinstance(details, dict):
            for key, value in details.items():
                print(f"    {key}: {value}")
        print()
    
    def test_scope_database_integrity(self):
        """Test 1: Verify all scopes are properly loaded with complete data"""
        print("=" * 60)
        print("TEST 1: SCOPE DATABASE INTEGRITY")
        print("=" * 60)
        
        scopes = self.manager.get_all_scopes()
        
        # Test scope count
        expected_scopes = 8  # 4 Vaonis + 2 ZWO + 2 DwarfLab
        actual_count = len(scopes)
        self.log_result(
            "Scope Count",
            actual_count == expected_scopes,
            f"Expected {expected_scopes}, got {actual_count}",
            {'expected': expected_scopes, 'actual': actual_count}
        )
        
        # Test each scope for required fields
        required_fields = [
            'name', 'manufacturer', 'scope_type', 'aperture_mm', 'focal_length_mm',
            'focal_ratio', 'sensor_model', 'sensor_type', 'resolution_mp',
            'pixel_size_um', 'sensor_size_mm', 'native_fov_deg'
        ]
        
        for scope_id, scope in scopes.items():
            missing_fields = []
            for field in required_fields:
                if not hasattr(scope, field) or getattr(scope, field) is None:
                    missing_fields.append(field)
            
            self.log_result(
                f"Scope Completeness: {scope.name}",
                len(missing_fields) == 0,
                f"Missing fields: {missing_fields}" if missing_fields else "All fields present",
                {'scope_id': scope_id, 'missing_fields': missing_fields}
            )
    
    def test_manufacturer_coverage(self):
        """Test 2: Verify all requested manufacturers are represented"""
        print("=" * 60)
        print("TEST 2: MANUFACTURER COVERAGE")
        print("=" * 60)
        
        expected_manufacturers = ["Vaonis", "ZWO", "DwarfLab"]
        scopes = self.manager.get_all_scopes()
        
        for manufacturer in expected_manufacturers:
            manufacturer_scopes = self.manager.get_scopes_by_manufacturer(manufacturer)
            scope_count = len(manufacturer_scopes)
            
            # Expected counts per manufacturer
            expected_counts = {"Vaonis": 4, "ZWO": 2, "DwarfLab": 2}
            expected_count = expected_counts.get(manufacturer, 0)
            
            self.log_result(
                f"Manufacturer Coverage: {manufacturer}",
                scope_count == expected_count,
                f"Expected {expected_count} scopes, found {scope_count}",
                {
                    'manufacturer': manufacturer,
                    'expected': expected_count,
                    'actual': scope_count,
                    'scopes': [scope.name for scope in manufacturer_scopes.values()]
                }
            )
    
    def test_scope_type_coverage(self):
        """Test 3: Verify all scope types are properly categorized"""
        print("=" * 60)
        print("TEST 3: SCOPE TYPE COVERAGE")
        print("=" * 60)
        
        for scope_type in ScopeType:
            type_scopes = self.manager.get_scopes_by_type(scope_type)
            scope_count = len(type_scopes)
            
            # Expected counts per type
            expected_counts = {
                ScopeType.VAONIS: 4,
                ScopeType.ZWO: 2,
                ScopeType.DWARFLAB: 2
            }
            expected_count = expected_counts.get(scope_type, 0)
            
            self.log_result(
                f"Scope Type: {scope_type.value}",
                scope_count == expected_count,
                f"Expected {expected_count} scopes, found {scope_count}",
                {
                    'type': scope_type.value,
                    'expected': expected_count,
                    'actual': scope_count,
                    'scopes': [scope.name for scope in type_scopes.values()]
                }
            )
    
    def test_default_scope_configuration(self):
        """Test 4: Verify default scope is Vespera Passenger"""
        print("=" * 60)
        print("TEST 4: DEFAULT SCOPE CONFIGURATION")
        print("=" * 60)
        
        default_scope = self.manager.get_selected_scope()
        
        self.log_result(
            "Default Scope Name",
            default_scope.name == "Vespera Passenger",
            f"Expected 'Vespera Passenger', got '{default_scope.name}'",
            {'expected': 'Vespera Passenger', 'actual': default_scope.name}
        )
        
        self.log_result(
            "Default Scope Manufacturer",
            default_scope.manufacturer == "Vaonis",
            f"Expected 'Vaonis', got '{default_scope.manufacturer}'",
            {'expected': 'Vaonis', 'actual': default_scope.manufacturer}
        )
        
        self.log_result(
            "Default Scope Flag",
            default_scope.is_default == True,
            f"Expected True, got {default_scope.is_default}",
            {'expected': True, 'actual': default_scope.is_default}
        )
    
    def test_scope_selection_switching(self):
        """Test 5: Test switching between all scope configurations"""
        print("=" * 60)
        print("TEST 5: SCOPE SELECTION SWITCHING")
        print("=" * 60)
        
        scopes = self.manager.get_all_scopes()
        original_scope = self.manager.get_selected_scope()
        
        for scope_id, scope in scopes.items():
            # Test setting scope
            success = set_selected_scope(scope_id)
            self.log_result(
                f"Set Scope: {scope.name}",
                success == True,
                f"Failed to set scope {scope_id}" if not success else "Successfully set",
                {'scope_id': scope_id, 'scope_name': scope.name}
            )
            
            # Test retrieving set scope
            if success:
                current_scope = get_selected_scope()
                self.log_result(
                    f"Retrieve Scope: {scope.name}",
                    current_scope.name == scope.name,
                    f"Expected '{scope.name}', got '{current_scope.name}'",
                    {'expected': scope.name, 'actual': current_scope.name}
                )
        
        # Restore original scope
        set_selected_scope("vespera_passenger")
    
    def test_fov_calculations(self):
        """Test 6: Test FOV calculations for all scopes"""
        print("=" * 60)
        print("TEST 6: FOV CALCULATIONS")
        print("=" * 60)
        
        scopes = self.manager.get_all_scopes()
        
        for scope_id, scope in scopes.items():
            # Test native FOV
            fov_width, fov_height = scope.native_fov_deg
            
            self.log_result(
                f"Native FOV Valid: {scope.name}",
                fov_width > 0 and fov_height > 0,
                f"FOV: {fov_width:.2f}° × {fov_height:.2f}°",
                {
                    'scope': scope.name,
                    'fov_width': fov_width,
                    'fov_height': fov_height,
                    'aperture': scope.aperture_mm,
                    'focal_length': scope.focal_length_mm
                }
            )
            
            # Test mosaic FOV if available
            if scope.has_mosaic_mode and scope.mosaic_fov_deg:
                mosaic_width, mosaic_height = scope.mosaic_fov_deg
                
                self.log_result(
                    f"Mosaic FOV Valid: {scope.name}",
                    mosaic_width > fov_width and mosaic_height > fov_height,
                    f"Mosaic FOV: {mosaic_width:.2f}° × {mosaic_height:.2f}°",
                    {
                        'scope': scope.name,
                        'native_fov': f"{fov_width:.2f}° × {fov_height:.2f}°",
                        'mosaic_fov': f"{mosaic_width:.2f}° × {mosaic_height:.2f}°"
                    }
                )
    
    def test_target_compatibility_matrix(self):
        """Test 7: Test target compatibility across all scopes"""
        print("=" * 60)
        print("TEST 7: TARGET COMPATIBILITY MATRIX")
        print("=" * 60)
        
        # Test targets of various sizes (in arcminutes)
        test_targets = [
            ('Small Target', 10),      # 10 arcmin
            ('Medium Target', 60),     # 1 degree
            ('Large Target', 180),     # 3 degrees
            ('Very Large Target', 300) # 5 degrees
        ]
        
        scopes = self.manager.get_all_scopes()
        
        for target_name, target_size in test_targets:
            compatibility = self.manager.calculate_fov_for_target(target_size)
            
            compatible_count = sum(1 for is_compatible in compatibility.values() if is_compatible)
            total_scopes = len(scopes)
            
            self.log_result(
                f"Target Compatibility: {target_name} ({target_size}')",
                compatible_count > 0,  # At least one scope should be compatible
                f"{compatible_count}/{total_scopes} scopes compatible",
                {
                    'target_size_arcmin': target_size,
                    'compatible_scopes': [
                        scope_id for scope_id, is_compatible in compatibility.items() 
                        if is_compatible
                    ],
                    'compatibility_ratio': f"{compatible_count}/{total_scopes}"
                }
            )
    
    def test_scope_recommendations(self):
        """Test 8: Test scope recommendation system"""
        print("=" * 60)
        print("TEST 8: SCOPE RECOMMENDATION SYSTEM")
        print("=" * 60)
        
        test_targets = [30, 60, 120, 300]  # Various target sizes in arcminutes
        
        for target_size in test_targets:
            recommendations = self.manager.get_optimal_scopes_for_target(target_size)
            
            self.log_result(
                f"Recommendations for {target_size}' target",
                len(recommendations) > 0,
                f"Got {len(recommendations)} recommendations",
                {
                    'target_size_arcmin': target_size,
                    'recommendation_count': len(recommendations),
                    'top_recommendations': recommendations[:3] if recommendations else []
                }
            )
    
    def test_advanced_filter_integration(self):
        """Test 9: Test integration with advanced filter system"""
        print("=" * 60)
        print("TEST 9: ADVANCED FILTER INTEGRATION")
        print("=" * 60)
        
        filter_system = AdvancedFilter()
        scopes = self.manager.get_all_scopes()
        
        for scope_id, scope in scopes.items():
            # Test setting scope in filter
            filter_system.selected_scope = scope_id
            
            self.log_result(
                f"Filter Integration: {scope.name}",
                filter_system.selected_scope == scope_id,
                f"Filter scope set to {scope_id}",
                {'scope_id': scope_id, 'scope_name': scope.name}
            )
            
            # Test mosaic mode toggle
            filter_system.use_mosaic_mode = True
            self.log_result(
                f"Mosaic Mode: {scope.name}",
                filter_system.use_mosaic_mode == True,
                "Mosaic mode enabled",
                {'scope_id': scope_id, 'mosaic_enabled': filter_system.use_mosaic_mode}
            )
            
            filter_system.use_mosaic_mode = False
    
    def test_scope_specifications_accuracy(self):
        """Test 10: Verify specific scope specifications are accurate"""
        print("=" * 60)
        print("TEST 10: SCOPE SPECIFICATIONS ACCURACY")
        print("=" * 60)
        
        # Test specific known specifications
        test_specs = {
            'vespera_passenger': {
                'aperture_mm': 50,
                'focal_length_mm': 200,
                'manufacturer': 'Vaonis',
                'sensor_model': 'Sony IMX462'
            },
            'seestar_s50': {
                'aperture_mm': 50,
                'focal_length_mm': 250,
                'manufacturer': 'ZWO',
                'sensor_model': 'Sony IMX462'
            },
            'dwarf_2': {
                'aperture_mm': 24,
                'focal_length_mm': 100,
                'manufacturer': 'DwarfLab',
                'sensor_model': 'Sony IMX415'
            }
        }
        
        for scope_id, expected_specs in test_specs.items():
            scope = self.manager.get_scope(scope_id)
            
            if scope:
                for spec_name, expected_value in expected_specs.items():
                    actual_value = getattr(scope, spec_name, None)
                    
                    self.log_result(
                        f"Spec Accuracy: {scope.name} - {spec_name}",
                        actual_value == expected_value,
                        f"Expected {expected_value}, got {actual_value}",
                        {
                            'scope': scope.name,
                            'specification': spec_name,
                            'expected': expected_value,
                            'actual': actual_value
                        }
                    )
            else:
                self.log_result(
                    f"Scope Exists: {scope_id}",
                    False,
                    f"Scope {scope_id} not found",
                    {'scope_id': scope_id}
                )
    
    def test_utility_functions(self):
        """Test 11: Test all utility functions"""
        print("=" * 60)
        print("TEST 11: UTILITY FUNCTIONS")
        print("=" * 60)
        
        # Test get_all_scope_names
        scope_names = get_all_scope_names()
        expected_names = [
            "Vespera Passenger", "Vespera I", "Vespera II", "Vespera Pro",
            "Seestar S50", "Seestar S30", "Dwarf II", "Dwarf III"
        ]
        
        self.log_result(
            "Scope Names Function",
            len(scope_names) == len(expected_names),
            f"Expected {len(expected_names)} names, got {len(scope_names)}",
            {
                'expected_count': len(expected_names),
                'actual_count': len(scope_names),
                'names': scope_names
            }
        )
        
        # Test each expected name is present
        for expected_name in expected_names:
            self.log_result(
                f"Scope Name Present: {expected_name}",
                expected_name in scope_names,
                f"Name '{expected_name}' {'found' if expected_name in scope_names else 'missing'}",
                {'expected_name': expected_name, 'found': expected_name in scope_names}
            )
        
        # Test calculate_target_fov_compatibility
        compatibility = calculate_target_fov_compatibility(60)  # 1 degree target
        
        self.log_result(
            "FOV Compatibility Function",
            isinstance(compatibility, dict) and len(compatibility) > 0,
            f"Returned compatibility for {len(compatibility)} scopes",
            {
                'target_size': 60,
                'compatible_scopes': len([s for s, c in compatibility.items() if c]),
                'total_scopes': len(compatibility)
            }
        )
    
    def test_data_export_functionality(self):
        """Test 12: Test data export capabilities"""
        print("=" * 60)
        print("TEST 12: DATA EXPORT FUNCTIONALITY")
        print("=" * 60)
        
        try:
            # Test JSON export
            export_data = self.manager.export_scope_data()
            parsed_data = json.loads(export_data)
            
            self.log_result(
                "JSON Export",
                isinstance(parsed_data, dict) and len(parsed_data) > 0,
                f"Exported data for {len(parsed_data)} scopes",
                {
                    'export_size': len(export_data),
                    'scope_count': len(parsed_data),
                    'sample_scopes': list(parsed_data.keys())[:3]
                }
            )
            
            # Test scope comparison
            scope_ids = ['vespera_passenger', 'seestar_s50', 'dwarf_2']
            comparison = self.manager.get_scope_comparison(scope_ids)
            
            self.log_result(
                "Scope Comparison",
                len(comparison) == len(scope_ids),
                f"Comparison data for {len(comparison)} scopes",
                {
                    'requested_scopes': len(scope_ids),
                    'returned_data': len(comparison),
                    'scopes': list(comparison.keys())
                }
            )
            
        except Exception as e:
            self.log_result(
                "Export Functionality",
                False,
                f"Export failed: {str(e)}",
                {'error': str(e)}
            )
    
    def test_edge_cases_and_error_handling(self):
        """Test 13: Test edge cases and error handling"""
        print("=" * 60)
        print("TEST 13: EDGE CASES AND ERROR HANDLING")
        print("=" * 60)
        
        # Test invalid scope ID
        invalid_scope = self.manager.get_scope("invalid_scope_id")
        self.log_result(
            "Invalid Scope ID",
            invalid_scope is None,
            "Correctly returned None for invalid scope ID",
            {'result': invalid_scope}
        )
        
        # Test invalid scope name
        invalid_scope_id = self.manager.get_scope_id_by_name("Invalid Scope Name")
        self.log_result(
            "Invalid Scope Name",
            invalid_scope_id is None,
            "Correctly returned None for invalid scope name",
            {'result': invalid_scope_id}
        )
        
        # Test setting invalid scope
        success = set_selected_scope("invalid_scope_id")
        self.log_result(
            "Set Invalid Scope",
            success == False,
            "Correctly rejected invalid scope ID",
            {'result': success}
        )
        
        # Test extreme target sizes
        extreme_sizes = [0, -10, 1000000]  # Zero, negative, extremely large
        for size in extreme_sizes:
            try:
                compatibility = self.manager.calculate_fov_for_target(size)
                self.log_result(
                    f"Extreme Target Size: {size}",
                    isinstance(compatibility, dict),
                    f"Handled extreme size {size} gracefully",
                    {'size': size, 'result_type': type(compatibility).__name__}
                )
            except Exception as e:
                self.log_result(
                    f"Extreme Target Size: {size}",
                    False,
                    f"Failed to handle extreme size: {str(e)}",
                    {'size': size, 'error': str(e)}
                )
    
    def run_all_tests(self):
        """Run all configuration tests"""
        print("🔭 SMART TELESCOPE SCOPE CONFIGURATION TESTING")
        print("=" * 80)
        print("Testing all scope types and configurations...")
        print("=" * 80)
        print()
        
        # Run all test methods
        test_methods = [
            self.test_scope_database_integrity,
            self.test_manufacturer_coverage,
            self.test_scope_type_coverage,
            self.test_default_scope_configuration,
            self.test_scope_selection_switching,
            self.test_fov_calculations,
            self.test_target_compatibility_matrix,
            self.test_scope_recommendations,
            self.test_advanced_filter_integration,
            self.test_scope_specifications_accuracy,
            self.test_utility_functions,
            self.test_data_export_functionality,
            self.test_edge_cases_and_error_handling
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                test_name = test_method.__name__.replace('test_', '').replace('_', ' ').title()
                self.log_result(
                    f"Test Execution: {test_name}",
                    False,
                    f"Test failed with exception: {str(e)}",
                    {'error': str(e), 'test_method': test_method.__name__}
                )
        
        # Print final summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("=" * 80)
        print("🔭 SMART SCOPE CONFIGURATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.test_results['passed']} ✅")
        print(f"Failed: {self.test_results['failed']} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if self.test_results['failed'] > 0:
            print("FAILED TESTS:")
            print("-" * 40)
            for error in self.test_results['errors']:
                print(f"❌ {error}")
            print()
        
        if self.test_results['warnings']:
            print("WARNINGS:")
            print("-" * 40)
            for warning in self.test_results['warnings']:
                print(f"⚠️  {warning}")
            print()
        
        # Print scope summary
        print("SCOPE CONFIGURATION SUMMARY:")
        print("-" * 40)
        scopes = self.manager.get_all_scopes()
        for scope_id, scope in scopes.items():
            fov_w, fov_h = scope.native_fov_deg
            print(f"✅ {scope.name} ({scope.manufacturer})")
            print(f"   Aperture: {scope.aperture_mm}mm, FL: {scope.focal_length_mm}mm")
            print(f"   FOV: {fov_w:.2f}° × {fov_h:.2f}°")
            if scope.has_mosaic_mode and scope.mosaic_fov_deg:
                mosaic_w, mosaic_h = scope.mosaic_fov_deg
                print(f"   Mosaic FOV: {mosaic_w:.2f}° × {mosaic_h:.2f}°")
            print()
        
        print("=" * 80)
        if success_rate == 100:
            print("🎉 ALL SCOPE CONFIGURATIONS WORKING PERFECTLY!")
        elif success_rate >= 90:
            print("✅ SCOPE CONFIGURATIONS MOSTLY WORKING - MINOR ISSUES DETECTED")
        elif success_rate >= 70:
            print("⚠️  SCOPE CONFIGURATIONS PARTIALLY WORKING - SOME ISSUES DETECTED")
        else:
            print("❌ SCOPE CONFIGURATIONS HAVE SIGNIFICANT ISSUES")
        print("=" * 80)
        
        return success_rate == 100


def main():
    """Main test execution"""
    print("Starting comprehensive smart scope configuration testing...")
    print()
    
    tester = ScopeConfigurationTester()
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)