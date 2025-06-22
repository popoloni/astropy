#!/usr/bin/env python3
"""
Automated Test Runner for astroseasonplanner.py
Extracts weekly analysis data and validates twilight period consistency.
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


class AstroSeasonPlannerTester:
    """Test runner for astroseasonplanner.py frontend"""
    
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
    
    def run_astroseasonplanner(self, args: List[str] = None) -> Tuple[int, str, str]:
        """Run astroseasonplanner.py with given arguments"""
        cmd = ['python', 'astroseasonplanner.py']
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
        return result.returncode, result.stdout, result.stderr
    
    def parse_weekly_analysis(self, output: str) -> List[Dict[str, Any]]:
        """Parse weekly analysis data from output"""
        weeks = []
        
        # Look for weekly analysis sections
        week_pattern = r"Week\s+(\d+).*?(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})"
        week_matches = re.findall(week_pattern, output, re.IGNORECASE)
        
        for match in week_matches:
            week_num, start_date, end_date = match
            
            # Look for object count in this week's section
            week_section_start = output.find(f"Week {week_num}")
            next_week_start = output.find(f"Week {int(week_num)+1}")
            if next_week_start == -1:
                week_section = output[week_section_start:]
            else:
                week_section = output[week_section_start:next_week_start]
            
            # Parse object count for this week
            object_count = self.parse_object_count(week_section)
            
            # Parse observation windows for this week
            observation_windows = self.parse_observation_windows(week_section)
            
            weeks.append({
                'week_number': int(week_num),
                'start_date': start_date,
                'end_date': end_date,
                'object_count': object_count,
                'observation_windows': observation_windows
            })
        
        return weeks
    
    def parse_object_count(self, text: str) -> int:
        """Parse object count from text section"""
        count_patterns = [
            r"(\d+)\s+objects?\s+(?:visible|selected|found)",
            r"Found\s+(\d+)\s+objects?",
            r"Total\s+objects?:\s*(\d+)",
            r"Visible\s+objects?:\s*(\d+)"
        ]
        
        for pattern in count_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return int(matches[-1])
        
        # Count object entries
        object_patterns = [
            r"^\s*M\d+",
            r"^\s*NGC\d+", 
            r"^\s*IC\d+",
            r"^\s*[A-Z]{2,}\s+\d+"
        ]
        
        total_count = 0
        for pattern in object_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            total_count += len(matches)
        
        return total_count
    
    def parse_observation_windows(self, text: str) -> List[str]:
        """Parse observation windows from text section"""
        window_patterns = [
            r"(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})",
            r"Session:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})",
            r"Night:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})"
        ]
        
        windows = []
        for pattern in window_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                windows.append(f"{match[0]} - {match[1]}")
        
        return list(set(windows))  # Remove duplicates
    
    def parse_quarterly_summary(self, output: str) -> Dict[str, Any]:
        """Parse quarterly summary information"""
        summary = {
            'total_weeks': 0,
            'total_objects': 0,
            'average_objects_per_week': 0,
            'observation_periods': []
        }
        
        # Look for quarterly summary
        summary_pattern = r"Quarter.*?Summary"
        summary_match = re.search(summary_pattern, output, re.IGNORECASE | re.DOTALL)
        
        if summary_match:
            summary_text = summary_match.group()
            
            # Parse total weeks
            weeks_match = re.search(r"(\d+)\s+weeks?", summary_text, re.IGNORECASE)
            if weeks_match:
                summary['total_weeks'] = int(weeks_match.group(1))
            
            # Parse total objects
            objects_match = re.search(r"(\d+)\s+total\s+objects?", summary_text, re.IGNORECASE)
            if objects_match:
                summary['total_objects'] = int(objects_match.group(1))
            
            # Calculate average
            if summary['total_weeks'] > 0:
                summary['average_objects_per_week'] = summary['total_objects'] / summary['total_weeks']
        
        return summary
    
    def test_quarterly_scenarios(self) -> Dict[str, Any]:
        """Test quarterly analysis with different twilight scenarios"""
        results = {}
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        
        for scenario_name, scenario in self.scenarios.items():
            if scenario_name == 'test_parameters':
                continue
            
            print(f"Testing {scenario_name} for quarterly analysis...")
            
            try:
                # Set configuration
                twilight_type = scenario['config']['twilight_type']
                self.set_twilight_config(twilight_type)
                
                quarter_results = {}
                
                # Test each quarter
                for quarter in quarters:
                    print(f"  Testing {quarter}...")
                    
                    returncode, stdout, stderr = self.run_astroseasonplanner([
                        '--quarter', quarter, '--no-plots'
                    ])
                    
                    if returncode == 0:
                        weekly_analysis = self.parse_weekly_analysis(stdout)
                        quarterly_summary = self.parse_quarterly_summary(stdout)
                        
                        quarter_results[quarter] = {
                            'success': True,
                            'weekly_analysis': weekly_analysis,
                            'quarterly_summary': quarterly_summary,
                            'total_weeks_analyzed': len(weekly_analysis),
                            'output_length': len(stdout)
                        }
                    else:
                        quarter_results[quarter] = {
                            'success': False,
                            'error': f"Command failed with code {returncode}",
                            'stderr': stderr[:200] if stderr else ""
                        }
                
                results[scenario_name] = {
                    'twilight_type': twilight_type,
                    'quarters': quarter_results,
                    'success': all(q.get('success', False) for q in quarter_results.values())
                }
                
            except Exception as e:
                results[scenario_name] = {
                    'twilight_type': twilight_type,
                    'error': f"Exception: {str(e)}",
                    'success': False
                }
        
        return results
    
    def test_command_line_options(self) -> Dict[str, Any]:
        """Test various command line options"""
        test_cases = [
            {
                'name': 'quarter_q2',
                'args': ['--quarter', 'Q2', '--no-plots'],
                'description': 'Test Q2 analysis without plots'
            },
            {
                'name': 'help',
                'args': ['--help'],
                'description': 'Test help output'
            },
            {
                'name': 'all_quarters',
                'args': ['--no-plots'],
                'description': 'Test all quarters without plots'
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            try:
                returncode, stdout, stderr = self.run_astroseasonplanner(test_case['args'])
                
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
    
    def validate_twilight_consistency(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate twilight period consistency across scenarios"""
        validation = {
            'consistent_across_quarters': True,
            'object_count_variations': False,
            'twilight_period_variations': False,
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
                'total_objects_across_quarters': 0,
                'average_objects_per_week': 0,
                'observation_windows': []
            }
            
            quarters = result.get('quarters', {})
            total_weeks = 0
            total_objects = 0
            
            for quarter, quarter_data in quarters.items():
                if quarter_data.get('success', False):
                    weekly_analysis = quarter_data.get('weekly_analysis', [])
                    total_weeks += len(weekly_analysis)
                    
                    for week in weekly_analysis:
                        total_objects += week.get('object_count', 0)
                        for window in week.get('observation_windows', []):
                            if window not in scenario_stats[scenario_name]['observation_windows']:
                                scenario_stats[scenario_name]['observation_windows'].append(window)
            
            scenario_stats[scenario_name]['total_objects_across_quarters'] = total_objects
            if total_weeks > 0:
                scenario_stats[scenario_name]['average_objects_per_week'] = total_objects / total_weeks
        
        # Check for variations between twilight types
        twilight_types = list(set(stats['twilight_type'] for stats in scenario_stats.values()))
        
        if len(twilight_types) > 1:
            # Compare object counts between twilight types
            object_counts = [(name, stats['total_objects_across_quarters']) 
                           for name, stats in scenario_stats.items()]
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
            
            validation['twilight_period_variations'] = len(all_windows) > 1
            
            if not validation['twilight_period_variations']:
                validation['issues'].append(
                    "Observation windows are identical across different twilight types"
                )
        
        validation['statistics'] = scenario_stats
        
        return validation
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all astroseasonplanner tests"""
        print("Starting AstroSeasonPlanner Tests...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'frontend': 'astroseasonplanner.py',
            'quarterly_scenarios': self.test_quarterly_scenarios(),
            'command_line_options': self.test_command_line_options()
        }
        
        # Add validation
        results['validation'] = self.validate_twilight_consistency(results['quarterly_scenarios'])
        
        return results


def main():
    """Run the astroseasonplanner tests"""
    tester = AstroSeasonPlannerTester()
    results = tester.run_all_tests()
    
    # Save results
    results_file = os.path.join(os.path.dirname(__file__), 'astroseasonplanner_test_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*50)
    print("ASTROSEASONPLANNER TEST RESULTS")
    print("="*50)
    
    validation = results.get('validation', {})
    quarterly_results = results.get('quarterly_scenarios', {})
    
    successful_scenarios = sum(1 for r in quarterly_results.values() if r.get('success', False))
    total_scenarios = len(quarterly_results)
    
    print(f"Total Scenarios: {total_scenarios}")
    print(f"Successful Scenarios: {successful_scenarios}")
    print(f"Failed Scenarios: {total_scenarios - successful_scenarios}")
    print(f"Consistent Across Quarters: {'✓' if validation.get('consistent_across_quarters', False) else '✗'}")
    print(f"Object Count Variations: {'✓' if validation.get('object_count_variations', False) else '✗'}")
    print(f"Twilight Period Variations: {'✓' if validation.get('twilight_period_variations', False) else '✗'}")
    
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
            print(f"    Total Objects: {scenario_stats['total_objects_across_quarters']}")
            print(f"    Avg Objects/Week: {scenario_stats['average_objects_per_week']:.1f}")
            print(f"    Unique Windows: {len(scenario_stats['observation_windows'])}")
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    main() 