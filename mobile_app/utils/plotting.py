"""
Mobile Plotting Utilities
Matplotlib integration for Kivy mobile app with touch-optimized plots
"""

import os
import sys
import io
import tempfile
from datetime import datetime, timedelta
from kivy.logger import Logger

# Matplotlib backend configuration for mobile
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for mobile
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np

# Add parent directory to path for astropy imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from astronightplanner import (
        plot_object_trajectory, plot_visibility_chart, plot_quarterly_trajectories,
        create_mosaic_trajectory_plot, create_mosaic_grid_plot
    )
    from astroseasonplanner import plot_weekly_analysis
    from astronomy import calculate_altaz, find_visibility_window
    from analysis.reporting import ReportGenerator
    ASTROPY_AVAILABLE = True
except ImportError as e:
    Logger.warning(f"PlottingUtils: Astropy modules not available: {e}")
    ASTROPY_AVAILABLE = False

# Add logging import
from mobile_app.utils.app_logger import log_error, log_warning, log_info, log_debug

class MobilePlotGenerator:
    """Generate mobile-optimized plots for astronomical data"""
    
    def __init__(self):
        self.figure_size = (8, 6)  # Mobile-optimized size
        self.dpi = 100
        self.style_config = {
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.titlesize': 14
        }
        
    def configure_mobile_style(self):
        """Configure matplotlib for mobile display"""
        plt.rcParams.update(self.style_config)
        plt.style.use('default')
        
    def create_trajectory_plot(self, target, location, start_time=None, end_time=None):
        """Create trajectory plot for a single target"""
        if not ASTROPY_AVAILABLE:
            return self._create_placeholder_plot("Trajectory Plot", "Astropy modules not available")
            
        try:
            log_info(f"Creating trajectory plot for {getattr(target, 'name', 'Unknown')}")
            self.configure_mobile_style()
            
            if start_time is None:
                start_time = datetime.now()
            if end_time is None:
                end_time = start_time + timedelta(hours=12)
            
            # Ensure target has required attributes
            target = self._normalize_target(target)
            log_debug(f"Normalized target: {target}")
                
            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
            
            # Plot trajectory with error handling
            try:
                plot_object_trajectory(ax, target, start_time, end_time, 'blue')
            except Exception as e:
                log_error(f"Error in plot_object_trajectory", e, {'target': str(target)})
                # Fallback: create simple altitude plot
                self._create_simple_altitude_plot(ax, target, start_time, end_time)
            
            # Mobile-specific formatting
            target_name = getattr(target, 'name', target.get('name', 'Target') if isinstance(target, dict) else 'Target')
            ax.set_title(f"Trajectory: {target_name}", fontsize=12, pad=20)
            ax.grid(True, alpha=0.3)
            
            # Optimize for mobile viewing
            plt.tight_layout()
            
            return self._save_plot_to_temp(fig)
            
        except Exception as e:
            log_error(f"Error creating trajectory plot", e, {'target': str(target)})
            return self._create_placeholder_plot("Trajectory Plot", f"Error: {str(e)}")
    
    def create_visibility_chart(self, targets, location, start_time=None, end_time=None):
        """Create visibility chart for multiple targets"""
        if not ASTROPY_AVAILABLE:
            return self._create_placeholder_plot("Visibility Chart", "Astropy modules not available")
            
        try:
            log_info(f"Creating visibility chart for {len(targets)} targets")
            self.configure_mobile_style()
            
            # Use twilight times if not provided - CRITICAL: Use only twilight range, not extended range
            if start_time is None or end_time is None:
                try:
                    from astronomy import find_configured_twilight
                    today = datetime.now()  # Use datetime instead of date
                    twilight_start, twilight_end = find_configured_twilight(today)
                    if twilight_start and twilight_end:
                        start_time = twilight_start
                        end_time = twilight_end
                        log_info(f"Using configured twilight times: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
                    else:
                        raise Exception("Twilight calculation returned None")
                except Exception as e:
                    log_error(f"Could not get twilight times: {e}")
                    # Use precise astronomical twilight as fallback (not extended evening-to-morning)
                    today = datetime.now()
                    start_time = datetime.combine(today.date(), datetime.min.time().replace(hour=23, minute=55))
                    end_time = datetime.combine(today.date() + timedelta(days=1), datetime.min.time().replace(hour=2, minute=57))
                    log_info(f"Using astronomical twilight fallback: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
            
            # IMPORTANT: Ensure we don't extend the time range beyond twilight times
            # The chart should only show the actual observing window, not an extended range
            log_info(f"Final chart time range: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
            
            # Use ALL targets - no mobile limits to match desktop functionality
            # Normalize all targets
            normalized_targets = []
            for i, target in enumerate(targets):
                normalized = self._normalize_target(target)
                normalized_targets.append(normalized)
                log_debug(f"Target {i}: {type(target)} -> {type(normalized)} (name: {getattr(normalized, 'name', 'Unknown')})")
            log_info(f"Normalized {len(normalized_targets)} targets")
                
            # Use the desktop plotting function directly - it creates its own figure
            try:
                log_info(f"Attempting to create desktop-style visibility chart for {len(normalized_targets)} targets")
                
                # Try to generate a basic schedule for better visualization
                schedule = None
                try:
                    from analysis import generate_observation_schedule
                    from models import SchedulingStrategy
                    schedule = generate_observation_schedule(
                        normalized_targets, start_time, end_time,
                        strategy=SchedulingStrategy.LONGEST_DURATION
                    )
                    log_info(f"Generated schedule with {len(schedule)} observations")
                except Exception as e:
                    log_warning(f"Could not generate schedule: {e}")
                    import traceback
                    log_warning(f"Schedule error traceback: {traceback.format_exc()}")
                
                # Check if plot_visibility_chart is available
                if 'plot_visibility_chart' not in globals():
                    raise ImportError("plot_visibility_chart function not available")
                
                log_info(f"Calling plot_visibility_chart with {len(normalized_targets)} targets, time range {start_time} to {end_time}")
                
                # CRITICAL: Pass the exact twilight time range to the plotting function
                log_info(f"About to call plot_visibility_chart with:")
                log_info(f"  - start_time: {start_time} (formatted: {start_time.strftime('%H:%M')})")
                log_info(f"  - end_time: {end_time} (formatted: {end_time.strftime('%H:%M')})")
                log_info(f"  - timezone: {start_time.tzinfo}")
                
                fig, ax = plot_visibility_chart(normalized_targets, start_time, end_time, 
                                              schedule=schedule,
                                              title="Tonight's Visibility", use_margins=False)
                
                if fig is None or ax is None:
                    raise ValueError("plot_visibility_chart returned None")
                
                # Check what title was actually created
                actual_title = ax.get_title()
                log_info(f"Plot title created: {actual_title}")
                
                # CRITICAL FIX: Force correct x-axis limits to prevent timezone conversion issues
                # The desktop plotting function may have timezone conversion issues, so we force the correct limits
                ax.set_xlim(start_time, end_time)
                log_info(f"Forced x-axis limits to correct twilight range: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
                
                # Apply mobile-specific sizing
                fig.set_size_inches(self.figure_size)
                fig.set_dpi(self.dpi)
                
                log_info("Successfully created visibility chart using desktop plotting function")
            except Exception as e:
                log_error(f"Error in plot_visibility_chart: {type(e).__name__}: {str(e)}", e, {
                    'targets_count': len(normalized_targets),
                    'start_time': str(start_time),
                    'end_time': str(end_time),
                    'plot_function_available': 'plot_visibility_chart' in globals()
                })
                import traceback
                log_error(f"Full traceback: {traceback.format_exc()}")
                
                # Fallback: create desktop-style horizontal bar chart instead of simple chart
                log_info("Creating desktop-style bar chart as fallback")
                fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
                self._create_desktop_style_visibility_chart(ax, normalized_targets, start_time, end_time, schedule)
                log_info("Created desktop-style fallback visibility chart")
            
            # Mobile-specific formatting
            plt.tight_layout()
            
            return self._save_plot_to_temp(fig)
            
        except Exception as e:
            log_error(f"Error creating visibility chart", e, {'targets_count': len(targets) if targets else 0})
            return self._create_placeholder_plot("Visibility Chart", f"Error: {str(e)}")
    
    def create_mosaic_plot(self, mosaic_groups, start_time=None, end_time=None):
        """Create mosaic planning visualization"""
        if not ASTROPY_AVAILABLE:
            return self._create_placeholder_plot("Mosaic Plan", "Astropy modules not available")
            
        try:
            self.configure_mobile_style()
            
            if start_time is None:
                start_time = datetime.now()
            if end_time is None:
                end_time = start_time + timedelta(hours=12)
                
            # Create trajectory plot
            fig = create_mosaic_trajectory_plot(mosaic_groups, start_time, end_time)
            
            # Mobile-specific formatting
            fig.set_size_inches(self.figure_size)
            fig.set_dpi(self.dpi)
            plt.tight_layout()
            
            return self._save_plot_to_temp(fig)
            
        except Exception as e:
            Logger.error(f"MobilePlotGenerator: Error creating mosaic plot: {e}")
            return self._create_placeholder_plot("Mosaic Plan", f"Error: {str(e)}")
    
    def create_mosaic_grid_plot(self, mosaic_groups, start_time=None, end_time=None):
        """Create mosaic grid visualization"""
        if not ASTROPY_AVAILABLE:
            return self._create_placeholder_plot("Mosaic Grid", "Astropy modules not available")
            
        try:
            self.configure_mobile_style()
            
            if start_time is None:
                start_time = datetime.now()
            if end_time is None:
                end_time = start_time + timedelta(hours=12)
                
            # Create grid plot
            fig = create_mosaic_grid_plot(mosaic_groups, start_time, end_time)
            
            # Mobile-specific formatting
            fig.set_size_inches(self.figure_size)
            fig.set_dpi(self.dpi)
            plt.tight_layout()
            
            return self._save_plot_to_temp(fig)
            
        except Exception as e:
            Logger.error(f"MobilePlotGenerator: Error creating mosaic grid plot: {e}")
            return self._create_placeholder_plot("Mosaic Grid", f"Error: {str(e)}")
    
    def create_target_altitude_plot(self, target, location, date=None):
        """Create altitude vs time plot for a single target with altitude AND azimuth constraints"""
        try:
            self.configure_mobile_style()
            
            if date is None:
                date = datetime.now().date()
                
            # Create time range for the night (sunset to sunrise)
            start_time = datetime.combine(date, datetime.min.time().replace(hour=18))
            end_time = start_time + timedelta(hours=12)
            
            # Get location coordinates and constraints safely
            try:
                if isinstance(location, dict):
                    lat = location.get('latitude', location.get('lat', 40.0))
                    lon = location.get('longitude', location.get('lon', -74.0))
                    min_altitude = location.get('min_altitude', 30)
                    max_altitude = location.get('max_altitude', 90)
                    min_azimuth = location.get('min_azimuth', 0)
                    max_azimuth = location.get('max_azimuth', 360)
                else:
                    lat = getattr(location, 'latitude', getattr(location, 'lat', 40.0))
                    lon = getattr(location, 'longitude', getattr(location, 'lon', -74.0))
                    min_altitude = getattr(location, 'min_altitude', 30)
                    max_altitude = getattr(location, 'max_altitude', 90)
                    min_azimuth = getattr(location, 'min_azimuth', 0)
                    max_azimuth = getattr(location, 'max_azimuth', 360)
                lat, lon = float(lat), float(lon)
                min_altitude = float(min_altitude)
                max_altitude = float(max_altitude)
                min_azimuth = float(min_azimuth)
                max_azimuth = float(max_azimuth)
                
                log_debug(f"Using constraints: Alt {min_altitude}°-{max_altitude}°, Az {min_azimuth}°-{max_azimuth}°")
            except (ValueError, TypeError):
                lat, lon = 40.0, -74.0  # Default to NYC coordinates
                min_altitude, max_altitude = 30, 90
                min_azimuth, max_azimuth = 0, 360
                log_warning("Using default location coordinates and constraints")
            
            # Generate more time points for smooth interpolation (every 5 minutes)
            times = []
            altitudes = []
            azimuths = []
            constraint_status = []  # Track which constraints are met
            
            current_time = start_time
            
            while current_time <= end_time:
                times.append(current_time)
                
                # Calculate altitude using proper astronomical calculations
                if ASTROPY_AVAILABLE:
                    try:
                        alt, az = calculate_altaz(target, current_time)
                        altitudes.append(float(alt))
                        azimuths.append(float(az))
                        
                        # Check ALL constraints: altitude AND azimuth AND above horizon
                        alt_constraint_met = min_altitude <= alt <= max_altitude
                        az_constraint_met = min_azimuth <= az <= max_azimuth
                        above_horizon = alt > 0
                        
                        # Object is fully observable only if ALL constraints are met
                        all_constraints_met = alt_constraint_met and az_constraint_met and above_horizon
                        constraint_status.append({
                            'all_met': all_constraints_met,
                            'alt_met': alt_constraint_met,
                            'az_met': az_constraint_met,
                            'above_horizon': above_horizon,
                            'altitude': alt,
                            'azimuth': az
                        })
                            
                    except Exception as e:
                        log_warning(f"Altitude calculation failed at {current_time}: {e}")
                        # Fallback to realistic calculation
                        alt, az = self._calculate_realistic_altitude(target, current_time, lat, lon)
                        altitudes.append(alt)
                        azimuths.append(az)
                        
                        # Check constraints for fallback too
                        alt_constraint_met = min_altitude <= alt <= max_altitude
                        az_constraint_met = min_azimuth <= az <= max_azimuth
                        above_horizon = alt > 0
                        all_constraints_met = alt_constraint_met and az_constraint_met and above_horizon
                        constraint_status.append({
                            'all_met': all_constraints_met,
                            'alt_met': alt_constraint_met,
                            'az_met': az_constraint_met,
                            'above_horizon': above_horizon,
                            'altitude': alt,
                            'azimuth': az
                        })
                else:
                    # Demo data with realistic astronomical behavior
                    alt, az = self._calculate_realistic_altitude(target, current_time, lat, lon)
                    altitudes.append(alt)
                    azimuths.append(az)
                    
                    # Check constraints
                    alt_constraint_met = min_altitude <= alt <= max_altitude
                    az_constraint_met = min_azimuth <= az <= max_azimuth
                    above_horizon = alt > 0
                    all_constraints_met = alt_constraint_met and az_constraint_met and above_horizon
                    constraint_status.append({
                        'all_met': all_constraints_met,
                        'alt_met': alt_constraint_met,
                        'az_met': az_constraint_met,
                        'above_horizon': above_horizon,
                        'altitude': alt,
                        'azimuth': az
                    })
                
                current_time += timedelta(minutes=5)  # Finer granularity for smoother curves
            
            # Create plot
            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
            
            # Convert to numpy arrays for better plotting
            times_np = np.array(times)
            altitudes_np = np.array(altitudes)
            azimuths_np = np.array(azimuths)
            
            # Plot full trajectory (including outside constraints) in gray
            visible_mask = altitudes_np > 0
            if np.any(visible_mask):
                ax.plot(times_np[visible_mask], altitudes_np[visible_mask], '--', 
                       color='gray', linewidth=1, alpha=0.5, label='Above horizon')
            
            # Plot segments based on constraint status
            valid_times = []
            valid_altitudes = []
            partial_times = []
            partial_altitudes = []
            
            for i, status in enumerate(constraint_status):
                if status['above_horizon']:
                    if status['all_met']:
                        # All constraints met - this is the good data
                        valid_times.append(times[i])
                        valid_altitudes.append(altitudes[i])
                    elif status['alt_met'] or status['az_met']:
                        # Some constraints met - show as partial
                        partial_times.append(times[i])
                        partial_altitudes.append(altitudes[i])
            
            # Plot partially valid portions (some constraints met) in orange
            if partial_times:
                ax.plot(partial_times, partial_altitudes, '-', 
                       color='orange', linewidth=1.5, alpha=0.7, label='Partial constraints')
            
            # Plot fully valid portions (all constraints met) in blue
            if valid_times:
                ax.plot(valid_times, valid_altitudes, 'b-', linewidth=2, label='Full constraints met')
                ax.fill_between(valid_times, 0, valid_altitudes, alpha=0.3, color='blue', label='Observable window')
            
            # Add constraint lines
            ax.axhline(y=min_altitude, color='r', linestyle='--', alpha=0.7, 
                      label=f'Min altitude ({min_altitude}°)')
            if max_altitude < 90:
                ax.axhline(y=max_altitude, color='r', linestyle='--', alpha=0.7, 
                          label=f'Max altitude ({max_altitude}°)')
            ax.axhline(y=0, color='k', linestyle='-', alpha=0.5, label='Horizon')
            
            # Highlight optimal observation window (all constraints met)
            if valid_times and valid_altitudes:
                optimal_alts = [alt for alt in valid_altitudes if alt >= min_altitude]
                optimal_times = [valid_times[i] for i, alt in enumerate(valid_altitudes) if alt >= min_altitude]
                if optimal_times and optimal_alts:
                    ax.fill_between(optimal_times, min_altitude, optimal_alts, 
                                   alpha=0.2, color='green', 
                                   label='Optimal observing')
            
            # Set proper limits and labels
            ax.set_xlabel('Time (Local)')
            ax.set_ylabel('Altitude (degrees)')
            target_name = self.get_target_name(target)
            
            # Add constraint info to title
            constraint_text = f"Alt {min_altitude}°-{max_altitude}°, Az {min_azimuth}°-{max_azimuth}°"
            ax.set_title(f"Altitude Profile: {target_name}\n({constraint_text})")
                
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper right', fontsize=8)
            
            # Set altitude range
            ax.set_ylim(-10, min(90, max_altitude + 10))
            
            # Format time axis nicely
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            plt.xticks(rotation=45)
            
            # Add twilight times if available
            try:
                from astronightplanner import find_astronomical_twilight
                twilight_times = find_astronomical_twilight(date)
                if twilight_times and len(twilight_times) == 2:
                    evening_twilight, morning_twilight = twilight_times
                    ax.axvline(x=evening_twilight, color='orange', linestyle=':', alpha=0.7, label='Evening twilight')
                    ax.axvline(x=morning_twilight, color='orange', linestyle=':', alpha=0.7, label='Morning twilight')
            except Exception:
                pass  # Twilight calculation optional
            
            # Add text box with constraint summary
            observable_count = sum(1 for status in constraint_status if status['all_met'])
            total_points = len(constraint_status)
            observable_pct = (observable_count / total_points * 100) if total_points > 0 else 0
            
            info_text = f"Observable: {observable_pct:.0f}% of night\n"
            info_text += f"Constraints: Alt {min_altitude}°-{max_altitude}°, Az {min_azimuth}°-{max_azimuth}°"
            
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=8, 
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            
            log_info(f"Created altitude plot with {observable_pct:.0f}% observable time")
            return self._save_plot_to_temp(fig)
            
        except Exception as e:
            log_error(f"Error creating altitude plot", e, {'target': str(target)})
            return self._create_placeholder_plot("Altitude Plot", f"Error: {str(e)}")
    
    def _calculate_realistic_altitude(self, target, time, lat, lon):
        """Calculate realistic altitude using simplified astronomical formulas"""
        try:
            # Get target coordinates safely
            if isinstance(target, dict):
                target_ra = float(target.get('ra', 0))  # radians
                target_dec = float(target.get('dec', 0))  # radians
            else:
                target_ra = float(getattr(target, 'ra', 0))
                target_dec = float(getattr(target, 'dec', 0))
            
            # Convert to degrees if needed (assume small values are in radians)
            if abs(target_ra) > 2 * np.pi:
                target_ra = np.radians(target_ra / 15)  # Convert hours to radians
            if abs(target_dec) > np.pi:
                target_dec = np.radians(target_dec)
            
            # Calculate Local Sidereal Time (simplified)
            days_since_j2000 = (time - datetime(2000, 1, 1, 12, 0, 0)).total_seconds() / 86400.0
            lst_degrees = (100.46 + 0.985647 * days_since_j2000 + lon + 15 * (time.hour + time.minute/60.0 + time.second/3600.0)) % 360
            lst_radians = np.radians(lst_degrees)
            
            # Calculate Hour Angle
            hour_angle = lst_radians - target_ra
            
            # Calculate altitude using spherical trigonometry
            lat_rad = np.radians(lat)
            altitude_rad = np.arcsin(
                np.sin(target_dec) * np.sin(lat_rad) + 
                np.cos(target_dec) * np.cos(lat_rad) * np.cos(hour_angle)
            )
            altitude_deg = np.degrees(altitude_rad)
            
            # Calculate azimuth
            azimuth_rad = np.arctan2(
                -np.sin(hour_angle),
                np.tan(target_dec) * np.cos(lat_rad) - np.sin(lat_rad) * np.cos(hour_angle)
            )
            azimuth_deg = (np.degrees(azimuth_rad) + 360) % 360
            
            return altitude_deg, azimuth_deg
            
        except Exception as e:
            log_warning(f"Realistic altitude calculation failed: {e}")
            # Ultimate fallback - simple sine curve
            hours_from_start = (time.hour - 18) % 24
            altitude = 45 * np.sin(np.pi * hours_from_start / 12) - 10
            return max(-90, min(90, altitude)), (hours_from_start * 15) % 360

    def get_target_name(self, target):
        """Safely get target name"""
        try:
            if isinstance(target, dict):
                return target.get('name', 'Unknown Target')
            else:
                return getattr(target, 'name', 'Unknown Target')
        except Exception:
            return 'Unknown Target'
    
    def _create_placeholder_plot(self, title, message):
        """Create a placeholder plot when data is not available"""
        try:
            self.configure_mobile_style()
            
            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
            
            ax.text(0.5, 0.5, message, 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   fontsize=12,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            
            ax.set_title(title)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            plt.tight_layout()
            
            return self._save_plot_to_temp(fig)
            
        except Exception as e:
            Logger.error(f"MobilePlotGenerator: Error creating placeholder: {e}")
            return None
    
    def _save_plot_to_temp(self, fig):
        """Save plot to temporary file and return path"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Save plot
            fig.savefig(temp_path, dpi=self.dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close(fig)  # Free memory
            
            Logger.info(f"MobilePlotGenerator: Plot saved to {temp_path}")
            return temp_path
            
        except Exception as e:
            Logger.error(f"MobilePlotGenerator: Error saving plot: {e}")
            return None

    def _normalize_target(self, target):
        """Normalize target object to ensure it has required attributes"""
        try:
            if isinstance(target, dict):
                # Create an object-like class that desktop functions can use
                class TargetObject:
                    def __init__(self, data):
                        self.name = data.get('name', 'Unknown')
                        self.ra = float(data.get('ra', 0))
                        self.dec = float(data.get('dec', 0))
                        self.magnitude = float(data.get('magnitude', 10))
                        self.object_type = data.get('object_type', 'Unknown')
                        self.optimal_time = data.get('optimal_time')
                        self.visibility_hours = float(data.get('visibility_hours', 4))
                        self.near_moon = data.get('near_moon', False)
                        self.score = float(data.get('score', 0))
                        self.is_mosaic_candidate = data.get('is_mosaic_candidate', False)
                        self.size = data.get('size', 'Unknown')
                        self.fov = data.get('fov', 'Unknown')
                        self.sufficient_time = data.get('sufficient_time', True)
                        self.moon_influence_periods = data.get('moon_influence_periods', [])
                        
                        # Add any additional attributes from the original dict
                        for key, value in data.items():
                            if not hasattr(self, key):
                                setattr(self, key, value)
                
                return TargetObject(target)
            else:
                # For object-style targets, ensure attributes exist
                if not hasattr(target, 'near_moon'):
                    target.near_moon = False
                if not hasattr(target, 'score'):
                    target.score = 0
                if not hasattr(target, 'is_mosaic_candidate'):
                    target.is_mosaic_candidate = False
                if not hasattr(target, 'visibility_hours'):
                    target.visibility_hours = 4.0
                if not hasattr(target, 'sufficient_time'):
                    target.sufficient_time = True
                if not hasattr(target, 'moon_influence_periods'):
                    target.moon_influence_periods = []
                return target
                
        except Exception as e:
            log_error(f"Error normalizing target", e, {'target': str(target)})
            # Return minimal valid object
            class MinimalTarget:
                def __init__(self):
                    self.name = 'Unknown'
                    self.ra = 0
                    self.dec = 0
                    self.magnitude = 10
                    self.object_type = 'Unknown'
                    self.near_moon = False
                    self.score = 0
                    self.is_mosaic_candidate = False
                    self.visibility_hours = 4.0
                    self.sufficient_time = True
                    self.moon_influence_periods = []
            return MinimalTarget()
    
    def _create_simple_altitude_plot(self, ax, target, start_time, end_time):
        """Create a simple altitude plot as fallback"""
        try:
            # Generate time points
            times = []
            altitudes = []
            current_time = start_time
            
            while current_time <= end_time:
                times.append(current_time)
                
                # Simple altitude calculation (demonstration)
                hour_diff = (current_time - start_time).total_seconds() / 3600
                # Simple sine curve peaking at midnight
                altitude = 30 + 40 * np.sin(np.pi * hour_diff / 12)
                altitudes.append(max(0, altitude))
                
                current_time += timedelta(minutes=30)
            
            ax.plot(times, altitudes, 'b-', linewidth=2)
            ax.set_ylabel('Altitude (degrees)')
            ax.set_xlabel('Time')
            ax.set_ylim(0, 90)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            
            log_info("Created simple altitude plot as fallback")
            
        except Exception as e:
            log_error(f"Error creating simple altitude plot", e)
            ax.text(0.5, 0.5, 'Plot generation failed', ha='center', va='center', transform=ax.transAxes)
    
    def _create_desktop_style_visibility_chart(self, ax, targets, start_time, end_time, schedule=None):
        """Create a desktop-style horizontal bar visibility chart as fallback"""
        try:
            from matplotlib.dates import DateFormatter
            import matplotlib.dates as mdates
            
            log_info(f"Creating desktop-style visibility chart for {len(targets)} targets")
            
            # Ensure times are timezone-aware
            if start_time.tzinfo is None:
                from astronomy import get_local_timezone
                local_tz = get_local_timezone()
                start_time = local_tz.localize(start_time)
                end_time = local_tz.localize(end_time)
            
            # Get visibility periods for each target
            target_periods = []
            for target in targets:
                try:
                    if ASTROPY_AVAILABLE:
                        from astronomy import find_visibility_window
                        periods = find_visibility_window(target, start_time, end_time, use_margins=True)
                        if periods:
                            target_periods.append((target, periods))
                    else:
                        # Fallback: create dummy visibility period
                        dummy_start = start_time + timedelta(hours=1)
                        dummy_end = end_time - timedelta(hours=1)
                        target_periods.append((target, [(dummy_start, dummy_end)]))
                except Exception as e:
                    log_warning(f"Could not get visibility for {target.get('name', 'Unknown')}: {e}")
                    # Create a dummy period anyway
                    dummy_start = start_time + timedelta(hours=1)
                    dummy_end = end_time - timedelta(hours=1)
                    target_periods.append((target, [(dummy_start, dummy_end)]))
            
            # Sort by visibility start time (reverse for chart display)
            target_periods.sort(key=lambda x: x[1][0][0] if x[1] else start_time, reverse=True)
            
            # Plot horizontal bars for each target
            y_positions = range(len(target_periods))
            bar_height = 0.6
            
            for i, (target, periods) in enumerate(target_periods):
                target_name = target.get('name', 'Unknown') if isinstance(target, dict) else getattr(target, 'name', 'Unknown')
                
                # Determine bar color based on target properties
                if isinstance(target, dict):
                    near_moon = target.get('near_moon', False)
                    sufficient_time = target.get('sufficient_time', True)
                else:
                    near_moon = getattr(target, 'near_moon', False)
                    sufficient_time = getattr(target, 'sufficient_time', True)
                
                # Choose color based on status
                if not sufficient_time:
                    color = 'pink'  # Insufficient time
                    alpha = 0.6
                elif near_moon:
                    color = 'orange'  # Moon interference
                    alpha = 0.8
                else:
                    color = 'lightblue'  # Normal visibility
                    alpha = 0.8
                
                # Plot visibility periods as horizontal bars
                for period_start, period_end in periods:
                    # Ensure periods are within plot range
                    plot_start = max(period_start, start_time)
                    plot_end = min(period_end, end_time)
                    
                    if plot_start < plot_end:
                        duration = plot_end - plot_start
                        ax.barh(i, duration, left=plot_start, height=bar_height,
                               color=color, alpha=alpha, edgecolor='black', linewidth=0.5)
                
                # Add scheduled observation overlay if available
                if schedule:
                    for sched_start, sched_end, sched_obj in schedule:
                        sched_name = sched_obj.get('name', 'Unknown') if isinstance(sched_obj, dict) else getattr(sched_obj, 'name', 'Unknown')
                        if sched_name == target_name:
                            # Overlay scheduled period with hatching
                            sched_duration = sched_end - sched_start
                            ax.barh(i, sched_duration, left=sched_start, height=bar_height * 1.1,
                                   color='none', edgecolor='red', hatch='///', linewidth=1.5, alpha=0.9)
            
            # Setup axes
            ax.set_ylim(-0.5, len(target_periods) - 0.5)
            ax.set_xlim(start_time, end_time)
            
            # Y-axis labels (target names)
            target_names = [target.get('name', 'Unknown') if isinstance(target, dict) else getattr(target, 'name', 'Unknown')
                           for target, _ in target_periods]
            ax.set_yticks(y_positions)
            ax.set_yticklabels(target_names, fontsize=8)
            ax.set_ylabel('Objects', fontsize=10)
            
            # X-axis formatting
            ax.set_xlabel('Local Time', fontsize=10)
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=30))
            
            # Grid
            ax.grid(True, axis='x', alpha=0.3)
            ax.set_axisbelow(True)
            
            # Title
            ax.set_title("Tonight's Visibility", fontsize=12, fontweight='bold')
            
            # Create legend
            legend_elements = [
                plt.Rectangle((0, 0), 1, 1, facecolor='lightblue', alpha=0.8, label='Recommended'),
                plt.Rectangle((0, 0), 1, 1, facecolor='pink', alpha=0.6, label='Insufficient Time'),
                plt.Rectangle((0, 0), 1, 1, facecolor='orange', alpha=0.8, label='Moon Interference')
            ]
            
            if schedule:
                legend_elements.append(
                    plt.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='red', 
                                hatch='///', label='Scheduled Observation')
                )
            
            ax.legend(handles=legend_elements, loc='upper right', fontsize=8)
            
            log_info(f"Created desktop-style visibility chart with {len(target_periods)} targets")
            
        except Exception as e:
            log_error(f"Error creating desktop-style visibility chart", e)
            import traceback
            log_error(f"Desktop-style chart error traceback: {traceback.format_exc()}")
            # Ultimate fallback
            ax.text(0.5, 0.5, 'Desktop-style chart generation failed', ha='center', va='center', transform=ax.transAxes)

    def _create_simple_visibility_chart(self, ax, targets, start_time, end_time):
        """Create a simple visibility chart as fallback (altitude curves)"""
        try:
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
            
            for i, target in enumerate(targets[:8]):  # Limit to 8 targets
                color = colors[i % len(colors)]
                target_name = target.get('name', f'Target {i+1}') if isinstance(target, dict) else getattr(target, 'name', f'Target {i+1}')
                
                # Simple visibility curve
                times = []
                altitudes = []
                current_time = start_time
                
                while current_time <= end_time:
                    times.append(current_time)
                    
                    # Offset each target slightly for variety
                    hour_diff = (current_time - start_time).total_seconds() / 3600
                    altitude = 20 + i*5 + 35 * np.sin(np.pi * (hour_diff + i) / 12)
                    altitudes.append(max(0, altitude))
                    
                    current_time += timedelta(minutes=30)
                
                ax.plot(times, altitudes, color=color, linewidth=2, label=target_name, alpha=0.8)
            
            ax.set_ylabel('Altitude (degrees)')
            ax.set_xlabel('Time')
            ax.set_ylim(0, 90)
            ax.set_title("Tonight's Visibility Chart")
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            
            # Add legend
            if targets:
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
            
            log_info(f"Created simple visibility chart for {len(targets)} targets")
            
        except Exception as e:
            log_error(f"Error creating simple visibility chart", e)
            ax.text(0.5, 0.5, 'Chart generation failed', ha='center', va='center', transform=ax.transAxes)

# Global instance
mobile_plot_generator = MobilePlotGenerator()