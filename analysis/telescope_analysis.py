"""
Telescope Analysis Module
Common functions for telescope specifications, exposure calculations, and quality predictions
Shared between CLI scripts and mobile app
"""

import json
import math
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass, asdict
from enum import Enum


class ScopeType(Enum):
    """Types of smart telescopes"""
    VAONIS = "vaonis"
    ZWO = "zwo"
    DWARFLAB = "dwarflab"


class TargetType(Enum):
    """Types of astronomical targets"""
    PLANETARY_NEBULA = "planetary_nebula"
    EMISSION_NEBULA = "emission_nebula"
    REFLECTION_NEBULA = "reflection_nebula"
    GALAXY = "galaxy"
    GLOBULAR_CLUSTER = "globular_cluster"
    OPEN_CLUSTER = "open_cluster"
    SUPERNOVA_REMNANT = "supernova_remnant"
    DARK_NEBULA = "dark_nebula"
    STAR_FIELD = "star_field"
    COMET = "comet"
    ASTEROID = "asteroid"
    PLANET = "planet"
    MOON = "moon"
    SUN = "sun"


@dataclass
class ScopeSpecifications:
    """Complete telescope specifications"""
    name: str
    manufacturer: str
    scope_type: ScopeType
    aperture_mm: float
    focal_length_mm: float
    focal_ratio: float
    sensor_model: str
    sensor_type: str
    resolution_mp: float
    pixel_size_um: float
    sensor_size_mm: Tuple[float, float]
    native_fov_deg: Tuple[float, float]
    has_mosaic_mode: bool
    mosaic_fov_deg: Optional[Tuple[float, float]] = None
    weight_kg: float = 0.0
    price_usd: int = 0
    min_exposure_sec: float = 0.1
    max_exposure_sec: float = 600.0
    iso_range: Tuple[int, int] = (100, 25600)


class ExposureRecommendation(NamedTuple):
    """Exposure recommendation result"""
    single_exposure_sec: float
    total_frames: int
    total_time_min: float
    iso_setting: int
    binning_mode: str
    confidence: float
    reasoning: str


class QualityMetrics(NamedTuple):
    """Image quality prediction metrics"""
    resolution_score: float  # 0-100
    sensitivity_score: float  # 0-100
    noise_score: float  # 0-100 (higher is better)
    overall_score: float  # 0-100
    limiting_magnitude: float
    pixel_scale_arcsec: float
    snr_estimate: float
    quality_class: str  # "Excellent", "Good", "Fair", "Poor"


