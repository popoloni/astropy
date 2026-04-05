#!/usr/bin/env python3
"""
UX Features Test Suite
Comprehensive testing for gesture controls and theme system
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add mobile app to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root_dir, 'mobile_app'))

class TestGestureManager(unittest.TestCase):
    """Test gesture manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Kivy dependencies
        sys.modules['kivy'] = Mock()
        sys.modules['kivy.vector'] = Mock()
        sys.modules['kivy.clock'] = Mock()
        sys.modules['kivy.logger'] = Mock()
        
        from utils.gesture_manager import GestureManager
        self.gesture_manager = GestureManager()
    
    def test_gesture_manager_creation(self):
        """Test gesture manager can be created"""
        self.assertIsNotNone(self.gesture_manager)
        self.assertIsNotNone(self.gesture_manager.sensitivity_config)
    
    def test_sensitivity_configuration(self):
        """Test gesture sensitivity configuration"""
        config = {
            'swipe_threshold': 100,
            'long_press_duration': 1.0,
            'double_tap_interval': 0.3
        }
        
        from utils.gesture_manager import GestureManager
        manager = GestureManager(sensitivity_config=config)
        
        self.assertEqual(manager.sensitivity_config['swipe_threshold'], 100)
        self.assertEqual(manager.sensitivity_config['long_press_duration'], 1.0)
        self.assertEqual(manager.sensitivity_config['double_tap_interval'], 0.3)
    
    def test_callback_registration(self):
        """Test gesture callback registration"""
        callback = Mock()
        self.gesture_manager.register_callback('swipe_left', callback)
        
        # Verify callback is registered
        self.assertIn('swipe_left', self.gesture_manager.callbacks)
        self.assertEqual(self.gesture_manager.callbacks['swipe_left'], callback)

class TestThemeManager(unittest.TestCase):
    """Test theme manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Kivy dependencies
        sys.modules['kivy'] = Mock()
        sys.modules['kivy.logger'] = Mock()
        
        from utils.theme_manager import ThemeManager
        self.theme_manager = ThemeManager()
    
    def test_theme_manager_creation(self):
        """Test theme manager can be created"""
        self.assertIsNotNone(self.theme_manager)
        self.assertIsNotNone(self.theme_manager.themes)
        self.assertIsNotNone(self.theme_manager.current_theme)
    
    def test_available_themes(self):
        """Test available themes"""
        themes = self.theme_manager.get_available_themes()
        
        self.assertIsInstance(themes, list)
        self.assertGreater(len(themes), 0)
        
        # Check required themes exist
        theme_ids = [theme['id'] for theme in themes]
        self.assertIn('light', theme_ids)
        self.assertIn('dark', theme_ids)
        self.assertIn('red_night', theme_ids)
    
    def test_theme_switching(self):
        """Test theme switching functionality"""
        original_theme = self.theme_manager.current_theme
        
        # Switch to different theme
        new_theme = 'dark' if original_theme != 'dark' else 'light'
        success = self.theme_manager.set_theme(new_theme)
        
        self.assertTrue(success)
        self.assertEqual(self.theme_manager.current_theme, new_theme)
        
        # Switch back
        self.theme_manager.set_theme(original_theme)
        self.assertEqual(self.theme_manager.current_theme, original_theme)
    
    def test_invalid_theme(self):
        """Test handling of invalid theme"""
        success = self.theme_manager.set_theme('invalid_theme')
        self.assertFalse(success)
    
    def test_color_retrieval(self):
        """Test color retrieval from themes"""
        color = self.theme_manager.get_color('background_primary')
        self.assertIsNotNone(color)
        self.assertIsInstance(color, (list, tuple))
        self.assertEqual(len(color), 4)  # RGBA
        
        # Test all color values are between 0 and 1
        for value in color:
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 1)
    
    def test_theme_metadata(self):
        """Test theme metadata"""
        themes = self.theme_manager.get_available_themes()
        
        for theme in themes:
            self.assertIn('id', theme)
            self.assertIn('name', theme)
            self.assertIn('description', theme)
            self.assertIn('current', theme)
            
            self.assertIsInstance(theme['id'], str)
            self.assertIsInstance(theme['name'], str)
            self.assertIsInstance(theme['description'], str)
            self.assertIsInstance(theme['current'], bool)

class TestAstronomyGestures(unittest.TestCase):
    """Test astronomy-specific gesture patterns"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Kivy dependencies
        sys.modules['kivy'] = Mock()
        sys.modules['kivy.logger'] = Mock()
        
        from utils.gesture_manager import AstronomyGestures
        self.astronomy_gestures = AstronomyGestures()
    
    def test_astronomy_gestures_creation(self):
        """Test astronomy gestures can be created"""
        self.assertIsNotNone(self.astronomy_gestures)
    
    def test_gesture_patterns(self):
        """Test gesture patterns are available"""
        patterns = self.astronomy_gestures.get_gesture_patterns()
        
        self.assertIsInstance(patterns, dict)
        self.assertGreater(len(patterns), 0)
        
        # Check for expected patterns
        expected_patterns = [
            'target_add_to_plan',
            'target_remove_from_plan',
            'target_view_details',
            'target_toggle_planned'
        ]
        
        for pattern in expected_patterns:
            self.assertIn(pattern, patterns)
    
    def test_pattern_metadata(self):
        """Test pattern metadata structure"""
        patterns = self.astronomy_gestures.get_gesture_patterns()
        
        for pattern_name, pattern_info in patterns.items():
            self.assertIsInstance(pattern_info, dict)
            self.assertIn('gesture', pattern_info)
            self.assertIn('description', pattern_info)

