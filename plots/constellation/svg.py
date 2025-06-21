#!/usr/bin/env python3
"""
SVG Constellation Plotting Module

Contains core SVG plotting functions migrated from show_all_constellations.py
"""

import numpy as np
from typing import List, Dict, Tuple


def coord_to_svg(ra: float, de: float, config, bounds: Tuple[float, float, float, float]) -> Tuple[float, float]:
    """Convert celestial coordinates to SVG coordinates"""
    min_ra, max_ra, min_de, max_de = bounds
    
    # Convert to SVG coordinates 
    # For astronomical displays: RA increases right to left (east to west)
    # So we flip the RA coordinate transformation
    x = config.width * (1 - (ra - min_ra) / (max_ra - min_ra))
    # SVG Y axis is inverted compared to celestial coordinates
    y = config.height * (1 - (de - min_de) / (max_de - min_de))
    
    return x, y


def create_svg_output(config, bounds: Tuple[float, float, float, float], 
                     elements: List[str], stats) -> str:
    """Create complete SVG document"""
    min_ra, max_ra, min_de, max_de = bounds
    
    # SVG header with proper scaling
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{config.width}" height="{config.height}" 
     viewBox="0 0 {config.width} {config.height}"
     xmlns="http://www.w3.org/2000/svg"
     style="background-color: {config.background_color};">
     
  <!-- Scalable constellation visualization -->
  <defs>
    <!-- Star symbol -->
    <g id="star">
      <polygon points="0,-1 0.3,-0.3 1,0 0.3,0.3 0,1 -0.3,0.3 -1,0 -0.3,-0.3" 
               fill="currentColor" stroke="none"/>
    </g>
    
    <!-- Bright star symbol -->
    <g id="bright-star">
      <polygon points="0,-1.2 0.35,-0.35 1.2,0 0.35,0.35 0,1.2 -0.35,0.35 -1.2,0 -0.35,-0.35" 
               fill="currentColor" stroke="none"/>
    </g>
  </defs>
  
  <!-- Grid lines -->
  <g id="grid" stroke="#333" stroke-width="0.1" opacity="0.3">
'''
    
    # Add coordinate grid for reference
    if max_ra - min_ra > 90:  # Large area - add grid
        for ra in range(int(min_ra), int(max_ra) + 30, 30):
            x, _ = coord_to_svg(ra, 0, config, bounds)
            svg_content += f'    <line x1="{x}" y1="0" x2="{x}" y2="{config.height}"/>\n'
        
        for de in range(int(min_de), int(max_de) + 30, 30):
            _, y = coord_to_svg(0, de, config, bounds)
            svg_content += f'    <line x1="0" y1="{y}" x2="{config.width}" y2="{y}"/>\n'
    
    svg_content += '  </g>\n\n'
    
    # Add all plot elements
    svg_content += '  <!-- Constellation elements -->\n'
    svg_content += '\n'.join(elements)
    
    # Add title and info
    title = f"Celestial Sky ({stats.constellations} constellations)" if stats.constellations > 1 else "Constellation View"
    svg_content += f'''
  
  <!-- Title and info -->
  <text x="{config.width/2}" y="25" text-anchor="middle" 
        fill="white" font-size="{config.constellation_font_size * 1.5}" font-weight="bold">
    {title}
  </text>
  
  <text x="10" y="{config.height - 10}" fill="white" font-size="{config.font_size}">
    RA: {min_ra:.1f}° to {max_ra:.1f}° | DE: {min_de:.1f}° to {max_de:.1f}° | 
    Stars: {stats.stars} | DSO: {stats.dso} | Vector SVG
  </text>
  
