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
        # Add parent directory to path for imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Use shared ConstellationPlotter for data access
        from plots.constellation import ConstellationPlotter
        self.plotter = ConstellationPlotter(catalogs_path)
        
        # Access data through shared plotter
        self.constellations = self.plotter.constellations
        self.objects = self.plotter.objects
        self.nebula_paths = self.plotter.nebula_paths
        self.simbad_objects = self.plotter.simbad_objects
        
        # Initialize live viewer (Pythonista or macOS browser)
        if PYTHONISTA_AVAILABLE:
            self.live_viewer = PythonistaWebView()
        else:
            self.live_viewer = MacOSBrowserView()
    
    def find_constellation(self, constellation_id: str) -> Optional[Dict]:
        """Find constellation data by ID"""
        return self.plotter.find_constellation(constellation_id)
    
    def get_constellation_objects(self, constellation_id: str) -> List[Dict]:
        """Get all deep sky objects for a constellation"""
        return self.plotter.get_constellation_objects(constellation_id)
    
    def get_nebula_paths_for_objects(self, object_ids: List[str]) -> List[Dict]:
        """Get nebula paths for given object IDs"""
        return self.plotter.get_nebula_paths_for_objects(object_ids)
    
    @staticmethod
    def normalize_ra(ra: float) -> float:
        """Normalize RA to 0-360 range"""
        from astronomy.celestial import normalize_ra
        return normalize_ra(ra)
    
    def get_dso_color_and_category(self, obj: Dict, use_colors: bool = True) -> Tuple[str, str]:
        """Get color and category name for a DSO object"""
        from astronomy.celestial import get_dso_color_and_category
        return get_dso_color_and_category(obj, use_colors)
    
    def find_simbad_ellipse(self, object_id: str, min_size: float = 0.0167) -> Optional[Dict]:
        """Find SIMBAD ellipse data for an object"""
        ellipse_data = self.plotter.find_simbad_ellipse(object_id)
        if ellipse_data:
            a, b = ellipse_data.get('a', 0), ellipse_data.get('b', 0)
            if max(a, b) > min_size:
                return ellipse_data
        return None
    
    def normalize_constellation_coordinates(self, constellation: Dict, objects: List[Dict]):
        """Normalize coordinates and handle RA wraparound"""
        return self.plotter.normalize_constellation_coordinates(constellation, objects)
    
    def separate_stars_and_dso(self, objects: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Separate star objects from actual deep sky objects"""
        from astronomy.celestial import separate_stars_and_dso
        return separate_stars_and_dso(objects)
    
    def coord_to_svg(self, ra: float, de: float, config: VectorConfig, 
                    bounds: Tuple[float, float, float, float]) -> Tuple[float, float]:
        """Convert celestial coordinates to SVG coordinates"""
        from plots.constellation.svg import coord_to_svg
        return coord_to_svg(ra, de, config, bounds)
    
    def create_svg_output(self, config: VectorConfig, bounds: Tuple[float, float, float, float], 
                         elements: List[str], stats: ObjectStats) -> str:
        """Create complete SVG document"""
        from plots.constellation.svg import create_svg_output
        return create_svg_output(config, bounds, elements, stats)
    
    # [Previous plotting methods remain the same - plot_stars_svg, plot_constellation_lines_svg, etc.]
    # [I'll include the key ones here but the full implementation would include all]
    
    def plot_stars_svg(self, stars: List[Dict], config: VectorConfig, 
                      bounds: Tuple[float, float, float, float]) -> Tuple[List[str], Dict[str, Tuple[float, float]]]:
        """Generate SVG elements for constellation stars"""
        from plots.constellation.svg import plot_stars_svg
        return plot_stars_svg(stars, config, bounds)
    
    def plot_constellation_lines_svg(self, constellation: Dict, star_positions: Dict[str, Tuple[float, float]], 
                                   config: VectorConfig) -> List[str]:
        """Generate SVG elements for constellation lines"""
        from plots.constellation.svg import plot_constellation_lines_svg
        return plot_constellation_lines_svg(constellation, star_positions, config)
    
    def plot_bright_stars_svg(self, bright_stars: List[Dict], config: VectorConfig, 
                            bounds: Tuple[float, float, float, float]) -> List[str]:
        """Generate SVG elements for bright stars"""
        from plots.constellation.svg import plot_bright_stars_svg
        return plot_bright_stars_svg(bright_stars, config, bounds)
    
    def plot_dso_objects_svg(self, dso_objects: List[Dict], nebula_path_ids: set, 
                           config: VectorConfig, bounds: Tuple[float, float, float, float], 
                           stats: ObjectStats) -> List[str]:
        """Generate SVG elements for deep sky objects"""
        from plots.constellation.svg import plot_dso_objects_svg
        return plot_dso_objects_svg(dso_objects, nebula_path_ids, config, bounds, stats, self)
    
    def plot_nebula_paths_svg(self, nebula_paths: List[Dict], config: VectorConfig, 
                            bounds: Tuple[float, float, float, float]) -> List[str]:
        """Generate SVG elements for nebula paths"""
        from plots.constellation.svg import plot_nebula_paths_svg
        return plot_nebula_paths_svg(nebula_paths, config, bounds)
    
    def calculate_bounds(self, constellation_data_list: List[Tuple[Dict, str]], 
                        objects_dict: Dict[str, List[Dict]]) -> Tuple[float, float, float, float]:
        """Calculate bounding box for all data"""
        from plots.constellation.svg import calculate_bounds
        return calculate_bounds(constellation_data_list, objects_dict)
    
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
