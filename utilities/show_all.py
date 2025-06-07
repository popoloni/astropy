#!/usr/bin/env python3
"""
Constellation Visualizer

This script visualizes constellation data including:
- Stars (white dots)
- Constellation shapes/lines (light blue)
- Deep sky objects (red dots with labels)
- Nebula paths (red outlines)

Usage: python show_all.py [constellation_id] [options]
Examples: 
  python show_all.py                    # Show all constellations in grid view
  python show_all.py Ori               # Show Orion constellation
  python show_all.py --all             # List all available constellations
"""

import json
import sys
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any
from matplotlib.patches import Ellipse


@dataclass
class PlotConfig:
    """Configuration for plot appearance and behavior"""
    # Display options
    show_labels: bool = True
    show_dso: bool = True
    show_ellipses: bool = True
    show_star_names: bool = False
    use_dso_colors: bool = True
    
    # Resolution settings
    width: int = 16
    height: int = 8
    dpi: int = 200
    
    # Visual settings
    background_color: str = 'black'
    star_color: str = 'white'
    line_color: str = 'lightblue'
    label_color: str = 'yellow'
    bright_star_color: str = 'gold'
    
    @property
    def figsize(self) -> Tuple[int, int]:
        return (self.width, self.height)
    
    @property
    def pixel_dimensions(self) -> Tuple[int, int]:
        return (self.width * self.dpi, self.height * self.dpi)

    @classmethod
    def for_device(cls, device: str) -> 'PlotConfig':
        """Create device-optimized configurations"""
        configs = {
            'ipad': cls(width=12, height=6, dpi=200),
            'imac': cls(width=20, height=10, dpi=150),
            'default': cls(width=16, height=8, dpi=200)
        }
        return configs.get(device, configs['default'])


@dataclass 
class ObjectStats:
    """Statistics for plotted objects"""
    constellations: int = 0
    stars: int = 0
    bright_stars: int = 0
    dso: int = 0
    ellipses: int = 0
    nebula_paths: int = 0
    dso_categories: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.dso_categories is None:
            self.dso_categories = {}