def get_telescope_database() -> Dict[str, ScopeSpecifications]:
    """Get complete telescope database"""
    scopes = {}
    
    # Vaonis Vespera I
    scopes["vespera_1"] = ScopeSpecifications(
        name="Vespera I",
        manufacturer="Vaonis",
        scope_type=ScopeType.VAONIS,
        aperture_mm=50,
        focal_length_mm=200,
        focal_ratio=4.0,
        sensor_model="Sony IMX462",
        sensor_type="CMOS",
        resolution_mp=2.1,
        pixel_size_um=2.9,
        sensor_size_mm=(5.6, 3.2),
        native_fov_deg=(1.6, 1.6),
        has_mosaic_mode=True,
        mosaic_fov_deg=(4.18, 2.45),
        weight_kg=5.0,
        price_usd=1499
    )
    
    # Vaonis Vespera II
    scopes["vespera_2"] = ScopeSpecifications(
        name="Vespera II",
        manufacturer="Vaonis",
        scope_type=ScopeType.VAONIS,
        aperture_mm=50,
        focal_length_mm=200,
        focal_ratio=4.0,
        sensor_model="Sony IMX585",
        sensor_type="CMOS",
        resolution_mp=8.4,
        pixel_size_um=2.9,
        sensor_size_mm=(13.4, 8.9),
        native_fov_deg=(1.6, 1.6),
        has_mosaic_mode=True,
        mosaic_fov_deg=(4.18, 2.45),
        weight_kg=5.0,
        price_usd=1990
    )
    
    # Vaonis Vespera Pro
    scopes["vespera_pro"] = ScopeSpecifications(
        name="Vespera Pro",
        manufacturer="Vaonis",
        scope_type=ScopeType.VAONIS,
        aperture_mm=50,
        focal_length_mm=200,
        focal_ratio=4.0,
        sensor_model="Sony IMX678",
        sensor_type="CMOS STARVIS 2",
        resolution_mp=12.5,
        pixel_size_um=2.0,
        sensor_size_mm=(7.1, 7.1),
        native_fov_deg=(1.6, 1.6),
        has_mosaic_mode=True,
        mosaic_fov_deg=(4.18, 2.45),
        weight_kg=5.5,
        price_usd=2690
    )
    
    # Vaonis Vespera Passenger
    scopes["vespera_passenger"] = ScopeSpecifications(
        name="Vespera Passenger",
        manufacturer="Vaonis",
        scope_type=ScopeType.VAONIS,
        aperture_mm=50,
        focal_length_mm=200,
        focal_ratio=4.0,
        sensor_model="Sony IMX678",
        sensor_type="CMOS STARVIS 2",
        resolution_mp=12.5,
        pixel_size_um=2.0,
        sensor_size_mm=(7.1, 7.1),
        native_fov_deg=(1.6, 1.6),
        has_mosaic_mode=True,
        mosaic_fov_deg=(4.18, 2.45),
        weight_kg=5.5,
        price_usd=2690
    )
    
    # ZWO Seestar S50
    scopes["seestar_s50"] = ScopeSpecifications(
        name="Seestar S50",
        manufacturer="ZWO",
        scope_type=ScopeType.ZWO,
        aperture_mm=50,
        focal_length_mm=250,
        focal_ratio=5.0,
        sensor_model="Sony IMX462",
        sensor_type="CMOS",
        resolution_mp=2.1,
        pixel_size_um=2.9,
        sensor_size_mm=(5.6, 3.2),
        native_fov_deg=(0.7, 1.2),  # x1 normal mode
        has_mosaic_mode=True,
        mosaic_fov_deg=(1.44, 2.55),  # x2 mosaic mode from blog post
        weight_kg=3.0,
        price_usd=499
    )
    
    # ZWO Seestar S30
    scopes["seestar_s30"] = ScopeSpecifications(
        name="Seestar S30",
        manufacturer="ZWO",
        scope_type=ScopeType.ZWO,
        aperture_mm=30,
        focal_length_mm=150,
        focal_ratio=5.0,
        sensor_model="Sony IMX462",
        sensor_type="CMOS",
        resolution_mp=2.1,
        pixel_size_um=2.9,
        sensor_size_mm=(5.6, 3.2),
        native_fov_deg=(1.22, 2.17),  # x1 normal mode from blog post
        has_mosaic_mode=True,  # S30 also has mosaic mode
        mosaic_fov_deg=(2.44, 4.34),  # x2 mosaic mode (approximate 2x coverage)
        weight_kg=2.0,
        price_usd=299
    )
    
    # DwarfLab Dwarf 2
    scopes["dwarf_2"] = ScopeSpecifications(
        name="Dwarf II",
        manufacturer="DwarfLab",
        scope_type=ScopeType.DWARFLAB,
        aperture_mm=24,
        focal_length_mm=100,
        focal_ratio=4.2,
        sensor_model="Sony IMX415",
        sensor_type="CMOS STARVIS 2",
        resolution_mp=8.3,
        pixel_size_um=1.45,
        sensor_size_mm=(5.8, 3.3),
        native_fov_deg=(3.2, 1.8),
        has_mosaic_mode=True,
        mosaic_fov_deg=(6.4, 3.6),
        weight_kg=1.2,
        price_usd=459
    )
    
    # DwarfLab Dwarf 3
    scopes["dwarf_3"] = ScopeSpecifications(
        name="Dwarf III",
        manufacturer="DwarfLab",
        scope_type=ScopeType.DWARFLAB,
        aperture_mm=35,
        focal_length_mm=150,
        focal_ratio=4.3,
        sensor_model="Sony IMX678",
        sensor_type="CMOS STARVIS 2",
        resolution_mp=12.5,
        pixel_size_um=2.0,
        sensor_size_mm=(7.1, 7.1),
        native_fov_deg=(3.0, 1.7),
        has_mosaic_mode=True,
        mosaic_fov_deg=(6.0, 3.4),
        weight_kg=1.5,
        price_usd=599
    )
    
    return scopes


