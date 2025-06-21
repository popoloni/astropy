#!/usr/bin/env python3
"""
Test suite for smart telescope scope management system
Tests the complete smart scope functionality including database, filtering, and UI integration
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import smart scope modules
from mobile_app.utils.smart_scopes import (
    ScopeSpecifications, SmartScopeManager, get_scope_manager, get_all_scope_names
)
from mobile_app.utils.advanced_filter import AdvancedFilter


class TestScopeSpecifications(unittest.TestCase):
    """Test ScopeSpecifications class"""
    
    def setUp(self):
        """Set up test scope manager"""
        self.manager = SmartScopeManager()
        self.scope = self.manager.get_scope("vespera_passenger")
    
    def test_scope_properties(self):
        """Test basic scope properties"""
        self.assertEqual(self.scope.name, "Vespera Passenger")
        self.assertEqual(self.scope.manufacturer, "Vaonis")
        self.assertEqual(self.scope.aperture_mm, 50)
        self.assertEqual(self.scope.focal_length_mm, 200)
        self.assertTrue(self.scope.is_default)
    
    def test_fov_properties(self):
        """Test field of view properties"""
        # Test native FOV
        fov_width, fov_height = self.scope.native_fov_deg
        self.assertGreater(fov_width, 0)
        self.assertGreater(fov_height, 0)
        
        # Test mosaic FOV
        if self.scope.has_mosaic_mode:
            mosaic_width, mosaic_height = self.scope.mosaic_fov_deg
            self.assertGreater(mosaic_width, fov_width)
            self.assertGreater(mosaic_height, fov_height)
    
    def test_sensor_properties(self):
        """Test sensor specifications"""
        self.assertGreater(self.scope.resolution_mp, 0)
        self.assertGreater(self.scope.pixel_size_um, 0)
        
        sensor_width, sensor_height = self.scope.sensor_size_mm
        self.assertGreater(sensor_width, 0)
        self.assertGreater(sensor_height, 0)
    
    def test_capabilities(self):
        """Test scope capabilities"""
        self.assertTrue(self.scope.has_goto)
        self.assertTrue(self.scope.has_tracking)
        self.assertTrue(self.scope.has_live_stacking)


class TestSmartScopeManager(unittest.TestCase):
    """Test SmartScopeManager class"""
    
    def setUp(self):
        """Set up test scope manager"""
        self.manager = SmartScopeManager()
    
    def test_scope_database_loading(self):
        """Test that all scopes are loaded correctly"""
        scopes = self.manager.get_all_scopes()
        
        # Should have all requested scopes
        scope_names = [scope.name for scope in scopes.values()]
        
        # Check for Vaonis scopes
        self.assertIn("Vespera Passenger", scope_names)
        self.assertIn("Vespera I", scope_names)
        self.assertIn("Vespera II", scope_names)
        self.assertIn("Vespera Pro", scope_names)
        
        # Check for ZWO scopes
        self.assertIn("Seestar S50", scope_names)
        self.assertIn("Seestar S30", scope_names)
        
        # Check for DwarfLab scopes
        self.assertIn("Dwarf II", scope_names)
        self.assertIn("Dwarf III", scope_names)
    
    def test_default_scope(self):
        """Test default scope (Vespera Passenger)"""
        default_scope = self.manager.get_selected_scope()
        
        self.assertIsNotNone(default_scope)
        self.assertEqual(default_scope.name, "Vespera Passenger")
        self.assertEqual(default_scope.manufacturer, "Vaonis")
        self.assertTrue(default_scope.is_default)
    
    def test_scope_retrieval(self):
        """Test scope retrieval by ID and name"""
        # Test by ID
        scope = self.manager.get_scope("vespera_passenger")
        self.assertIsNotNone(scope)
        self.assertEqual(scope.name, "Vespera Passenger")
        
        # Test by name
        scope_id = self.manager.get_scope_id_by_name("Vespera Passenger")
        self.assertEqual(scope_id, "vespera_passenger")
        
        # Test invalid scope
        invalid_scope = self.manager.get_scope("invalid_scope")
        self.assertIsNone(invalid_scope)
    
    def test_scope_filtering(self):
        """Test scope filtering functionality"""
        # Filter by manufacturer
        vaonis_scopes = self.manager.get_scopes_by_manufacturer("Vaonis")
        self.assertTrue(all(scope.manufacturer == "Vaonis" for scope in vaonis_scopes.values()))
        self.assertEqual(len(vaonis_scopes), 4)  # 4 Vaonis scopes
        
        # Filter by type
        from mobile_app.utils.smart_scopes import ScopeType
        vaonis_type_scopes = self.manager.get_scopes_by_type(ScopeType.VAONIS)
        self.assertEqual(len(vaonis_type_scopes), 4)
    
    def test_scope_recommendations(self):
        """Test scope recommendation system"""
        # Test for small target
        recommendations = self.manager.get_optimal_scopes_for_target(30)  # 30 arcmin
        self.assertTrue(len(recommendations) > 0)
        
        # Test for large target
        large_recommendations = self.manager.get_optimal_scopes_for_target(300)  # 5 degrees
        self.assertTrue(len(large_recommendations) > 0)


class TestAdvancedFilterIntegration(unittest.TestCase):
    """Test integration with advanced filter system"""
    
    def setUp(self):
        """Set up test filter with scope"""
        self.filter = AdvancedFilter()
        self.manager = get_scope_manager()
    
    def test_scope_filter_integration(self):
        """Test scope selection in advanced filter"""
        # Set a specific scope
        self.filter.selected_scope = "vespera_passenger"
        
        # Test scope retrieval
        scope = self.manager.get_scope(self.filter.selected_scope)
        self.assertIsNotNone(scope)
        self.assertEqual(scope.name, "Vespera Passenger")
    
    def test_mosaic_mode_integration(self):
        """Test mosaic mode in advanced filter"""
        self.filter.use_mosaic_mode = True
        self.filter.selected_scope = "vespera_passenger"
        
        # Test that mosaic mode is properly set
        self.assertTrue(self.filter.use_mosaic_mode)
    
    def test_fov_compatibility_filtering(self):
        """Test FOV-based target filtering"""
        # Mock target data
        mock_targets = [
            {'name': 'Small Target', 'size_arcmin': 20},
            {'name': 'Medium Target', 'size_arcmin': 60},
            {'name': 'Large Target', 'size_arcmin': 300}
        ]
        
        # Set scope and test filtering
        self.filter.selected_scope = "vespera_passenger"
        scope = self.manager.get_scope(self.filter.selected_scope)
        
        # Test FOV compatibility using the manager's method
        compatibility = self.manager.calculate_fov_for_target(60)  # 1 degree target
        self.assertIn("vespera_passenger", compatibility)
        
        # Test large target compatibility
        large_compatibility = self.manager.calculate_fov_for_target(300)  # 5 degree target
        self.assertIn("vespera_passenger", large_compatibility)


class TestScopeUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_get_scope_manager(self):
        """Test global scope manager function"""
        manager = get_scope_manager()
        self.assertIsInstance(manager, SmartScopeManager)
        
        # Should return same instance (singleton pattern)
        manager2 = get_scope_manager()
        self.assertIs(manager, manager2)
    
    def test_get_all_scope_names(self):
        """Test scope names utility function"""
        names = get_all_scope_names()
        
        self.assertIsInstance(names, list)
        self.assertTrue(len(names) > 0)
        
        # Should include all major scopes
        self.assertIn("Vespera Passenger", names)
        self.assertIn("Seestar S50", names)
        self.assertIn("Dwarf II", names)


class TestSpecificScopeSpecs(unittest.TestCase):
    """Test specific telescope specifications"""
    
    def setUp(self):
        """Set up scope manager"""
        self.manager = get_scope_manager()
    
    def test_vaonis_specifications(self):
        """Test Vaonis telescope specifications"""
        # Test Vespera Passenger (default)
        passenger = self.manager.get_scope("vespera_passenger")
        self.assertEqual(passenger.aperture_mm, 50)
        self.assertEqual(passenger.focal_length_mm, 200)
        self.assertTrue(passenger.has_goto)
        
        # Test Vespera Pro
        pro = self.manager.get_scope("vespera_pro")
        self.assertEqual(pro.aperture_mm, 50)
        self.assertEqual(pro.focal_length_mm, 250)
        self.assertTrue(pro.has_autofocus)
    
    def test_zwo_specifications(self):
        """Test ZWO telescope specifications"""
        # Test Seestar S50
        s50 = self.manager.get_scope("seestar_s50")
        self.assertEqual(s50.aperture_mm, 50)
        self.assertEqual(s50.focal_length_mm, 250)
        self.assertTrue(s50.has_goto)
        
        # Test Seestar S30
        s30 = self.manager.get_scope("seestar_s30")
        self.assertEqual(s30.aperture_mm, 30)
        self.assertEqual(s30.focal_length_mm, 150)
    
    def test_dwarflab_specifications(self):
        """Test DwarfLab telescope specifications"""
        # Test Dwarf II
        dwarf2 = self.manager.get_scope("dwarf_2")
        self.assertEqual(dwarf2.aperture_mm, 24)
        self.assertEqual(dwarf2.focal_length_mm, 100)
        self.assertTrue(dwarf2.has_goto)
        
        # Test Dwarf III
        dwarf3 = self.manager.get_scope("dwarf_3")
        self.assertEqual(dwarf3.aperture_mm, 35)
        self.assertEqual(dwarf3.focal_length_mm, 150)


def run_smart_scope_tests():
    """Run all smart scope tests"""
    print("Running Smart Telescope Scope Management Tests...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestScopeSpecifications,
        TestSmartScopeManager,
        TestAdvancedFilterIntegration,
        TestScopeUtilityFunctions,
        TestSpecificScopeSpecs
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SMART SCOPE TESTS SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_smart_scope_tests()
    sys.exit(0 if success else 1)