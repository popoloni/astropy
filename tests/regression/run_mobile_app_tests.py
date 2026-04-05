#!/usr/bin/env python3
"""
Automated Test Runner for Mobile App Configuration
Tests settings loading, twilight integration, and validates against desktop behavior.
"""

import json
import os
import sys
import subprocess
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class MobileAppTester:
    """Test runner for mobile app configuration integration"""
    
    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        self.mobile_dir = os.path.join(self.base_dir, 'mobile_app')
        self.scenarios_file = os.path.join(os.path.dirname(__file__), 'test_scenarios.json')
        self.scenarios = self.load_test_scenarios()
    
    def load_test_scenarios(self) -> Dict[str, Any]:
        """Load test scenarios from JSON file"""
        try:
            with open(self.scenarios_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Scenarios file {self.scenarios_file} not found")
            return {}
    
    def set_twilight_config(self, twilight_type: str):
        """Set twilight configuration for testing"""
        # Update main config
        config_path = os.path.join(self.base_dir, 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'visibility' not in config:
            config['visibility'] = {}
        config['visibility']['twilight_type'] = twilight_type
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        # Update mobile app config
        mobile_config_path = os.path.join(self.mobile_dir, 'astroscope_settings.json')
        if os.path.exists(mobile_config_path):
            with open(mobile_config_path, 'r') as f:
                mobile_config = json.load(f)
            
            if 'visibility' not in mobile_config:
                mobile_config['visibility'] = {}
            mobile_config['visibility']['twilight_type'] = twilight_type
            
            with open(mobile_config_path, 'w') as f:
                json.dump(mobile_config, f, indent=4)
    
    def run_mobile_app_test(self, test_mode: str = 'config') -> Tuple[int, str, str]:
        """Run mobile app in test mode"""
        # Create a simple test script to check configuration loading
        test_script = f"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from config.settings import load_config
    from mobile_app.utils.app_state import AppState
    from mobile_app.main import load_tonights_targets
    from datetime import datetime
    
    print("=== MOBILE APP CONFIGURATION TEST ===")
    
    # Test configuration loading
    config = load_config()
    twilight_type = config.get('visibility', {{}}).get('twilight_type', 'unknown')
    print(f"Loaded twilight type: {{twilight_type}}")
    
    # Test app state initialization
    app_state = AppState()
    print(f"App state initialized: {{app_state is not None}}")
    
    # Test target loading (simplified)
    current_date = datetime.now()
    print(f"Testing target loading for date: {{current_date.strftime('%Y-%m-%d')}}")
    
    # Check for hardcoded times in main.py
    with open('main.py', 'r') as f:
        main_content = f.read()
        
    hardcoded_times = []
    if 'hour=22, minute=26' in main_content:
        hardcoded_times.append('22:26')
    if 'hour=5, minute=32' in main_content:
        hardcoded_times.append('05:32')
    
    if hardcoded_times:
        print(f"WARNING: Found hardcoded times: {{', '.join(hardcoded_times)}}")
    else:
        print("No hardcoded times detected")
    
    print("=== TEST COMPLETED ===")
    
except Exception as e:
    print(f"ERROR: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        
        # Write test script
        test_script_path = os.path.join(self.mobile_dir, 'test_config.py')
        with open(test_script_path, 'w') as f:
            f.write(test_script)
        
        try:
            # Run the test script
            result = subprocess.run([
                'python', 'test_config.py'
            ], capture_output=True, text=True, cwd=self.mobile_dir)
            
            return result.returncode, result.stdout, result.stderr
        finally:
            # Clean up test script
            if os.path.exists(test_script_path):
                os.remove(test_script_path)
    
    def parse_mobile_config_output(self, output: str) -> Dict[str, Any]:
        """Parse mobile app configuration test output"""
        result = {
            'twilight_type_loaded': 'unknown',
            'app_state_initialized': False,
            'hardcoded_times_detected': [],
            'errors': []
        }
        
        # Parse twilight type
        twilight_match = re.search(r"Loaded twilight type:\s*(\w+)", output)
        if twilight_match:
            result['twilight_type_loaded'] = twilight_match.group(1)
        
        # Parse app state initialization
        if "App state initialized: True" in output:
            result['app_state_initialized'] = True
        
        # Parse hardcoded times warning
        times_match = re.search(r"WARNING: Found hardcoded times:\s*(.+)", output)
        if times_match:
            times_str = times_match.group(1)
            result['hardcoded_times_detected'] = [t.strip() for t in times_str.split(',')]
        
        # Parse errors
        error_matches = re.findall(r"ERROR:\s*(.+)", output)
        result['errors'] = error_matches
        
        return result
    
    def test_mobile_configuration_loading(self) -> Dict[str, Any]:
        """Test mobile app configuration loading with different twilight types"""
        results = {}
        
        for scenario_name, scenario in self.scenarios.items():
            if scenario_name == 'test_parameters':
                continue
            
            print(f"Testing mobile app configuration for {scenario_name}...")
            
            try:
                # Set configuration
                twilight_type = scenario['config']['twilight_type']
                self.set_twilight_config(twilight_type)
                
                # Run mobile app configuration test
                returncode, stdout, stderr = self.run_mobile_app_test('config')
                
                if returncode == 0:
                    # Parse results
                    config_result = self.parse_mobile_config_output(stdout)
                    
                    results[scenario_name] = {
                        'success': True,
                        'expected_twilight': twilight_type,
                        'loaded_twilight': config_result['twilight_type_loaded'],
                        'twilight_matches': config_result['twilight_type_loaded'] == twilight_type,
                        'app_state_initialized': config_result['app_state_initialized'],
                        'hardcoded_times_detected': config_result['hardcoded_times_detected'],
                        'has_hardcoded_times': len(config_result['hardcoded_times_detected']) > 0,
                        'errors': config_result['errors'],
                        'output': stdout
                    }
                else:
                    results[scenario_name] = {
                        'success': False,
                        'expected_twilight': twilight_type,
                        'error': f"Test failed with code {returncode}",
                        'stderr': stderr,
                        'stdout': stdout
                    }
                    
            except Exception as e:
                results[scenario_name] = {
                    'success': False,
                    'expected_twilight': twilight_type,
                    'error': f"Exception: {str(e)}"
                }
        
        return results
    
    def test_config_synchronization(self) -> Dict[str, Any]:
        """Test synchronization between desktop and mobile app configurations"""
        sync_results = {
            'desktop_mobile_sync': True,
            'config_files_exist': {},
            'config_consistency': {},
            'issues': []
        }
        
        # Check if configuration files exist
        desktop_config = os.path.join(self.base_dir, 'config.json')
        mobile_config = os.path.join(self.mobile_dir, 'astroscope_settings.json')
        
        sync_results['config_files_exist'] = {
            'desktop_config': os.path.exists(desktop_config),
            'mobile_config': os.path.exists(mobile_config)
        }
        
        if not sync_results['config_files_exist']['desktop_config']:
            sync_results['issues'].append("Desktop config.json not found")
        
        if not sync_results['config_files_exist']['mobile_config']:
            sync_results['issues'].append("Mobile astroscope_settings.json not found")
        
        # Compare configurations if both exist
        if all(sync_results['config_files_exist'].values()):
            try:
                with open(desktop_config, 'r') as f:
                    desktop_cfg = json.load(f)
                
                with open(mobile_config, 'r') as f:
                    mobile_cfg = json.load(f)
                
                # Compare twilight settings
                desktop_twilight = desktop_cfg.get('visibility', {}).get('twilight_type', '')
                mobile_twilight = mobile_cfg.get('visibility', {}).get('twilight_type', '')
                
                sync_results['config_consistency'] = {
                    'desktop_twilight': desktop_twilight,
                    'mobile_twilight': mobile_twilight,
                    'twilight_matches': desktop_twilight == mobile_twilight
                }
                
                if not sync_results['config_consistency']['twilight_matches']:
                    sync_results['desktop_mobile_sync'] = False
                    sync_results['issues'].append(
                        f"Twilight type mismatch: desktop={desktop_twilight}, mobile={mobile_twilight}"
                    )
                
            except Exception as e:
                sync_results['issues'].append(f"Error comparing configurations: {e}")
                sync_results['desktop_mobile_sync'] = False
        
        return sync_results
    
    def validate_against_desktop_behavior(self, mobile_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mobile app behavior against desktop expectations"""
        validation = {
            'configuration_consistency': True,
            'hardcoded_issues_detected': False,
            'app_initialization_success': True,
            'issues': [],
            'statistics': {}
        }
        
        # Analyze mobile configuration results
        successful_tests = 0
        total_tests = 0
        hardcoded_detections = 0
        
        for scenario_name, result in mobile_results.items():
            if not isinstance(result, dict):
                continue
                
            total_tests += 1
            
            if result.get('success', False):
                successful_tests += 1
                
                # Check configuration consistency
                if not result.get('twilight_matches', False):
                    validation['configuration_consistency'] = False
                    validation['issues'].append(
                        f"Configuration mismatch in {scenario_name}: "
                        f"expected {result.get('expected_twilight', '')}, "
                        f"got {result.get('loaded_twilight', '')}"
                    )
                
                # Check for hardcoded times
                if result.get('has_hardcoded_times', False):
                    hardcoded_detections += 1
                    validation['hardcoded_issues_detected'] = True
                    validation['issues'].append(
                        f"Hardcoded times detected in {scenario_name}: "
                        f"{', '.join(result.get('hardcoded_times_detected', []))}"
                    )
                
                # Check app initialization
                if not result.get('app_state_initialized', False):
                    validation['app_initialization_success'] = False
                    validation['issues'].append(f"App state initialization failed in {scenario_name}")
        
        validation['statistics'] = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': total_tests - successful_tests,
            'hardcoded_detections': hardcoded_detections,
            'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        return validation
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all mobile app tests"""
        print("Starting Mobile App Tests...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'frontend': 'mobile_app/main.py',
            'configuration_loading': self.test_mobile_configuration_loading(),
            'config_synchronization': self.test_config_synchronization()
        }
        
        # Add validation
        results['validation'] = self.validate_against_desktop_behavior(results['configuration_loading'])
        
        return results


def main():
    """Run the mobile app tests"""
    tester = MobileAppTester()
    results = tester.run_all_tests()
    
    # Save results
    results_file = os.path.join(os.path.dirname(__file__), 'mobile_app_test_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*50)
    print("MOBILE APP TEST RESULTS")
    print("="*50)
    
    validation = results.get('validation', {})
    config_results = results.get('configuration_loading', {})
    sync_results = results.get('config_synchronization', {})
    
    stats = validation.get('statistics', {})
    print(f"Total Tests: {stats.get('total_tests', 0)}")
    print(f"Successful Tests: {stats.get('successful_tests', 0)}")
    print(f"Failed Tests: {stats.get('failed_tests', 0)}")
    print(f"Success Rate: {stats.get('success_rate', 0):.1f}%")
    
    print(f"Configuration Consistency: {'✓' if validation.get('configuration_consistency', False) else '✗'}")
    print(f"App Initialization Success: {'✓' if validation.get('app_initialization_success', False) else '✗'}")
    print(f"Desktop-Mobile Sync: {'✓' if sync_results.get('desktop_mobile_sync', False) else '✗'}")
    
    # Critical issue detection
    if validation.get('hardcoded_issues_detected', False):
        print(f"⚠️  CRITICAL: Hardcoded Times Detected: {stats.get('hardcoded_detections', 0)} instances")
    
    if validation.get('issues'):
        print("\nISSUES DETECTED:")
        for issue in validation['issues']:
            print(f"  ⚠️  {issue}")
    
    # Synchronization issues
    sync_issues = sync_results.get('issues', [])
    if sync_issues:
        print("\nSYNCHRONIZATION ISSUES:")
        for issue in sync_issues:
            print(f"  ⚠️  {issue}")
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    main() 