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


class ScopeManager:
    """Manages smart telescope scopes and their capabilities"""
    
    def __init__(self):
        self.selected_scope_id = "seestar_s50"  # Default scope
        self.mosaic_mode_enabled = False
    
    def get_all_scopes(self) -> Dict[str, ScopeSpecifications]:
        """Get all available scopes"""
        return get_telescope_database()
    
    def get_scope(self, scope_id: str) -> Optional[ScopeSpecifications]:
        """Get specific scope by ID"""
        return get_telescope_by_id(scope_id)
    
    def get_scope_names(self) -> List[str]:
        """Get list of all scope names for UI"""
        scopes = self.get_all_scopes()
        return [scope.name for scope in scopes.values()]
    
    def get_scope_ids(self) -> List[str]:
        """Get list of all scope IDs"""
        return list(self.get_all_scopes().keys())
    
    def get_scopes_by_manufacturer(self, manufacturer: str) -> Dict[str, ScopeSpecifications]:
        """Get scopes by manufacturer"""
        all_scopes = self.get_all_scopes()
        return {
            scope_id: scope for scope_id, scope in all_scopes.items()
            if scope.manufacturer.lower() == manufacturer.lower()
        }
    
    def get_scopes_by_type(self, scope_type: ScopeType) -> Dict[str, ScopeSpecifications]:
        """Get scopes by type"""
        all_scopes = self.get_all_scopes()
        return {
            scope_id: scope for scope_id, scope in all_scopes.items()
            if scope.scope_type == scope_type
        }
    
    def set_selected_scope(self, scope_id: str) -> bool:
        """Set the currently selected scope"""
        if scope_id in self.get_all_scopes():
            self.selected_scope_id = scope_id
            return True
        return False
    
    def get_selected_scope(self) -> Optional[ScopeSpecifications]:
        """Get currently selected scope"""
        if self.selected_scope_id:
            return self.get_scope(self.selected_scope_id)
        return None
    
    def get_selected_scope_id(self) -> Optional[str]:
        """Get currently selected scope ID"""
        return self.selected_scope_id
    
    def set_mosaic_mode(self, enabled: bool):
        """Enable/disable mosaic mode"""
        self.mosaic_mode_enabled = enabled
    
    def is_mosaic_mode_enabled(self) -> bool:
        """Check if mosaic mode is enabled"""
        return self.mosaic_mode_enabled
    
    def calculate_fov_for_target(self, target_size_arcmin: float) -> Dict[str, bool]:
        """Calculate which scopes can capture a target of given size"""
        results = {}
        for scope_id in self.get_scope_ids():
            results[scope_id] = calculate_fov_compatibility(
                scope_id, target_size_arcmin, self.mosaic_mode_enabled
            )
        return results
    
    def get_compatible_scopes(self, target_size_arcmin: float) -> List[str]:
        """Get list of scope IDs compatible with target size"""
        compatibility = self.calculate_fov_for_target(target_size_arcmin)
        return [scope_id for scope_id, compatible in compatibility.items() if compatible]
    
    def get_scope_recommendations(self, target_size_arcmin: float) -> List[Tuple[str, str]]:
        """Get scope recommendations for target size"""
        recommendations = []
        target_size_deg = target_size_arcmin / 60.0
        
        for scope_id, scope in self.get_all_scopes().items():
            native_fov = min(scope.native_fov_deg)
            
            if target_size_deg <= native_fov:
                recommendations.append((scope_id, "Perfect fit - native FOV"))
            elif scope.has_mosaic_mode and scope.mosaic_fov_deg:
                mosaic_fov = min(scope.mosaic_fov_deg)
                if target_size_deg <= mosaic_fov:
                    recommendations.append((scope_id, "Good fit - mosaic mode required"))
                else:
                    recommendations.append((scope_id, "Too large - target exceeds FOV"))
            else:
                recommendations.append((scope_id, "Too large - no mosaic mode"))
        
        return recommendations
    
    def compare_scopes(self, scope_ids: List[str]) -> Dict[str, Dict]:
        """Compare multiple scopes"""
        comparison = {}
        
        for scope_id in scope_ids:
            scope = self.get_scope(scope_id)
            if scope:
                comparison[scope_id] = {
                    'name': scope.name,
                    'manufacturer': scope.manufacturer,
                    'aperture_mm': scope.aperture_mm,
                    'focal_length_mm': scope.focal_length_mm,
                    'resolution_mp': scope.resolution_mp,
                    'native_fov_deg': scope.native_fov_deg,
                    'has_mosaic_mode': scope.has_mosaic_mode,
                    'mosaic_fov_deg': scope.mosaic_fov_deg,
                    'price_usd': scope.price_usd,
                    'pixel_scale_arcsec': calculate_pixel_scale(scope_id)
                }
        
        return comparison
    
    def export_scope_data(self, filename: str = "scope_data.json") -> bool:
        """Export scope data to JSON file"""
        return export_telescope_data(filename)


