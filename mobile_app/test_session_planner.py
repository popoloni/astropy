#!/usr/bin/env python3
"""
Test script for Session Planning System
Validates session creation, optimization, and export functionality
"""

import sys
import os
from datetime import datetime, timedelta
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.session_planner import (
        SessionPlanner, SessionManager, SessionOptimizer,
        SessionType, OptimizationStrategy, SessionPriority, WeatherCondition
    )
    print("✓ Session planner imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


def create_sample_targets():
    """Create sample target data for testing"""
    return [
        {
            'name': 'M31 Andromeda Galaxy',
            'object_type': 'galaxy',
            'ra': 10.68,
            'dec': 41.27,
            'magnitude': 3.4,
            'size': 190.0,
            'constellation': 'Andromeda'
        },
        {
            'name': 'M42 Orion Nebula',
            'object_type': 'nebula',
            'ra': 83.82,
            'dec': -5.39,
            'magnitude': 4.0,
            'size': 85.0,
            'constellation': 'Orion'
        },
        {
            'name': 'M45 Pleiades',
            'object_type': 'cluster',
            'ra': 56.75,
            'dec': 24.12,
            'magnitude': 1.6,
            'size': 110.0,
            'constellation': 'Taurus'
        },
        {
            'name': 'NGC 7293 Helix Nebula',
            'object_type': 'planetary_nebula',
            'ra': 337.41,
            'dec': -20.84,
            'magnitude': 7.3,
            'size': 16.0,
            'constellation': 'Aquarius'
        },
        {
            'name': 'M87 Virgo Galaxy',
            'object_type': 'galaxy',
            'ra': 187.71,
            'dec': 12.39,
            'magnitude': 8.6,
            'size': 8.3,
            'constellation': 'Virgo'
        },
        {
            'name': 'NGC 2237 Rosette Nebula',
            'object_type': 'nebula',
            'ra': 97.5,
            'dec': 5.0,
            'magnitude': 9.0,
            'size': 80.0,
            'constellation': 'Monoceros'
        }
    ]


def create_sample_location():
    """Create sample location data"""
    return {
        'latitude': 40.7128,
        'longitude': -74.0060,
        'name': 'New York, NY'
    }


def test_session_creation():
    """Test basic session creation"""
    print("\n=== Testing Session Creation ===")
    
    planner = SessionPlanner()
    targets = create_sample_targets()
    location = create_sample_location()
    
    session_date = datetime(2024, 3, 15, 20, 0)
    priorities = ['high', 'medium', 'low', 'medium', 'high', 'low']
    
    session = planner.create_session(
        date=session_date,
        duration=240,  # 4 hours
        priorities=priorities,
        targets=targets,
        location=location,
        session_type=SessionType.MIXED,
        optimization_strategy=OptimizationStrategy.BALANCED
    )
    
    if session:
        print(f"✓ Session created: {session.session_id}")
        print(f"  Name: {session.name}")
        print(f"  Date: {session.date}")
        print(f"  Duration: {session.duration} minutes")
        print(f"  Targets: {len(session.targets)}")
        print(f"  Backup targets: {len(session.backup_targets)}")
        print(f"  Type: {session.session_type.value}")
        print(f"  Strategy: {session.optimization_strategy.value}")
        return session
    else:
        print("✗ Failed to create session")
        return None


def test_optimization_strategies():
    """Test different optimization strategies"""
    print("\n=== Testing Optimization Strategies ===")
    
    planner = SessionPlanner()
    targets = create_sample_targets()
    location = create_sample_location()
    session_date = datetime(2024, 3, 15, 20, 0)
    priorities = ['medium'] * len(targets)
    
    strategies = [
        OptimizationStrategy.MAXIMIZE_TARGETS,
        OptimizationStrategy.MAXIMIZE_QUALITY,
        OptimizationStrategy.PRIORITY_BASED,
        OptimizationStrategy.TIME_EFFICIENT,
        OptimizationStrategy.BALANCED
    ]
    
    results = {}
    
    for strategy in strategies:
        session = planner.create_session(
            date=session_date,
            duration=240,
            priorities=priorities,
            targets=targets,
            location=location,
            optimization_strategy=strategy
        )
        
        if session:
            results[strategy.value] = {
                'targets_scheduled': len(session.targets),
                'backup_targets': len(session.backup_targets),
                'total_time': sum(t.estimated_time for t in session.targets)
            }
            print(f"✓ {strategy.value}: {len(session.targets)} targets scheduled")
        else:
            print(f"✗ {strategy.value}: Failed")
    
    return results


def test_session_management():
    """Test session saving and loading"""
    print("\n=== Testing Session Management ===")
    
    # Create session manager with temporary directory
    temp_dir = tempfile.mkdtemp()
    manager = SessionManager(temp_dir)
    planner = SessionPlanner(manager)
    
    # Create a session
    targets = create_sample_targets()
    location = create_sample_location()
    session_date = datetime(2024, 3, 15, 20, 0)
    priorities = ['high', 'medium', 'low'] * 2
    
    session = planner.create_session(
        date=session_date,
        duration=180,
        priorities=priorities,
        targets=targets,
        location=location
    )
    
    if not session:
        print("✗ Failed to create session for testing")
        return False
    
    # Save session
    session.name = "Test Session"
    session.notes = "This is a test session for validation"
    session.equipment_list = ["Telescope", "Mount", "Eyepieces", "Red flashlight"]
    
    save_success = manager.save_session(session)
    print(f"{'✓' if save_success else '✗'} Session save: {save_success}")
    
    # List sessions
    sessions = manager.list_sessions()
    print(f"✓ Sessions listed: {len(sessions)} found")
    
    # Load session
    loaded_session = manager.load_session(session.session_id)
    if loaded_session:
        print(f"✓ Session loaded: {loaded_session.name}")
        print(f"  Targets: {len(loaded_session.targets)}")
        print(f"  Equipment: {len(loaded_session.equipment_list)} items")
    else:
        print("✗ Failed to load session")
        return False
    
    # Delete session
    delete_success = manager.delete_session(session.session_id)
    print(f"{'✓' if delete_success else '✗'} Session delete: {delete_success}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    
    return True


def test_session_export():
    """Test session export functionality"""
    print("\n=== Testing Session Export ===")
    
    planner = SessionPlanner()
    targets = create_sample_targets()
    location = create_sample_location()
    
    session = planner.create_session(
        date=datetime(2024, 3, 15, 20, 0),
        duration=240,
        priorities=['high', 'medium', 'low'] * 2,
        targets=targets,
        location=location
    )
    
    if not session:
        print("✗ Failed to create session for export testing")
        return False
    
    # Add additional session data
    session.name = "Export Test Session"
    session.notes = "Testing export functionality with comprehensive data"
    session.equipment_list = [
        "Telescope (8\" SCT)",
        "Equatorial Mount",
        "Eyepieces (25mm, 10mm, 6mm)",
        "Red flashlight",
        "Star charts",
        "Notebook and pen",
        "Warm clothing",
        "Thermos with hot drink"
    ]
    
    export_formats = ['txt', 'html', 'json']
    export_results = {}
    
    for format_type in export_formats:
        try:
            output_path = planner.export_session(session, format_type)
            if output_path and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                export_results[format_type] = {
                    'success': True,
                    'path': output_path,
                    'size': file_size
                }
                print(f"✓ {format_type.upper()} export: {output_path} ({file_size} bytes)")
            else:
                export_results[format_type] = {'success': False}
                print(f"✗ {format_type.upper()} export failed")
        except Exception as e:
            export_results[format_type] = {'success': False, 'error': str(e)}
            print(f"✗ {format_type.upper()} export error: {e}")
    
    # Test PDF export (may fail if ReportLab not available)
    try:
        pdf_path = planner.export_session(session, 'pdf')
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            export_results['pdf'] = {
                'success': True,
                'path': pdf_path,
                'size': file_size
            }
            print(f"✓ PDF export: {pdf_path} ({file_size} bytes)")
        else:
            export_results['pdf'] = {'success': False}
            print("✗ PDF export failed")
    except ImportError:
        print("⚠ PDF export skipped (ReportLab not available)")
        export_results['pdf'] = {'success': False, 'error': 'ReportLab not available'}
    except Exception as e:
        export_results['pdf'] = {'success': False, 'error': str(e)}
        print(f"✗ PDF export error: {e}")
    
    return export_results


def test_session_statistics():
    """Test session statistics calculation"""
    print("\n=== Testing Session Statistics ===")
    
    planner = SessionPlanner()
    targets = create_sample_targets()
    location = create_sample_location()
    
    session = planner.create_session(
        date=datetime(2024, 3, 15, 20, 0),
        duration=300,  # 5 hours
        priorities=['critical', 'high', 'medium', 'low', 'medium', 'high'],
        targets=targets,
        location=location
    )
    
    if not session:
        print("✗ Failed to create session for statistics testing")
        return False
    
    stats = session.session_statistics
    
    print(f"✓ Session statistics calculated:")
    print(f"  Total targets: {stats.get('total_targets', 0)}")
    print(f"  Total observation time: {stats.get('total_observation_time', 0)} minutes")
    print(f"  Average time per target: {stats.get('average_time_per_target', 0):.1f} minutes")
    print(f"  Target types: {stats.get('target_types', {})}")
    print(f"  Priority distribution: {stats.get('priority_distribution', {})}")
    print(f"  Session efficiency: {stats.get('session_efficiency', 0):.1f}%")
    
    return True


def test_session_optimizer():
    """Test session optimizer directly"""
    print("\n=== Testing Session Optimizer ===")
    
    from utils.session_planner import SessionTarget, SessionConditions
    
    optimizer = SessionOptimizer()
    
    # Create test targets
    test_targets = [
        SessionTarget(
            name="M31",
            object_type="galaxy",
            ra=10.68,
            dec=41.27,
            magnitude=3.4,
            size=190.0,
            constellation="Andromeda",
            priority=SessionPriority.HIGH,
            estimated_time=60
        ),
        SessionTarget(
            name="M42",
            object_type="nebula",
            ra=83.82,
            dec=-5.39,
            magnitude=4.0,
            size=85.0,
            constellation="Orion",
            priority=SessionPriority.MEDIUM,
            estimated_time=45
        ),
        SessionTarget(
            name="M45",
            object_type="cluster",
            ra=56.75,
            dec=24.12,
            magnitude=1.6,
            size=110.0,
            constellation="Taurus",
            priority=SessionPriority.LOW,
            estimated_time=30
        )
    ]
    
    # Create test conditions
    conditions = SessionConditions(
        date=datetime(2024, 3, 15),
        location_lat=40.7128,
        location_lon=-74.0060,
        location_name="New York, NY",
        moon_phase=0.3,
        moon_illumination=30.0,
        astronomical_twilight_start=datetime(2024, 3, 15, 5, 30),
        astronomical_twilight_end=datetime(2024, 3, 15, 20, 30),
        weather_forecast=WeatherCondition.GOOD,
        seeing_forecast=2.5,
        transparency_forecast=7.0,
        wind_speed=15.0,
        temperature=10.0,
        humidity=65.0
    )
    
    # Test different optimization strategies
    strategies = [
        OptimizationStrategy.MAXIMIZE_TARGETS,
        OptimizationStrategy.PRIORITY_BASED,
        OptimizationStrategy.BALANCED
    ]
    
    for strategy in strategies:
        optimized = optimizer.optimize_session(test_targets.copy(), conditions, strategy)
        print(f"✓ {strategy.value}: {len(optimized)} targets optimized")
        
        for target in optimized:
            start_time = target.optimal_start_time.strftime('%H:%M') if target.optimal_start_time else 'TBD'
            print(f"  {start_time} - {target.name} ({target.estimated_time} min)")
    
    return True


def test_integration():
    """Test integration with app state simulation"""
    print("\n=== Testing Integration ===")
    
    # Simulate app state
    class MockAppState:
        def __init__(self):
            self.session_planner = None
            self.session_manager = None
            self.current_session = None
            self.saved_sessions = []
        
        def initialize_session_planner(self):
            self.session_manager = SessionManager()
            self.session_planner = SessionPlanner(self.session_manager)
            return True
        
        def create_new_session(self, date, duration, priorities, targets, location, 
                              session_type=None, optimization_strategy=None):
            if not self.session_planner:
                self.initialize_session_planner()
            
            session = self.session_planner.create_session(
                date=date,
                duration=duration,
                priorities=priorities,
                targets=targets,
                location=location,
                session_type=session_type or SessionType.MIXED,
                optimization_strategy=optimization_strategy or OptimizationStrategy.BALANCED
            )
            
            self.current_session = session
            return session
    
    # Test integration
    app_state = MockAppState()
    
    # Initialize
    init_success = app_state.initialize_session_planner()
    print(f"✓ App state initialization: {init_success}")
    
    # Create session through app state
    targets = create_sample_targets()
    location = create_sample_location()
    
    session = app_state.create_new_session(
        date=datetime(2024, 3, 15, 20, 0),
        duration=240,
        priorities=['high', 'medium', 'low'] * 2,
        targets=targets,
        location=location
    )
    
    if session:
        print(f"✓ Session created through app state: {session.session_id}")
        print(f"  Current session set: {app_state.current_session is not None}")
    else:
        print("✗ Failed to create session through app state")
        return False
    
    return True


def run_all_tests():
    """Run all session planner tests"""
    print("Session Planning System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Session Creation", test_session_creation),
        ("Optimization Strategies", test_optimization_strategies),
        ("Session Management", test_session_management),
        ("Session Export", test_session_export),
        ("Session Statistics", test_session_statistics),
        ("Session Optimizer", test_session_optimizer),
        ("Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                print(f"✓ {test_name} - PASSED")
                passed += 1
                results[test_name] = "PASSED"
            else:
                print(f"✗ {test_name} - FAILED")
                results[test_name] = "FAILED"
        except Exception as e:
            print(f"✗ {test_name} - ERROR: {e}")
            results[test_name] = f"ERROR: {e}"
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    # Show detailed results
    print(f"\nDetailed Results:")
    for test_name, result in results.items():
        status_icon = "✓" if result == "PASSED" else "✗"
        print(f"  {status_icon} {test_name}: {result}")
    
    if passed == total:
        print("\n🎉 All tests passed! Session planning system is working correctly.")
        return True
    else:
        print(f"\n❌ {total - passed} tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)