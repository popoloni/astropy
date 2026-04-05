#!/usr/bin/env python3
"""
CLI Telescope Analysis Script
Demonstrates telescope analysis capabilities using common functions
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.telescope_analysis import (
    get_telescope_database, get_telescope_by_id, TargetType,
    calculate_fov_compatibility, calculate_pixel_scale,
    calculate_exposure_recommendation, calculate_quality_metrics,
    compare_telescopes_for_target, export_telescope_data
)


def list_telescopes():
    """List all available telescopes"""
    print("🔭 AVAILABLE TELESCOPES")
    print("=" * 50)
    
    database = get_telescope_database()
    
    for telescope_id, scope in database.items():
        print(f"\n📡 {scope.name} ({scope.manufacturer})")
        print(f"   ID: {telescope_id}")
        print(f"   Aperture: {scope.aperture_mm}mm")
        print(f"   Focal Length: {scope.focal_length_mm}mm (f/{scope.focal_ratio})")
        print(f"   FOV: {scope.native_fov_deg[0]:.2f}° × {scope.native_fov_deg[1]:.2f}°")
        if scope.has_mosaic_mode and scope.mosaic_fov_deg:
            print(f"   Mosaic FOV: {scope.mosaic_fov_deg[0]:.2f}° × {scope.mosaic_fov_deg[1]:.2f}°")
        print(f"   Price: ${scope.price_usd:,}")


def analyze_telescope(telescope_id: str):
    """Analyze specific telescope"""
    scope = get_telescope_by_id(telescope_id)
    if not scope:
        print(f"❌ Telescope '{telescope_id}' not found")
        return
    
    print(f"🔭 TELESCOPE ANALYSIS: {scope.name}")
    print("=" * 50)
    
    print(f"\n📊 Specifications:")
    print(f"   Manufacturer: {scope.manufacturer}")
    print(f"   Aperture: {scope.aperture_mm}mm")
    print(f"   Focal Length: {scope.focal_length_mm}mm")
    print(f"   Focal Ratio: f/{scope.focal_ratio}")
    print(f"   Sensor: {scope.sensor_model} ({scope.sensor_type})")
    print(f"   Resolution: {scope.resolution_mp}MP")
    print(f"   Pixel Size: {scope.pixel_size_um}μm")
    print(f"   Native FOV: {scope.native_fov_deg[0]:.2f}° × {scope.native_fov_deg[1]:.2f}°")
    
    if scope.has_mosaic_mode and scope.mosaic_fov_deg:
        print(f"   Mosaic FOV: {scope.mosaic_fov_deg[0]:.2f}° × {scope.mosaic_fov_deg[1]:.2f}°")
    
    print(f"   Weight: {scope.weight_kg}kg")
    print(f"   Price: ${scope.price_usd:,}")
    
    # Calculate pixel scale
    pixel_scale = calculate_pixel_scale(telescope_id)
    if pixel_scale:
        print(f"   Pixel Scale: {pixel_scale:.2f}\"/pixel")
    
    # Test FOV compatibility with various target sizes
    print(f"\n🎯 Target Compatibility:")
    test_sizes = [15, 30, 60, 120, 180, 300]  # arcminutes
    
    for size in test_sizes:
        compatible = calculate_fov_compatibility(telescope_id, size, use_mosaic=True)
        status = "✅" if compatible else "❌"
        print(f"   {status} {size}' ({size/60:.1f}°) target")


def calculate_exposure(telescope_id: str, target_type_str: str, magnitude: float = 10.0,
                      duration: float = 120.0, pollution: str = "moderate", moon: float = 0.0):
    """Calculate exposure recommendation"""
    scope = get_telescope_by_id(telescope_id)
    if not scope:
        print(f"❌ Telescope '{telescope_id}' not found")
        return
    
    # Parse target type
    try:
        target_type = TargetType(target_type_str.lower().replace(' ', '_'))
    except ValueError:
        print(f"❌ Invalid target type '{target_type_str}'")
        print("Valid types:", [t.value for t in TargetType])
        return
    
    print(f"📸 EXPOSURE CALCULATION")
    print("=" * 50)
    print(f"Telescope: {scope.name}")
    print(f"Target: {target_type.value.replace('_', ' ').title()}")
    print(f"Magnitude: {magnitude}")
    print(f"Session Duration: {duration} min")
    print(f"Light Pollution: {pollution}")
    print(f"Moon Phase: {moon:.1f}")
    print()
    
    exposure = calculate_exposure_recommendation(
        telescope_id=telescope_id,
        target_type=target_type,
        target_magnitude=magnitude,
        session_duration_min=duration,
        moon_phase=moon,
        light_pollution=pollution
    )
    
    if exposure:
        print(f"📊 Recommendation:")
        print(f"   Single Exposure: {exposure.single_exposure_sec}s")
        print(f"   Total Frames: {exposure.total_frames}")
        print(f"   Total Time: {exposure.total_time_min} min")
        print(f"   ISO Setting: {exposure.iso_setting}")
        print(f"   Binning Mode: {exposure.binning_mode}")
        print(f"   Confidence: {exposure.confidence}%")
        print(f"   Reasoning: {exposure.reasoning}")
    else:
        print("❌ Failed to calculate exposure")


def predict_quality(telescope_id: str, target_type_str: str, magnitude: float = 10.0,
                   size: float = 60.0, seeing: float = 2.0, pollution: str = "moderate"):
    """Predict image quality"""
    scope = get_telescope_by_id(telescope_id)
    if not scope:
        print(f"❌ Telescope '{telescope_id}' not found")
        return
    
    # Parse target type
    try:
        target_type = TargetType(target_type_str.lower().replace(' ', '_'))
    except ValueError:
        print(f"❌ Invalid target type '{target_type_str}'")
        print("Valid types:", [t.value for t in TargetType])
        return
    
    print(f"📊 QUALITY PREDICTION")
    print("=" * 50)
    print(f"Telescope: {scope.name}")
    print(f"Target: {target_type.value.replace('_', ' ').title()}")
    print(f"Magnitude: {magnitude}")
    print(f"Size: {size}' ({size/60:.1f}°)")
    print(f"Seeing: {seeing}\"")
    print(f"Light Pollution: {pollution}")
    print()
    
    quality = calculate_quality_metrics(
        telescope_id=telescope_id,
        target_type=target_type,
        target_size_arcmin=size,
        target_magnitude=magnitude,
        seeing_arcsec=seeing,
        light_pollution=pollution
    )
    
    if quality:
        print(f"📈 Quality Metrics:")
        print(f"   Overall Score: {quality.overall_score}/100 ({quality.quality_class})")
        print(f"   Resolution Score: {quality.resolution_score}/100")
        print(f"   Sensitivity Score: {quality.sensitivity_score}/100")
        print(f"   Noise Score: {quality.noise_score}/100")
        print(f"   Limiting Magnitude: {quality.limiting_magnitude}")
        print(f"   Pixel Scale: {quality.pixel_scale_arcsec}\"/pixel")
        print(f"   SNR Estimate: {quality.snr_estimate}")
    else:
        print("❌ Failed to predict quality")


def compare_for_target(target_type_str: str, magnitude: float = 10.0,
                      size: float = 60.0, pollution: str = "moderate"):
    """Compare all telescopes for a specific target"""
    # Parse target type
    try:
        target_type = TargetType(target_type_str.lower().replace(' ', '_'))
    except ValueError:
        print(f"❌ Invalid target type '{target_type_str}'")
        print("Valid types:", [t.value for t in TargetType])
        return
    
    print(f"🏆 TELESCOPE COMPARISON")
    print("=" * 50)
    print(f"Target: {target_type.value.replace('_', ' ').title()}")
    print(f"Magnitude: {magnitude}")
    print(f"Size: {size}' ({size/60:.1f}°)")
    print(f"Light Pollution: {pollution}")
    print()
    
    results = compare_telescopes_for_target(
        target_type=target_type,
        target_magnitude=magnitude,
        target_size_arcmin=size,
        light_pollution=pollution
    )
    
    print("📊 Rankings (by Overall Quality Score):")
    print("-" * 50)
    
    for i, result in enumerate(results, 1):
        scope = result['scope']
        quality = result['quality']
        exposure = result['exposure']
        compatible = result['fov_compatible']
        
        compat_icon = "✅" if compatible else "❌"
        print(f"{i}. {compat_icon} {scope.name} ({scope.manufacturer})")
        print(f"   Quality: {quality.overall_score}/100 ({quality.quality_class})")
        print(f"   Exposure: {exposure.single_exposure_sec}s × {exposure.total_frames} frames")
        print(f"   Confidence: {exposure.confidence}%")
        print(f"   Price: ${scope.price_usd:,}")
        print()


def export_data(filename: str = "telescope_database.json"):
    """Export telescope database"""
    success = export_telescope_data(filename)
    if success:
        print(f"✅ Telescope database exported to {filename}")
    else:
        print(f"❌ Failed to export database to {filename}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Telescope Analysis CLI Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List telescopes
    subparsers.add_parser('list', help='List all available telescopes')
    
    # Analyze telescope
    analyze_parser = subparsers.add_parser('analyze', help='Analyze specific telescope')
    analyze_parser.add_argument('telescope_id', help='Telescope ID to analyze')
    
    # Calculate exposure
    exposure_parser = subparsers.add_parser('exposure', help='Calculate exposure recommendation')
    exposure_parser.add_argument('telescope_id', help='Telescope ID')
    exposure_parser.add_argument('target_type', help='Target type (e.g., galaxy, emission_nebula)')
    exposure_parser.add_argument('--magnitude', type=float, default=10.0, help='Target magnitude')
    exposure_parser.add_argument('--duration', type=float, default=120.0, help='Session duration (min)')
    exposure_parser.add_argument('--pollution', default='moderate', choices=['dark', 'moderate', 'bright'], help='Light pollution')
    exposure_parser.add_argument('--moon', type=float, default=0.0, help='Moon phase (0.0-1.0)')
    
    # Predict quality
    quality_parser = subparsers.add_parser('quality', help='Predict image quality')
    quality_parser.add_argument('telescope_id', help='Telescope ID')
    quality_parser.add_argument('target_type', help='Target type (e.g., galaxy, emission_nebula)')
    quality_parser.add_argument('--magnitude', type=float, default=10.0, help='Target magnitude')
    quality_parser.add_argument('--size', type=float, default=60.0, help='Target size (arcmin)')
    quality_parser.add_argument('--seeing', type=float, default=2.0, help='Seeing (arcsec)')
    quality_parser.add_argument('--pollution', default='moderate', choices=['dark', 'moderate', 'bright'], help='Light pollution')
    
    # Compare telescopes
    compare_parser = subparsers.add_parser('compare', help='Compare telescopes for target')
    compare_parser.add_argument('target_type', help='Target type (e.g., galaxy, emission_nebula)')
    compare_parser.add_argument('--magnitude', type=float, default=10.0, help='Target magnitude')
    compare_parser.add_argument('--size', type=float, default=60.0, help='Target size (arcmin)')
    compare_parser.add_argument('--pollution', default='moderate', choices=['dark', 'moderate', 'bright'], help='Light pollution')
    
    # Export data
    export_parser = subparsers.add_parser('export', help='Export telescope database')
    export_parser.add_argument('--filename', default='telescope_database.json', help='Output filename')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_telescopes()
    elif args.command == 'analyze':
        analyze_telescope(args.telescope_id)
    elif args.command == 'exposure':
        calculate_exposure(args.telescope_id, args.target_type, args.magnitude,
                         args.duration, args.pollution, args.moon)
    elif args.command == 'quality':
        predict_quality(args.telescope_id, args.target_type, args.magnitude,
                       args.size, args.seeing, args.pollution)
    elif args.command == 'compare':
        compare_for_target(args.target_type, args.magnitude, args.size, args.pollution)
    elif args.command == 'export':
        export_data(args.filename)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()