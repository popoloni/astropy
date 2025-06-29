#!/usr/bin/env python3
"""
Automated Test Runner for run_mosaic_plots.py
Captures mosaic analysis output and validates observation period consistency.
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


class MosaicPlotsTester:
    """Test runner for run_mosaic_plots.py wrapper"""
    
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
    
    def run_mosaic_plots(self, args: List[str] = None) -> Tuple[int, str, str]:
        """Run run_mosaic_plots.py with given arguments"""
        cmd = ['python', 'wrappers/run_mosaic_plots.py']
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
        return result.returncode, result.stdout, result.stderr
    
    def parse_mosaic_analysis(self, output: str) -> Dict[str, Any]:
        """Parse mosaic analysis data from output"""
        analysis = {
            'mosaic_groups': [],
            'total_objects': 0,
            'observation_windows': [],
            'execution_summary': {}
        }
        
        # Look for mosaic group information
        group_pattern = r"Mosaic Group\s+(\d+).*?(\d+)\s+objects?"
        group_matches = re.findall(group_pattern, output, re.IGNORECASE)
        
        for match in group_matches:
            group_num, object_count = match
            analysis['mosaic_groups'].append({
                'group_number': int(group_num),
                'object_count': int(object_count)
            })
            analysis['total_objects'] += int(object_count)
        
        # Parse observation windows
        window_patterns = [
            r"Observation Window:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})",
            r"Session:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})",
            r"Night:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})"
        ]
        
        for pattern in window_patterns:
            matches = re.findall(pattern, output)
            for match in matches:
                window = f"{match[0]} - {match[1]}"
                if window not in analysis['observation_windows']:
                    analysis['observation_windows'].append(window)
        
        # Parse execution summary
        summary_patterns = [
            (r"Total execution time:\s*([\d.]+)", 'execution_time'),
            (r"Objects processed:\s*(\d+)", 'objects_processed'),
            (r"Plots generated:\s*(\d+)", 'plots_generated'),
            (r"Analysis completed:\s*(\w+)", 'analysis_completed')
        ]
        
        for pattern, key in summary_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                analysis['execution_summary'][key] = match.group(1)
        
        return analysis
    
    def parse_object_details(self, output: str) -> List[Dict[str, Any]]:
        """Parse detailed object information from output"""
        objects = []
        
        # Look for object entries with mosaic information
        object_pattern = r"(M\d+|NGC\d+|IC\d+|[A-Z]+\s*\d+).*?Group\s+(\d+).*?(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})"
        matches = re.findall(object_pattern, output, re.MULTILINE)
        
        for match in matches:
            objects.append({
                'name': match[0].strip(),
                'mosaic_group': int(match[1]),
                'start_time': match[2],
                'end_time': match[3]
            })
        
        return objects
    
    def parse_mosaic_statistics(self, output: str) -> Dict[str, Any]:
        """Parse mosaic-specific statistics from output"""
        stats = {
            'total_mosaic_groups': 0,
            'average_objects_per_group': 0,
            'largest_group_size': 0,
            'smallest_group_size': 0,
            'coverage_efficiency': 0
        }
        
        # Parse total groups
        groups_match = re.search(r"Total\s+mosaic\s+groups:\s*(\d+)", output, re.IGNORECASE)
        if groups_match:
            stats['total_mosaic_groups'] = int(groups_match.group(1))
        
        # Parse efficiency metrics
        efficiency_match = re.search(r"Coverage\s+efficiency:\s*([\d.]+)%", output, re.IGNORECASE)
        if efficiency_match:
            stats['coverage_efficiency'] = float(efficiency_match.group(1))
        
        # Parse group size statistics
        avg_match = re.search(r"Average\s+objects\s+per\s+group:\s*([\d.]+)", output, re.IGNORECASE)
        if avg_match:
            stats['average_objects_per_group'] = float(avg_match.group(1))
        
        largest_match = re.search(r"Largest\s+group:\s*(\d+)", output, re.IGNORECASE)
        if largest_match:
            stats['largest_group_size'] = int(largest_match.group(1))
        
        smallest_match = re.search(r"Smallest\s+group:\s*(\d+)", output, re.IGNORECASE)
        if smallest_match:
            stats['smallest_group_size'] = int(smallest_match.group(1))
        
        return stats
    
    def test_twilight_scenarios(self) -> Dict[str, Any]:
        """Test mosaic plots with different twilight scenarios"""
        results = {}
        
        for scenario_name, scenario in self.scenarios.items():
            if scenario_name == 'test_parameters':
                continue
            
            print(f"Testing {scenario_name} for mosaic plots...")
            
            try:
                # Set configuration
                twilight_type = scenario['config']['twilight_type']
                self.set_twilight_config(twilight_type)
                
                # Run mosaic plots (with no-plots to avoid GUI issues)
                returncode, stdout, stderr = self.run_mosaic_plots(['--no-plots'])
                
                if returncode == 0:
                    # Parse results
                    mosaic_analysis = self.parse_mosaic_analysis(stdout)
                    object_details = self.parse_object_details(stdout)
                    mosaic_statistics = self.parse_mosaic_statistics(stdout)
                    
                    results[scenario_name] = {
                        'success': True,
                        'twilight_type': twilight_type,
                        'mosaic_analysis': mosaic_analysis,
                        'object_details': object_details[:10],  # First 10 objects
                        'mosaic_statistics': mosaic_statistics,
                        'total_objects': mosaic_analysis['total_objects'],
                        'total_groups': len(mosaic_analysis['mosaic_groups']),
                        'observation_windows': mosaic_analysis['observation_windows'],
                        'output_length': len(stdout)
                    }
                else:
                    results[scenario_name] = {
                        'success': False,
                        'twilight_type': twilight_type,
                        'error': f"Command failed with code {returncode}",
                        'stderr': stderr[:300] if stderr else "",
                        'stdout_sample': stdout[:300] if stdout else ""
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
                'name': 'no_plots',
                'args': ['--no-plots'],
                'description': 'Test without plots generation'
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
                returncode, stdout, stderr = self.run_mosaic_plots(test_case['args'])
                
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
    
    def validate_mosaic_consistency(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mosaic analysis consistency across twilight scenarios"""
        validation = {
            'object_count_variations': False,
            'observation_window_variations': False,
            'mosaic_group_variations': False,
            'issues': [],
            'statistics': {}
        }
        
        # Collect statistics for analysis
        scenario_stats = {}
        
        for scenario_name, result in results.items():
            if not result.get('success', False):
                continue
            
            scenario_stats[scenario_name] = {
                'twilight_type': result.get('twilight_type', ''),
                'total_objects': result.get('total_objects', 0),
                'total_groups': result.get('total_groups', 0),
                'observation_windows': result.get('observation_windows', []),
                'mosaic_statistics': result.get('mosaic_statistics', {})
            }
        
        # Check for variations between twilight types
        if len(scenario_stats) > 1:
            # Compare object counts
            object_counts = [(name, stats['total_objects']) for name, stats in scenario_stats.items()]
            unique_counts = set(count for _, count in object_counts)
            validation['object_count_variations'] = len(unique_counts) > 1
            
            if not validation['object_count_variations']:
                validation['issues'].append(
                    "Object counts are identical across different twilight types - possible hardcoded issue"
                )
            
            # Compare observation windows
            all_windows = []
            for stats in scenario_stats.values():
                for window in stats['observation_windows']:
                    if window not in all_windows:
                        all_windows.append(window)
            
            validation['observation_window_variations'] = len(all_windows) > 1
            
            if not validation['observation_window_variations']:
                validation['issues'].append(
                    "Observation windows are identical across different twilight types"
                )
            
            # Compare mosaic group counts
            group_counts = [(name, stats['total_groups']) for name, stats in scenario_stats.items()]
            unique_group_counts = set(count for _, count in group_counts)
            validation['mosaic_group_variations'] = len(unique_group_counts) > 1
            
            if not validation['mosaic_group_variations']:
                validation['issues'].append(
                    "Mosaic group counts are identical across different twilight types"
                )
        
        validation['statistics'] = scenario_stats
        
        return validation
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all mosaic plots tests"""
        print("Starting Mosaic Plots Tests...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'frontend': 'run_mosaic_plots.py',
            'twilight_scenarios': self.test_twilight_scenarios(),
            'command_line_options': self.test_command_line_options()
        }
        
        # Add validation
        results['validation'] = self.validate_mosaic_consistency(results['twilight_scenarios'])
        
        return results


def main():
    """Run the mosaic plots tests"""
    tester = MosaicPlotsTester()
    results = tester.run_all_tests()
    
    # Save results
    results_file = os.path.join(os.path.dirname(__file__), 'mosaic_plots_test_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*50)
    print("MOSAIC PLOTS TEST RESULTS")
    print("="*50)
    
    validation = results.get('validation', {})
    twilight_results = results.get('twilight_scenarios', {})
    
    successful_scenarios = sum(1 for r in twilight_results.values() if r.get('success', False))
    total_scenarios = len(twilight_results)
    
    print(f"Total Scenarios: {total_scenarios}")
    print(f"Successful Scenarios: {successful_scenarios}")
    print(f"Failed Scenarios: {total_scenarios - successful_scenarios}")
    print(f"Object Count Variations: {'✓' if validation.get('object_count_variations', False) else '✗'}")
    print(f"Observation Window Variations: {'✓' if validation.get('observation_window_variations', False) else '✗'}")
    print(f"Mosaic Group Variations: {'✓' if validation.get('mosaic_group_variations', False) else '✗'}")
    
    if validation.get('issues'):
        print("\nISSUES DETECTED:")
        for issue in validation['issues']:
            print(f"  ⚠️  {issue}")
    
    # Print statistics summary
    stats = validation.get('statistics', {})
    if stats:
        print("\nSTATISTICS SUMMARY:")
        for scenario_name, scenario_stats in stats.items():
            print(f"  {scenario_name} ({scenario_stats['twilight_type']}):")
            print(f"    Total Objects: {scenario_stats['total_objects']}")
            print(f"    Total Groups: {scenario_stats['total_groups']}")
            print(f"    Unique Windows: {len(scenario_stats['observation_windows'])}")
            
            mosaic_stats = scenario_stats.get('mosaic_statistics', {})
            if mosaic_stats.get('coverage_efficiency'):
                print(f"    Coverage Efficiency: {mosaic_stats['coverage_efficiency']:.1f}%")
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    main() 