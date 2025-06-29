"""
Desktop constellation plotting functions for AstroScope application.
This module provides constellation plotting functions extracted from the
constellation_visualizer utility to make them available as shared functions.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Ellipse
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import logging

from ..base import setup_altaz_plot, PlotConfig, get_color_cycle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConstellationPlotter:
    """Constellation plotting class with shared functionality"""
    
    def __init__(self, catalogs_path=None):
        if catalogs_path is None:
            # Automatically detect the catalogs path relative to this script
            script_dir = Path(__file__).parent
            self.catalogs_path = script_dir.parent.parent / "catalogs"
        else:
            self.catalogs_path = Path(catalogs_path)
        
        self.constellations = self._load_json("constellations.json")
        self.objects = self._load_json("objects.json")
        self.nebula_paths = self._load_json("nebula-paths.json")
        self.simbad_objects = self._load_json("simbad-objects.json")
        
    def _load_json(self, filename):
        """Load and parse JSON file"""
        file_path = self.catalogs_path / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Could not find {file_path}")
            return []
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {file_path}")
            return []
    
    def find_constellation(self, constellation_id):
        """Find constellation data by ID"""
        for constellation in self.constellations:
            if constellation["id"].lower() == constellation_id.lower():
                return constellation
        return None
    
    def get_constellation_objects(self, constellation_id):
        """Get all deep sky objects for a constellation"""
        constellation_objects = []
        for obj in self.objects:
            if obj.get("constellation", "").lower() == constellation_id.lower():
                constellation_objects.append(obj)
        return constellation_objects
    
    def get_nebula_paths_for_objects(self, object_ids):
        """Get nebula paths for given object IDs"""
        paths = []
        for nebula in self.nebula_paths:
            if nebula["objectId"] in object_ids:
                paths.append(nebula)
        return paths
    
    def normalize_ra(self, ra):
        """Normalize RA to 0-360 range"""
        while ra < 0:
            ra += 360
        while ra >= 360:
            ra -= 360
        return ra
    
    def get_dso_color_and_category(self, obj, use_colors=True):
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
    
    def find_simbad_ellipse(self, object_id):
        """Find SIMBAD ellipse data for an object"""
        for simbad_obj in self.simbad_objects:
            # Try multiple matching methods
            if (simbad_obj.get('catalogId') == object_id or 
                simbad_obj.get('commonName') == object_id or
                simbad_obj.get('idNgc') == object_id):
                
                ellipse_data = simbad_obj.get('ellipse')
                if ellipse_data:
                    # Only return ellipses that are large enough to be visible (>3 arcmin = 0.05°)
                    a = ellipse_data.get('a', 0)
                    b = ellipse_data.get('b', 0)
                    if max(a, b) > 0.05:  # 3 arcminutes threshold
                        return ellipse_data
        return None
    
    def draw_ellipse(self, ax, ra, de, ellipse_data, color, alpha=0.6):
        """Draw an ellipse on the plot"""
        a = ellipse_data['a']  # semi-major axis in degrees
        b = ellipse_data['b']  # semi-minor axis in degrees  
        angle = ellipse_data['r']  # rotation angle in degrees
        
        # Create ellipse patch
        ellipse = Ellipse((ra, de), width=2*a, height=2*b, angle=angle,
                         fill=False, edgecolor=color, linewidth=1.5, 
                         linestyle='--', alpha=alpha)
        ax.add_patch(ellipse)
    
    def normalize_constellation_coordinates(self, constellation, objects):
        """Normalize all RA coordinates to the same system"""
        # Normalize all RA coordinates to the same system
        for star in constellation["stars"]:
            star["ra"] = self.normalize_ra(star["ra"])
        
        for obj in objects:
            obj["ra"] = self.normalize_ra(obj["ra"])
        
        # Check if we need to handle RA wraparound (around 0°/360°)
        star_ras = [star["ra"] for star in constellation["stars"]]
        object_ras = [obj["ra"] for obj in objects]
        all_ras = star_ras + object_ras
        
        if len(all_ras) > 0:
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


def plot_constellation_stars(ax, constellation, color='white', size_factor=1.0):
    """Plot constellation stars"""
    star_positions = {}
    for star in constellation["stars"]:
        ra = star["ra"]
        de = star["de"]
        magnitude = star.get("visualMagnitude", 5)
        star_id = star["id"]
        
        # Convert magnitude to marker size (brighter stars = larger)
        size = max(20, 200 / (magnitude + 2)) * size_factor
        
        ax.scatter(ra, de, s=size, c=color, marker='*', alpha=0.8, edgecolors='lightgray')
        star_positions[star_id] = (ra, de)
    
    return star_positions


def plot_constellation_lines(ax, constellation, star_positions, color='lightblue', linewidth=1.5):
    """Plot constellation shape lines"""
    for shape in constellation.get("shapes", []):
        if len(shape) == 2:
            star1_id, star2_id = shape
            if star1_id in star_positions and star2_id in star_positions:
                x1, y1 = star_positions[star1_id]
                x2, y2 = star_positions[star2_id]
                ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, alpha=0.7)


def plot_deep_sky_objects(ax, plotter, objects, use_dso_colors=True, show_ellipses=True, objects_with_paths=None):
    """Plot deep sky objects with color coding and ellipses"""
    if objects_with_paths is None:
        objects_with_paths = set()
    
    # Separate stars from actual deep sky objects
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
    
    # Plot bright stars from objects list (yellow star markers)
    for obj in stars_in_objects:
        ra = obj["ra"]
        de = obj["de"]
        name = obj["id"]
        magnitude = obj.get("magnitude", 5)
        
        # Size based on magnitude (brighter = larger)
        size = max(100, 300 / (magnitude + 1))
        
        # Plot as yellow star
        ax.scatter(ra, de, s=size, c='gold', marker='*', alpha=0.9, 
                  edgecolors='orange', linewidth=1)
        
        # Add label
        ax.annotate(name, (ra, de), xytext=(5, 5), textcoords='offset points',
                   fontsize=9, color='gold', weight='bold')
    
    # Plot actual deep sky objects with color coding
    ellipse_count = 0
    for obj in actual_dso:
        ra = obj["ra"]
        de = obj["de"]
        name = obj["id"]
        
        # Get color based on object type
        color, _ = plotter.get_dso_color_and_category(obj, use_dso_colors)
        edge_color = 'darkred' if color == 'red' else color
        
        # Check if object has ellipse data and if we should show it
        has_ellipse = False
        if show_ellipses and name not in objects_with_paths:
            ellipse_data = plotter.find_simbad_ellipse(name)
            if ellipse_data:
                plotter.draw_ellipse(ax, ra, de, ellipse_data, color)
                ellipse_count += 1
                has_ellipse = True
        
        # Only plot center marker if:
        # - Object doesn't have a nebula path AND
        # - (Object doesn't have an ellipse OR ellipse mode is off)
        if name not in objects_with_paths and (not has_ellipse or not show_ellipses):
            if show_ellipses and not has_ellipse:
                # Small + marker for objects without boundaries when ellipse mode is on
                ax.scatter(ra, de, s=40, c=color, marker='+', alpha=0.8, linewidths=2)
            else:
                # Regular dot when ellipse mode is off or when object has ellipse
                ax.scatter(ra, de, s=100, c=color, marker='o', alpha=0.8, edgecolors=edge_color)
        
        # Always add label (even for objects with nebula paths)
        label_color = 'red' if not use_dso_colors else color
        ax.annotate(name, (ra, de), xytext=(5, 5), textcoords='offset points',
                   fontsize=8, color=label_color, weight='bold')
    
    return stars_in_objects, actual_dso, ellipse_count


def plot_nebula_paths(ax, nebula_paths, color='red', linewidth=2, alpha=0.6):
    """Plot nebula boundaries as red outlines"""
    for nebula in nebula_paths:
        path_coords = nebula["path"]
        if len(path_coords) > 2:
            # Extract RA and Dec coordinates
            ras = [coord[0] for coord in path_coords]
            des = [coord[1] for coord in path_coords]
            
            # Close the path by connecting last point to first
            ras.append(ras[0])
            des.append(des[0])
            
            # Plot as red outline
            ax.plot(ras, des, color=color, linewidth=linewidth, alpha=alpha)
            
            # Optional: fill with transparent red
            ax.fill(ras, des, color=color, alpha=0.1)


def create_constellation_legend(ax, constellation, stars_in_objects, actual_dso, nebula_paths, 
                               ellipse_count, use_dso_colors=True):
    """Create comprehensive legend for constellation plot"""
    legend_elements = [
        plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='white', 
                  markersize=10, label=f'Constellation Stars ({len(constellation["stars"])})', 
                  linestyle='None', markeredgecolor='lightgray'),
        plt.Line2D([0], [0], color='lightblue', linewidth=2, label='Constellation Lines'),
        plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='gold', 
                  markersize=12, label=f'Bright Stars ({len(stars_in_objects)})', 
                  linestyle='None', markeredgecolor='orange')
    ]
    
    # Add DSO legend entries based on mode
    if use_dso_colors:
        # Group DSOs by color/category  
        dso_categories = {}
        plotter = ConstellationPlotter()  # Create instance for category function
        for obj in actual_dso:
            color, category = plotter.get_dso_color_and_category(obj, use_dso_colors)
            if category not in dso_categories:
                dso_categories[category] = {'color': color, 'count': 0}
            dso_categories[category]['count'] += 1
        
        # Add legend entries for each category present
        for category, info in sorted(dso_categories.items()):
            legend_elements.append(
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=info['color'], 
                          markersize=8, label=f'{category} ({info["count"]})', 
                          linestyle='None', markeredgecolor=info['color'])
            )
    else:
        # Single red entry for all DSOs
        legend_elements.append(
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                      markersize=8, label=f'Deep Sky Objects ({len(actual_dso)})', 
                      linestyle='None', markeredgecolor='darkred')
        )
    
    # Add nebula boundaries
    legend_elements.append(
        plt.Line2D([0], [0], color='red', linewidth=2, label=f'Nebula Boundaries ({len(nebula_paths)})')
    )
    
    # Add object ellipses if shown
    if ellipse_count > 0:
        legend_elements.append(
            plt.Line2D([0], [0], color='gray', linewidth=1.5, linestyle='--', 
                      label=f'Object Boundaries ({ellipse_count})')
        )
    
    ax.legend(handles=legend_elements, loc='upper right', fancybox=True, 
             framealpha=0.9, facecolor='black', edgecolor='white', 
             labelcolor='white', fontsize=9)


def plot_constellation_map(constellation_id, use_dso_colors=True, show_ellipses=True, catalogs_path=None):
    """Main function to plot a complete constellation map"""
    # Create plotter instance
    plotter = ConstellationPlotter(catalogs_path)
    
    # Find constellation data
    constellation = plotter.find_constellation(constellation_id)
    if not constellation:
        logger.error(f"Constellation '{constellation_id}' not found!")
        return None
    
    # Get associated objects
    objects = plotter.get_constellation_objects(constellation_id)
    object_ids = [obj["id"] for obj in objects]
    nebula_paths = plotter.get_nebula_paths_for_objects(object_ids)
    
    # Normalize coordinates
    plotter.normalize_constellation_coordinates(constellation, objects)
    
    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    
    # Plot constellation stars
    star_positions = plot_constellation_stars(ax, constellation)
    
    # Plot constellation lines
    plot_constellation_lines(ax, constellation, star_positions)
    
    # Get objects with nebula paths
    objects_with_paths = set(nebula["objectId"] for nebula in nebula_paths)
    
    # Plot deep sky objects
    stars_in_objects, actual_dso, ellipse_count = plot_deep_sky_objects(
        ax, plotter, objects, use_dso_colors, show_ellipses, objects_with_paths)
    
    # Plot nebula paths
    plot_nebula_paths(ax, nebula_paths)
    
    # Set up the plot
    ax.set_xlabel('Right Ascension (degrees)', color='white')
    ax.set_ylabel('Declination (degrees)', color='white')
    ax.set_title(f'Constellation {constellation_id.upper()}', color='white', fontsize=16)
    
    # Invert RA axis (astronomical convention)
    ax.invert_xaxis()
    
    # Set tick colors
    ax.tick_params(colors='white')
    
    # Add grid
    ax.grid(True, alpha=0.3, color='gray')
    
    # Create legend
    create_constellation_legend(ax, constellation, stars_in_objects, actual_dso, 
                               nebula_paths, ellipse_count, use_dso_colors)
    
    plt.tight_layout()
    
    return fig, ax 