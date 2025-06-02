"""
Schedule reporting and formatting functions.
"""

from astronomy import (
    format_time, calculate_required_exposure, get_moon_phase_icon,
    find_visibility_window, calculate_visibility_duration, utc_to_local,
    calculate_required_panels, calculate_moon_phase, calculate_moon_position
)
from config.settings import BORTLE_INDEX, SINGLE_EXPOSURE, LATITUDE, LONGITUDE
import math

# Additional imports needed for ReportGenerator
from datetime import timedelta

# Import from visualization for get_abbreviated_name
try:
    from visualization.plotting import get_abbreviated_name
except ImportError:
    # Fallback to get_abbreviated_name from main module
    import re
    def get_abbreviated_name(full_name):
        """Get abbreviated name (catalog designation) from full name"""
        # First try to find Messier number
        m_match = re.match(r'M(\d+)', full_name)
        if m_match:
            return f"M{m_match.group(1)}"
        
        # Then try NGC number
        ngc_match = re.match(r'NGC\s*(\d+)', full_name)
        if ngc_match:
            return f"NGC{ngc_match.group(1)}"
        
        # Then try IC number
        ic_match = re.match(r'IC\s*(\d+)', full_name)
        if ic_match:
            return f"IC{ic_match.group(1)}"
        
        # Then try SH2 number
        sh2_match = re.match(r'SH2-(\d+)', full_name)
        if sh2_match:
            return f"SH2-{sh2_match.group(1)}"
        
        # Then try SH number
        sh_match = re.match(r'SH\s*(\d+)', full_name)
        if sh_match:
            return f"SH{sh_match.group(1)}"
            
        # Then try Barnard number
        b_match = re.match(r'B\s*(\d+)', full_name)
        if b_match:
            return f"B{b_match.group(1)}"
        
        # Then try Gum number
        gum_match = re.match(r'Gum\s*(\d+)', full_name)
        if gum_match:
            return f"GUM{gum_match.group(1)}"    

        # If no catalog number found, return first word
        return full_name.split()[0]


def print_schedule_strategy_report(schedule, strategy):
    """Print schedule details based on strategy"""
    print(f"\nObservation Schedule ({strategy.value})")
    print("=" * 50)
    
    total_objects = len(schedule)
    total_time = sum((end - start).total_seconds() / 3600 
                     for start, end, _ in schedule)
    
    print(f"Total objects: {total_objects}")
    print(f"Total observation time: {total_time:.1f} hours")
    
    for start, end, obj in schedule:
        duration = (end - start).total_seconds() / 3600
        exposure_time, frames, panels = calculate_required_exposure(
            obj.magnitude, BORTLE_INDEX, obj.fov)
        
        print(f"\n{obj.name}")
        print(f"Start: {format_time(start)}")
        print(f"End: {format_time(end)}")
        print(f"Duration: {duration:.1f} hours")
        print(f"Required exposure: {exposure_time:.1f} hours")
        print(f"Panels: {panels}")
        if panels > 1:
            print(f"Mosaic: {math.ceil(math.sqrt(panels))}x{math.ceil(math.sqrt(panels))}")


def generate_schedule_section_content(schedule, strategy):
    """Generate schedule section content for reports"""
    if not schedule:
        return "No schedule generated.\n"
        
    content = f"Strategy: {strategy.value}\n\n"
    
    # Calculate total time and format schedule
    total_time = sum((end - start).total_seconds() / 3600 for start, end, _ in schedule)
    content += f"Total objects: {len(schedule)}\n"
    content += f"Total observation time: {total_time:.1f} hours\n\n"
    
    for start, end, obj in schedule:
        duration = (end - start).total_seconds() / 3600
        
        # Calculate exposure requirements if object has magnitude
        if hasattr(obj, 'magnitude') and obj.magnitude is not None:
            exposure_time, frames, panels = calculate_required_exposure(
                obj.magnitude, BORTLE_INDEX, obj.fov)
            
            content += (
                f"{obj.name}\n"
                f"  Start: {format_time(start)}\n"
                f"  End: {format_time(end)}\n"
                f"  Duration: {duration:.1f} hours\n"
                f"  Required exposure: {exposure_time:.1f} hours\n"
            )
            if panels > 1:
                content += f"  Mosaic: {math.ceil(math.sqrt(panels))}x{math.ceil(math.sqrt(panels))}\n"
        else:
            # Object without magnitude
            content += (
                f"{obj.name}\n"
                f"  Start: {format_time(start)}\n"
                f"  End: {format_time(end)}\n"
                f"  Duration: {duration:.1f} hours\n"
            )
        content += "\n"
    
    return content