def get_telescope_by_id(telescope_id: str) -> Optional[ScopeSpecifications]:
    """Get telescope specifications by ID"""
    database = get_telescope_database()
    return database.get(telescope_id)


def get_telescopes_by_manufacturer(manufacturer: str) -> List[ScopeSpecifications]:
    """Get all telescopes from a specific manufacturer"""
    database = get_telescope_database()
    return [scope for scope in database.values() if scope.manufacturer.lower() == manufacturer.lower()]


def calculate_fov_compatibility(telescope_id: str, target_size_arcmin: float, use_mosaic: bool = True) -> bool:
    """Check if telescope can capture target of given size"""
    scope = get_telescope_by_id(telescope_id)
    if not scope:
        return False
    
    target_size_deg = target_size_arcmin / 60.0
    
    # Check native FOV
    native_fov = min(scope.native_fov_deg)
    if target_size_deg <= native_fov:
        return True
    
    # Check mosaic FOV if available and requested
    if use_mosaic and scope.has_mosaic_mode and scope.mosaic_fov_deg:
        mosaic_fov = min(scope.mosaic_fov_deg)
        return target_size_deg <= mosaic_fov
    
    return False


def calculate_pixel_scale(telescope_id: str) -> Optional[float]:
    """Calculate pixel scale in arcseconds per pixel"""
    scope = get_telescope_by_id(telescope_id)
    if not scope:
        return None
    
    # Pixel scale = (pixel_size_μm / focal_length_mm) * 206265
    return (scope.pixel_size_um / scope.focal_length_mm) * 206.265