class ConstellationVisualizer:
    def __init__(self, catalogs_path=None):
        if catalogs_path is None:
            # Automatically detect the catalogs path relative to this script
            script_dir = Path(__file__).parent
            self.catalogs_path = script_dir.parent / "catalogs"
        else:
            self.catalogs_path = Path(catalogs_path)
        
        # Load all data catalogs
        self.constellations = self._load_json("constellations.json")
        self.objects = self._load_json("objects.json")
        self.nebula_paths = self._load_json("nebula-paths.json")
        self.simbad_objects = self._load_json("simbad-objects.json")
        
    def _load_json(self, filename: str) -> List[Dict]:
        """Load and parse JSON file with error handling"""
        file_path = self.catalogs_path / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Could not find {file_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {file_path}")
            return []
        except UnicodeDecodeError as e:
            print(f"Error: Unicode decode error in {file_path}: {e}")
            return []
    
    def find_constellation(self, constellation_id: str) -> Optional[Dict]:
        """Find constellation data by ID"""
        for constellation in self.constellations:
            if constellation["id"].lower() == constellation_id.lower():
                return constellation
        return None
    
    def get_constellation_objects(self, constellation_id: str) -> List[Dict]:
        """Get all deep sky objects for a constellation"""
        return [obj for obj in self.objects 
                if obj.get("constellation", "").lower() == constellation_id.lower()]
    
    def get_nebula_paths_for_objects(self, object_ids: List[str]) -> List[Dict]:
        """Get nebula paths for given object IDs"""
        return [nebula for nebula in self.nebula_paths 
                if nebula["objectId"] in object_ids]
    
    @staticmethod
    def normalize_ra(ra: float) -> float:
        """Normalize RA to 0-360 range"""
        while ra < 0:
            ra += 360
        while ra >= 360:
            ra -= 360
        return ra
    
    def get_dso_color_and_category(self, obj: Dict, use_colors: bool = True) -> Tuple[str, str]:
        """Get color and category name for a DSO object"""
        if not use_colors:
            return 'red', 'Deep Sky Objects'
        
        category = obj.get("category", "unknown").lower()
        
        # Major category classification
        if any(x in category for x in ['galaxy']):
            return 'steelblue', 'Galaxies'
        elif any(x in category for x in ['nebula']):
            return 'mediumorchid', 'Nebulae'  
        elif any(x in category for x in ['cluster']):
            return 'orange', 'Clusters'
        else:
            return 'darkorange', 'Other Objects'
    
    def find_simbad_ellipse(self, object_id: str, min_size: float = 0.0167) -> Optional[Dict]:
        """Find SIMBAD ellipse data for an object"""
        for simbad_obj in self.simbad_objects:
            # Try multiple matching methods
            if (simbad_obj.get('catalogId') == object_id or 
                simbad_obj.get('commonName') == object_id or
                simbad_obj.get('idNgc') == object_id):
                
                ellipse_data = simbad_obj.get('ellipse')
                if ellipse_data:
                    # Check minimum size threshold
                    a = ellipse_data.get('a', 0)
                    b = ellipse_data.get('b', 0)
                    if max(a, b) > min_size:  # 1 arcminute threshold
                        return ellipse_data
        return None
    
    def draw_ellipse(self, ax, ra: float, de: float, ellipse_data: Dict, 
                    color: str, alpha: float = 0.6, linewidth: float = 1.5):
        """Draw an ellipse on the plot"""
        a = ellipse_data['a']  # semi-major axis in degrees
        b = ellipse_data['b']  # semi-minor axis in degrees  
        angle = ellipse_data['r']  # rotation angle in degrees
        
        # Create ellipse patch
        ellipse = Ellipse((ra, de), width=2*a, height=2*b, angle=angle,
                         fill=False, edgecolor=color, linewidth=linewidth, 
                         linestyle='--', alpha=alpha)
        ax.add_patch(ellipse)
    
    def normalize_constellation_coordinates(self, constellation: Dict, objects: List[Dict]):
        """Normalize coordinates and handle RA wraparound for a constellation"""
        # Normalize all RA coordinates 
        for star in constellation["stars"]:
            star["ra"] = self.normalize_ra(star["ra"])
        
        for obj in objects:
            obj["ra"] = self.normalize_ra(obj["ra"])
        
        # Handle RA wraparound (around 0°/360°)
        star_ras = [star["ra"] for star in constellation["stars"]]
        object_ras = [obj["ra"] for obj in objects]
        all_ras = star_ras + object_ras
        
        if len(all_ras) > 1:
            ra_range = max(all_ras) - min(all_ras)
            # If the range is > 180°, we might have wraparound issue
            if ra_range > 180:
                # Convert coordinates > 180° to negative values for better plotting
                for star in constellation["stars"]:
                    if star["ra"] > 180:
                        star["ra"] -= 360
                
                for obj in objects:
                    if obj["ra"] > 180:
                        obj["ra"] -= 360
    
    def separate_stars_and_dso(self, objects: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Separate star objects from actual deep sky objects"""
        stars_in_objects = []
        actual_dso = []
        
        for obj in objects:
            category = obj.get("category", "").lower()
            obj_type = obj.get("type", "").lower()
            
            # Check if this is a star (not a deep sky object)
            if "star" in category or obj_type == "star":
                stars_in_objects.append(obj)
            else:
                actual_dso.append(obj)
        
        return stars_in_objects, actual_dso
    
    def plot_stars(self, ax, stars: List[Dict], config: PlotConfig) -> Dict[str, Tuple[float, float]]:
        """Plot constellation stars and return their positions"""
        star_positions = {}
        for star in stars:
            ra = star["ra"]
            de = star["de"]
            magnitude = star.get("visualMagnitude", 5)
            star_id = star["id"]
            
            # Convert magnitude to marker size (brighter stars = larger)
            size = max(5 if config.width > 15 else 20, 80 / (magnitude + 1))
            
            ax.scatter(ra, de, s=size, c=config.star_color, marker='*', alpha=0.8, 
                      edgecolors='lightgray', linewidths=0.3 if config.width > 15 else 0.5)
            star_positions[star_id] = (ra, de)
            
            # Add star names for bright stars if requested
            if config.show_star_names and magnitude < 2.5:
                star_name = star.get("name", star_id)
                ax.annotate(star_name, (ra, de), xytext=(3, 3), 
                           textcoords='offset points', 
                           fontsize=4 if config.width > 15 else 8,
                           color='lightblue', alpha=0.7)
        
        return star_positions
    
    def plot_constellation_lines(self, ax, constellation: Dict, star_positions: Dict[str, Tuple[float, float]], config: PlotConfig):
        """Plot constellation shape lines"""
        for shape in constellation.get("shapes", []):
            if len(shape) == 2:
                star1_id, star2_id = shape
                if star1_id in star_positions and star2_id in star_positions:
                    x1, y1 = star_positions[star1_id]
                    x2, y2 = star_positions[star2_id]
                    
                    # Handle RA wraparound for lines
                    if abs(x2 - x1) > 180:
                        continue
                        
                    ax.plot([x1, x2], [y1, y2], color=config.line_color, 
                           linewidth=1 if config.width > 15 else 1.5, alpha=0.7)
    
    def plot_bright_stars(self, ax, bright_stars: List[Dict], config: PlotConfig):
        """Plot bright stars from objects list"""
        for obj in bright_stars:
            ra = obj["ra"]
            de = obj["de"]
            name = obj["id"]
            magnitude = obj.get("magnitude", 5)
            
            # Size based on magnitude (brighter = larger)
            size = max(30 if config.width > 15 else 100, 120 / (magnitude + 1))
            
            # Plot as gold star
            ax.scatter(ra, de, s=size, c=config.bright_star_color, marker='*', alpha=0.9, 
                      edgecolors='orange', linewidths=0.5 if config.width > 15 else 1)
            
            # Add label
            label_size = 4 if config.width > 15 else 7  # Smaller, more subtle
            ax.annotate(name, (ra, de), xytext=(2, 2), textcoords='offset points',
                       fontsize=label_size, color=config.bright_star_color, weight='normal')
    
    def plot_dso_objects(self, ax, dso_objects: List[Dict], nebula_path_ids: set, 
                        config: PlotConfig, stats: ObjectStats) -> int:
        """Plot deep sky objects and return ellipse count"""
        ellipse_count = 0
        
        for obj in dso_objects:
            ra = obj["ra"]
            de = obj["de"]
            name = obj["id"]
            magnitude = obj.get("magnitude", 10)
            
            # Get color based on object type
            color, category = self.get_dso_color_and_category(obj, config.use_dso_colors)
            edge_color = 'darkred' if color == 'red' else color
            
            # Track categories for legend
            if category not in stats.dso_categories:
                stats.dso_categories[category] = {'color': color, 'count': 0}
            stats.dso_categories[category]['count'] += 1
            
            # Check for ellipse data
            has_ellipse = False
            if config.show_ellipses and name not in nebula_path_ids:
                ellipse_data = self.find_simbad_ellipse(name)
                if ellipse_data:
                    linewidth = 0.8 if config.width > 15 else 1.5
                    self.draw_ellipse(ax, ra, de, ellipse_data, color, 
                                    alpha=0.6, linewidth=linewidth)
                    ellipse_count += 1
                    has_ellipse = True
            
            # Plot center marker if appropriate
            if name not in nebula_path_ids and (not has_ellipse or not config.show_ellipses):
                # Size based on magnitude for DSOs
                size = max(15 if config.width > 15 else 40, 60 / (magnitude + 1)) if magnitude < 15 else (15 if config.width > 15 else 40)
                
                if config.show_ellipses and not has_ellipse:
                    ax.scatter(ra, de, s=size, c=color, marker='+', 
                             alpha=0.8, linewidths=1.5 if config.width > 15 else 2)
                else:
                    ax.scatter(ra, de, s=size, c=color, marker='o', 
                             alpha=0.8, edgecolors=edge_color, linewidths=0.5)
            
            # Add DSO labels  
            label_color = 'red' if not config.use_dso_colors else color
            label_size = 3 if config.width > 15 else 6  # Even smaller for less clutter
            ax.annotate(name, (ra, de), xytext=(2, 2), textcoords='offset points',
                       fontsize=label_size, color=label_color, weight='normal', alpha=0.8)
        
        return ellipse_count
    
    def plot_nebula_paths(self, ax, nebula_paths: List[Dict], config: PlotConfig):
        """Plot nebula boundary paths"""
        for nebula in nebula_paths:
            path_coords = nebula["path"]
            if len(path_coords) > 2:
                ras = [coord[0] for coord in path_coords]
                des = [coord[1] for coord in path_coords]
                
                # Close the path
                ras.append(ras[0])
                des.append(des[0])
                
                # Plot nebula boundary
                linewidth = 1.2 if config.width > 15 else 2
                ax.plot(ras, des, color='red', linewidth=linewidth, alpha=0.7)
                ax.fill(ras, des, color='red', alpha=0.1)
    
    def setup_plot_style(self, ax, config: PlotConfig, title: str = None):
        """Set up plot styling, axes, and grid"""
        ax.set_facecolor(config.background_color)
        
        # Set axis labels and title
        fontsize = 14 if config.width > 15 else 12
        title_size = 18 if config.width > 15 else 16
        
        ax.set_xlabel('Right Ascension (degrees)', color='white', fontsize=fontsize, weight='bold')
        ax.set_ylabel('Declination (degrees)', color='white', fontsize=fontsize, weight='bold')
        
        if title:
            ax.set_title(title, color='white', fontsize=title_size, weight='bold', 
                        pad=20 if config.width > 15 else 10)
        
        # Invert RA axis (astronomical convention)
        ax.invert_xaxis()
        
        # Get current axis limits to determine appropriate grid spacing
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ra_range = abs(xlim[1] - xlim[0])
        de_range = abs(ylim[1] - ylim[0])
        
        # Determine grid spacing based on range
        if ra_range > 180:  # Full sky or large region
            ra_major_step = 30
            ra_minor_step = 15
            de_major_step = 30
            de_minor_step = 15
        elif ra_range > 60:  # Medium region
            ra_major_step = 15
            ra_minor_step = 5
            de_major_step = 15
            de_minor_step = 5
        else:  # Small region (individual constellation)
            ra_major_step = 10
            ra_minor_step = 2
            de_major_step = 10
            de_minor_step = 2
        
        # Grid setup
        if config.width > 15:  # High resolution grid
            # Calculate tick ranges based on actual axis limits
            ra_start = int(min(xlim) // ra_major_step) * ra_major_step
            ra_end = int(max(xlim) // ra_major_step + 1) * ra_major_step
            de_start = int(min(ylim) // de_major_step) * de_major_step
            de_end = int(max(ylim) // de_major_step + 1) * de_major_step
            
            ra_major_ticks = np.arange(ra_start, ra_end + ra_major_step, ra_major_step)
            ra_minor_ticks = np.arange(ra_start, ra_end + ra_minor_step, ra_minor_step)
            de_major_ticks = np.arange(max(de_start, -90), min(de_end, 90) + de_major_step, de_major_step)
            de_minor_ticks = np.arange(max(de_start, -90), min(de_end, 90) + de_minor_step, de_minor_step)
            
            ax.set_xticks(ra_major_ticks)
            ax.set_xticks(ra_minor_ticks, minor=True)
            ax.set_yticks(de_major_ticks)
            ax.set_yticks(de_minor_ticks, minor=True)
            
            ax.grid(True, which='major', alpha=0.4, color='gray', linewidth=0.8)
            ax.grid(True, which='minor', alpha=0.2, color='gray', linewidth=0.4)
        else:
            ax.grid(True, alpha=0.3, color='gray')
        
        ax.tick_params(colors='white', labelsize=10)
    
    def add_celestial_reference_lines(self, ax, config: PlotConfig):
        """Add celestial reference lines for grid view"""
        if config.width <= 15:  # Only for grid view
            return
            
        # Celestial equator
        ax.axhline(y=0, color='cyan', linewidth=1.5, alpha=0.7, 
                  linestyle=':', label='Celestial Equator')
        
        # Ecliptic (approximate)
        ecliptic_ra = np.linspace(0, 360, 360)
        ecliptic_de = 23.44 * np.sin(np.radians(ecliptic_ra - 80))
        ax.plot(ecliptic_ra, ecliptic_de, color='orange', linewidth=1.5, 
               alpha=0.6, linestyle='--', label='Ecliptic')
        
        # Galactic equator (rough approximation)
        galactic_ra = np.linspace(0, 360, 360)
        galactic_de = 20 * np.sin(np.radians(galactic_ra * 2 - 40)) + 10 * np.cos(np.radians(galactic_ra - 120))
        galactic_de = np.clip(galactic_de, -60, 60)  # Rough bounds
        ax.plot(galactic_ra, galactic_de, color='purple', linewidth=1, 
               alpha=0.4, linestyle='-.', label='Galactic Plane (approx)')
    
    def create_legend(self, ax, stats: ObjectStats, config: PlotConfig, is_grid_view: bool = False):
        """Create comprehensive legend"""
        legend_elements = []
        
        # Stars
        legend_elements.append(
            plt.Line2D([0], [0], marker='*', color='w', markerfacecolor=config.star_color, 
                      markersize=8 if config.width > 15 else 10, 
                      label=f'Constellation Stars ({stats.stars})', 
                      linestyle='None', markeredgecolor='lightgray')
        )
        
        # Constellation lines
        if is_grid_view:
            legend_elements.append(
                plt.Line2D([0], [0], color=config.line_color, linewidth=1.5, 
                          label=f'Constellation Lines ({stats.constellations})')
            )
        else:
            legend_elements.append(
                plt.Line2D([0], [0], color=config.line_color, linewidth=2, 
                          label='Constellation Lines')
            )
        
        # Bright stars
        if stats.bright_stars > 0:
            legend_elements.append(
                plt.Line2D([0], [0], marker='*', color='w', markerfacecolor=config.bright_star_color, 
                          markersize=10 if config.width > 15 else 12, 
                          label=f'Named Stars ({stats.bright_stars})', 
                          linestyle='None', markeredgecolor='orange')
            )
        
        # DSO categories or single entry
        if config.use_dso_colors and stats.dso_categories:
            for category, info in sorted(stats.dso_categories.items()):
                legend_elements.append(
                    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=info['color'], 
                              markersize=6, label=f'{category} ({info["count"]})', 
                              linestyle='None', markeredgecolor=info['color'])
                )
        elif stats.dso > 0:
            legend_elements.append(
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                          markersize=6, label=f'Deep Sky Objects ({stats.dso})', 
                          linestyle='None', markeredgecolor='darkred')
            )
        
        # Nebula boundaries
        if stats.nebula_paths > 0:
            legend_elements.append(
                plt.Line2D([0], [0], color='red', linewidth=2, 
                          label=f'Nebula Boundaries ({stats.nebula_paths})')
            )
        
        # Object ellipses
        if config.show_ellipses and stats.ellipses > 0:
            legend_elements.append(
                plt.Line2D([0], [0], color='gray', linewidth=1.5, linestyle='--', 
                          label=f'Object Boundaries ({stats.ellipses})')
            )
        
        # Reference lines for grid view
        if is_grid_view and config.width > 15:
            legend_elements.extend([
                plt.Line2D([0], [0], color='cyan', linewidth=1.5, linestyle=':', 
                          label='Celestial Equator'),
                plt.Line2D([0], [0], color='orange', linewidth=1.5, linestyle='--', 
                          label='Ecliptic'),
                plt.Line2D([0], [0], color='purple', linewidth=1, linestyle='-.', 
                          label='Galactic Plane (approx)')
            ])
        
        # Create legend
        fontsize = 9 if config.width > 15 else 9
        ax.legend(handles=legend_elements, loc='upper right', fancybox=True, 
                 framealpha=0.95 if is_grid_view else 0.9, 
                 facecolor=config.background_color, edgecolor='white', 
                 labelcolor='white', fontsize=fontsize, 
                 bbox_to_anchor=(0.99, 0.99) if is_grid_view else None)
    
    def plot_all_constellations_grid(self, config: PlotConfig):
        """Plot all constellations in a single high-resolution grid view"""
        print(f"Generating constellation grid view ({config.pixel_dimensions[0]}x{config.pixel_dimensions[1]} pixels)...")
        
        # Create high resolution plot
        fig, ax = plt.subplots(1, 1, figsize=config.figsize, dpi=config.dpi)
        ax.set_facecolor(config.background_color)
        fig.patch.set_facecolor(config.background_color)
        
        stats = ObjectStats()
        
        # Plot each constellation
        for constellation in self.constellations:
            if not constellation.get("stars"):
                continue
                
            stats.constellations += 1
            constellation_id = constellation["id"]
            
            # Get constellation objects and nebula paths
            objects = self.get_constellation_objects(constellation_id)
            object_ids = [obj["id"] for obj in objects]
            nebula_paths = self.get_nebula_paths_for_objects(object_ids)
            nebula_path_ids = set(nebula["objectId"] for nebula in nebula_paths)
            
            # Normalize coordinates
            self.normalize_constellation_coordinates(constellation, objects)
            
            # Plot constellation stars
            star_positions = self.plot_stars(ax, constellation["stars"], config)
            stats.stars += len(constellation["stars"])
            
            # Plot constellation lines
            self.plot_constellation_lines(ax, constellation, star_positions, config)
            
            # Add constellation labels
            if config.show_labels and star_positions:
                center_ra = np.mean([pos[0] for pos in star_positions.values()])
                center_de = np.mean([pos[1] for pos in star_positions.values()])
                
                # Use very small, subtle labels for grid view (like original version)
                fontsize = 4 if config.width > 15 else 6
                ax.annotate(constellation_id, (center_ra, center_de), 
                           fontsize=fontsize, color=config.label_color, alpha=0.7,
                           ha='center', va='center', weight='normal',
                           bbox=dict(boxstyle="round,pad=0.05", facecolor=config.background_color, 
                                   alpha=0.5, edgecolor='none'))
            
            # Plot DSOs if requested
            if config.show_dso and objects:
                bright_stars, actual_dso = self.separate_stars_and_dso(objects)
                
                # Plot bright stars
                self.plot_bright_stars(ax, bright_stars, config)
                stats.bright_stars += len(bright_stars)
                
                # Plot DSOs
                ellipse_count = self.plot_dso_objects(ax, actual_dso, nebula_path_ids, config, stats)
                stats.ellipses += ellipse_count
                stats.dso += len(actual_dso)
                
                # Plot nebula paths
                self.plot_nebula_paths(ax, nebula_paths, config)
                stats.nebula_paths += len(nebula_paths)
        
        # Set up plot appearance
        ax.set_xlim(0, 360)
        ax.set_ylim(-90, 90)
        self.setup_plot_style(ax, config, 'Complete Celestial Sky - All Constellations with Deep Sky Objects')
        
        # Add reference lines for grid view
        self.add_celestial_reference_lines(ax, config)
        
        # Create legend
        self.create_legend(ax, stats, config, is_grid_view=True)
        
        plt.tight_layout()
        plt.show()
        
        # Print summary
        self.print_stats_summary(stats, config)
    
    def calculate_constellation_bounds(self, constellation: Dict, objects: List[Dict]) -> Tuple[float, float, float, float]:
        """Calculate the bounding box for a constellation and its objects"""
        all_ras = []
        all_des = []
        
        # Add constellation star coordinates
        for star in constellation["stars"]:
            all_ras.append(star["ra"])
            all_des.append(star["de"])
        
        # Add object coordinates
        for obj in objects:
            all_ras.append(obj["ra"])
            all_des.append(obj["de"])
        
        if not all_ras:
            return 0, 360, -90, 90  # Fallback to full sky
        
        min_ra, max_ra = min(all_ras), max(all_ras)
        min_de, max_de = min(all_des), max(all_des)
        
        # Add padding (10% of range, minimum 5 degrees)
        ra_range = max_ra - min_ra
        de_range = max_de - min_de
        
        ra_padding = max(ra_range * 0.1, 5.0)
        de_padding = max(de_range * 0.1, 5.0)
        
        # Apply padding
        min_ra -= ra_padding
        max_ra += ra_padding
        min_de -= de_padding
        max_de += de_padding
        
        # Clamp declination to valid range
        min_de = max(min_de, -90)
        max_de = min(max_de, 90)
        
        return min_ra, max_ra, min_de, max_de

    def plot_constellation(self, constellation_id: str, config: PlotConfig):
        """Plot individual constellation with all elements"""
        print(f"Generating focused view for constellation {constellation_id.upper()} ({config.pixel_dimensions[0]}x{config.pixel_dimensions[1]} pixels)...")
        
        # Find constellation data
        constellation = self.find_constellation(constellation_id)
        if not constellation:
            print(f"Constellation '{constellation_id}' not found!")
            return
        
        # Get associated objects and paths
        objects = self.get_constellation_objects(constellation_id)
        object_ids = [obj["id"] for obj in objects]
        nebula_paths = self.get_nebula_paths_for_objects(object_ids)
        nebula_path_ids = set(nebula["objectId"] for nebula in nebula_paths)
        
        # Normalize coordinates
        self.normalize_constellation_coordinates(constellation, objects)
        
        # Calculate constellation bounds
        min_ra, max_ra, min_de, max_de = self.calculate_constellation_bounds(constellation, objects)
        print(f"Constellation bounds: RA {min_ra:.1f}° to {max_ra:.1f}°, DE {min_de:.1f}° to {max_de:.1f}°")
        
        # Create the plot with proper DPI
        fig, ax = plt.subplots(1, 1, figsize=config.figsize, dpi=config.dpi)
        ax.set_facecolor(config.background_color)
        fig.patch.set_facecolor(config.background_color)
        
        stats = ObjectStats()
        stats.constellations = 1
        
        # Plot constellation elements
        star_positions = self.plot_stars(ax, constellation["stars"], config)
        stats.stars = len(constellation["stars"])
        
        self.plot_constellation_lines(ax, constellation, star_positions, config)
        
        # Plot objects if available
        if objects:
            bright_stars, actual_dso = self.separate_stars_and_dso(objects)
            
            self.plot_bright_stars(ax, bright_stars, config)
            stats.bright_stars = len(bright_stars)
            
            stats.ellipses = self.plot_dso_objects(ax, actual_dso, nebula_path_ids, config, stats)
            stats.dso = len(actual_dso)
            
            self.plot_nebula_paths(ax, nebula_paths, config)
            stats.nebula_paths = len(nebula_paths)
        
        # Set up plot appearance with constellation-specific bounds
        ax.set_xlim(min_ra, max_ra)
        ax.set_ylim(min_de, max_de)
        self.setup_plot_style(ax, config, f'Constellation {constellation_id.upper()}')
        
        # Create legend
        self.create_legend(ax, stats, config, is_grid_view=False)
        
        plt.tight_layout()
        plt.show()
    
    def print_stats_summary(self, stats: ObjectStats, config: PlotConfig):
        """Print summary statistics"""
        if stats.constellations > 1:  # Grid view
            print(f"High-resolution grid view complete:")
            print(f"  • {stats.constellations} constellations")
        else:  # Individual constellation
            print(f"Individual constellation view complete:")
        
        print(f"  • {stats.stars} constellation stars")
        if stats.bright_stars > 0:
            print(f"  • {stats.bright_stars} named bright stars")
        if stats.dso > 0:
            print(f"  • {stats.dso} deep sky objects")
        if stats.ellipses > 0:
            print(f"  • {stats.ellipses} object boundaries")
        if stats.nebula_paths > 0:
            print(f"  • {stats.nebula_paths} nebula boundaries")
        
        # Always show resolution information
        print(f"Resolution: {config.width}x{config.height} inches at {config.dpi} DPI ({config.pixel_dimensions[0]}x{config.pixel_dimensions[1]} pixels)")
    
    def list_available_constellations(self) -> List[str]:
        """List all available constellation IDs"""
        constellation_ids = [const["id"] for const in self.constellations]
        constellation_ids.sort()
        return constellation_ids


def main():
    parser = argparse.ArgumentParser(
        description='Visualize astronomical constellations with stars, lines, and deep sky objects.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python show_all.py                       # Show all constellations (default: 3200x1600 pixels)
  python show_all.py --imac                # Optimized for iMac (3000x1500 pixels)
  python show_all.py --ipad                # Optimized for iPad (2400x1200 pixels)
  python show_all.py Ori                   # Orion with colored DSOs and ellipses
  python show_all.py Cyg --no-colors-for-dso  # Cygnus with red DSOs only
  python show_all.py And --no-ellipses     # Andromeda with dots only (no ellipses)
  python show_all.py --all                 # List all available constellation IDs
        """
    )
    
    parser.add_argument('constellation_id', nargs='?', 
                       help='Constellation ID (e.g., Ori, Cyg, UMa). If omitted, shows high-resolution grid view of all constellations.')
    parser.add_argument('--no-colors-for-dso', action='store_true',
                       help='Use red color for all deep sky objects (classic mode)')
    parser.add_argument('--no-ellipses', action='store_true',
                       help='Hide object boundary ellipses (dots only mode)')
    parser.add_argument('--all', action='store_true',
                       help='List all available constellation IDs')
    parser.add_argument('--no-labels', action='store_true',
                       help='Hide constellation labels in grid view')
    parser.add_argument('--no-dso', action='store_true',
                       help='Hide deep sky objects in grid view (stars and lines only)')
    parser.add_argument('--show-star-names', action='store_true',
                       help='Show names for bright stars in grid view')
    parser.add_argument('--imac', action='store_true',
                       help='Optimize for iMac display (20x10 inches, 150 DPI = 3000x1500 pixels)')
    parser.add_argument('--ipad', action='store_true',
                       help='Optimize for iPad display (12x6 inches, 200 DPI = 2400x1200 pixels)')
    
    args = parser.parse_args()
    
    # Create visualizer
    visualizer = ConstellationVisualizer()
    
    # Handle --all flag (list constellations)
    if args.all:
        available = visualizer.list_available_constellations()
        print(f"Available constellations ({len(available)}):")
        for i, const_id in enumerate(available):
            print(f"{const_id}", end="  ")
            if (i + 1) % 10 == 0:  # New line every 10 items
                print()
        print()
        return
    
    # Create configuration based on arguments
    if args.imac:
        config = PlotConfig.for_device('imac')
        print("Using iMac optimization: 20x10 inches at 150 DPI (3000x1500 pixels)")
    elif args.ipad:
        config = PlotConfig.for_device('ipad')
        print("Using iPad optimization: 12x6 inches at 200 DPI (2400x1200 pixels)")
    else:
        config = PlotConfig.for_device('default')
        if not args.constellation_id:
            print("Using default optimization: 16x8 inches at 200 DPI (3200x1600 pixels)")
    
    # Apply argument overrides to config
    config.show_labels = not args.no_labels
    config.show_dso = not args.no_dso
    config.show_ellipses = not args.no_ellipses
    config.use_dso_colors = not args.no_colors_for_dso
    config.show_star_names = args.show_star_names
    
    # If no constellation specified, show grid view
    if not args.constellation_id:
        print("No constellation specified. Showing high-resolution grid view of all constellations...")
        print("This creates a detailed image perfect for iPad viewing and zooming.")
        print("Use --all to list available constellation IDs")
        print("Use a constellation ID to view individual constellation details")
        
        visualizer.plot_all_constellations_grid(config)
        return
    
    # Plot individual constellation
    visualizer.plot_constellation(args.constellation_id, config)


if __name__ == "__main__":
    main()
