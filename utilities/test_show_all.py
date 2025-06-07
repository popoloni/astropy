#!/usr/bin/env python3
"""
Test script for the refactored show_all.py
Tests basic functionality without displaying plots
"""

import sys
from pathlib import Path

# Add parent directory to path to import show_all
sys.path.insert(0, str(Path(__file__).parent))

from show_all import ConstellationVisualizer, PlotConfig, ObjectStats


def test_basic_functionality():
    """Test basic loading and configuration functionality"""
    print("Testing basic functionality...")
    
    # Test data loading
    visualizer = ConstellationVisualizer()
    
    # Verify data was loaded
    assert len(visualizer.constellations) > 0, "No constellations loaded"
    assert len(visualizer.objects) > 0, "No objects loaded"
    print(f"✓ Loaded {len(visualizer.constellations)} constellations")
    print(f"✓ Loaded {len(visualizer.objects)} deep sky objects")
    
    # Test constellation finding
    orion = visualizer.find_constellation("Ori")
    assert orion is not None, "Could not find Orion constellation"
    assert orion["id"] == "Ori", "Wrong constellation returned"
    print("✓ Constellation finding works")
    
    # Test object finding
    orion_objects = visualizer.get_constellation_objects("Ori")
    assert len(orion_objects) > 0, "No objects found for Orion"
    print(f"✓ Found {len(orion_objects)} objects for Orion")
    
    # Test coordinate normalization
    test_ra = 400.0  # Should be normalized to 40.0
    normalized = visualizer.normalize_ra(test_ra)
    assert normalized == 40.0, f"RA normalization failed: {normalized}"
    print("✓ RA normalization works")


def test_plot_configurations():
    """Test plot configuration functionality"""
    print("\nTesting plot configurations...")
    
    # Test default config
    default_config = PlotConfig.for_device('default')
    assert default_config.width == 16, "Default width incorrect"
    assert default_config.height == 8, "Default height incorrect"
    assert default_config.dpi == 200, "Default DPI incorrect"
    print("✓ Default configuration works")
    
    # Test iPad config
    ipad_config = PlotConfig.for_device('ipad')
    assert ipad_config.width == 12, "iPad width incorrect"
    assert ipad_config.height == 6, "iPad height incorrect"
    assert ipad_config.dpi == 200, "iPad DPI incorrect"
    print("✓ iPad configuration works")
    
    # Test iMac config
    imac_config = PlotConfig.for_device('imac')
    assert imac_config.width == 20, "iMac width incorrect"
    assert imac_config.height == 10, "iMac height incorrect"
    assert imac_config.dpi == 150, "iMac DPI incorrect"
    print("✓ iMac configuration works")
    
    # Test pixel dimensions calculation
    pixels = default_config.pixel_dimensions
    expected = (16 * 200, 8 * 200)
    assert pixels == expected, f"Pixel calculation wrong: {pixels} vs {expected}"
    print("✓ Pixel dimension calculation works")


def test_object_separation():
    """Test separation of stars and DSOs"""
    print("\nTesting object separation...")
    
    visualizer = ConstellationVisualizer()
    orion_objects = visualizer.get_constellation_objects("Ori")
    
    bright_stars, dso_objects = visualizer.separate_stars_and_dso(orion_objects)
    
    # Verify separation worked
    total_objects = len(bright_stars) + len(dso_objects)
    assert total_objects == len(orion_objects), "Object separation lost objects"
    print(f"✓ Separated {len(bright_stars)} stars and {len(dso_objects)} DSOs")
    
    # Check that stars are properly categorized
    for star in bright_stars:
        category = star.get("category", "").lower()
        obj_type = star.get("type", "").lower()
        assert "star" in category or obj_type == "star", "Non-star in star list"
    print("✓ Star categorization correct")