</svg>'''
    
    return svg_content


def calculate_bounds(constellation_data_list: List[Tuple[Dict, str]], 
                    objects_dict: Dict[str, List[Dict]]) -> Tuple[float, float, float, float]:
    """Calculate bounding box for all data"""
    all_ras, all_des = [], []
    
    for constellation, constellation_id in constellation_data_list:
        for star in constellation["stars"]:
            all_ras.append(star["ra"])
            all_des.append(star["de"])
        
        for obj in objects_dict.get(constellation_id, []):
            all_ras.append(obj["ra"])
            all_des.append(obj["de"])
    
    if not all_ras:
        return 0, 360, -90, 90
    
    min_ra, max_ra = min(all_ras), max(all_ras)
    min_de, max_de = min(all_des), max(all_des)
    
    # Add padding
    ra_range = max_ra - min_ra
    de_range = max_de - min_de
    
    if ra_range > 180:  # Full sky view
        return 0, 360, -90, 90
    
    # Add 10% padding, minimum 5 degrees
    ra_padding = max(ra_range * 0.1, 5.0)
    de_padding = max(de_range * 0.1, 5.0)
    
    return (max(min_ra - ra_padding, 0), 
           min(max_ra + ra_padding, 360),
           max(min_de - de_padding, -90), 
           min(max_de + de_padding, 90))


def plot_stars_svg(stars: List[Dict], config, bounds: Tuple[float, float, float, float]) -> Tuple[List[str], Dict[str, Tuple[float, float]]]:
    """Generate SVG elements for constellation stars"""
    elements = []
    star_positions = {}
    
    for star in stars:
        ra, de = star["ra"], star["de"]
        magnitude = star.get("visualMagnitude", 5)
        star_id = star["id"]
        
        x, y = coord_to_svg(ra, de, config, bounds)
        
        # Size based on magnitude
        size = max(0.5, config.star_base_size / (magnitude + 1))
        
        # Create star element
        elements.append(f'  <use href="#star" x="{x}" y="{y}" '
                      f'transform="scale({size})" fill="{config.star_color}" opacity="0.9"/>')
        
        star_positions[star_id] = (x, y)
        
        # Add star names for bright stars if requested
        if config.show_star_names and magnitude < 2.5:
            star_name = star.get("name", star_id)
            elements.append(f'  <text x="{x + 3}" y="{y - 3}" fill="#87CEEB" '
                          f'font-size="{config.font_size * 0.8}" opacity="0.8">{star_name}</text>')
    
    return elements, star_positions


def plot_constellation_lines_svg(constellation: Dict, star_positions: Dict[str, Tuple[float, float]], 
                               config) -> List[str]:
    """Generate SVG elements for constellation lines"""
    elements = []
    
    for shape in constellation.get("shapes", []):
        if len(shape) == 2:
            star1_id, star2_id = shape
            if star1_id in star_positions and star2_id in star_positions:
                x1, y1 = star_positions[star1_id]
                x2, y2 = star_positions[star2_id]
                
                # Skip wraparound lines
                if abs(x2 - x1) <= config.width * 0.7:  # Reasonable threshold
                    elements.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                                  f'stroke="{config.line_color}" stroke-width="{config.line_width}" '
                                  f'opacity="0.8"/>')
    
    return elements


def plot_bright_stars_svg(bright_stars: List[Dict], config, bounds: Tuple[float, float, float, float]) -> List[str]:
    """Generate SVG elements for bright stars"""
    elements = []
    
    for obj in bright_stars:
        ra, de = obj["ra"], obj["de"]
        name = obj["id"]
        magnitude = obj.get("magnitude", 5)
        
        x, y = coord_to_svg(ra, de, config, bounds)
        
        # Size based on magnitude
        size = max(0.8, config.bright_star_base_size / (magnitude + 1))
        
        # Create bright star element
        elements.append(f'  <use href="#bright-star" x="{x}" y="{y}" '
                      f'transform="scale({size})" fill="{config.bright_star_color}" opacity="0.95"/>')
        
        # Add label
        elements.append(f'  <text x="{x + 3}" y="{y - 3}" fill="{config.bright_star_color}" '
                      f'font-size="{config.font_size * 0.9}" font-weight="bold">{name}</text>')
    
    return elements


def plot_dso_objects_svg(dso_objects: List[Dict], nebula_path_ids: set, 
                       config, bounds: Tuple[float, float, float, float], 
                       stats, plotter) -> List[str]:
    """Generate SVG elements for deep sky objects"""
    # Import astronomy utilities for DSO color function
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from astronomy.celestial import get_dso_color_and_category
    
    elements = []
    
    for obj in dso_objects:
        ra, de = obj["ra"], obj["de"]
        name = obj["id"]
        magnitude = obj.get("magnitude", 10)
        
        x, y = coord_to_svg(ra, de, config, bounds)
        
        # Get color and track categories
        color, category = get_dso_color_and_category(obj, config.use_dso_colors)
        if category not in stats.dso_categories:
            stats.dso_categories[category] = {'color': color, 'count': 0}
        stats.dso_categories[category]['count'] += 1
        
        # Check for ellipse
        has_ellipse = False
        if config.show_ellipses and name not in nebula_path_ids:
            ellipse_data = plotter.find_simbad_ellipse(name)
            if ellipse_data and ellipse_data.get('a', 0) > 0.0167:  # Minimum size check
                # Convert ellipse to SVG coordinates
                a = ellipse_data['a'] * config.width / 360  # Scale to SVG
                b = ellipse_data['b'] * config.height / 180
                angle = ellipse_data['r']
                
                elements.append(f'  <ellipse cx="{x}" cy="{y}" rx="{a}" ry="{b}" '
                              f'transform="rotate({angle} {x} {y})" '
                              f'fill="none" stroke="{color}" stroke-width="0.2" '
                              f'stroke-dasharray="2,1" opacity="0.7"/>')
                stats.ellipses += 1
                has_ellipse = True
        
        # Plot center marker if appropriate
        if name not in nebula_path_ids and (not has_ellipse or not config.show_ellipses):
            size = max(0.5, config.dso_base_size / (magnitude + 1)) if magnitude < 15 else 0.5
            
            if config.show_ellipses and not has_ellipse:
                # Plus marker
                elements.append(f'  <g transform="translate({x},{y}) scale({size})">')
                elements.append(f'    <line x1="-2" y1="0" x2="2" y2="0" stroke="{color}" stroke-width="0.5"/>')
                elements.append(f'    <line x1="0" y1="-2" x2="0" y2="2" stroke="{color}" stroke-width="0.5"/>')
                elements.append('  </g>')
            else:
                # Circle marker
                elements.append(f'  <circle cx="{x}" cy="{y}" r="{size}" '
                              f'fill="{color}" stroke="{color}" stroke-width="0.1" opacity="0.9"/>')
        
        # Add label
        label_color = '#FF0000' if not config.use_dso_colors else color
        elements.append(f'  <text x="{x + 2}" y="{y + 2}" fill="{label_color}" '
                      f'font-size="{config.font_size * 0.7}" font-weight="bold" opacity="0.9">{name}</text>')
    
    return elements


def plot_nebula_paths_svg(nebula_paths: List[Dict], config, bounds: Tuple[float, float, float, float]) -> List[str]:
    """Generate SVG elements for nebula paths"""
    elements = []
    
    for nebula in nebula_paths:
        path_coords = nebula["path"]
        if len(path_coords) > 2:
            # Convert coordinates to SVG path
            svg_path = "M "
            for i, coord in enumerate(path_coords):
                x, y = coord_to_svg(coord[0], coord[1], config, bounds)
                if i == 0:
                    svg_path += f"{x},{y} "
                else:
                    svg_path += f"L {x},{y} "
            svg_path += "Z"  # Close path
            
            # Add filled path
            elements.append(f'  <path d="{svg_path}" fill="#FF0000" fill-opacity="0.1" '
                          f'stroke="#FF0000" stroke-width="0.3" stroke-opacity="0.7"/>')
    
    return elements