def calculate_exposure_recommendation(telescope_id: str, target_type: TargetType,
                                    target_magnitude: float = 10.0, session_duration_min: float = 120.0,
                                    moon_phase: float = 0.0, light_pollution: str = "moderate") -> Optional[ExposureRecommendation]:
    """Calculate optimal exposure settings for telescope/target combination"""
    scope = get_telescope_by_id(telescope_id)
    if not scope:
        return None
    
    # Target-specific exposure parameters
    target_parameters = {
        TargetType.PLANETARY_NEBULA: {
            'base_exposure_sec': 180,
            'magnitude_factor': 1.2,
            'frames_multiplier': 1.0,
            'iso_preference': 'medium',
            'binning_preference': 'x1'
        },
        TargetType.EMISSION_NEBULA: {
            'base_exposure_sec': 300,
            'magnitude_factor': 1.5,
            'frames_multiplier': 1.2,
            'iso_preference': 'low',
            'binning_preference': 'x1'
        },
        TargetType.REFLECTION_NEBULA: {
            'base_exposure_sec': 240,
            'magnitude_factor': 1.3,
            'frames_multiplier': 1.1,
            'iso_preference': 'medium',
            'binning_preference': 'x1'
        },
        TargetType.GALAXY: {
            'base_exposure_sec': 300,
            'magnitude_factor': 1.4,
            'frames_multiplier': 1.3,
            'iso_preference': 'low',
            'binning_preference': 'x1'
        },
        TargetType.GLOBULAR_CLUSTER: {
            'base_exposure_sec': 120,
            'magnitude_factor': 1.0,
            'frames_multiplier': 0.8,
            'iso_preference': 'medium',
            'binning_preference': 'x1'
        },
        TargetType.OPEN_CLUSTER: {
            'base_exposure_sec': 60,
            'magnitude_factor': 0.8,
            'frames_multiplier': 0.6,
            'iso_preference': 'high',
            'binning_preference': 'x1'
        },
        TargetType.SUPERNOVA_REMNANT: {
            'base_exposure_sec': 300,
            'magnitude_factor': 1.6,
            'frames_multiplier': 1.4,
            'iso_preference': 'low',
            'binning_preference': 'x1'
        },
        TargetType.STAR_FIELD: {
            'base_exposure_sec': 30,
            'magnitude_factor': 0.5,
            'frames_multiplier': 0.4,
            'iso_preference': 'high',
            'binning_preference': 'x1'
        },
        TargetType.COMET: {
            'base_exposure_sec': 120,
            'magnitude_factor': 1.1,
            'frames_multiplier': 0.9,
            'iso_preference': 'medium',
            'binning_preference': 'x1'
        },
        TargetType.PLANET: {
            'base_exposure_sec': 1,
            'magnitude_factor': 0.1,
            'frames_multiplier': 2.0,
            'iso_preference': 'low',
            'binning_preference': 'x1'
        }
    }
    
    params = target_parameters.get(target_type, target_parameters[TargetType.GALAXY])
    
    # Base exposure calculation
    base_exposure = params['base_exposure_sec']
    
    # Adjust for target magnitude
    magnitude_adjustment = math.pow(2.512, (target_magnitude - 10.0) * params['magnitude_factor'])
    adjusted_exposure = base_exposure * magnitude_adjustment
    
    # Adjust for scope aperture (larger aperture = shorter exposure needed)
    aperture_factor = (50.0 / scope.aperture_mm) ** 2  # Normalize to 50mm
    adjusted_exposure *= aperture_factor
    
    # Adjust for sensor sensitivity (higher MP usually means smaller pixels, less sensitive)
    sensor_factor = math.sqrt(scope.resolution_mp / 2.1)  # Normalize to 2.1MP
    adjusted_exposure *= sensor_factor
    
    # Adjust for light pollution
    pollution_factors = {"dark": 0.7, "moderate": 1.0, "bright": 1.5}
    adjusted_exposure *= pollution_factors.get(light_pollution, 1.0)
    
    # Adjust for moon phase
    moon_factor = 1.0 + (moon_phase * 0.3)  # Up to 30% longer exposure for full moon
    adjusted_exposure *= moon_factor
    
    # Clamp exposure to scope limits
    adjusted_exposure = max(scope.min_exposure_sec, min(adjusted_exposure, scope.max_exposure_sec))
    
    # Calculate number of frames
    base_frames = int(session_duration_min * 60 / adjusted_exposure)
    target_frames = int(base_frames * params['frames_multiplier'])
    target_frames = max(10, min(target_frames, 200))  # Reasonable limits
    
    # Calculate total time
    total_time = (target_frames * adjusted_exposure) / 60.0
    
    # Select ISO setting
    iso_preferences = {
        'low': scope.iso_range[0],
        'medium': int((scope.iso_range[0] + scope.iso_range[1]) / 2),
        'high': scope.iso_range[1]
    }
    iso_setting = iso_preferences.get(params['iso_preference'], iso_preferences['medium'])
    
    # Binning mode (most smart scopes use x1)
    binning_mode = params['binning_preference']
    
    # Calculate confidence based on scope suitability
    confidence = _calculate_exposure_confidence(scope, target_type, adjusted_exposure, target_frames)
    
    # Generate reasoning
    reasoning = _generate_exposure_reasoning(scope, target_type, adjusted_exposure, target_frames, 
                                           light_pollution, moon_phase)
    
    return ExposureRecommendation(
        single_exposure_sec=round(adjusted_exposure, 1),
        total_frames=target_frames,
        total_time_min=round(total_time, 1),
        iso_setting=iso_setting,
        binning_mode=binning_mode,
        confidence=round(confidence, 1),
        reasoning=reasoning
    )