def print_combined_report(objects, start_time, end_time, bortle_index):
    """Print a combined report including visibility and imaging information."""
    from astronomy import find_visibility_window, calculate_visibility_duration, format_time, calculate_required_panels, calculate_required_exposure
    
    print("\nNIGHT OBSERVATION REPORT")
    print(f"Date: {start_time.date()}")
    print(f"Location: Milano, Italy")
    print("-" * 50)
    
    # Sort objects by visibility duration for the entire night
    sorted_objects = []
    for obj in objects:
        visibility_periods = find_visibility_window(obj, start_time, end_time, use_margins=True)
        if visibility_periods:
            duration = calculate_visibility_duration(visibility_periods)
            # Store the visibility periods with the object for later use
            obj.visibility_periods = visibility_periods
            sorted_objects.append((obj, duration))
    
    # Sort by duration in descending order
    sorted_objects.sort(key=lambda x: x[1], reverse=True)
    
    # Print visibility information for each object
    for obj, duration in sorted_objects:
        # Get the first and last visibility periods
        first_period = obj.visibility_periods[0]
        last_period = obj.visibility_periods[-1]
        
        # Calculate total visibility duration in hours
        hours = duration
        
        # Get imaging requirements
        required_panels = calculate_required_panels(obj.fov) if obj.fov else None
        required_exposure = calculate_required_exposure(obj.magnitude, bortle_index, obj.fov) if obj.magnitude and obj.fov else None
        
        print(f"\n{obj.name}:")
        print(f"Visibility: {format_time(first_period[0])} - {format_time(last_period[1])} ({hours:.1f} hours)")
        
        if required_panels is not None:
            print(f"Required panels: {required_panels}")
        if required_exposure is not None:
            print(f"Required exposure: {required_exposure[0]:.1f} hours")
        
        # Check if object is near moon during any visibility period
        if hasattr(obj, 'near_moon') and obj.near_moon:
            print("WARNING: Object will be near the moon during some visibility periods")
        
        # Check if object has sufficient time for imaging
        if required_exposure is not None:
            if hours >= required_exposure[0]:
                print("✓ Sufficient time for imaging")
            else:
                print("✗ Insufficient time for imaging")
    
    print("\n" + "-" * 50)


def print_objects_by_type(objects, abbreviate=False):
    """Print objects organized by type"""
    objects_by_type = {}
    for obj in objects:
        obj_type = getattr(obj, 'type', 'unknown')
        if obj_type not in objects_by_type:
            objects_by_type[obj_type] = []
        objects_by_type[obj_type].append(obj)
    
    print("\nObjects by type:")
    print("=" * 50)
    for obj_type, obj_list in objects_by_type.items():
        print(f"\n{obj_type.replace('_', ' ').title()} ({len(obj_list)}):")
        for obj in obj_list:
            print(f"  {obj.name}")
            if not abbreviate:
                if hasattr(obj, 'fov') and obj.fov:
                    print(f"    FOV: {obj.fov}")
                if hasattr(obj, 'comments') and obj.comments:
                    print(f"    Comments: {obj.comments}") 

