"""
Smart Telescope Scope Manager
Manages specifications and capabilities of various smart telescopes
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


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
            native_fov_deg=(1.3, 0.7),
            has_mosaic_mode=True,
            mosaic_fov_deg=(2.6, 1.4),
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
            native_fov_deg=(2.1, 1.2),
            has_mosaic_mode=False,
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
            if use_mosaic and scope.has_mosaic_mode and scope.mosaic_fov_deg:
                fov = max(scope.mosaic_fov_deg)
            else:
                fov = max(scope.native_fov_deg)
            
            # Target should fit within FOV with some margin
            results[scope_id] = fov >= target_size_deg * 1.2
        
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