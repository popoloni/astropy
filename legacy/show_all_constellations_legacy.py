#!/usr/bin/env python3
"""
Constellation Visualizer - Vector SVG Edition with Live Pythonista Viewing

This script creates scalable vector constellation visualizations using SVG output.
Perfect for high-resolution displays and infinite zooming capability.
Includes live viewing in Pythonista!

Usage: python show_all.py [constellation_id] [options]
Examples: 
  python show_all.py                   # SVG grid view with live preview
  python show_all.py Ori               # SVG view of Orion with live preview
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
import io
import base64
import webbrowser
import tempfile
import os

# Pythonista-specific imports
try:
    import console
    import ui
    from objc_util import *
    PYTHONISTA_AVAILABLE = True
    print("🍎 Pythonista detected - Live SVG viewing enabled!")
except ImportError:
    PYTHONISTA_AVAILABLE = False
    print("💻 Running on desktop - Browser SVG viewing enabled!")


@dataclass
class VectorConfig:
    """Configuration for vector SVG output"""
    # Display options
    show_labels: bool = True
    show_dso: bool = True
    show_ellipses: bool = True
    show_star_names: bool = False
    use_dso_colors: bool = True
    
    # SVG output settings
    width: int = 1200        # SVG width in units (scalable)
    height: int = 600        # SVG height in units (scalable)
    save_svg: bool = True    # Whether to save SVG file
    svg_filename: str = "images/constellation_map.svg"
    show_live: bool = True   # Whether to show live preview
    
    # Visual settings (all scalable)
    background_color: str = '#000000'
    star_color: str = '#FFFFFF'
    line_color: str = '#87CEEB'
    label_color: str = '#FFFF00'
    bright_star_color: str = '#FFD700'
    
    # Base sizes (will scale with SVG)
    star_base_size: float = 2.0
    bright_star_base_size: float = 3.0
    dso_base_size: float = 1.5
    line_width: float = 0.3
    font_size: float = 4.0
    constellation_font_size: float = 6.0
    
    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height
    
    @classmethod
    def for_grid_view(cls) -> 'VectorConfig':
        """Optimized for full sky grid view"""
        return cls(
            width=1440,          # 2:1 aspect ratio for celestial coordinates
            height=720,
            svg_filename="images/celestial_grid.svg",
            star_base_size=1.5,
            font_size=3.0,
            constellation_font_size=5.0,
            line_width=0.2
        )
    
    @classmethod  
    def for_constellation(cls, constellation_id: str) -> 'VectorConfig':
        """Optimized for single constellation view"""
        return cls(
            width=800,           # Square-ish for individual constellations
            height=600,
            svg_filename=f"images/constellation_{constellation_id.lower()}.svg",
            star_base_size=3.0,
            font_size=5.0,
            constellation_font_size=8.0,
            line_width=0.5
        )


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


class PythonistaWebView:
    """Live SVG viewer for Pythonista using WebView"""
    
    def __init__(self, title: str = "Constellation Map"):
        self.title = title
        self.webview = None
        
    def show_svg(self, svg_content: str, stats: ObjectStats):
        """Display SVG content in Pythonista WebView"""
        if not PYTHONISTA_AVAILABLE:
            print("Pythonista not available - skipping live view")
            return
            
        try:
            # Create HTML wrapper for the SVG with zoom controls
            html_content = self._create_html_wrapper(svg_content, stats)
            
            # Create and show WebView
            self.webview = ui.WebView()
            self.webview.name = self.title
            self.webview.background_color = 'black'
            
            # Load the HTML content
            self.webview.load_html(html_content)
            
            # Present full screen
            self.webview.present('fullscreen', hide_title_bar=False)
            
            print("🌟 Live SVG view opened in Pythonista WebView!")
            print("   • Pinch to zoom for infinite detail")
            print("   • Tap and drag to pan around")
            print("   • Perfect vector scaling!")
            
        except Exception as e:
            print(f"Error showing live view: {e}")
            
    def _create_html_wrapper(self, svg_content: str, stats: ObjectStats) -> str:
        """Create HTML wrapper with zoom controls and stats"""
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=10.0, user-scalable=yes">
    <title>{self.title}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #000;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}
        
        .header {{
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px 16px;
            font-size: 14px;
            border-bottom: 1px solid #333;
            flex-shrink: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .stats {{
            font-size: 12px;
            opacity: 0.8;
        }}
        
        .svg-container {{
            flex: 1;
            overflow: hidden;
            position: relative;
            background: #000;
        }}
        
        .svg-wrapper {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        svg {{
            max-width: 100%;
            max-height: 100%;
            width: auto;
            height: auto;
        }}
        
        .zoom-controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        
        .zoom-btn {{
            width: 40px;
            height: 40px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            color: white;
            font-size: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            user-select: none;
        }}
        
        .zoom-btn:active {{
            background: rgba(255,255,255,0.2);
        }}
        
        .instructions {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            right: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 8px;
            border-radius: 5px;
            font-size: 12px;
            text-align: center;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <strong>🌟 {self.title}</strong>
        </div>
        <div class="stats">
            ⭐ {stats.stars} stars • 🌌 {stats.dso} DSO • 🌟 {stats.bright_stars} named
        </div>
    </div>
    
    <div class="svg-container">
        <div class="svg-wrapper" id="svgWrapper">
            {svg_content}
        </div>
        
        <div class="zoom-controls">
            <div class="zoom-btn" onclick="zoomIn()">+</div>
            <div class="zoom-btn" onclick="zoomOut()">−</div>
            <div class="zoom-btn" onclick="resetZoom()">⌂</div>
        </div>
        
        <div class="instructions">
            📍 Pinch to zoom • ✋ Drag to pan • Perfect vector scaling
        </div>
    </div>
    
    <script>
        let currentScale = 1;
        let translateX = 0;
        let translateY = 0;
        
        const svg = document.querySelector('svg');
        const wrapper = document.getElementById('svgWrapper');
        
        function updateTransform() {{
            svg.style.transform = `scale(${{currentScale}}) translate(${{translateX}}px, ${{translateY}}px)`;
        }}
        
        function zoomIn() {{
            currentScale = Math.min(currentScale * 1.5, 20);
            updateTransform();
        }}
        
        function zoomOut() {{
            currentScale = Math.max(currentScale / 1.5, 0.1);
            updateTransform();
        }}
        
        function resetZoom() {{
            currentScale = 1;
            translateX = 0;
            translateY = 0;
            updateTransform();
        }}
        
        // Touch/mouse pan support
        let isDragging = false;
        let lastX, lastY;
        
        wrapper.addEventListener('mousedown', startDrag);
        wrapper.addEventListener('touchstart', startDrag);
        
        function startDrag(e) {{
            isDragging = true;
            const point = e.touches ? e.touches[0] : e;
            lastX = point.clientX;
            lastY = point.clientY;
            e.preventDefault();
        }}
        
        document.addEventListener('mousemove', drag);
        document.addEventListener('touchmove', drag);
        
        function drag(e) {{
            if (!isDragging) return;
            
            const point = e.touches ? e.touches[0] : e;
            const deltaX = point.clientX - lastX;
            const deltaY = point.clientY - lastY;
            
            translateX += deltaX / currentScale;
            translateY += deltaY / currentScale;
            
            lastX = point.clientX;
            lastY = point.clientY;
            
            updateTransform();
            e.preventDefault();
        }}
        
        document.addEventListener('mouseup', stopDrag);
        document.addEventListener('touchend', stopDrag);
        
        function stopDrag() {{
            isDragging = false;
        }}
        
        // Hide instructions after 3 seconds
        setTimeout(() => {{
            const instructions = document.querySelector('.instructions');
            if (instructions) {{
                instructions.style.opacity = '0';
                setTimeout(() => instructions.style.display = 'none', 500);
            }}
        }}, 3000);
    </script>
</body>
</html>'''


class MacOSBrowserView:
    """Live SVG viewer for macOS using default web browser"""
    
    def __init__(self, title: str = "Constellation Map"):
        self.title = title
        self.temp_html_file = None
        
    def show_svg(self, svg_content: str, stats: ObjectStats):
        """Display SVG content in default web browser"""
        try:
            # Create HTML wrapper for the SVG with zoom controls
            html_content = self._create_html_wrapper(svg_content, stats)
            
            # Create a temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                self.temp_html_file = f.name
            
            # Open in default browser
            webbrowser.open(f'file://{self.temp_html_file}')
            
            print("🌐 Live SVG view opened in your web browser!")
            print("   • Mouse wheel to zoom in/out")
            print("   • Click and drag to pan around")
            print("   • Perfect vector scaling!")
            print("   • Zoom buttons in top-right corner")
            
        except Exception as e:
            print(f"Error showing browser view: {e}")
            
    def _create_html_wrapper(self, svg_content: str, stats: ObjectStats) -> str:
        """Create HTML wrapper with zoom controls and stats"""
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}
        
        .header {{
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 12px 20px;
            font-size: 16px;
            border-bottom: 2px solid #333;
            flex-shrink: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }}
        
        .title {{
            font-weight: 600;
            color: #FFD700;
        }}
        
        .stats {{
            font-size: 14px;
            opacity: 0.9;
            color: #87CEEB;
        }}
        
        .controls {{
            display: flex;
            gap: 10px;
        }}
        
        .control-btn {{
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}
        
        .control-btn:hover {{
            background: rgba(255,255,255,0.2);
            border-color: rgba(255,255,255,0.5);
        }}
        
        .svg-container {{
            flex: 1;
            overflow: hidden;
            position: relative;
            background: #000;
        }}
        
        .svg-wrapper {{
            width: 100%;
            height: 100%;
            cursor: grab;
            transition: transform 0.1s ease-out;
        }}
        
        .svg-wrapper:active {{
            cursor: grabbing;
        }}
        
        .instructions {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-size: 14px;
            border: 1px solid #333;
            transition: opacity 0.5s;
            max-width: 300px;
        }}
        
        .instructions h4 {{
            margin: 0 0 10px 0;
            color: #FFD700;
        }}
        
        .instructions ul {{
            margin: 0;
            padding-left: 20px;
        }}
        
        .instructions li {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="title">{self.title}</div>
            <div class="stats">{stats.constellations} constellations • {stats.stars} stars • {stats.dso} DSOs</div>
        </div>
        <div class="controls">
            <button class="control-btn" onclick="zoomIn()">Zoom In</button>
            <button class="control-btn" onclick="zoomOut()">Zoom Out</button>
            <button class="control-btn" onclick="resetZoom()">Reset</button>
        </div>
    </div>
    
    <div class="svg-container">
        <div class="svg-wrapper" id="svgWrapper">
            {svg_content}
        </div>
        
        <div class="instructions" id="instructions">
            <h4>🌟 Navigation</h4>
            <ul>
                <li>Mouse wheel: Zoom in/out</li>
                <li>Click & drag: Pan around</li>
                <li>Use zoom buttons above</li>
                <li>Vector graphics = infinite detail!</li>
            </ul>
        </div>
    </div>

    <script>
        const wrapper = document.getElementById('svgWrapper');
        const svg = wrapper.querySelector('svg');
        
        let currentScale = 1;
        let translateX = 0;
        let translateY = 0;
        
        // Set initial SVG size to fit container
        if (svg) {{
            svg.style.width = '100%';
            svg.style.height = '100%';
        }}
        
        function updateTransform() {{
            wrapper.style.transform = `translate(${{translateX}}px, ${{translateY}}px) scale(${{currentScale}})`;
        }}
        
        // Zoom with mouse wheel
        wrapper.addEventListener('wheel', (e) => {{
            e.preventDefault();
            
            const rect = wrapper.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const zoom = e.deltaY > 0 ? 0.9 : 1.1;
            const newScale = Math.min(Math.max(currentScale * zoom, 0.1), 20);
            
            // Zoom towards mouse position
            const scaleDiff = newScale - currentScale;
            translateX -= (x - translateX) * scaleDiff / currentScale;
            translateY -= (y - translateY) * scaleDiff / currentScale;
            
            currentScale = newScale;
            updateTransform();
        }});
        
        function zoomIn() {{
            currentScale = Math.min(currentScale * 1.5, 20);
            updateTransform();
        }}
        
        function zoomOut() {{
            currentScale = Math.max(currentScale / 1.5, 0.1);
            updateTransform();
        }}
        
        function resetZoom() {{
            currentScale = 1;
            translateX = 0;
            translateY = 0;
            updateTransform();
        }}
        
        // Pan support
        let isDragging = false;
        let lastX, lastY;
        
        wrapper.addEventListener('mousedown', (e) => {{
            isDragging = true;
            lastX = e.clientX;
            lastY = e.clientY;
            e.preventDefault();
        }});
        
        document.addEventListener('mousemove', (e) => {{
            if (!isDragging) return;
            
            const deltaX = e.clientX - lastX;
            const deltaY = e.clientY - lastY;
            
            translateX += deltaX;
            translateY += deltaY;
            
            lastX = e.clientX;
            lastY = e.clientY;
            
            updateTransform();
            e.preventDefault();
        }});
        
        document.addEventListener('mouseup', () => {{
            isDragging = false;
        }});
        
        // Hide instructions after 4 seconds
        setTimeout(() => {{
            const instructions = document.getElementById('instructions');
            if (instructions) {{
                instructions.style.opacity = '0';
                setTimeout(() => instructions.style.display = 'none', 500);
            }}
        }}, 4000);
        
        // Cleanup temp file notification (for development)
        window.addEventListener('beforeunload', () => {{
            // Note: The temp file will be cleaned up by the OS eventually
            console.log('Closing constellation viewer...');
        }});
    </script>
</body>
</html>'''

    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_html_file and os.path.exists(self.temp_html_file):
            try:
                os.unlink(self.temp_html_file)
            except:
                pass  # Let OS handle cleanup


class SVGConstellationVisualizer:
    def __init__(self, catalogs_path=None):
        if catalogs_path is None:
            script_dir = Path(__file__).parent
            # Since we're now in legacy/, go up two levels to reach catalogs/
            self.catalogs_path = script_dir.parent / "catalogs"
        else:
            self.catalogs_path = Path(catalogs_path)
        
        # Load all data catalogs
        self.constellations = self._load_json("constellations.json")
        self.objects = self._load_json("objects.json")
        self.nebula_paths = self._load_json("nebula-paths.json")
        self.simbad_objects = self._load_json("simbad-objects.json")
        
        # Initialize live viewer (Pythonista or macOS browser)
        if PYTHONISTA_AVAILABLE:
            self.live_viewer = PythonistaWebView()
        else:
            self.live_viewer = MacOSBrowserView()
        
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
        return ra % 360
    
    def get_dso_color_and_category(self, obj: Dict, use_colors: bool = True) -> Tuple[str, str]:
        """Get color and category name for a DSO object"""
        if not use_colors:
            return '#FF0000', 'Deep Sky Objects'
        
        category = obj.get("category", "unknown").lower()
        
        if any(x in category for x in ['galaxy']):
            return '#4682B4', 'Galaxies'
        elif any(x in category for x in ['nebula']):
            return '#BA55D3', 'Nebulae'  
        elif any(x in category for x in ['cluster']):
            return '#FFA500', 'Clusters'
        else:
            return '#FF8C00', 'Other Objects'
    
    def find_simbad_ellipse(self, object_id: str, min_size: float = 0.0167) -> Optional[Dict]:
        """Find SIMBAD ellipse data for an object"""
        for simbad_obj in self.simbad_objects:
            if (simbad_obj.get('catalogId') == object_id or 
                simbad_obj.get('commonName') == object_id or
                simbad_obj.get('idNgc') == object_id):
                
                ellipse_data = simbad_obj.get('ellipse')
                if ellipse_data:
                    a, b = ellipse_data.get('a', 0), ellipse_data.get('b', 0)
                    if max(a, b) > min_size:
                        return ellipse_data
        return None
    
    def normalize_constellation_coordinates(self, constellation: Dict, objects: List[Dict]):
        """Normalize coordinates and handle RA wraparound"""
        # Normalize all RA coordinates 
        for star in constellation["stars"]:
            star["ra"] = self.normalize_ra(star["ra"])
        
        for obj in objects:
            obj["ra"] = self.normalize_ra(obj["ra"])
        
        # Handle RA wraparound
        star_ras = [star["ra"] for star in constellation["stars"]]
        object_ras = [obj["ra"] for obj in objects]
        all_ras = star_ras + object_ras
        
        if len(all_ras) > 1:
            ra_range = max(all_ras) - min(all_ras)
            if ra_range > 180:
                for item in constellation["stars"] + objects:
                    if item["ra"] > 180:
                        item["ra"] -= 360
    
    def separate_stars_and_dso(self, objects: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Separate star objects from actual deep sky objects"""
        stars_in_objects = []
        actual_dso = []
        
        for obj in objects:
            category = obj.get("category", "").lower()
            obj_type = obj.get("type", "").lower()
            
            if "star" in category or obj_type == "star":
                stars_in_objects.append(obj)
            else:
                actual_dso.append(obj)
        
        return stars_in_objects, actual_dso
    
    def coord_to_svg(self, ra: float, de: float, config: VectorConfig, 
                    bounds: Tuple[float, float, float, float]) -> Tuple[float, float]:
        """Convert celestial coordinates to SVG coordinates"""
        min_ra, max_ra, min_de, max_de = bounds
        
        # Convert to SVG coordinates 
        # For astronomical displays: RA increases right to left (east to west)
        # So we flip the RA coordinate transformation
        x = config.width * (1 - (ra - min_ra) / (max_ra - min_ra))
        # SVG Y axis is inverted compared to celestial coordinates
        y = config.height * (1 - (de - min_de) / (max_de - min_de))
        
        return x, y
    
    def create_svg_output(self, config: VectorConfig, bounds: Tuple[float, float, float, float], 
                         elements: List[str], stats: ObjectStats) -> str:
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
                x, _ = self.coord_to_svg(ra, 0, config, bounds)
                svg_content += f'    <line x1="{x}" y1="0" x2="{x}" y2="{config.height}"/>\n'
            
            for de in range(int(min_de), int(max_de) + 30, 30):
                _, y = self.coord_to_svg(0, de, config, bounds)
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
    
    # [Previous plotting methods remain the same - plot_stars_svg, plot_constellation_lines_svg, etc.]
    # [I'll include the key ones here but the full implementation would include all]
    
    def plot_stars_svg(self, stars: List[Dict], config: VectorConfig, 
                      bounds: Tuple[float, float, float, float]) -> Tuple[List[str], Dict[str, Tuple[float, float]]]:
        """Generate SVG elements for constellation stars"""
        elements = []
        star_positions = {}
        
        for star in stars:
            ra, de = star["ra"], star["de"]
            magnitude = star.get("visualMagnitude", 5)
            star_id = star["id"]
            
            x, y = self.coord_to_svg(ra, de, config, bounds)
            
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
    
    def plot_constellation_lines_svg(self, constellation: Dict, star_positions: Dict[str, Tuple[float, float]], 
                                   config: VectorConfig) -> List[str]:
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
    
    def plot_bright_stars_svg(self, bright_stars: List[Dict], config: VectorConfig, 
                            bounds: Tuple[float, float, float, float]) -> List[str]:
        """Generate SVG elements for bright stars"""
        elements = []
        
        for obj in bright_stars:
            ra, de = obj["ra"], obj["de"]
            name = obj["id"]
            magnitude = obj.get("magnitude", 5)
            
            x, y = self.coord_to_svg(ra, de, config, bounds)
            
            # Size based on magnitude
            size = max(0.8, config.bright_star_base_size / (magnitude + 1))
            
            # Create bright star element
            elements.append(f'  <use href="#bright-star" x="{x}" y="{y}" '
                          f'transform="scale({size})" fill="{config.bright_star_color}" opacity="0.95"/>')
            
            # Add label
            elements.append(f'  <text x="{x + 3}" y="{y - 3}" fill="{config.bright_star_color}" '
                          f'font-size="{config.font_size * 0.9}" font-weight="bold">{name}</text>')
        
        return elements
    
    def plot_dso_objects_svg(self, dso_objects: List[Dict], nebula_path_ids: set, 
                           config: VectorConfig, bounds: Tuple[float, float, float, float], 
                           stats: ObjectStats) -> List[str]:
        """Generate SVG elements for deep sky objects"""
        elements = []
        
        for obj in dso_objects:
            ra, de = obj["ra"], obj["de"]
            name = obj["id"]
            magnitude = obj.get("magnitude", 10)
            
            x, y = self.coord_to_svg(ra, de, config, bounds)
            
            # Get color and track categories
            color, category = self.get_dso_color_and_category(obj, config.use_dso_colors)
            if category not in stats.dso_categories:
                stats.dso_categories[category] = {'color': color, 'count': 0}
            stats.dso_categories[category]['count'] += 1
            
            # Check for ellipse
            has_ellipse = False
            if config.show_ellipses and name not in nebula_path_ids:
                ellipse_data = self.find_simbad_ellipse(name)
                if ellipse_data:
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
    
    def plot_nebula_paths_svg(self, nebula_paths: List[Dict], config: VectorConfig, 
                            bounds: Tuple[float, float, float, float]) -> List[str]:
        """Generate SVG elements for nebula paths"""
        elements = []
        
        for nebula in nebula_paths:
            path_coords = nebula["path"]
            if len(path_coords) > 2:
                # Convert coordinates to SVG path
                svg_path = "M "
                for i, coord in enumerate(path_coords):
                    x, y = self.coord_to_svg(coord[0], coord[1], config, bounds)
                    if i == 0:
                        svg_path += f"{x},{y} "
                    else:
                        svg_path += f"L {x},{y} "
                svg_path += "Z"  # Close path
                
                # Add filled path
                elements.append(f'  <path d="{svg_path}" fill="#FF0000" fill-opacity="0.1" '
                              f'stroke="#FF0000" stroke-width="0.3" stroke-opacity="0.7"/>')
        
        return elements
    
    def calculate_bounds(self, constellation_data_list: List[Tuple[Dict, str]], 
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
    
    def plot_vector_visualization(self, constellation_data_list: List[Tuple[Dict, str]], 
                                config: VectorConfig, is_grid_view: bool = True) -> ObjectStats:
        """Create complete vector visualization with live viewing"""
        print(f"Generating vector SVG visualization...")
        print(f"Output: {config.svg_filename} ({config.width}x{config.height} SVG units)")
        
        stats = ObjectStats()
        all_elements = []
        
        # Prepare objects for all constellations
        objects_dict = {}
        for constellation, constellation_id in constellation_data_list:
            objects_dict[constellation_id] = self.get_constellation_objects(constellation_id)
        
        # Calculate bounds
        bounds = self.calculate_bounds(constellation_data_list, objects_dict)
        print(f"Coordinate bounds: RA {bounds[0]:.1f}° to {bounds[1]:.1f}°, DE {bounds[2]:.1f}° to {bounds[3]:.1f}°")
        
        # Process each constellation
        for constellation, constellation_id in constellation_data_list:
            if not constellation.get("stars"):
                continue
                
            stats.constellations += 1
            objects = objects_dict[constellation_id]
            
            # Normalize coordinates
            self.normalize_constellation_coordinates(constellation, objects)
            
            # Plot constellation stars
            star_elements, star_positions = self.plot_stars_svg(constellation["stars"], config, bounds)
            all_elements.extend(star_elements)
            stats.stars += len(constellation["stars"])
            
            # Plot constellation lines
            line_elements = self.plot_constellation_lines_svg(constellation, star_positions, config)
            all_elements.extend(line_elements)
            
            # Add constellation labels for grid view
            if config.show_labels and star_positions and is_grid_view:
                center_ra = np.mean([star["ra"] for star in constellation["stars"]])
                center_de = np.mean([star["de"] for star in constellation["stars"]])
                x, y = self.coord_to_svg(center_ra, center_de, config, bounds)
                
                all_elements.append(f'  <text x="{x}" y="{y}" text-anchor="middle" '
                                  f'fill="{config.label_color}" font-size="{config.constellation_font_size}" '
                                  f'font-weight="bold" opacity="0.8">{constellation_id}</text>')
            
            # Process DSOs if requested
            if config.show_dso and objects:
                object_ids = [obj["id"] for obj in objects]
                nebula_paths = self.get_nebula_paths_for_objects(object_ids)
                nebula_path_ids = {nebula["objectId"] for nebula in nebula_paths}
                
                bright_stars, actual_dso = self.separate_stars_and_dso(objects)
                
                # Plot bright stars
                bright_star_elements = self.plot_bright_stars_svg(bright_stars, config, bounds)
                all_elements.extend(bright_star_elements)
                stats.bright_stars += len(bright_stars)
                
                # Plot DSOs
                dso_elements = self.plot_dso_objects_svg(actual_dso, nebula_path_ids, config, bounds, stats)
                all_elements.extend(dso_elements)
                stats.dso += len(actual_dso)
                
                # Plot nebula paths
                nebula_elements = self.plot_nebula_paths_svg(nebula_paths, config, bounds)
                all_elements.extend(nebula_elements)
                stats.nebula_paths += len(nebula_paths)
        
        # Create complete SVG
        svg_content = self.create_svg_output(config, bounds, all_elements, stats)
        
        # Save SVG file
        if config.save_svg:
            svg_path = Path(config.svg_filename)
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            print(f"Vector SVG saved: {svg_path.absolute()}")
            print(f"File size: {len(svg_content)} characters")
        
        # Show live preview (Pythonista WebView or macOS Browser)
        if config.show_live and self.live_viewer:
            title = f"Celestial Sky Grid" if is_grid_view else f"Constellation View"
            self.live_viewer.title = title
            self.live_viewer.show_svg(svg_content, stats)
        
        return stats
    
    def plot_all_constellations_grid(self, config: VectorConfig):
        """Create vector grid view of all constellations"""
        constellation_data_list = [(const, const["id"]) for const in self.constellations 
                                 if const.get("stars")]
        
        stats = self.plot_vector_visualization(constellation_data_list, config, is_grid_view=True)
        self._print_stats_summary(stats, config, is_grid=True)
    
    def plot_constellation(self, constellation_id: str, config: VectorConfig):
        """Create vector view of individual constellation"""
        constellation = self.find_constellation(constellation_id)
        if not constellation:
            print(f"Constellation '{constellation_id}' not found!")
            return
        
        constellation_data_list = [(constellation, constellation_id)]
        stats = self.plot_vector_visualization(constellation_data_list, config, is_grid_view=False)
        self._print_stats_summary(stats, config, is_grid=False)
    
    def _print_stats_summary(self, stats: ObjectStats, config: VectorConfig, is_grid: bool):
        """Print summary statistics"""
        if is_grid:
            print(f"\nVector grid view complete:")
            print(f"  • {stats.constellations} constellations")
        else:
            print(f"\nVector constellation view complete:")
        
        print(f"  • {stats.stars} constellation stars")
        if stats.bright_stars > 0:
            print(f"  • {stats.bright_stars} named bright stars")
        if stats.dso > 0:
            print(f"  • {stats.dso} deep sky objects")
        if stats.ellipses > 0:
            print(f"  • {stats.ellipses} object boundaries")
        if stats.nebula_paths > 0:
            print(f"  • {stats.nebula_paths} nebula boundaries")
        
        print(f"\nSVG Output: {config.svg_filename}")
        if PYTHONISTA_AVAILABLE:
            print(f"🌟 Live view opened in Pythonista WebView!")
            print(f"   • Pinch to zoom for infinite detail")
            print(f"   • Perfect vector scaling!")
        else:
            print(f"🌐 Live view opened in your web browser!")
            print(f"   • Mouse wheel zoom and click-drag pan")
            print(f"   • Perfect vector scaling!")
        print(f"Scalable vector format - infinite zoom capability!")
    
    def list_available_constellations(self) -> List[str]:
        """List all available constellation IDs"""
        constellation_ids = [const["id"] for const in self.constellations]
        constellation_ids.sort()
        return constellation_ids


def main():
    parser = argparse.ArgumentParser(
        description='Create scalable vector constellation visualizations with live Pythonista viewing.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python show_all.py                       # Vector SVG grid view with live preview
  python show_all.py Ori                   # Vector SVG Orion view with live preview
  python show_all.py Cyg --no-colors-for-dso  # Cygnus with red DSOs only
  python show_all.py And --no-ellipses     # Andromeda dots-only mode
  python show_all.py --all                 # List all constellation IDs
  
🌟 Pythonista Features:
  • Live interactive WebView with zoom controls
  • Pinch-to-zoom with infinite detail
  • Pan and drag support
  • Perfect vector scaling
  • Professional iPad viewing experience
        """
    )
    
    parser.add_argument('constellation_id', nargs='?', 
                       help='Constellation ID (e.g., Ori, Cyg, UMa). If omitted, shows vector grid view of all constellations.')
    parser.add_argument('--no-colors-for-dso', action='store_true',
                       help='Use red color for all deep sky objects (classic mode)')
    parser.add_argument('--no-ellipses', action='store_true',
                       help='Hide object boundary ellipses (dots only mode)')
    parser.add_argument('--all', action='store_true',
                       help='List all available constellation IDs')
    parser.add_argument('--no-labels', action='store_true',
                       help='Hide constellation labels in grid view')
    parser.add_argument('--no-dso', action='store_true',
                       help='Hide deep sky objects (stars and lines only)')
    parser.add_argument('--show-star-names', action='store_true',
                       help='Show names for bright stars')
    parser.add_argument('--output', type=str,
                       help='Custom SVG filename (default: auto-generated)')
    parser.add_argument('--no-live', action='store_true',
                       help='Disable live preview (SVG file only)')
    
    args = parser.parse_args()
    
    # Create visualizer
    visualizer = SVGConstellationVisualizer()
    
    # Handle --all flag (list constellations)
    if args.all:
        available = visualizer.list_available_constellations()
        print(f"Available constellations ({len(available)}):")
        for i, const_id in enumerate(available):
            print(f"{const_id}", end="  ")
            if (i + 1) % 10 == 0:
                print()
        print()
        return
    
    # Create configuration
    if args.constellation_id:
        config = VectorConfig.for_constellation(args.constellation_id)
        print(f"Creating vector SVG view for constellation {args.constellation_id.upper()}")
    else:
        config = VectorConfig.for_grid_view()
        print("Creating vector SVG grid view of all constellations")
        if PYTHONISTA_AVAILABLE:
            print("Perfect for iPad viewing with infinite zoom capability!")
    
    # Apply argument overrides
    config.show_labels = not args.no_labels
    config.show_dso = not args.no_dso
    config.show_ellipses = not args.no_ellipses
    config.use_dso_colors = not args.no_colors_for_dso
    config.show_star_names = args.show_star_names
    config.show_live = not args.no_live
    
    if args.output:
        config.svg_filename = args.output
    
    # Generate visualization
    if args.constellation_id:
        visualizer.plot_constellation(args.constellation_id, config)
    else:
        visualizer.plot_all_constellations_grid(config)


if __name__ == "__main__":
    main()