class ExposureCalculator:
    """Calculate optimal exposure settings for scope/target combinations"""
    
    def calculate_exposure(self, scope: ScopeSpecifications, target_type: TargetType,
                          target_magnitude: float = 10.0, session_duration_min: float = 120.0,
                          moon_phase: float = 0.0, light_pollution: str = "moderate") -> ExposureRecommendation:
        """Calculate optimal exposure settings using common analysis functions"""
        # Find scope ID for the given scope
        database = get_telescope_database()
        scope_id = None
        for sid, s in database.items():
            if s.name == scope.name and s.manufacturer == scope.manufacturer:
                scope_id = sid
                break
        
        if not scope_id:
            # Fallback to basic calculation if scope not found
            return ExposureRecommendation(
                single_exposure_sec=180.0,
                total_frames=40,
                total_time_min=120.0,
                iso_setting=1600,
                binning_mode="x1",
                confidence=50.0,
                reasoning="Unknown scope - using default settings"
            )
        
        result = calculate_exposure_recommendation(
            telescope_id=scope_id,
            target_type=target_type,
            target_magnitude=target_magnitude,
            session_duration_min=session_duration_min,
            moon_phase=moon_phase,
            light_pollution=light_pollution
        )
        
        return result if result else ExposureRecommendation(
            single_exposure_sec=180.0,
            total_frames=40,
            total_time_min=120.0,
            iso_setting=1600,
            binning_mode="x1",
            confidence=50.0,
            reasoning="Calculation failed - using default settings"
        )


class QualityPredictor:
    """Predict image quality metrics based on scope capabilities"""
    
    def predict_quality(self, scope: ScopeSpecifications, target_type: TargetType,
                       target_size_arcmin: float = 60.0, target_magnitude: float = 10.0,
                       seeing_arcsec: float = 2.0, light_pollution: str = "moderate") -> QualityMetrics:
        """Predict image quality using common analysis functions"""
        # Find scope ID for the given scope
        database = get_telescope_database()
        scope_id = None
        for sid, s in database.items():
            if s.name == scope.name and s.manufacturer == scope.manufacturer:
                scope_id = sid
                break
        
        if not scope_id:
            # Fallback to basic calculation if scope not found
            return QualityMetrics(
                resolution_score=50.0,
                sensitivity_score=50.0,
                noise_score=50.0,
                overall_score=50.0,
                limiting_magnitude=12.0,
                pixel_scale_arcsec=2.0,
                snr_estimate=10.0,
                quality_class="Fair"
            )
        
        result = calculate_quality_metrics(
            telescope_id=scope_id,
            target_type=target_type,
            target_size_arcmin=target_size_arcmin,
            target_magnitude=target_magnitude,
            seeing_arcsec=seeing_arcsec,
            light_pollution=light_pollution
        )
        
        return result if result else QualityMetrics(
            resolution_score=50.0,
            sensitivity_score=50.0,
            noise_score=50.0,
            overall_score=50.0,
            limiting_magnitude=12.0,
            pixel_scale_arcsec=2.0,
            snr_estimate=10.0,
            quality_class="Fair"
        )


# Global instances
_scope_manager = None
_exposure_calculator = None
_quality_predictor = None

def get_scope_manager() -> ScopeManager:
    """Get global scope manager instance"""
    global _scope_manager
    if _scope_manager is None:
        _scope_manager = ScopeManager()
    return _scope_manager

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

# Convenience functions for backward compatibility
def get_selected_scope() -> Optional[ScopeSpecifications]:
    """Get selected scope"""
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