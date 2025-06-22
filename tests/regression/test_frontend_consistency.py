#!/usr/bin/env python3
"""
Frontend Consistency Test Suite for DSO Selection Algorithm
Tests twilight configuration loading, object count variations, and consistency across frontends.
"""

import json
import os
import sys
import subprocess
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import tempfile
import shutil

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import load_config


class FrontendConsistencyTester:
    """Test suite for validating DSO selection consistency across frontends"""
    
    def __init__(self, scenarios_file: str = None):
        self.scenarios_file = scenarios_file or os.path.join(
            os.path.dirname(__file__), 'test_scenarios.json'
        )
        self.scenarios = self.load_test_scenarios()
        self.results = {}
        self.original_config = None
        
    def load_test_scenarios(self) -> Dict[str, Any]:
        """Load test scenarios from JSON file"""
        try:
            with open(self.scenarios_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Scenarios file {self.scenarios_file} not found")
            return {}
    
    def backup_config(self):
        """Backup original configuration"""
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.original_config = json.load(f)
    
    def restore_config(self):
        """Restore original configuration"""
        if self.original_config:
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
            with open(config_path, 'w') as f:
                json.dump(self.original_config, f, indent=4)
    
    def set_twilight_config(self, twilight_type: str):
        """Set twilight configuration for testing"""
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
        
        # Load current config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update twilight type
        if 'visibility' not in config:
            config['visibility'] = {}
        config['visibility']['twilight_type'] = twilight_type
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    
    def test_twilight_configuration_loading(self) -> Dict[str, bool]:
        """Test that twilight configuration is loaded correctly"""
        results = {}
        
        for scenario_name, scenario in self.scenarios.items():
            if scenario_name == 'test_parameters':
                continue
                
            try:
                # Set configuration
                twilight_type = scenario['config']['twilight_type']
                self.set_twilight_config(twilight_type)
                
                # Load and verify configuration
                config = load_config()
                loaded_twilight = config.get('visibility', {}).get('twilight_type', '')
                
                results[scenario_name] = loaded_twilight == twilight_type
                
            except Exception as e:
                print(f"Error testing {scenario_name}: {e}")
                results[scenario_name] = False
        
        return results
    
    def parse_observation_window(self, output: str) -> Tuple[str, str]:
        """Parse observation window from frontend output"""
        # Look for patterns like "Observation Window: 21:12 - 06:48"
        window_pattern = r"Observation Window:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})"
        match = re.search(window_pattern, output)
        
        if match:
            return match.group(1), match.group(2)
        
        # Alternative patterns
        alt_patterns = [
            r"Session:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})",
            r"Night:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})",
            r"Twilight:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})"
        ]
        
        for pattern in alt_patterns:
            match = re.search(pattern, output)
            if match:
                return match.group(1), match.group(2)
        
        return None, None
    
    def parse_object_count(self, output: str) -> int:
        """Parse object count from frontend output"""
        # Look for patterns indicating object count
        count_patterns = [
            r"(\d+)\s+objects?\s+visible",
            r"Found\s+(\d+)\s+objects?",
            r"Total\s+objects?:\s*(\d+)",
            r"Objects?\s+selected:\s*(\d+)",
            r"Visible\s+objects?:\s*(\d+)"
        ]
        
        for pattern in count_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                # Return the last (usually most relevant) count found
                return int(matches[-1])
        
        # Count lines that look like object entries
        object_lines = re.findall(r"^\s*[A-Z]+\d+|^\s*M\d+|^\s*NGC\d+", output, re.MULTILINE)
        if object_lines:
            return len(object_lines)
        
        return 0
    
    def test_object_count_variations(self) -> Dict[str, Dict[str, Any]]:
        """Test that object counts vary correctly by twilight type"""
        results = {}
        
        for scenario_name, scenario in self.scenarios.items():
            if scenario_name == 'test_parameters':
                continue
            
            try:
                # Set configuration
                twilight_type = scenario['config']['twilight_type']
                self.set_twilight_config(twilight_type)
                
                # Test astronightplanner.py
                result = subprocess.run([
                    'python', 'astronightplanner.py', '--report-only'
                ], capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..', '..'))
                
                if result.returncode == 0:
                    output = result.stdout
                    start_time, end_time = self.parse_observation_window(output)
                    object_count = self.parse_object_count(output)
                    
                    results[scenario_name] = {
                        'twilight_type': twilight_type,
                        'observation_window': f"{start_time} - {end_time}" if start_time else "Not found",
                        'object_count': object_count,
                        'expected_range': scenario['expected_objects_range'],
                        'within_expected_range': (
                            scenario['expected_objects_range'][0] <= object_count <= scenario['expected_objects_range'][1]
                        ) if object_count > 0 else False,
                        'output_sample': output[:500] + "..." if len(output) > 500 else output
                    }
                else:
                    results[scenario_name] = {
                        'error': f"Command failed: {result.stderr}",
                        'twilight_type': twilight_type
                    }
                    
            except Exception as e:
                results[scenario_name] = {
                    'error': f"Exception: {e}",
                    'twilight_type': twilight_type
                }
        
        return results
    
    def test_observation_window_calculations(self) -> Dict[str, Dict[str, Any]]:
        """Test that observation windows are calculated correctly"""
        results = {}
        
        for scenario_name, scenario in self.scenarios.items():
            if scenario_name == 'test_parameters':
                continue
            
            try:
                # Set configuration
                twilight_type = scenario['config']['twilight_type']
                self.set_twilight_config(twilight_type)
                
                # Test observation window calculation
                result = subprocess.run([
                    'python', 'astronightplanner.py', '--report-only'
                ], capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..', '..'))
                
                if result.returncode == 0:
                    output = result.stdout
                    start_time, end_time = self.parse_observation_window(output)
                    
                    results[scenario_name] = {
                        'twilight_type': twilight_type,
                        'calculated_window': f"{start_time} - {end_time}" if start_time else "Not found",
                        'expected_window': scenario['expected_window'],
                        'window_matches': f"{start_time} - {end_time}" == scenario['expected_window'] if start_time else False
                    }
                else:
                    results[scenario_name] = {
                        'error': f"Command failed: {result.stderr}",
                        'twilight_type': twilight_type
                    }
                    
            except Exception as e:
                results[scenario_name] = {
                    'error': f"Exception: {e}",
                    'twilight_type': twilight_type
                }
        
        return results
    
    def test_multi_night_object_handling(self) -> Dict[str, Any]:
        """Test multi-night object handling (placeholder for Phase 2)"""
        return {
            'status': 'not_implemented',
            'note': 'Multi-night mode will be implemented in Phase 2'
        }
    
    def test_mobile_app_configuration_integration(self) -> Dict[str, Any]:
        """Test mobile app configuration integration (placeholder for Phase 3)"""
        return {
            'status': 'not_implemented', 
            'note': 'Mobile app integration will be tested in Phase 3'
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all consistency tests"""
        print("Starting Frontend Consistency Tests...")
        
        # Backup original configuration
        self.backup_config()
        
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'twilight_configuration_loading': self.test_twilight_configuration_loading(),
                'object_count_variations': self.test_object_count_variations(),
                'observation_window_calculations': self.test_observation_window_calculations(),
                'multi_night_object_handling': self.test_multi_night_object_handling(),
                'mobile_app_configuration_integration': self.test_mobile_app_configuration_integration()
            }
            
            # Generate summary
            results['summary'] = self.generate_test_summary(results)
            
            return results
            
        finally:
            # Always restore original configuration
            self.restore_config()
    
    def generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of test results"""
        summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'critical_issues': [],
            'warnings': []
        }
        
        # Analyze twilight configuration loading
        config_results = results.get('twilight_configuration_loading', {})
        for scenario, passed in config_results.items():
            summary['total_tests'] += 1
            if passed:
                summary['passed_tests'] += 1
            else:
                summary['failed_tests'] += 1
                summary['critical_issues'].append(f"Twilight configuration loading failed for {scenario}")
        
        # Analyze object count variations
        count_results = results.get('object_count_variations', {})
        object_counts = []
        for scenario, result in count_results.items():
            if 'error' not in result:
                summary['total_tests'] += 1
                if result.get('within_expected_range', False):
                    summary['passed_tests'] += 1
                else:
                    summary['failed_tests'] += 1
                    summary['warnings'].append(f"Object count for {scenario} outside expected range: {result.get('object_count', 0)}")
                
                object_counts.append((scenario, result.get('object_count', 0)))
        
        # Check if object counts vary (critical issue if they don't)
        unique_counts = set(count for _, count in object_counts)
        if len(unique_counts) <= 1 and len(object_counts) > 1:
            summary['critical_issues'].append("Object counts are identical across different twilight types - hardcoded sun altitude issue confirmed")
        
        return summary


def main():
    """Run the frontend consistency tests"""
    tester = FrontendConsistencyTester()
    results = tester.run_all_tests()
    
    # Save results
    results_file = os.path.join(os.path.dirname(__file__), 'baseline_broken.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("FRONTEND CONSISTENCY TEST RESULTS")
    print("="*60)
    
    summary = results.get('summary', {})
    print(f"Total Tests: {summary.get('total_tests', 0)}")
    print(f"Passed: {summary.get('passed_tests', 0)}")
    print(f"Failed: {summary.get('failed_tests', 0)}")
    
    if summary.get('critical_issues'):
        print("\nCRITICAL ISSUES:")
        for issue in summary['critical_issues']:
            print(f"  ⚠️  {issue}")
    
    if summary.get('warnings'):
        print("\nWARNINGS:")
        for warning in summary['warnings']:
            print(f"  ⚠️  {warning}")
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    main() 