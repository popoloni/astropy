"""
Smart Telescope Scope Manager
Manages specifications and capabilities of various smart telescopes
Uses common telescope analysis functions from analysis module
"""

import sys
import os
from typing import Dict, List, Optional, Tuple

# Add parent directories to path for importing common functions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from analysis.telescope_analysis import (
    ScopeSpecifications, ScopeType, TargetType,
    ExposureRecommendation, QualityMetrics,
    get_telescope_database, get_telescope_by_id,
    calculate_fov_compatibility, calculate_pixel_scale,
    calculate_exposure_recommendation, calculate_quality_metrics,
    compare_telescopes_for_target, export_telescope_data
)


class ScopeType(Enum):
    """Types of smart telescopes"""
    VAONIS = "vaonis"
    ZWO = "zwo"
    DWARFLAB = "dwarflab"


@dataclass
class ScopeSpecifications:
    """Specifications for a smart telescope"""
    # Basic info
    name: str
    manufacturer: str
    scope_type: ScopeType
    
    # Optical specifications
    aperture_mm: float
    focal_length_mm: float
    focal_ratio: float
    
    # Sensor specifications
    sensor_model: str
    sensor_type: str
    resolution_mp: float
    pixel_size_um: float
    sensor_size_mm: Tuple[float, float]  # width, height
    
    # Field of view
    native_fov_deg: Tuple[float, float]  # width, height in degrees
    mosaic_fov_deg: Optional[Tuple[float, float]] = None  # enhanced FOV if available
    
    # Additional capabilities
    has_goto: bool = True
    has_tracking: bool = True
    has_autofocus: bool = True
    has_autoguiding: bool = True
    has_mosaic_mode: bool = False
    has_live_stacking: bool = True
    
    # Imaging capabilities
    max_exposure_sec: float = 300
    min_exposure_sec: float = 0.1
    iso_range: Tuple[int, int] = (100, 25600)
    
    # Physical specifications
    weight_kg: float = 5.0
    dimensions_mm: Tuple[float, float, float] = (400, 200, 200)  # L, W, H
    
    # Price and availability
    price_usd: Optional[float] = None
    is_available: bool = True
    
    # Default scope indicator
    is_default: bool = False