class TestIntegration(unittest.TestCase):
    """Test integration between components"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Kivy dependencies
        sys.modules['kivy'] = Mock()
        sys.modules['kivy.logger'] = Mock()
        sys.modules['kivy.vector'] = Mock()
        sys.modules['kivy.clock'] = Mock()
    
    def test_theme_manager_singleton(self):
        """Test theme manager singleton pattern"""
        from utils.theme_manager import get_theme_manager
        
        manager1 = get_theme_manager()
        manager2 = get_theme_manager()
        
        self.assertIs(manager1, manager2)
    
    def test_gesture_and_theme_compatibility(self):
        """Test gesture manager and theme manager work together"""
        from utils.gesture_manager import GestureManager
        from utils.theme_manager import get_theme_manager
        
        gesture_manager = GestureManager()
        theme_manager = get_theme_manager()
        
        # Both should be created successfully
        self.assertIsNotNone(gesture_manager)
        self.assertIsNotNone(theme_manager)
        
        # Theme switching shouldn't affect gesture manager
        original_theme = theme_manager.current_theme
        theme_manager.set_theme('dark')
        
        # Gesture manager should still work
        callback = Mock()
        gesture_manager.register_callback('swipe_left', callback)
        self.assertIn('swipe_left', gesture_manager.callbacks)
        
        # Restore theme
        theme_manager.set_theme(original_theme)

class TestErrorHandling(unittest.TestCase):
    """Test error handling in UX components"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Kivy dependencies
        sys.modules['kivy'] = Mock()
        sys.modules['kivy.logger'] = Mock()
        sys.modules['kivy.vector'] = Mock()
        sys.modules['kivy.clock'] = Mock()
    
    def test_gesture_manager_invalid_config(self):
        """Test gesture manager with invalid configuration"""
        from utils.gesture_manager import GestureManager
        
        # Should handle invalid config gracefully
        invalid_config = {'invalid_key': 'invalid_value'}
        manager = GestureManager(sensitivity_config=invalid_config)
        
        self.assertIsNotNone(manager)
        # Should fall back to defaults for missing keys
        self.assertIn('swipe_threshold', manager.sensitivity_config)
    
    def test_theme_manager_missing_colors(self):
        """Test theme manager with missing color definitions"""
        from utils.theme_manager import ThemeManager
        
        manager = ThemeManager()
        
        # Should handle missing colors gracefully
        color = manager.get_color('nonexistent_color')
        self.assertIsNotNone(color)  # Should return default color
    
    def test_callback_error_handling(self):
        """Test gesture callback error handling"""
        from utils.gesture_manager import GestureManager
        
        manager = GestureManager()
        
        # Register callback that raises exception
        def error_callback(*args, **kwargs):
            raise Exception("Test error")
        
        manager.register_callback('swipe_left', error_callback)
        
        # Should handle callback errors gracefully
        # (This would be tested with actual gesture detection)
        self.assertIn('swipe_left', manager.callbacks)

def run_tests():
    """Run all UX feature tests"""
    print("UX Features Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_classes = [
        TestGestureManager,
        TestThemeManager,
        TestAstronomyGestures,
        TestIntegration,
        TestErrorHandling
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 All UX feature tests passed!")
    else:
        print("\n❌ Some UX feature tests failed")
    
    return success

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)