def test_dso_color_classification():
    """Test DSO color and category classification"""
    print("\nTesting DSO classification...")
    
    visualizer = ConstellationVisualizer()
    
    # Test galaxy classification
    galaxy_obj = {"category": "galaxy", "type": "spiral"}
    color, category = visualizer.get_dso_color_and_category(galaxy_obj, True)
    assert color == 'steelblue', f"Galaxy color wrong: {color}"
    assert category == 'Galaxies', f"Galaxy category wrong: {category}"
    print("✓ Galaxy classification works")
    
    # Test nebula classification
    nebula_obj = {"category": "emission nebula", "type": "nebula"}
    color, category = visualizer.get_dso_color_and_category(nebula_obj, True)
    assert color == 'mediumorchid', f"Nebula color wrong: {color}"
    assert category == 'Nebulae', f"Nebula category wrong: {category}"
    print("✓ Nebula classification works")
    
    # Test cluster classification
    cluster_obj = {"category": "open cluster", "type": "cluster"}
    color, category = visualizer.get_dso_color_and_category(cluster_obj, True)
    assert color == 'orange', f"Cluster color wrong: {color}"
    assert category == 'Clusters', f"Cluster category wrong: {category}"
    print("✓ Cluster classification works")
    
    # Test no-color mode
    color, category = visualizer.get_dso_color_and_category(galaxy_obj, False)
    assert color == 'red', f"No-color mode wrong: {color}"
    assert category == 'Deep Sky Objects', f"No-color category wrong: {category}"
    print("✓ No-color mode works")


def test_constellation_bounds():
    """Test constellation bounds calculation"""
    print("\nTesting constellation bounds calculation...")
    
    visualizer = ConstellationVisualizer()
    orion = visualizer.find_constellation("Ori")
    orion_objects = visualizer.get_constellation_objects("Ori")
    
    # Normalize coordinates first
    visualizer.normalize_constellation_coordinates(orion, orion_objects)
    
    # Calculate bounds
    min_ra, max_ra, min_de, max_de = visualizer.calculate_constellation_bounds(orion, orion_objects)
    
    # Verify bounds are reasonable for Orion
    assert min_ra < max_ra, "Invalid RA bounds"
    assert min_de < max_de, "Invalid DE bounds"
    assert max_ra - min_ra < 180, "RA range too large for single constellation"
    assert max_de - min_de < 90, "DE range too large for single constellation"
    
    # Orion should be roughly in the right area
    assert min_ra < 90 and max_ra > 60, "Orion RA bounds seem wrong"
    assert min_de < 30 and max_de > -20, "Orion DE bounds seem wrong"
    
    print(f"✓ Orion bounds: RA {min_ra:.1f}° to {max_ra:.1f}°, DE {min_de:.1f}° to {max_de:.1f}°")


def test_constellation_listing():
    """Test constellation listing functionality"""
    print("\nTesting constellation listing...")
    
    visualizer = ConstellationVisualizer()
    constellations = visualizer.list_available_constellations()
    
    assert len(constellations) == 88, f"Wrong number of constellations: {len(constellations)}"
    assert "Ori" in constellations, "Orion not in constellation list"
    assert "UMa" in constellations, "Ursa Major not in constellation list"
    
    # Check that list is sorted
    assert constellations == sorted(constellations), "Constellation list not sorted"
    print(f"✓ Listed {len(constellations)} constellations correctly")


def test_statistics_object():
    """Test ObjectStats functionality"""
    print("\nTesting statistics tracking...")
    
    stats = ObjectStats()
    assert stats.constellations == 0, "Stats not initialized to zero"
    assert stats.dso_categories == {}, "DSO categories not initialized"
    print("✓ Statistics object initialization works")
    
    # Test category tracking
    stats.dso_categories['Galaxies'] = {'color': 'steelblue', 'count': 5}
    stats.dso_categories['Nebulae'] = {'color': 'mediumorchid', 'count': 3}
    
    assert len(stats.dso_categories) == 2, "Category tracking failed"
    assert stats.dso_categories['Galaxies']['count'] == 5, "Galaxy count wrong"
    print("✓ Category tracking works")


def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("TESTING REFACTORED SHOW_ALL.PY")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_plot_configurations()
        test_object_separation()
        test_dso_color_classification()
        test_constellation_bounds()
        test_constellation_listing()
        test_statistics_object()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("The refactored code is working correctly.")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests() 