def calculate_quality_metrics(telescope_id: str, target_type: TargetType,
                            target_size_arcmin: float = 60.0, target_magnitude: float = 10.0,
                            seeing_arcsec: float = 2.0, light_pollution: str = "moderate") -> Optional[QualityMetrics]:
    """Calculate image quality metrics for telescope/target combination"""
    scope = get_telescope_by_id(telescope_id)
    if not scope:
        return None
    
    # Reference values for quality scoring
    reference_aperture = 50.0  # mm
    reference_resolution = 2.1  # MP
    reference_pixel_size = 2.9  # μm
    
    # Calculate pixel scale
    pixel_scale = (scope.pixel_size_um / scope.focal_length_mm) * 206.265
    
    # Calculate resolution score
    resolution_score = _calculate_resolution_score(scope, target_type, pixel_scale, seeing_arcsec, reference_aperture)
    
    # Calculate sensitivity score
    sensitivity_score = _calculate_sensitivity_score(scope, target_magnitude, light_pollution, reference_aperture, reference_pixel_size)
    
    # Calculate noise score
    noise_score = _calculate_noise_score(scope, light_pollution, reference_resolution, reference_pixel_size)
    
    # Calculate overall score
    overall_score = (resolution_score * 0.3 + sensitivity_score * 0.4 + noise_score * 0.3)
    
    # Calculate limiting magnitude
    limiting_magnitude = _calculate_limiting_magnitude(scope, light_pollution)
    
    # Estimate SNR
    snr_estimate = _estimate_snr(scope, target_magnitude, light_pollution, reference_aperture)
    
    # Determine quality class
    quality_class = _determine_quality_class(overall_score)
    
    return QualityMetrics(
        resolution_score=round(resolution_score, 1),
        sensitivity_score=round(sensitivity_score, 1),
        noise_score=round(noise_score, 1),
        overall_score=round(overall_score, 1),
        limiting_magnitude=round(limiting_magnitude, 1),
        pixel_scale_arcsec=round(pixel_scale, 2),
        snr_estimate=round(snr_estimate, 1),
        quality_class=quality_class
    )


def compare_telescopes_for_target(target_type: TargetType, target_magnitude: float = 10.0,
                                target_size_arcmin: float = 60.0, light_pollution: str = "moderate") -> List[Dict]:
    """Compare all telescopes for a specific target"""
    database = get_telescope_database()
    results = []
    
    for telescope_id, scope in database.items():
        # Get quality prediction
        quality = calculate_quality_metrics(
            telescope_id=telescope_id,
            target_type=target_type,
            target_size_arcmin=target_size_arcmin,
            target_magnitude=target_magnitude,
            light_pollution=light_pollution
        )
        
        # Get exposure recommendation
        exposure = calculate_exposure_recommendation(
            telescope_id=telescope_id,
            target_type=target_type,
            target_magnitude=target_magnitude,
            light_pollution=light_pollution
        )
        
        if quality and exposure:
            results.append({
                'telescope_id': telescope_id,
                'scope': scope,
                'quality': quality,
                'exposure': exposure,
                'fov_compatible': calculate_fov_compatibility(telescope_id, target_size_arcmin)
            })
    
    # Sort by overall quality score
    results.sort(key=lambda x: x['quality'].overall_score, reverse=True)
    return results


def export_telescope_data(filename: str = "telescope_database.json") -> bool:
    """Export telescope database to JSON file"""
    try:
        database = get_telescope_database()
        export_data = {}
        
        for telescope_id, scope in database.items():
            export_data[telescope_id] = asdict(scope)
            # Convert enum to string for JSON serialization
            export_data[telescope_id]['scope_type'] = scope.scope_type.value
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return True
    except Exception:
        return False


# Helper functions

