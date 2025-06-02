"""
Tests for configuration and precision settings
"""

import unittest
import sys
import os
import json
from datetime import datetime

# Add the astropy root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import precision module with fallback handling
try:
    from astronomy.precision import get_precision_mode, set_precision_mode
    from astronomy.precision.config import PrecisionConfigError
    PRECISION_AVAILABLE = True
except ImportError:
    PRECISION_AVAILABLE = False
    # Create a dummy exception class for testing
    class PrecisionConfigError(Exception):
        pass

class TestPrecisionConfiguration(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        if not PRECISION_AVAILABLE:
            self.skipTest("Precision module not available")
    
    def test_precision_mode_setting(self):
        """Test setting precision modes"""
        # Test auto mode
        set_precision_mode('auto')
        self.assertEqual(get_precision_mode(), 'auto')
        
        # Test standard mode
        set_precision_mode('standard')
        self.assertEqual(get_precision_mode(), 'standard')
        
        # Test high precision mode
        set_precision_mode('high')
        self.assertEqual(get_precision_mode(), 'high')
    
    def test_invalid_precision_mode(self):
        """Test handling of invalid precision modes"""
        with self.assertRaises(PrecisionConfigError):
            set_precision_mode('invalid_mode')
    
    def test_config_file_reading(self):
        """Test reading configuration from file"""
        # Check if config.json exists and is readable
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check that config has expected keys
            self.assertIsInstance(config, dict)
            # Don't enforce specific keys as config may vary
        else:
            self.skipTest("config.json not found")
    
    def test_precision_consistency(self):
        """Test that precision settings are consistent"""
        original_mode = get_precision_mode()
        
        try:
            # Test mode changes
            for mode in ['auto', 'standard', 'high']:
                set_precision_mode(mode)
                self.assertEqual(get_precision_mode(), mode)
            
        finally:
            # Restore original mode
            set_precision_mode(original_mode)

if __name__ == '__main__':
    unittest.main()