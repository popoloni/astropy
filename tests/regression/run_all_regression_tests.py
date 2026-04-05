#!/usr/bin/env python3
"""
Master Regression Test Runner for DSO Selection Algorithm
Coordinates all frontend tests and generates comprehensive comparison reports.
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import individual test runners
from test_frontend_consistency import FrontendConsistencyTester
from run_astronightplanner_tests import AstroNightPlannerTester
from run_astroseasonplanner_tests import AstroSeasonPlannerTester
from run_mosaic_plots_tests import MosaicPlotsTester
from run_mobile_app_tests import MobileAppTester


class MasterRegressionTester:
    """Master test runner for all frontend regression tests"""
    
    def __init__(self, phase: str = "baseline"):
        self.phase = phase
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        self.results_dir = os.path.dirname(__file__)
        self.all_results = {}
        
    def run_frontend_consistency_tests(self) -> Dict[str, Any]:
        """Run the main frontend consistency tests"""
        print("Running Frontend Consistency Tests...")
        try:
            tester = FrontendConsistencyTester()
            return tester.run_all_tests()
        except Exception as e:
            return {
                'error': f"Frontend consistency tests failed: {e}",
                'timestamp': datetime.now().isoformat()
            }
    
    def run_astronightplanner_tests(self) -> Dict[str, Any]:
        """Run astronightplanner.py specific tests"""
        print("Running AstroNightPlanner Tests...")
        try:
            tester = AstroNightPlannerTester()
            return tester.run_all_tests()
        except Exception as e:
            return {
                'error': f"AstroNightPlanner tests failed: {e}",
                'timestamp': datetime.now().isoformat()
            }
    
    def run_astroseasonplanner_tests(self) -> Dict[str, Any]:
        """Run astroseasonplanner.py specific tests"""
        print("Running AstroSeasonPlanner Tests...")
        try:
            tester = AstroSeasonPlannerTester()
            return tester.run_all_tests()
        except Exception as e:
            return {
                'error': f"AstroSeasonPlanner tests failed: {e}",
                'timestamp': datetime.now().isoformat()
            }
    
    def run_mosaic_plots_tests(self) -> Dict[str, Any]:
        """Run mosaic plots wrapper tests"""
        print("Running Mosaic Plots Tests...")
        try:
            tester = MosaicPlotsTester()
            return tester.run_all_tests()
        except Exception as e:
            return {
                'error': f"Mosaic plots tests failed: {e}",
                'timestamp': datetime.now().isoformat()
            }
    
    def run_mobile_app_tests(self) -> Dict[str, Any]:
        """Run mobile app configuration tests"""
        print("Running Mobile App Tests...")
        try:
            tester = MobileAppTester()
            return tester.run_all_tests()
        except Exception as e:
            return {
                'error': f"Mobile app tests failed: {e}",
                'timestamp': datetime.now().isoformat()
            }
    
    def save_results(self, filename: str = None) -> str:
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.phase}_regression_results_{timestamp}.json"
        
        results_path = os.path.join(self.results_dir, filename)
        
        with open(results_path, 'w') as f:
            json.dump(self.all_results, f, indent=2)
        
        return results_path
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all regression tests and generate comprehensive report"""
        print(f"Starting Master Regression Test Suite - Phase: {self.phase}")
        print("=" * 70)
        
        # Run all individual test suites
        self.all_results = {
            'timestamp': datetime.now().isoformat(),
            'phase': self.phase,
            'frontend_consistency_results': self.run_frontend_consistency_tests(),
            'astronightplanner_results': self.run_astronightplanner_tests(),
            'astroseasonplanner_results': self.run_astroseasonplanner_tests(),
            'mosaic_plots_results': self.run_mosaic_plots_tests(),
            'mobile_app_results': self.run_mobile_app_tests()
        }
        
        return self.all_results
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("MASTER REGRESSION TEST SUMMARY")
        print("=" * 70)
        
        print(f"Phase: {self.phase}")
        
        # Individual frontend summaries
        print("\nINDIVIDUAL FRONTEND RESULTS:")
        
        frontends = [
            ('Frontend Consistency', 'frontend_consistency_results'),
            ('AstroNightPlanner', 'astronightplanner_results'),
            ('AstroSeasonPlanner', 'astroseasonplanner_results'),
            ('Mosaic Plots', 'mosaic_plots_results'),
            ('Mobile App', 'mobile_app_results')
        ]
        
        for name, key in frontends:
            result = self.all_results.get(key, {})
            if 'error' in result:
                print(f"  {name}: ❌ FAILED - {result['error']}")
            else:
                print(f"  {name}: ✅ COMPLETED")


def main():
    """Main entry point for regression testing"""
    parser = argparse.ArgumentParser(description='Master Regression Test Runner for DSO Selection Algorithm')
    parser.add_argument('--phase', choices=['baseline', '1', '2', '3', 'final'], default='baseline',
                        help='Test phase to run')
    parser.add_argument('--baseline', action='store_true', help='Run baseline tests')
    parser.add_argument('--save-as', help='Custom filename for results')
    
    args = parser.parse_args()
    
    # Determine phase
    phase = args.phase
    if args.baseline:
        phase = 'baseline'
    
    # Run tests
    tester = MasterRegressionTester(phase=phase)
    results = tester.run_all_tests()
    
    # Save results
    results_file = tester.save_results(args.save_as)
    
    # Print summary
    tester.print_summary()
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    main() 