def _calculate_exposure_confidence(scope: ScopeSpecifications, target_type: TargetType,
                                 exposure_sec: float, frames: int) -> float:
    """Calculate confidence score for exposure recommendation"""
    confidence = 80.0  # Base confidence
    
    # Adjust for scope aperture
    if scope.aperture_mm >= 50:
        confidence += 10
    elif scope.aperture_mm >= 35:
        confidence += 5
    else:
        confidence -= 5
    
    # Adjust for exposure time reasonableness
    if 30 <= exposure_sec <= 300:
        confidence += 10
    elif exposure_sec < 10 or exposure_sec > 600:
        confidence -= 15
    
    # Adjust for frame count
    if 20 <= frames <= 100:
        confidence += 5
    elif frames < 10:
        confidence -= 10
    
    # Adjust for target type suitability
    if target_type in [TargetType.EMISSION_NEBULA, TargetType.GALAXY] and scope.aperture_mm >= 40:
        confidence += 5
    elif target_type in [TargetType.PLANET, TargetType.MOON] and scope.focal_length_mm >= 200:
        confidence += 5
    
    return max(0, min(100, confidence))


def _generate_exposure_reasoning(scope: ScopeSpecifications, target_type: TargetType,
                               exposure_sec: float, frames: int, light_pollution: str, moon_phase: float) -> str:
    """Generate human-readable reasoning for exposure settings"""
    reasons = []
    
    # Scope-specific reasoning
    if scope.aperture_mm >= 50:
        reasons.append(f"{scope.aperture_mm}mm aperture provides good light gathering")
    else:
        reasons.append(f"{scope.aperture_mm}mm aperture requires longer exposures")
    
    # Target-specific reasoning
    if target_type in [TargetType.EMISSION_NEBULA, TargetType.GALAXY]:
        reasons.append("Deep sky target requires longer exposures for detail")
    elif target_type in [TargetType.PLANET, TargetType.MOON]:
        reasons.append("Bright target allows shorter exposures to avoid overexposure")
    
    # Environmental factors
    if light_pollution == "bright":
        reasons.append("Light pollution increases required exposure time")
    elif light_pollution == "dark":
        reasons.append("Dark skies allow shorter exposures")
    
    if moon_phase > 0.5:
        reasons.append("Bright moon increases sky background")
    
    # Frame count reasoning
    if frames >= 50:
        reasons.append("Many frames improve signal-to-noise ratio")
    elif frames < 20:
        reasons.append("Limited frames due to time constraints")
    
    return "; ".join(reasons)


def _calculate_resolution_score(scope: ScopeSpecifications, target_type: TargetType,
                              pixel_scale: float, seeing_arcsec: float, reference_aperture: float) -> float:
    """Calculate resolution quality score (0-100)"""
    # Base score from aperture (larger aperture = better resolution)
    aperture_score = min(100, (scope.aperture_mm / reference_aperture) * 70)
    
    # Pixel scale factor (optimal pixel scale is ~1-2 arcsec/pixel for most targets)
    optimal_pixel_scale = 1.5
    if target_type in [TargetType.PLANET, TargetType.MOON]:
        optimal_pixel_scale = 0.5  # Planets benefit from finer sampling
    elif target_type in [TargetType.STAR_FIELD, TargetType.COMET]:
        optimal_pixel_scale = 2.0  # Wide field targets can use coarser sampling
    
    pixel_scale_factor = 1.0 / (1.0 + abs(pixel_scale - optimal_pixel_scale))
    pixel_scale_score = pixel_scale_factor * 30
    
    # Seeing factor (better seeing improves effective resolution)
    seeing_factor = max(0.5, 3.0 / seeing_arcsec)
    seeing_score = min(20, seeing_factor * 10)
    
    return min(100, aperture_score + pixel_scale_score + seeing_score)


