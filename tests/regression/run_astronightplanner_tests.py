#!/usr/bin/env python3
"""
Automated Test Runner for astronightplanner.py
Parses output for observation windows and object counts, validates against expected ranges.
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


class AstroNightPlannerTester:
    """Test runner for astronightplanner.py frontend"""
    
    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
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
        config_path = os.path.join(self.base_dir, 'config.json')
        
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
    
    def run_astronightplanner(self, args: List[str] = None) -> Tuple[int, str, str]:
        """Run astronightplanner.py with given arguments"""
        cmd = ['python', 'astronightplanner.py']
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
        return result.returncode, result.stdout, result.stderr
    
    def parse_observation_window(self, output: str) -> Tuple[str, str]:
        """Parse observation window from output"""
        patterns = [
            r"Observation Window:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})",
            r"Session:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})",
            r"Night:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})",
            r"Twilight.*?(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1), match.group(2)
        
        return None, None
    
    def parse_object_count(self, output: str) -> int:
        """Parse object count from output"""
        # Look for explicit count statements
        count_patterns = [
            r"(\d+)\s+objects?\s+(?:visible|selected|found)",
            r"Found\s+(\d+)\s+objects?",
            r"Total\s+objects?:\s*(\d+)",
            r"Visible\s+objects?:\s*(\d+)"
        ]
        
        for pattern in count_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                return int(matches[-1])
        
        # Count object entries in output
        object_patterns = [
            r"^\s*M\d+",  # Messier objects
            r"^\s*NGC\d+",  # NGC objects
            r"^\s*IC\d+",   # IC objects
            r"^\s*[A-Z]{2,}\s+\d+",  # Other catalog objects
        ]
        
        total_count = 0
        for pattern in object_patterns:
            matches = re.findall(pattern, output, re.MULTILINE)
            total_count += len(matches)
        
        return total_count
    
    def parse_twilight_type(self, output: str) -> str:
        """Parse twilight type from output"""
        patterns = [
            r"Twilight Type:\s*(\w+)",
            r"Using\s+(\w+)\s+twilight",
            r"(\w+)\s+Twilight"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        
        return "unknown"
    
    def extract_object_list(self, output: str) -> List[Dict[str, Any]]:
        """Extract detailed object information from output"""
        objects = []
        
        # Look for object entries with details
        object_pattern = r"(M\d+|NGC\d+|IC\d+|[A-Z]+\s*\d+).*?(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})"
        matches = re.findall(object_pattern, output, re.MULTILINE)
        
        for match in matches:
            objects.append({
                'name': match[0].strip(),
                'start_time': match[1],
                'end_time': match[2]
            })
        
        return objects
    
    def test_twilight_scenarios(self) -> Dict[str, Any]:
        """Test all twilight scenarios"""
        results = {}
        
        for scenario_name, scenario in self.scenarios.items():
            if scenario_name == 'test_parameters':
                continue
            
            print(f"Testing {scenario_name}...")
            
            try:
                # Set configuration
                twilight_type = scenario['config']['twilight_type']
                self.set_twilight_config(twilight_type)
                
                # Run astronightplanner
                returncode, stdout, stderr = self.run_astronightplanner(['--report-only'])
                
                if returncode == 0:
                    # Parse results
                    start_time, end_time = self.parse_observation_window(stdout)
                    object_count = self.parse_object_count(stdout)
                    detected_twilight = self.parse_twilight_type(stdout)
                    object_list = self.extract_object_list(stdout)
                    
                    results[scenario_name] = {
                        'success': True,
                        'twilight_type': twilight_type,
                        'detected_twilight': detected_twilight,
                        'observation_window': {
                            'start': start_time,
                            'end': end_time,
                            'formatted': f"{start_time} - {end_time}" if start_time else "Not found"
                        },
                        'object_count': object_count,
                        'expected_range': scenario.get('expected_objects_range', [0, 100]),
                        'within_expected_range': (
                            scenario['expected_objects_range'][0] <= object_count <= scenario['expected_objects_range'][1]
                        ) if object_count > 0 else False,
                        'objects': object_list[:5],  # First 5 objects for verification
                        'output_length': len(stdout),
                        'execution_time': None  # Could add timing if needed
                    }
                else:
                    results[scenario_name] = {
                        'success': False,
                        'twilight_type': twilight_type,
                        'error': f"Command failed with code {returncode}",
                        'stderr': stderr,
                        'stdout_sample': stdout[:200] if stdout else ""
                    }
                    
            except Exception as e:
                results[scenario_name] = {
                    'success': False,
                    'twilight_type': twilight_type,
                    'error': f"Exception: {str(e)}"
                }
        
        return results
    
    def test_command_line_options(self) -> Dict[str, Any]:
        """Test various command line options"""
        test_cases = [
            {
                'name': 'report_only',
                'args': ['--report-only'],
                'description': 'Test report-only mode'
            },
            {
                'name': 'no_plots',
                'args': ['--no-plots'],
                'description': 'Test without plots'
            },
            {
                'name': 'help',
                'args': ['--help'],
                'description': 'Test help output'
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            try:
                returncode, stdout, stderr = self.run_astronightplanner(test_case['args'])
                
                results[test_case['name']] = {
                    'success': returncode == 0,
                    'returncode': returncode,
                    'stdout_length': len(stdout),
                    'stderr_length': len(stderr),
                    'description': test_case['description']
                }
                
            except Exception as e:
                results[test_case['name']] = {
                    'success': False,
                    'error': str(e),
                    'description': test_case['description']
                }
        
        return results
    
    def validate_against_expected(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate results against expected values"""
        validation = {
            'total_scenarios': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'twilight_consistency': True,
            'object_count_variations': False,
            'observation_window_variations': False,
            'issues': []
        }
        
        object_counts = []
        observation_windows = []
        
        for scenario_name, result in results.items():
            if not isinstance(result, dict) or 'success' not in result:
                continue
                
            validation['total_scenarios'] += 1
            
            if result['success']:
                validation['successful_runs'] += 1
                
                # Collect data for analysis
                if 'object_count' in result:
                    object_counts.append((scenario_name, result['object_count']))
                
                if 'observation_window' in result and result['observation_window']['formatted'] != "Not found":
                    observation_windows.append((scenario_name, result['observation_window']['formatted']))
                
                # Check twilight consistency
                expected_twilight = result.get('twilight_type', '')
                detected_twilight = result.get('detected_twilight', '')
                if expected_twilight and detected_twilight and expected_twilight != detected_twilight:
                    validation['twilight_consistency'] = False
                    validation['issues'].append(f"Twilight mismatch in {scenario_name}: expected {expected_twilight}, detected {detected_twilight}")
            else:
                validation['failed_runs'] += 1
                validation['issues'].append(f"Failed to run {scenario_name}: {result.get('error', 'Unknown error')}")
        
        # Check for variations in object counts
        unique_counts = set(count for _, count in object_counts)
        validation['object_count_variations'] = len(unique_counts) > 1
        
        if not validation['object_count_variations'] and len(object_counts) > 1:
            validation['issues'].append("Object counts are identical across different twilight types - possible hardcoded issue")
        
        # Check for variations in observation windows
        unique_windows = set(window for _, window in observation_windows)
        validation['observation_window_variations'] = len(unique_windows) > 1
        
        if not validation['observation_window_variations'] and len(observation_windows) > 1:
            validation['issues'].append("Observation windows are identical across different twilight types")
        
        return validation
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all astronightplanner tests"""
        print("Starting AstroNightPlanner Tests...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'frontend': 'astronightplanner.py',
            'twilight_scenarios': self.test_twilight_scenarios(),
            'command_line_options': self.test_command_line_options()
        }
        
        # Add validation
        results['validation'] = self.validate_against_expected(results['twilight_scenarios'])
        
        return results


def main():
    """Run the astronightplanner tests"""
    tester = AstroNightPlannerTester()
    results = tester.run_all_tests()
    
    # Save results
    results_file = os.path.join(os.path.dirname(__file__), 'astronightplanner_test_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*50)
    print("ASTRONIGHTPLANNER TEST RESULTS")
    print("="*50)
    
    validation = results.get('validation', {})
    print(f"Total Scenarios: {validation.get('total_scenarios', 0)}")
    print(f"Successful Runs: {validation.get('successful_runs', 0)}")
    print(f"Failed Runs: {validation.get('failed_runs', 0)}")
    print(f"Twilight Consistency: {'✓' if validation.get('twilight_consistency', False) else '✗'}")
    print(f"Object Count Variations: {'✓' if validation.get('object_count_variations', False) else '✗'}")
    print(f"Observation Window Variations: {'✓' if validation.get('observation_window_variations', False) else '✗'}")
    
    if validation.get('issues'):
        print("\nISSUES DETECTED:")
        for issue in validation['issues']:
            print(f"  ⚠️  {issue}")
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    main() 