class SmartScopeManager:
    """Manages smart telescope specifications and selection"""
    
    def __init__(self):
        self.scopes = self._initialize_scopes()
        self.selected_scope = self._get_default_scope()
    
    def _initialize_scopes(self) -> Dict[str, ScopeSpecifications]:
        """Initialize all supported smart telescopes with their specifications"""
        scopes = {}
        
        # Vaonis Vespera Passenger (default)
        scopes["vespera_passenger"] = ScopeSpecifications(
            name="Vespera Passenger",
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
            native_fov_deg=(1.6, 0.9),
            has_mosaic_mode=True,
            mosaic_fov_deg=(3.2, 1.8),
            weight_kg=5.0,
            price_usd=1499,
            is_default=True
        )
        
        # Vaonis Vespera 1
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
            native_fov_deg=(1.6, 0.9),
            has_mosaic_mode=True,
            mosaic_fov_deg=(3.2, 1.8),
            weight_kg=5.0,
            price_usd=1499
        )
        
        # Vaonis Vespera 2
        scopes["vespera_2"] = ScopeSpecifications(
            name="Vespera II",
            manufacturer="Vaonis",
            scope_type=ScopeType.VAONIS,
            aperture_mm=50,
            focal_length_mm=200,
            focal_ratio=4.0,
            sensor_model="Sony IMX585",
            sensor_type="CMOS STARVIS 2",
            resolution_mp=8.3,
            pixel_size_um=2.9,
            sensor_size_mm=(11.1, 6.2),
            native_fov_deg=(3.4, 2.0),
            has_mosaic_mode=True,
            mosaic_fov_deg=(6.8, 4.0),
            weight_kg=5.0,
            price_usd=1990
        )
        
        # Vaonis Vespera Pro
        scopes["vespera_pro"] = ScopeSpecifications(
            name="Vespera Pro",
            manufacturer="Vaonis",
            scope_type=ScopeType.VAONIS,
            aperture_mm=50,
            focal_length_mm=250,
            focal_ratio=5.0,
            sensor_model="Sony IMX676",
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
            sensor_size_mm=(5.6, 3.2),
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
            resolution_mp=8.3,
            pixel_size_um=2.0,
            sensor_size_mm=(7.7, 4.3),
            native_fov_deg=(3.0, 1.7),
            has_mosaic_mode=True,
            mosaic_fov_deg=(6.0, 3.4),
            weight_kg=1.5,
            price_usd=599
        )
        
        return scopes
    
    def _get_default_scope(self) -> str:
        """Get the default scope (Vespera Passenger)"""
        for scope_id, scope in self.scopes.items():
            if scope.is_default:
                return scope_id
        return "vespera_passenger"  # fallback
    
    def get_scope(self, scope_id: str) -> Optional[ScopeSpecifications]:
        """Get scope specifications by ID"""
        return self.scopes.get(scope_id)
    
    def get_selected_scope(self) -> ScopeSpecifications:
        """Get currently selected scope specifications"""
        return self.scopes[self.selected_scope]
    
    def set_selected_scope(self, scope_id: str) -> bool:
        """Set the selected scope"""
        if scope_id in self.scopes:
            self.selected_scope = scope_id
            return True
        return False
    
    def get_all_scopes(self) -> Dict[str, ScopeSpecifications]:
        """Get all available scopes"""
        return self.scopes.copy()
    
    def get_scopes_by_manufacturer(self, manufacturer: str) -> Dict[str, ScopeSpecifications]:
        """Get scopes filtered by manufacturer"""
        return {
            scope_id: scope for scope_id, scope in self.scopes.items()
            if scope.manufacturer.lower() == manufacturer.lower()
        }
    
    def get_scopes_by_type(self, scope_type: ScopeType) -> Dict[str, ScopeSpecifications]:
        """Get scopes filtered by type"""
        return {
            scope_id: scope for scope_id, scope in self.scopes.items()
            if scope.scope_type == scope_type
        }
    
    def get_scope_names(self) -> List[str]:
        """Get list of all scope names for UI display"""
        return [scope.name for scope in self.scopes.values()]
    
    def get_scope_id_by_name(self, name: str) -> Optional[str]:
        """Get scope ID by display name"""
        for scope_id, scope in self.scopes.items():
            if scope.name == name:
                return scope_id
        return None
    
    def calculate_fov_for_target(self, target_size_arcmin: float, use_mosaic: bool = False) -> Dict[str, bool]:
        """
        Calculate which scopes can capture a target of given size
        Returns dict of scope_id: can_capture
        """
        results = {}
        target_size_deg = target_size_arcmin / 60.0
        
        for scope_id, scope in self.scopes.items():
            # First try native FOV
            native_fov = max(scope.native_fov_deg)
            can_capture_native = native_fov >= target_size_deg * 1.1
            
            # If native doesn't work, try mosaic mode
            can_capture_mosaic = False
            if scope.has_mosaic_mode and scope.mosaic_fov_deg:
                mosaic_fov = max(scope.mosaic_fov_deg)
                can_capture_mosaic = mosaic_fov >= target_size_deg * 1.1
            
            # If use_mosaic is specified, prefer mosaic mode
            if use_mosaic and scope.has_mosaic_mode and scope.mosaic_fov_deg:
                results[scope_id] = can_capture_mosaic
            else:
                # Can capture if either native or mosaic works
                results[scope_id] = can_capture_native or can_capture_mosaic
        
        return results
    
    def get_optimal_scopes_for_target(self, target_size_arcmin: float, 
                                    max_price: Optional[float] = None) -> List[Tuple[str, ScopeSpecifications]]:
        """
        Get optimal scopes for a target, sorted by suitability
        """
        suitable_scopes = []
        target_size_deg = target_size_arcmin / 60.0
        
        for scope_id, scope in self.scopes.items():
            # Check price constraint
            if max_price and scope.price_usd and scope.price_usd > max_price:
                continue
            
            # Check if target fits in FOV
            native_fov = max(scope.native_fov_deg)
            mosaic_fov = max(scope.mosaic_fov_deg) if scope.mosaic_fov_deg else native_fov
            
            if mosaic_fov >= target_size_deg * 1.2:  # 20% margin
                # Calculate suitability score
                fov_efficiency = target_size_deg / native_fov  # Higher is better
                resolution_score = scope.resolution_mp / 15.0  # Normalize to ~15MP max
                aperture_score = scope.aperture_mm / 60.0  # Normalize to ~60mm max
                
                suitability = (fov_efficiency * 0.4 + resolution_score * 0.3 + aperture_score * 0.3)
                suitable_scopes.append((scope_id, scope, suitability))
        
        # Sort by suitability score (descending)
        suitable_scopes.sort(key=lambda x: x[2], reverse=True)
        return [(scope_id, scope) for scope_id, scope, _ in suitable_scopes]
    
    def export_scope_data(self) -> str:
        """Export scope data as JSON string"""
        export_data = {}
        for scope_id, scope in self.scopes.items():
            export_data[scope_id] = asdict(scope)
            # Convert enum to string
            export_data[scope_id]['scope_type'] = scope.scope_type.value
        
        return json.dumps(export_data, indent=2)
    
    def get_scope_comparison(self, scope_ids: List[str]) -> Dict[str, Dict]:
        """Get comparison data for multiple scopes"""
        comparison = {}
        
        for scope_id in scope_ids:
            if scope_id in self.scopes:
                scope = self.scopes[scope_id]
                comparison[scope_id] = {
                    'name': scope.name,
                    'manufacturer': scope.manufacturer,
                    'aperture_mm': scope.aperture_mm,
                    'focal_length_mm': scope.focal_length_mm,
                    'resolution_mp': scope.resolution_mp,
                    'native_fov_deg': scope.native_fov_deg,
                    'mosaic_fov_deg': scope.mosaic_fov_deg,
                    'weight_kg': scope.weight_kg,
                    'price_usd': scope.price_usd,
                    'sensor_model': scope.sensor_model
                }
        
        return comparison