def _calculate_sensitivity_score(scope: ScopeSpecifications, target_magnitude: float,
                               light_pollution: str, reference_aperture: float, reference_pixel_size: float) -> float:
    """Calculate sensitivity quality score (0-100)"""
    # Base score from aperture (light gathering power scales with area)
    aperture_area = math.pi * (scope.aperture_mm / 2) ** 2
    reference_area = math.pi * (reference_aperture / 2) ** 2
    aperture_score = min(100, (aperture_area / reference_area) * 60)
    
    # Pixel size factor (larger pixels generally more sensitive)
    pixel_size_factor = scope.pixel_size_um / reference_pixel_size
    pixel_score = min(25, pixel_size_factor * 20)
    
    # Target magnitude factor (brighter targets easier to capture)
    magnitude_factor = max(0.5, (15.0 - target_magnitude) / 10.0)
    magnitude_score = magnitude_factor * 15
    
    # Light pollution penalty
    pollution_penalties = {"dark": 0, "moderate": -5, "bright": -15}
    pollution_penalty = pollution_penalties.get(light_pollution, -5)
    
    return max(0, min(100, aperture_score + pixel_score + magnitude_score + pollution_penalty))


def _calculate_noise_score(scope: ScopeSpecifications, light_pollution: str,
                         reference_resolution: float, reference_pixel_size: float) -> float:
    """Calculate noise performance score (0-100, higher is better)"""
    # Base score from sensor technology
    base_score = 70
    if "STARVIS" in scope.sensor_type:
        base_score += 15
    elif "CMOS" in scope.sensor_type:
        base_score += 5
    
    # Pixel size factor (larger pixels typically have better noise performance)
    pixel_size_factor = scope.pixel_size_um / reference_pixel_size
    pixel_score = min(20, pixel_size_factor * 15)
    
    # Resolution factor (higher resolution can mean smaller pixels and more noise)
    resolution_factor = reference_resolution / scope.resolution_mp
    resolution_score = min(10, resolution_factor * 8)
    
    # Light pollution penalty
    pollution_penalties = {"dark": 0, "moderate": -5, "bright": -15}
    pollution_penalty = pollution_penalties.get(light_pollution, -5)
    
    return max(0, min(100, base_score + pixel_score + resolution_score + pollution_penalty))


def _calculate_limiting_magnitude(scope: ScopeSpecifications, light_pollution: str) -> float:
    """Calculate estimated limiting magnitude"""
    # Base limiting magnitude from aperture
    # Rule of thumb: limiting magnitude ≈ 5 * log10(aperture_mm) + constant
    base_magnitude = 5.0 * math.log10(scope.aperture_mm) + 7.5
    
    # Adjust for light pollution
    pollution_adjustments = {"dark": 1.5, "moderate": 0.0, "bright": -2.0}
    pollution_adjustment = pollution_adjustments.get(light_pollution, 0.0)
    
    # Adjust for sensor sensitivity
    if "STARVIS" in scope.sensor_type:
        sensor_adjustment = 0.5
    else:
        sensor_adjustment = 0.0
    
    return base_magnitude + pollution_adjustment + sensor_adjustment


def _estimate_snr(scope: ScopeSpecifications, target_magnitude: float, light_pollution: str, reference_aperture: float) -> float:
    """Estimate signal-to-noise ratio"""
    # Simplified SNR estimation based on aperture and target brightness
    aperture_factor = (scope.aperture_mm / reference_aperture) ** 2
    magnitude_factor = math.pow(2.512, -(target_magnitude - 10.0))
    
    base_snr = 20.0 * aperture_factor * magnitude_factor
    
    # Adjust for light pollution
    pollution_factors = {"dark": 1.2, "moderate": 1.0, "bright": 0.6}
    pollution_factor = pollution_factors.get(light_pollution, 1.0)
    
    return base_snr * pollution_factor


def _determine_quality_class(overall_score: float) -> str:
    """Determine quality class from overall score"""
    if overall_score >= 85:
        return "Excellent"
    elif overall_score >= 70:
        return "Good"
    elif overall_score >= 55:
        return "Fair"
    else:
        return "Poor"