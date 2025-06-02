"""
Mobile Report Generation
Generate and display reports for mobile app
"""

import os
import sys
import tempfile
from datetime import datetime
from kivy.logger import Logger

# Add parent directory to path for astropy imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from analysis.reporting import ReportGenerator, generate_report, print_combined_report
    REPORTING_AVAILABLE = True
except ImportError as e:
    Logger.warning(f"MobileReports: Reporting modules not available: {e}")
    REPORTING_AVAILABLE = False

class MobileReportGenerator:
    """Generate mobile-optimized reports"""
    
    def __init__(self):
        self.report_generator = None
        if REPORTING_AVAILABLE:
            self.report_generator = ReportGenerator()
    
    def generate_session_report(self, app_state):
        """Generate a session report for mobile display"""
        if not REPORTING_AVAILABLE or not self.report_generator:
            return self._create_fallback_report(app_state)
        
        try:
            # Get current session data
            location = app_state.current_location
            visible_objects = app_state.visible_objects
            planned_objects = app_state.planned_objects
            
            if not location or not visible_objects:
                return "No data available for report generation."
            
            # Generate report using existing functionality
            report_data = {
                'location': location,
                'visible_objects': visible_objects,
                'planned_objects': planned_objects,
                'session_stats': app_state.get_session_stats(),
                'timestamp': datetime.now()
            }
            
            # Create mobile-formatted report
            report_text = self._format_mobile_report(report_data)
            
            return report_text
            
        except Exception as e:
            Logger.error(f"MobileReportGenerator: Error generating session report: {e}")
            return f"Error generating report: {str(e)}"
    
    def generate_target_report(self, target, app_state):
        """Generate a detailed report for a specific target"""
        if not REPORTING_AVAILABLE or not self.report_generator:
            return self._create_fallback_target_report(target, app_state)
        
        try:
            location = app_state.current_location
            if not location:
                return "Location required for target report."
            
            # Generate target-specific report
            report_data = {
                'target': target,
                'location': location,
                'timestamp': datetime.now()
            }
            
            report_text = self._format_target_report(report_data)
            
            return report_text
            
        except Exception as e:
            Logger.error(f"MobileReportGenerator: Error generating target report: {e}")
            return f"Error generating target report: {str(e)}"
    
    def generate_mosaic_report(self, mosaic_groups, app_state):
        """Generate a mosaic planning report"""
        if not mosaic_groups:
            return "No mosaic groups available for report."
        
        try:
            location = app_state.current_location
            if not location:
                return "Location required for mosaic report."
            
            report_data = {
                'mosaic_groups': mosaic_groups,
                'location': location,
                'timestamp': datetime.now()
            }
            
            report_text = self._format_mosaic_report(report_data)
            
            return report_text
            
        except Exception as e:
            Logger.error(f"MobileReportGenerator: Error generating mosaic report: {e}")
            return f"Error generating mosaic report: {str(e)}"
    
    def save_report_to_file(self, report_text, filename=None):
        """Save report to a temporary file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"astroscope_report_{timestamp}.txt"
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            temp_file.write(report_text)
            temp_file.close()
            
            Logger.info(f"MobileReportGenerator: Report saved to {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            Logger.error(f"MobileReportGenerator: Error saving report: {e}")
            return None
    
    def _format_mobile_report(self, report_data):
        """Format report for mobile display"""
        lines = []
        
        # Header
        lines.append("=" * 50)
        lines.append("ASTROSCOPE PLANNER - SESSION REPORT")
        lines.append("=" * 50)
        lines.append(f"Generated: {report_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Location
        location = report_data['location']
        lines.append("LOCATION:")
        lines.append(f"  Latitude: {location.get('latitude', 'N/A')}°")
        lines.append(f"  Longitude: {location.get('longitude', 'N/A')}°")
        lines.append(f"  Elevation: {location.get('elevation', 'N/A')} m")
        lines.append("")
        
        # Session Statistics
        stats = report_data['session_stats']
        lines.append("SESSION STATISTICS:")
        lines.append(f"  Total Targets: {stats['total_targets']}")
        lines.append(f"  Visible Tonight: {stats['visible_count']}")
        lines.append(f"  Planned Objects: {stats['planned_count']}")
        lines.append(f"  Completed: {stats['completed_count']}")
        lines.append("")
        
        # Top Visible Objects
        visible_objects = report_data['visible_objects'][:10]  # Top 10
        lines.append("TOP VISIBLE TARGETS:")
        lines.append("-" * 30)
        
        for i, obj in enumerate(visible_objects, 1):
            name = getattr(obj, 'name', f'Object {i}')
            obj_type = getattr(obj, 'type', 'Unknown')
            score = getattr(obj, 'score', 0)
            lines.append(f"{i:2d}. {name:<20} ({obj_type}) Score: {score:.1f}")
        
        lines.append("")
        
        # Planned Objects
        planned_objects = report_data['planned_objects']
        if planned_objects:
            lines.append("PLANNED OBJECTS:")
            lines.append("-" * 20)
            
            for i, obj in enumerate(planned_objects, 1):
                name = getattr(obj, 'name', f'Planned {i}')
                obj_type = getattr(obj, 'type', 'Unknown')
                lines.append(f"{i:2d}. {name} ({obj_type})")
            
            lines.append("")
        
        # Footer
        lines.append("=" * 50)
        lines.append("End of Report")
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def _format_target_report(self, report_data):
        """Format target-specific report"""
        lines = []
        target = report_data['target']
        
        # Header
        lines.append("=" * 50)
        lines.append("TARGET DETAILED REPORT")
        lines.append("=" * 50)
        lines.append(f"Generated: {report_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Target Information
        name = getattr(target, 'name', 'Unknown Target')
        obj_type = getattr(target, 'type', 'Unknown')
        lines.append(f"TARGET: {name}")
        lines.append(f"Type: {obj_type}")
        lines.append("")
        
        # Coordinates
        ra = getattr(target, 'ra', target.get('ra', 'N/A'))
        dec = getattr(target, 'dec', target.get('dec', 'N/A'))
        lines.append("COORDINATES:")
        lines.append(f"  RA: {ra}")
        lines.append(f"  Dec: {dec}")
        lines.append("")
        
        # Visibility Information
        score = getattr(target, 'score', 0)
        lines.append("VISIBILITY:")
        lines.append(f"  Score: {score:.1f}")
        lines.append("")
        
        # Additional Properties
        lines.append("PROPERTIES:")
        for attr in ['magnitude', 'size', 'constellation', 'catalog']:
            value = getattr(target, attr, target.get(attr, None))
            if value:
                lines.append(f"  {attr.title()}: {value}")
        
        lines.append("")
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def _format_mosaic_report(self, report_data):
        """Format mosaic planning report"""
        lines = []
        
        # Header
        lines.append("=" * 50)
        lines.append("MOSAIC PLANNING REPORT")
        lines.append("=" * 50)
        lines.append(f"Generated: {report_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Mosaic Groups
        mosaic_groups = report_data['mosaic_groups']
        lines.append(f"MOSAIC GROUPS: {len(mosaic_groups)}")
        lines.append("-" * 30)
        
        for i, group in enumerate(mosaic_groups, 1):
            group_name = group.get('name', f'Group {i}')
            panel_count = group.get('panel_count', 0)
            total_time = group.get('total_time', 0)
            
            lines.append(f"{i}. {group_name}")
            lines.append(f"   Panels: {panel_count}")
            lines.append(f"   Total Time: {total_time:.1f} hours")
            lines.append("")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def _create_fallback_report(self, app_state):
        """Create a basic report when full reporting is not available"""
        lines = []
        
        lines.append("ASTROSCOPE PLANNER - BASIC REPORT")
        lines.append("=" * 40)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        stats = app_state.get_session_stats()
        lines.append("SESSION SUMMARY:")
        lines.append(f"  Total Targets: {stats['total_targets']}")
        lines.append(f"  Visible Tonight: {stats['visible_count']}")
        lines.append(f"  Planned Objects: {stats['planned_count']}")
        lines.append("")
        
        lines.append("Note: Full reporting features require astropy modules.")
        lines.append("=" * 40)
        
        return "\n".join(lines)
    
    def _create_fallback_target_report(self, target, app_state):
        """Create a basic target report when full reporting is not available"""
        lines = []
        
        name = getattr(target, 'name', 'Unknown Target')
        lines.append(f"TARGET REPORT: {name}")
        lines.append("=" * 30)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        lines.append("Basic target information:")
        for attr in ['type', 'ra', 'dec', 'magnitude']:
            value = getattr(target, attr, target.get(attr, 'N/A'))
            lines.append(f"  {attr.title()}: {value}")
        
        lines.append("")
        lines.append("Note: Detailed analysis requires astropy modules.")
        lines.append("=" * 30)
        
        return "\n".join(lines)

# Global instance
mobile_report_generator = MobileReportGenerator()