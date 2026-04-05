#!/usr/bin/env python3
"""
Constellation Visualizer

This script visualizes constellation data using the shared plotting library.
It includes:
- Stars (white dots)
- Constellation shapes/lines (light blue)
- Deep sky objects (red dots with labels)
- Nebula paths (red outlines)

Usage: python constellation_visualizer.py <constellation_id>
Example: python constellation_visualizer.py Ori
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the shared constellation plotting library
from plots.constellation import plot_constellation_map, ConstellationPlotter


def visualize_constellation(constellation_id, use_dso_colors=True, show_ellipses=True):
    """Visualize a constellation using the shared plotting library"""
    # Use the shared plotting function
    result = plot_constellation_map(
        constellation_id=constellation_id,
        use_dso_colors=use_dso_colors,
        show_ellipses=show_ellipses
    )
    
    if result:
        import matplotlib.pyplot as plt
        plt.show()
        return True
    else:
        return False


def list_available_constellations():
    """List all available constellation IDs using the shared library"""
    plotter = ConstellationPlotter()
    constellation_ids = []
    for const in plotter.constellations:
        constellation_ids.append(const["id"])
    
    constellation_ids.sort()
    return constellation_ids


def main():
    parser = argparse.ArgumentParser(
        description='Visualize astronomical constellations with stars, lines, and deep sky objects.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python constellation_visualizer.py Ori                    # Orion with colored DSOs and ellipses
  python constellation_visualizer.py Cyg --no-colors-for-dso  # Cygnus with red DSOs only
  python constellation_visualizer.py And --no-ellipses     # Andromeda with dots only (no ellipses)
        """
    )
    
    parser.add_argument('constellation_id', nargs='?', 
                       help='Constellation ID (e.g., Ori, Cyg, UMa)')
    parser.add_argument('--no-colors-for-dso', action='store_true',
                       help='Use red color for all deep sky objects (classic mode)')
    parser.add_argument('--no-ellipses', action='store_true',
                       help='Hide object boundary ellipses (dots only mode)')
    
    args = parser.parse_args()
    
    # Show help if no constellation provided
    if not args.constellation_id:
        print("Usage: python constellation_visualizer.py <constellation_id> [options]")
        print("\nExamples:")
        print("  python constellation_visualizer.py Ori")
        print("  python constellation_visualizer.py Cyg --no-colors-for-dso")  
        print("  python constellation_visualizer.py And --no-ellipses")
        
        # Show available constellations
        available = list_available_constellations()
        print(f"\nAvailable constellations ({len(available)}):")
        for i, const_id in enumerate(available):
            print(f"{const_id}", end="  ")
            if (i + 1) % 10 == 0:  # New line every 10 items
                print()
        if len(available) % 10 != 0:
            print()  # Final newline if needed
        return
    
    # Parse options
    use_dso_colors = not args.no_colors_for_dso
    show_ellipses = not args.no_ellipses
    
    print(f"Visualizing constellation {args.constellation_id.upper()}...")
    print(f"DSO Colors: {'Enabled' if use_dso_colors else 'Disabled (all red)'}")
    print(f"Object Ellipses: {'Shown' if show_ellipses else 'Hidden'}")
    print()
    
    # Visualize the constellation
    success = visualize_constellation(
        constellation_id=args.constellation_id,
        use_dso_colors=use_dso_colors,
        show_ellipses=show_ellipses
    )
    
    if not success:
        print(f"Error: Constellation '{args.constellation_id}' not found!")
        print("Use --help to see available constellations.")
        sys.exit(1)


if __name__ == "__main__":
    main() 
