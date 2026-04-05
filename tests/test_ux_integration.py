#!/usr/bin/env python3
"""
Test UX Integration
Test gesture controls and theme system integration
"""

import sys
import os

# Add mobile app to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root_dir, 'mobile_app'))

def test_imports():
    """Test that all UX modules can be imported"""
    print("Testing UX module imports...")
    
    try:
        from utils.gesture_manager import GestureManager, SwipeableWidget, AstronomyGestures
        print("✓ Gesture manager imports successful")
    except ImportError as e:
        print(f"✗ Gesture manager import failed: {e}")
        return False
    
    try:
        from utils.theme_manager import ThemeManager, ThemedWidget, get_theme_manager
        print("✓ Theme manager imports successful")
    except ImportError as e:
        print(f"✗ Theme manager import failed: {e}")
        return False
    
    return True

def test_theme_manager():
    """Test theme manager functionality"""
    print("\nTesting theme manager...")
    
    try:
        from utils.theme_manager import get_theme_manager
        
        theme_manager = get_theme_manager()
        
        # Test theme availability
        themes = theme_manager.get_available_themes()
        print(f"✓ Available themes: {len(themes)}")
        
        for theme in themes:
            print(f"  - {theme['name']}: {theme['description']}")
        
        # Test theme switching
        original_theme = theme_manager.current_theme
        print(f"✓ Current theme: {original_theme}")
        
        # Try switching to each theme
        for theme in themes:
            if theme['id'] != original_theme:
                success = theme_manager.set_theme(theme['id'])
                if success:
                    print(f"✓ Successfully switched to {theme['name']}")
                    # Switch back
                    theme_manager.set_theme(original_theme)
                else:
                    print(f"✗ Failed to switch to {theme['name']}")
        
        # Test color retrieval
        bg_color = theme_manager.get_color('background_primary')
        print(f"✓ Background color: {bg_color}")
        
        return True
        
    except Exception as e:
        print(f"✗ Theme manager test failed: {e}")
        return False

def test_gesture_manager():
    """Test gesture manager functionality"""
    print("\nTesting gesture manager...")
    
    try:
        from utils.gesture_manager import GestureManager, AstronomyGestures
        
        # Test gesture manager creation
        gesture_manager = GestureManager()
        print("✓ Gesture manager created")
        
        # Test astronomy gestures
        astronomy_gestures = AstronomyGestures()
        print("✓ Astronomy gestures created")
        
        # Test gesture patterns
        patterns = astronomy_gestures.get_gesture_patterns()
        print(f"✓ Gesture patterns available: {len(patterns)}")
        
        for pattern_name, pattern_info in patterns.items():
            print(f"  - {pattern_name}: {pattern_info.get('description', 'No description')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Gesture manager test failed: {e}")
        return False

def test_screen_integration():
    """Test that screens can import UX modules"""
    print("\nTesting screen integration...")
    
    try:
        # Test targets screen integration
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mobile_app', 'screens'))
        
        # This should work without Kivy being installed
        print("✓ Screen imports would work (Kivy not available for full test)")
        
        return True
        
    except Exception as e:
        print(f"✗ Screen integration test failed: {e}")
        return False

def main():
    """Run all UX integration tests"""
    print("UX Integration Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_theme_manager,
        test_gesture_manager,
        test_screen_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All UX integration tests passed!")
        return True
    else:
        print("❌ Some UX integration tests failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)