#!/usr/bin/env python3
"""
Constellation Visualizer Demo

This script demonstrates how to use the ConstellationVisualizer class
and provides examples for popular constellations.
"""

from constellation_visualizer import ConstellationVisualizer
import matplotlib.pyplot as plt


def demo_popular_constellations():
    """Demo some popular constellations with interesting features"""
    
    # Create visualizer
    visualizer = ConstellationVisualizer()
    
    # Popular constellations to demo
    demo_constellations = [
        ("Ori", "Orion - The Hunter (rich in nebulae)"),
        ("UMa", "Ursa Major - The Big Dipper"),
        ("Cas", "Cassiopeia - The Queen"),
        ("Cyg", "Cygnus - The Swan"),
        ("And", "Andromeda - Contains the Andromeda Galaxy"),
        ("Sco", "Scorpius - The Scorpion")
    ]
    
    print("=== Constellation Visualizer Demo ===\n")
    
    for const_id, description in demo_constellations:
        constellation = visualizer.find_constellation(const_id)
        if constellation:
            objects = visualizer.get_constellation_objects(const_id)
            object_ids = [obj["id"] for obj in objects]
            nebula_paths = visualizer.get_nebula_paths_for_objects(object_ids)
            
            # Separate stars from actual DSOs
            stars_in_objects = []
            actual_dso = []
            for obj in objects:
                category = obj.get("category", "").lower()
                obj_type = obj.get("type", "").lower()
                if "star" in category or obj_type == "star":
                    stars_in_objects.append(obj)
                else:
                    actual_dso.append(obj)
            
            print(f"{description}")
            print(f"  - Constellation Stars: {len(constellation['stars'])}")
            print(f"  - Bright Stars: {len(stars_in_objects)}")
            print(f"  - Deep Sky Objects: {len(actual_dso)}")
            print(f"  - Nebula Paths: {len(nebula_paths)}")
            if stars_in_objects:
                print(f"  - Notable Stars: {', '.join([obj['id'] for obj in stars_in_objects[:2]])}")
            if actual_dso:
                print(f"  - Notable DSOs: {', '.join([obj['id'] for obj in actual_dso[:2]])}")
            print()
    
    print("To visualize any constellation, run:")
    print("python constellation_visualizer.py <constellation_id>")
    print("\nExamples:")
    for const_id, description in demo_constellations[:3]:
        print(f"python constellation_visualizer.py {const_id}")


def show_object_types():
    """Show statistics about different types of objects"""
    
    visualizer = ConstellationVisualizer()
    
    # Count object types
    object_types = {}
    constellations_with_objects = {}
    
    for obj in visualizer.objects:
        obj_type = obj.get("category", "unknown")
        constellation = obj.get("constellation", "unknown")
        
        if obj_type not in object_types:
            object_types[obj_type] = 0
        object_types[obj_type] += 1
        
        if constellation not in constellations_with_objects:
            constellations_with_objects[constellation] = 0
        constellations_with_objects[constellation] += 1
    
    print("=== Deep Sky Object Statistics ===\n")
    print("Object Types:")
    for obj_type, count in sorted(object_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {obj_type}: {count}")
    
    print(f"\nTotal Objects: {len(visualizer.objects)}")
    print(f"Total Constellations with Objects: {len(constellations_with_objects)}")
    
    # Show constellations with most objects
    print("\nTop 10 Constellations by Object Count:")
    top_constellations = sorted(constellations_with_objects.items(), 
                               key=lambda x: x[1], reverse=True)[:10]
    for constellation, count in top_constellations:
        print(f"  {constellation}: {count} objects")


def interactive_mode():
    """Interactive mode to explore constellations"""
    
    visualizer = ConstellationVisualizer()
    available = visualizer.list_available_constellations()
    
    print("=== Interactive Constellation Explorer ===\n")
    print("Available constellations:")
    for i, const_id in enumerate(available):
        print(f"{const_id}", end="  ")
        if (i + 1) % 10 == 0:
            print()
    print("\n")
    
    while True:
        try:
            constellation_id = input("Enter constellation ID (or 'quit' to exit): ").strip()
            
            if constellation_id.lower() in ['quit', 'q', 'exit']:
                break
            
            if constellation_id in available:
                            print(f"\nVisualizing {constellation_id}...")
            visualizer.plot_constellation(constellation_id, use_dso_colors=True, show_ellipses=True)
            else:
                print(f"Constellation '{constellation_id}' not found. Please try again.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            show_object_types()
        elif sys.argv[1] == "interactive":
            interactive_mode()
        else:
            demo_popular_constellations()
    else:
        demo_popular_constellations() 