class ReportGenerator:
    """Class to handle report generation and formatting"""
    def __init__(self, date, location_data):
        self.date = date
        self.location = location_data
        self.sections = []
        
    def add_section(self, title, content):
        """Add a section to the report"""
        self.sections.append({
            'title': title,
            'content': content
        })
    
    def format_section(self, section):
        """Format a single section"""
        output = f"\n{section['title']}\n"
        output += "=" * len(section['title']) + "\n"
        output += section['content']
        return output
    
    def generate_quick_summary(self, visible_objects, moon_affected_objects, start_time, end_time, moon_phase):
        """Generate quick summary section"""
        moon_icon, phase_name = get_moon_phase_icon(moon_phase)
        
        # Always show as full observation window (reverted from partial night filtering)
        observation_window_label = "Observation Window"
        
        content = (
            f"Date: {self.date.date()}\n"
            f"Location: {self.location['name']} ({LATITUDE:.2f}°N, {LONGITUDE:.2f}°E)\n\n"
            f"Observable Objects: {len(visible_objects)} total ({len(moon_affected_objects)} affected by moon)\n"
            f"{observation_window_label}: {format_time(start_time)} - {format_time(end_time)}\n"
            f"Moon Phase: {moon_icon} {phase_name} ({moon_phase:.1%})\n"
            f"Seeing Conditions: Bortle {BORTLE_INDEX}\n"
        )
        self.add_section("QUICK SUMMARY", content)
    
    def generate_timing_section(self, sunset, sunrise, twilight_evening, twilight_morning, moon_rise, moon_set):
        """Generate timing information section"""
        content = (
            f"Sunset: {format_time(sunset)}\n"
            f"Astronomical Twilight Begins: {format_time(twilight_evening)}\n"
        )
        if moon_rise:
            content += f"Moon Rise: {format_time(moon_rise)}\n"
        if moon_set:
            content += f"Moon Set: {format_time(moon_set)}\n"
        content += (
            f"Astronomical Twilight Ends: {format_time(twilight_morning)}\n"
            f"Sunrise: {format_time(sunrise)}\n"
        )
        self.add_section("TIMING INFORMATION", content)
    
    def generate_moon_conditions(self, moon_phase, moon_affected_objects):
        """Generate moon conditions section"""
        moon_icon, phase_name = get_moon_phase_icon(moon_phase)
        content = (
            f"Current Phase: {moon_icon} {phase_name} ({moon_phase:.1%})\n"
            f"Objects affected by moon: {len(moon_affected_objects)}\n\n"
        )
        if moon_affected_objects:
            content += "Affected objects:\n"
            for obj in moon_affected_objects:
                periods = getattr(obj, 'moon_influence_periods', [])
                
                # Calculate total minutes properly from timedelta objects
                total_minutes = sum(
                    int((end - start).total_seconds() / 60)
                    for start, end in periods
                )
                
                # Get the actual time ranges for interference
                if periods:
                    interference_times = []
                    for start, end in periods:
                        # Convert to local time for display
                        local_start = utc_to_local(start)
                        local_end = utc_to_local(end)
                        interference_times.append(f"{format_time(local_start)}-{format_time(local_end)}")
                    
                    interference_str = ", ".join(interference_times)
                    content += f"- {obj.name} ({total_minutes} minutes of interference, during: {interference_str})\n"
                else:
                    content += f"- {obj.name} ({total_minutes} minutes of interference)\n"
        else:
            content += "No objects are significantly affected by moon proximity.\n"
        self.add_section("MOON CONDITIONS", content)
    
    def generate_object_sections(self, visible_objects, insufficient_objects):
        """Generate sections for different object categories"""
        # Prime targets (sufficient time & good conditions)
        prime_targets = [obj for obj in visible_objects 
                        if not getattr(obj, 'near_moon', False)]
        if prime_targets:
            content = self._format_object_list("Prime observation targets:", prime_targets)
            self.add_section("PRIME TARGETS", content)
        
        # Moon-affected targets
        moon_affected = [obj for obj in visible_objects 
                        if getattr(obj, 'near_moon', False)]
        if moon_affected:
            content = self._format_object_list("Objects affected by moon:", moon_affected)
            self.add_section("MOON-AFFECTED TARGETS", content)
        
        # Time-limited targets
        if insufficient_objects:
            content = self._format_object_list("Objects with insufficient visibility time:", insufficient_objects)
            self.add_section("TIME-LIMITED TARGETS", content)
    
    def _format_object_list(self, header, objects):
        """Format a list of objects with their details"""
        # Time variables made available from outer scope
        start_time = self.date
        # Get end of day
        end_time = self.date.replace(hour=23, minute=59, second=59)
        
        # Sort by visibility start time
        sorted_objects = []
        for obj in objects:
            # Handle both individual objects and mosaic groups
            if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group:
                # For mosaic groups, use the overlap periods
                if obj.overlap_periods:
                    sorted_objects.append((obj, obj.overlap_periods[0][0]))
            else:
                periods = find_visibility_window(obj, start_time, end_time)
                if periods:
                    sorted_objects.append((obj, periods[0][0]))
        
        sorted_objects.sort(key=lambda x: x[1])
        sorted_objects = [x[0] for x in sorted_objects]
        
        # Format output
        content = f"{header}\n\n"
        
        for obj in sorted_objects:
            # Handle mosaic groups differently
            if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group:
                # Format mosaic group
                content += f"🎯 {obj.name}\n"
                content += f"Objects in group: {obj.object_count}\n"
                
                # List individual objects
                object_names = [get_abbreviated_name(o.name) for o in obj.objects]
                content += f"Components: {', '.join(object_names)}\n"
                
                # Total overlap duration
                total_overlap = obj.calculate_total_overlap_duration()
                content += f"Total overlap time: {total_overlap:.1f} hours\n"
                
                # Overlap periods
                content += "Overlap periods:\n"
                for period_start, period_end in obj.overlap_periods:
                    period_duration = (period_end - period_start).total_seconds() / 3600
                    content += f"  {format_time(period_start)} - {format_time(period_end)} ({period_duration:.1f}h)\n"
                
                content += f"Composite magnitude: {obj.magnitude:.1f}\n"
                content += f"Mosaic FOV: {obj.fov}\n"
                content += "Type: Mosaic Group\n"
                
            else:
                # Format individual object
                # Get visibility periods
                periods = find_visibility_window(obj, start_time, end_time)
                if not periods:
                    continue
                    
                visibility_start = periods[0][0]
                duration = calculate_visibility_duration(periods)
                visibility_end = periods[-1][1]
                
                # Get moon status
                moon_status = ""
                if hasattr(obj, 'near_moon') and obj.near_moon:
                    moon_phase = calculate_moon_phase(visibility_start)
                    moon_icon, _ = get_moon_phase_icon(moon_phase)
                    
                    # Find when moon rises if it's not already risen at the start of visibility
                    moon_alt_at_start, _ = calculate_moon_position(visibility_start)
                    if moon_alt_at_start < 0:
                        # Moon hasn't risen yet, find rise time
                        check_time = visibility_start
                        moon_rise_time = None
                        while check_time <= visibility_end:
                            moon_alt, _ = calculate_moon_position(check_time)
                            prev_moon_alt, _ = calculate_moon_position(check_time - timedelta(minutes=1))
                            if prev_moon_alt < 0 and moon_alt >= 0:
                                moon_rise_time = check_time
                                break
                            check_time += timedelta(minutes=1)
                        
                        if moon_rise_time:
                            moon_status = f"{moon_icon} Moon interference after {format_time(moon_rise_time)}"
                        else:
                            moon_status = "✨ Clear from moon"
                    else:
                        # Moon is already risen
                        moon_status = f"{moon_icon} Moon interference"
                else:
                    moon_status = "✨ Clear from moon"
                
                # Format the line
                content += f"{obj.name}\n"
                content += f"{moon_status}\n"
                content += f"Visibility: {format_time(visibility_start)} - {format_time(visibility_end)} ({duration:.1f} hours)\n"
                
                if hasattr(obj, 'magnitude') and obj.magnitude is not None:
                    content += f"Magnitude: {obj.magnitude}\n"
                
                if obj.fov:
                    content += f"Field of view: {obj.fov}\n"
                    # Calculate panels needed
                    panels = calculate_required_panels(obj.fov)
                    if panels > 1:
                        content += f"Mosaic panels needed: {panels}\n"
                
                # Calculate exposure requirements
                if hasattr(obj, 'magnitude') and obj.magnitude is not None:
                    exposure_time, frames, panels = calculate_required_exposure(obj.magnitude, BORTLE_INDEX, obj.fov)
                    content += f"Recommended exposure: {exposure_time:.1f}h ({frames} frames of {SINGLE_EXPOSURE}s)\n"
                
                if hasattr(obj, 'object_type') and obj.object_type:
                    content += f"Type: {obj.object_type}\n"
                
                content += "\n"
        
        return content
    
    def generate_schedule_section(self, schedule, strategy):
        """Generate schedule section using the reporting module"""
        content = generate_schedule_section_content(schedule, strategy)
        self.add_section("RECOMMENDED SCHEDULE", content)
    
    def generate_report(self):
        """Generate the complete report"""
        output = "NIGHT OBSERVATION REPORT\n"
        output += "=" * 23 + "\n"
        
        for section in self.sections:
            output += self.format_section(section)
            
        return output

# ============= VISIBILITY FUNCTIONS =============

# ============= TWILIGHT AND NIGHT FUNCTIONS =============

# ============= OBJECT SELECTION FUNCTIONS =============
# Object selection functions have been moved to analysis.object_selection module

# ============= PLOTTING FUNCTIONS =============