# Global scope manager instance
_scope_manager = None

def get_scope_manager() -> SmartScopeManager:
    """Get the global scope manager instance"""
    global _scope_manager
    if _scope_manager is None:
        _scope_manager = SmartScopeManager()
    return _scope_manager


# Convenience functions for easy access
def get_selected_scope() -> ScopeSpecifications:
    """Get currently selected scope"""
    return get_scope_manager().get_selected_scope()

def set_selected_scope(scope_id: str) -> bool:
    """Set selected scope"""
    return get_scope_manager().set_selected_scope(scope_id)

def get_all_scope_names() -> List[str]:
    """Get all scope names for UI"""
    return get_scope_manager().get_scope_names()

def calculate_target_fov_compatibility(target_size_arcmin: float) -> Dict[str, bool]:
    """Calculate which scopes can capture a target"""
    return get_scope_manager().calculate_fov_for_target(target_size_arcmin)


# Exposure and Quality Prediction Classes

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


class ExposureCalculator:
    """Calculate optimal exposure settings for scope/target combinations"""
    
    def __init__(self):
        # Target-specific exposure parameters
        self.target_parameters = {
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
    
    def calculate_exposure(self, scope: ScopeSpecifications, target_type: TargetType,
                          target_magnitude: float = 10.0, session_duration_min: float = 120.0,
                          moon_phase: float = 0.0, light_pollution: str = "moderate") -> ExposureRecommendation:
        """
        Calculate optimal exposure settings
        
        Args:
            scope: Telescope specifications
            target_type: Type of astronomical target
            target_magnitude: Target magnitude (lower = brighter)
            session_duration_min: Available imaging time in minutes
            moon_phase: Moon phase (0.0 = new moon, 1.0 = full moon)
            light_pollution: "dark", "moderate", "bright"
        """
        params = self.target_parameters.get(target_type, self.target_parameters[TargetType.GALAXY])
        
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
        confidence = self._calculate_confidence(scope, target_type, adjusted_exposure, target_frames)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(scope, target_type, adjusted_exposure, target_frames, 
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
    
    def _calculate_confidence(self, scope: ScopeSpecifications, target_type: TargetType,
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
    
    def _generate_reasoning(self, scope: ScopeSpecifications, target_type: TargetType,
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


class QualityPredictor:
    """Predict image quality metrics based on scope capabilities"""
    
    def __init__(self):
        # Reference values for quality scoring
        self.reference_aperture = 50.0  # mm
        self.reference_focal_length = 200.0  # mm
        self.reference_resolution = 2.1  # MP
        self.reference_pixel_size = 2.9  # μm
    
    def predict_quality(self, scope: ScopeSpecifications, target_type: TargetType,
                       target_size_arcmin: float = 60.0, target_magnitude: float = 10.0,
                       seeing_arcsec: float = 2.0, light_pollution: str = "moderate") -> QualityMetrics:
        """
        Predict image quality metrics for a scope/target combination
        
        Args:
            scope: Telescope specifications
            target_type: Type of astronomical target
            target_size_arcmin: Target size in arcminutes
            target_magnitude: Target magnitude
            seeing_arcsec: Atmospheric seeing in arcseconds
            light_pollution: "dark", "moderate", "bright"
        """
        # Calculate pixel scale
        pixel_scale = self._calculate_pixel_scale(scope)
        
        # Calculate resolution score
        resolution_score = self._calculate_resolution_score(scope, target_type, pixel_scale, seeing_arcsec)
        
        # Calculate sensitivity score
        sensitivity_score = self._calculate_sensitivity_score(scope, target_magnitude, light_pollution)
        
        # Calculate noise score
        noise_score = self._calculate_noise_score(scope, light_pollution)
        
        # Calculate overall score
        overall_score = (resolution_score * 0.3 + sensitivity_score * 0.4 + noise_score * 0.3)
        
        # Calculate limiting magnitude
        limiting_magnitude = self._calculate_limiting_magnitude(scope, light_pollution)
        
        # Estimate SNR
        snr_estimate = self._estimate_snr(scope, target_magnitude, light_pollution)
        
        # Determine quality class
        quality_class = self._determine_quality_class(overall_score)
        
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
    
    def _calculate_pixel_scale(self, scope: ScopeSpecifications) -> float:
        """Calculate pixel scale in arcseconds per pixel"""
        # Pixel scale = (pixel_size_μm / focal_length_mm) * 206265
        return (scope.pixel_size_um / scope.focal_length_mm) * 206.265
    
    def _calculate_resolution_score(self, scope: ScopeSpecifications, target_type: TargetType,
                                  pixel_scale: float, seeing_arcsec: float) -> float:
        """Calculate resolution quality score (0-100)"""
        # Base score from aperture (larger aperture = better resolution)
        aperture_score = min(100, (scope.aperture_mm / self.reference_aperture) * 70)
        
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
    
    def _calculate_sensitivity_score(self, scope: ScopeSpecifications, target_magnitude: float,
                                   light_pollution: str) -> float:
        """Calculate sensitivity quality score (0-100)"""
        # Base score from aperture (light gathering power scales with area)
        aperture_area = math.pi * (scope.aperture_mm / 2) ** 2
        reference_area = math.pi * (self.reference_aperture / 2) ** 2
        aperture_score = min(100, (aperture_area / reference_area) * 60)
        
        # Pixel size factor (larger pixels generally more sensitive)
        pixel_size_factor = scope.pixel_size_um / self.reference_pixel_size
        pixel_score = min(25, pixel_size_factor * 20)
        
        # Target magnitude factor (brighter targets easier to capture)
        magnitude_factor = max(0.5, (15.0 - target_magnitude) / 10.0)
        magnitude_score = magnitude_factor * 15
        
        # Light pollution penalty
        pollution_penalties = {"dark": 0, "moderate": -5, "bright": -15}
        pollution_penalty = pollution_penalties.get(light_pollution, -5)
        
        return max(0, min(100, aperture_score + pixel_score + magnitude_score + pollution_penalty))
    
    def _calculate_noise_score(self, scope: ScopeSpecifications, light_pollution: str) -> float:
        """Calculate noise performance score (0-100, higher is better)"""
        # Base score from sensor technology
        base_score = 70
        if "STARVIS" in scope.sensor_type:
            base_score += 15
        elif "CMOS" in scope.sensor_type:
            base_score += 5
        
        # Pixel size factor (larger pixels typically have better noise performance)
        pixel_size_factor = scope.pixel_size_um / self.reference_pixel_size
        pixel_score = min(20, pixel_size_factor * 15)
        
        # Resolution factor (higher resolution can mean smaller pixels and more noise)
        resolution_factor = self.reference_resolution / scope.resolution_mp
        resolution_score = min(10, resolution_factor * 8)
        
        # Light pollution penalty
        pollution_penalties = {"dark": 0, "moderate": -5, "bright": -15}
        pollution_penalty = pollution_penalties.get(light_pollution, -5)
        
        return max(0, min(100, base_score + pixel_score + resolution_score + pollution_penalty))
    
    def _calculate_limiting_magnitude(self, scope: ScopeSpecifications, light_pollution: str) -> float:
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
    
    def _estimate_snr(self, scope: ScopeSpecifications, target_magnitude: float, light_pollution: str) -> float:
        """Estimate signal-to-noise ratio"""
        # Simplified SNR estimation based on aperture and target brightness
        aperture_factor = (scope.aperture_mm / self.reference_aperture) ** 2
        magnitude_factor = math.pow(2.512, -(target_magnitude - 10.0))
        
        base_snr = 20.0 * aperture_factor * magnitude_factor
        
        # Adjust for light pollution
        pollution_factors = {"dark": 1.2, "moderate": 1.0, "bright": 0.6}
        pollution_factor = pollution_factors.get(light_pollution, 1.0)
        
        return base_snr * pollution_factor
    
    def _determine_quality_class(self, overall_score: float) -> str:
        """Determine quality class from overall score"""
        if overall_score >= 85:
            return "Excellent"
        elif overall_score >= 70:
            return "Good"
        elif overall_score >= 55:
            return "Fair"
        else:
            return "Poor"


# Global instances
_exposure_calculator = None
_quality_predictor = None

def get_exposure_calculator() -> ExposureCalculator:
    """Get global exposure calculator instance"""
    global _exposure_calculator
    if _exposure_calculator is None:
        _exposure_calculator = ExposureCalculator()
    return _exposure_calculator

def get_quality_predictor() -> QualityPredictor:
    """Get global quality predictor instance"""
    global _quality_predictor
    if _quality_predictor is None:
        _quality_predictor = QualityPredictor()
    return _quality_predictor