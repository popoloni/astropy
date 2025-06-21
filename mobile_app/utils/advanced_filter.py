"""
Advanced Filtering System for AstroScope Planner
Sophisticated filtering options for astronomical targets
"""

from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import math
from .smart_scopes import get_scope_manager, ScopeSpecifications


class ImagingDifficulty(Enum):
    """Imaging difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ObjectType(Enum):
    """Astronomical object types"""
    GALAXY = "galaxy"
    NEBULA = "nebula"
    CLUSTER = "cluster"
    PLANETARY_NEBULA = "planetary_nebula"
    SUPERNOVA_REMNANT = "supernova_remnant"
    STAR = "star"
    DOUBLE_STAR = "double_star"
    VARIABLE_STAR = "variable_star"


class FilterOperator(Enum):
    """Filter comparison operators"""
    EQUALS = "equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    BETWEEN = "between"
    IN = "in"
    NOT_IN = "not_in"


@dataclass
class FilterCriteria:
    """Individual filter criteria"""
    field: str
    operator: FilterOperator
    value: Any
    enabled: bool = True


@dataclass
class AdvancedFilter:
    """
    Advanced filtering system for astronomical targets
    
    Provides sophisticated filtering options including:
    - Magnitude range filtering
    - Object size filtering
    - Object type selection
    - Imaging difficulty assessment
    - Moon avoidance calculations
    - Custom criteria support
    """
    
    # Basic filters
    magnitude_range: Tuple[float, float] = (0.0, 15.0)
    size_range: Tuple[float, float] = (0.0, 180.0)  # arcminutes
    object_types: List[str] = field(default_factory=lambda: ['galaxy', 'nebula', 'cluster'])
    imaging_difficulty: str = 'intermediate'
    moon_avoidance: bool = True
    
    # Advanced filters
    altitude_range: Tuple[float, float] = (30.0, 90.0)  # degrees
    visibility_hours_min: float = 2.0
    constellation_filter: List[str] = field(default_factory=list)
    season_preference: Optional[str] = None  # 'spring', 'summer', 'autumn', 'winter'
    
    # Technical filters
    focal_length_range: Tuple[float, float] = (200.0, 3000.0)  # mm
    pixel_scale_range: Tuple[float, float] = (0.5, 5.0)  # arcsec/pixel
    exposure_time_max: float = 600.0  # seconds
    
    # Smart telescope selection
    selected_scope: Optional[str] = None  # Scope ID, None means use default
    use_mosaic_mode: bool = False  # Whether to use mosaic FOV when available
    
    # Custom criteria
    custom_criteria: List[FilterCriteria] = field(default_factory=list)
    
    # Filter settings
    combine_with_and: bool = True  # True for AND, False for OR
    enabled: bool = True

    def __post_init__(self):
        """Initialize filter after creation"""
        self.difficulty_scores = self._calculate_difficulty_scores()
        self.constellation_map = self._load_constellation_map()

    def _calculate_difficulty_scores(self) -> Dict[str, Tuple[float, float]]:
        """Calculate difficulty score ranges for each level"""
        return {
            'beginner': (1.0, 3.0),      # Easy, bright objects
            'intermediate': (2.5, 5.0),   # Moderate difficulty
            'advanced': (4.0, 7.0),       # Challenging objects
            'expert': (6.0, 10.0)         # Very difficult objects
        }

    def _load_constellation_map(self) -> Dict[str, List[str]]:
        """Load constellation to season mapping"""
        return {
            'spring': ['Leo', 'Virgo', 'Bootes', 'Corona Borealis', 'Hercules'],
            'summer': ['Scorpius', 'Sagittarius', 'Ophiuchus', 'Serpens', 'Aquila'],
            'autumn': ['Pegasus', 'Andromeda', 'Perseus', 'Cassiopeia', 'Cetus'],
            'winter': ['Orion', 'Taurus', 'Gemini', 'Auriga', 'Canis Major']
        }

    def apply_filters(self, targets: List[Dict]) -> List[Dict]:
        """
        Apply all enabled filters to target list
        
        Args:
            targets: List of target dictionaries
            
        Returns:
            Filtered list of targets
        """
        if not self.enabled:
            return targets

        filtered_targets = []
        
        for target in targets:
            if self._passes_all_filters(target):
                filtered_targets.append(target)
        
        return filtered_targets

    def _passes_all_filters(self, target: Dict) -> bool:
        """Check if target passes all enabled filters"""
        filter_results = []
        
        # Basic filters
        filter_results.append(self._check_magnitude_filter(target))
        filter_results.append(self._check_size_filter(target))
        filter_results.append(self._check_object_type_filter(target))
        filter_results.append(self._check_imaging_difficulty_filter(target))
        filter_results.append(self._check_moon_avoidance_filter(target))
        
        # Advanced filters
        filter_results.append(self._check_altitude_filter(target))
        filter_results.append(self._check_visibility_hours_filter(target))
        filter_results.append(self._check_constellation_filter(target))
        filter_results.append(self._check_season_filter(target))
        
        # Technical filters
        filter_results.append(self._check_focal_length_filter(target))
        filter_results.append(self._check_pixel_scale_filter(target))
        filter_results.append(self._check_exposure_time_filter(target))
        
        # Scope compatibility filter
        filter_results.append(self._check_scope_compatibility(target))
        
        # Custom criteria
        filter_results.append(self._check_custom_criteria(target))
        
        # Combine results based on AND/OR setting
        if self.combine_with_and:
            return all(filter_results)
        else:
            return any(filter_results)

    def _check_magnitude_filter(self, target: Dict) -> bool:
        """Check magnitude range filter"""
        magnitude = target.get('magnitude', target.get('mag', 999))
        if magnitude == 999:  # No magnitude data
            return True
        return self.magnitude_range[0] <= magnitude <= self.magnitude_range[1]

    def _check_size_filter(self, target: Dict) -> bool:
        """Check object size filter"""
        # Try different size field names
        size = target.get('size', target.get('major_axis', target.get('diameter', 0)))
        if size == 0:  # No size data
            return True
        return self.size_range[0] <= size <= self.size_range[1]

    def _check_object_type_filter(self, target: Dict) -> bool:
        """Check object type filter"""
        if not self.object_types:
            return True
        
        obj_type = target.get('object_type', target.get('type', '')).lower()
        return any(filter_type.lower() in obj_type for filter_type in self.object_types)

    def _check_imaging_difficulty_filter(self, target: Dict) -> bool:
        """Check imaging difficulty filter"""
        difficulty_score = self._calculate_imaging_difficulty_score(target)
        score_range = self.difficulty_scores.get(self.imaging_difficulty, (0, 10))
        return score_range[0] <= difficulty_score <= score_range[1]

    def _calculate_imaging_difficulty_score(self, target: Dict) -> float:
        """
        Calculate imaging difficulty score (1-10 scale)
        
        Factors:
        - Magnitude (dimmer = harder)
        - Size (smaller = harder)
        - Object type (some types are inherently harder)
        - Surface brightness
        """
        score = 5.0  # Base score
        
        # Magnitude factor
        magnitude = target.get('magnitude', target.get('mag', 10))
        if magnitude > 12:
            score += 2.0
        elif magnitude > 8:
            score += 1.0
        elif magnitude < 5:
            score -= 1.0
        
        # Size factor
        size = target.get('size', target.get('major_axis', 10))
        if size < 2:  # Very small objects
            score += 1.5
        elif size > 30:  # Large objects
            score -= 0.5
        
        # Object type factor
        obj_type = target.get('object_type', '').lower()
        if 'galaxy' in obj_type:
            score += 0.5
        elif 'planetary' in obj_type:
            score += 1.0
        elif 'nebula' in obj_type and 'planetary' not in obj_type:
            score -= 0.5
        elif 'cluster' in obj_type:
            score -= 1.0
        
        # Surface brightness factor
        surface_brightness = target.get('surface_brightness', 20)
        if surface_brightness > 22:  # Very low surface brightness
            score += 1.5
        elif surface_brightness < 18:  # High surface brightness
            score -= 0.5
        
        return max(1.0, min(10.0, score))

    def _check_moon_avoidance_filter(self, target: Dict) -> bool:
        """Check moon avoidance filter"""
        if not self.moon_avoidance:
            return True
        
        # Check if target is affected by moon
        moon_affected = target.get('moon_affected', False)
        moon_separation = target.get('moon_separation_deg', 180)
        
        # Avoid targets too close to moon (less than 30 degrees)
        return not moon_affected and moon_separation > 30

    def _check_altitude_filter(self, target: Dict) -> bool:
        """Check altitude range filter"""
        max_altitude = target.get('max_altitude', target.get('altitude', 0))
        if max_altitude == 0:  # No altitude data
            return True
        return self.altitude_range[0] <= max_altitude <= self.altitude_range[1]

    def _check_visibility_hours_filter(self, target: Dict) -> bool:
        """Check minimum visibility hours filter"""
        visibility_hours = target.get('visibility_hours', 0)
        if visibility_hours == 0:  # No visibility data
            return True
        return visibility_hours >= self.visibility_hours_min

    def _check_constellation_filter(self, target: Dict) -> bool:
        """Check constellation filter"""
        if not self.constellation_filter:
            return True
        
        constellation = target.get('constellation', '')
        return constellation in self.constellation_filter

    def _check_season_filter(self, target: Dict) -> bool:
        """Check season preference filter"""
        if not self.season_preference:
            return True
        
        constellation = target.get('constellation', '')
        season_constellations = self.constellation_map.get(self.season_preference, [])
        return constellation in season_constellations

    def _check_focal_length_filter(self, target: Dict) -> bool:
        """Check recommended focal length filter"""
        recommended_fl = target.get('recommended_focal_length', 1000)
        return self.focal_length_range[0] <= recommended_fl <= self.focal_length_range[1]

    def _check_pixel_scale_filter(self, target: Dict) -> bool:
        """Check pixel scale requirements filter"""
        required_pixel_scale = target.get('required_pixel_scale', 2.0)
        return self.pixel_scale_range[0] <= required_pixel_scale <= self.pixel_scale_range[1]

    def _check_exposure_time_filter(self, target: Dict) -> bool:
        """Check maximum exposure time filter"""
        recommended_exposure = target.get('recommended_exposure_time', 300)
        return recommended_exposure <= self.exposure_time_max

    def _check_custom_criteria(self, target: Dict) -> bool:
        """Check custom filter criteria"""
        if not self.custom_criteria:
            return True
        
        results = []
        for criteria in self.custom_criteria:
            if not criteria.enabled:
                continue
            
            result = self._evaluate_criteria(target, criteria)
            results.append(result)
        
        if not results:
            return True
        
        # Apply same AND/OR logic to custom criteria
        if self.combine_with_and:
            return all(results)
        else:
            return any(results)

    def _evaluate_criteria(self, target: Dict, criteria: FilterCriteria) -> bool:
        """Evaluate individual filter criteria"""
        target_value = target.get(criteria.field)
        if target_value is None:
            return True  # Skip if field doesn't exist
        
        if criteria.operator == FilterOperator.EQUALS:
            return target_value == criteria.value
        elif criteria.operator == FilterOperator.GREATER_THAN:
            return target_value > criteria.value
        elif criteria.operator == FilterOperator.LESS_THAN:
            return target_value < criteria.value
        elif criteria.operator == FilterOperator.BETWEEN:
            return criteria.value[0] <= target_value <= criteria.value[1]
        elif criteria.operator == FilterOperator.IN:
            return target_value in criteria.value
        elif criteria.operator == FilterOperator.NOT_IN:
            return target_value not in criteria.value
        
        return True

    def _check_scope_compatibility(self, target: Dict) -> bool:
        """Check if target is compatible with selected scope"""
        if not self.selected_scope:
            return True  # No scope filter applied
        
        scope_manager = get_scope_manager()
        scope = scope_manager.get_scope(self.selected_scope)
        if not scope:
            return True  # Invalid scope, skip filter
        
        # Get target size
        target_size = target.get('size', 0)  # in arcminutes
        if target_size <= 0:
            return True  # No size info, assume compatible
        
        # Determine FOV to use
        if self.use_mosaic_mode and scope.has_mosaic_mode and scope.mosaic_fov_deg:
            fov_deg = max(scope.mosaic_fov_deg)
        else:
            fov_deg = max(scope.native_fov_deg)
        
        # Convert target size to degrees and check if it fits with margin
        target_size_deg = target_size / 60.0
        return fov_deg >= target_size_deg * 1.2  # 20% margin for framing

    def get_scope_recommendations(self, target: Dict) -> List[Tuple[str, str, float]]:
        """
        Get scope recommendations for a specific target
        Returns list of (scope_id, scope_name, suitability_score)
        """
        target_size = target.get('size', 0)  # in arcminutes
        if target_size <= 0:
            return []
        
        scope_manager = get_scope_manager()
        recommendations = []
        
        for scope_id, scope in scope_manager.get_all_scopes().items():
            # Calculate suitability
            target_size_deg = target_size / 60.0
            
            # Check native FOV
            native_fov = max(scope.native_fov_deg)
            mosaic_fov = max(scope.mosaic_fov_deg) if scope.mosaic_fov_deg else native_fov
            
            # Skip if target doesn't fit even with mosaic
            if mosaic_fov < target_size_deg * 1.1:
                continue
            
            # Calculate suitability score
            fov_efficiency = min(target_size_deg / native_fov, 1.0)  # How well target fills FOV
            resolution_factor = scope.resolution_mp / 15.0  # Normalize to ~15MP
            aperture_factor = scope.aperture_mm / 60.0  # Normalize to ~60mm
            
            # Weight factors: FOV efficiency most important, then resolution, then aperture
            suitability = (fov_efficiency * 0.5 + resolution_factor * 0.3 + aperture_factor * 0.2)
            
            recommendations.append((scope_id, scope.name, suitability))
        
        # Sort by suitability (descending)
        recommendations.sort(key=lambda x: x[2], reverse=True)
        return recommendations

    def set_scope_filter(self, scope_id: str, use_mosaic: bool = False) -> bool:
        """Set scope filter with optional mosaic mode"""
        scope_manager = get_scope_manager()
        if scope_manager.get_scope(scope_id):
            self.selected_scope = scope_id
            self.use_mosaic_mode = use_mosaic
            return True
        return False

    def clear_scope_filter(self) -> None:
        """Clear scope filter"""
        self.selected_scope = None
        self.use_mosaic_mode = False

    def get_selected_scope_info(self) -> Optional[Dict[str, Any]]:
        """Get information about currently selected scope"""
        if not self.selected_scope:
            return None
        
        scope_manager = get_scope_manager()
        scope = scope_manager.get_scope(self.selected_scope)
        if not scope:
            return None
        
        fov_used = scope.mosaic_fov_deg if (self.use_mosaic_mode and scope.mosaic_fov_deg) else scope.native_fov_deg
        
        return {
            'scope_id': self.selected_scope,
            'name': scope.name,
            'manufacturer': scope.manufacturer,
            'aperture_mm': scope.aperture_mm,
            'focal_length_mm': scope.focal_length_mm,
            'resolution_mp': scope.resolution_mp,
            'fov_deg': fov_used,
            'using_mosaic': self.use_mosaic_mode and scope.has_mosaic_mode,
            'has_mosaic': scope.has_mosaic_mode
        }

    def add_custom_criteria(self, field: str, operator: FilterOperator, value: Any) -> None:
        """Add custom filter criteria"""
        criteria = FilterCriteria(field=field, operator=operator, value=value)
        self.custom_criteria.append(criteria)

    def remove_custom_criteria(self, field: str) -> None:
        """Remove custom filter criteria by field name"""
        self.custom_criteria = [c for c in self.custom_criteria if c.field != field]

    def get_filter_summary(self) -> Dict[str, Any]:
        """Get summary of current filter settings"""
        return {
            'magnitude_range': self.magnitude_range,
            'size_range': self.size_range,
            'object_types': self.object_types,
            'imaging_difficulty': self.imaging_difficulty,
            'moon_avoidance': self.moon_avoidance,
            'altitude_range': self.altitude_range,
            'visibility_hours_min': self.visibility_hours_min,
            'constellation_filter': self.constellation_filter,
            'season_preference': self.season_preference,
            'focal_length_range': self.focal_length_range,
            'pixel_scale_range': self.pixel_scale_range,
            'exposure_time_max': self.exposure_time_max,
            'selected_scope': self.selected_scope,
            'use_mosaic_mode': self.use_mosaic_mode,
            'custom_criteria_count': len(self.custom_criteria),
            'combine_with_and': self.combine_with_and,
            'enabled': self.enabled
        }

    def reset_to_defaults(self) -> None:
        """Reset all filters to default values"""
        self.magnitude_range = (0.0, 15.0)
        self.size_range = (0.0, 180.0)
        self.object_types = ['galaxy', 'nebula', 'cluster']
        self.imaging_difficulty = 'intermediate'
        self.moon_avoidance = True
        self.altitude_range = (30.0, 90.0)
        self.visibility_hours_min = 2.0
        self.constellation_filter = []
        self.season_preference = None
        self.focal_length_range = (200.0, 3000.0)
        self.pixel_scale_range = (0.5, 5.0)
        self.exposure_time_max = 600.0
        self.selected_scope = None
        self.use_mosaic_mode = False
        self.custom_criteria = []
        self.combine_with_and = True
        self.enabled = True

    def save_preset(self, name: str) -> Dict[str, Any]:
        """Save current filter settings as a preset"""
        preset = {
            'name': name,
            'settings': self.get_filter_summary(),
            'custom_criteria': [
                {
                    'field': c.field,
                    'operator': c.operator.value,
                    'value': c.value,
                    'enabled': c.enabled
                }
                for c in self.custom_criteria
            ]
        }
        return preset

    def load_preset(self, preset: Dict[str, Any]) -> None:
        """Load filter settings from a preset"""
        settings = preset.get('settings', {})
        
        # Load basic settings
        for key, value in settings.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Load custom criteria
        self.custom_criteria = []
        for criteria_data in preset.get('custom_criteria', []):
            criteria = FilterCriteria(
                field=criteria_data['field'],
                operator=FilterOperator(criteria_data['operator']),
                value=criteria_data['value'],
                enabled=criteria_data['enabled']
            )
            self.custom_criteria.append(criteria)


class FilterPresetManager:
    """Manage filter presets for quick access"""
    
    def __init__(self):
        self.presets = {}
        self._load_default_presets()

    def _load_default_presets(self) -> None:
        """Load default filter presets"""
        # Beginner preset
        beginner_filter = AdvancedFilter(
            magnitude_range=(0.0, 8.0),
            size_range=(10.0, 180.0),
            object_types=['cluster', 'nebula'],
            imaging_difficulty='beginner',
            moon_avoidance=True,
            altitude_range=(45.0, 90.0),
            visibility_hours_min=3.0
        )
        self.presets['beginner'] = beginner_filter.save_preset('Beginner Friendly')
        
        # Deep Sky preset
        deep_sky_filter = AdvancedFilter(
            magnitude_range=(8.0, 15.0),
            size_range=(2.0, 60.0),
            object_types=['galaxy', 'nebula', 'planetary_nebula'],
            imaging_difficulty='advanced',
            moon_avoidance=True,
            altitude_range=(30.0, 90.0),
            visibility_hours_min=2.0,
            exposure_time_max=900.0
        )
        self.presets['deep_sky'] = deep_sky_filter.save_preset('Deep Sky Objects')
        
        # Wide Field preset
        wide_field_filter = AdvancedFilter(
            magnitude_range=(0.0, 10.0),
            size_range=(30.0, 180.0),
            object_types=['nebula', 'cluster'],
            imaging_difficulty='intermediate',
            focal_length_range=(200.0, 800.0),
            pixel_scale_range=(2.0, 5.0)
        )
        self.presets['wide_field'] = wide_field_filter.save_preset('Wide Field Targets')

    def get_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """Get preset by name"""
        return self.presets.get(name)

    def save_preset(self, name: str, filter_obj: AdvancedFilter) -> None:
        """Save a new preset"""
        self.presets[name] = filter_obj.save_preset(name)

    def delete_preset(self, name: str) -> bool:
        """Delete a preset"""
        if name in self.presets:
            del self.presets[name]
            return True
        return False

    def list_presets(self) -> List[str]:
        """List all available presets"""
        return list(self.presets.keys())


# Example usage and testing
if __name__ == "__main__":
    # Create advanced filter
    filter_obj = AdvancedFilter()
    
    # Example target data
    sample_targets = [
        {
            'name': 'M31 Andromeda Galaxy',
            'magnitude': 3.4,
            'size': 190.0,
            'object_type': 'galaxy',
            'constellation': 'Andromeda',
            'max_altitude': 75.0,
            'visibility_hours': 6.0,
            'moon_separation_deg': 45.0,
            'recommended_focal_length': 600.0,
            'surface_brightness': 13.5
        },
        {
            'name': 'M42 Orion Nebula',
            'magnitude': 4.0,
            'size': 85.0,
            'object_type': 'nebula',
            'constellation': 'Orion',
            'max_altitude': 65.0,
            'visibility_hours': 4.0,
            'moon_separation_deg': 60.0,
            'recommended_focal_length': 1000.0,
            'surface_brightness': 17.0
        },
        {
            'name': 'NGC 7293 Helix Nebula',
            'magnitude': 7.3,
            'size': 16.0,
            'object_type': 'planetary_nebula',
            'constellation': 'Aquarius',
            'max_altitude': 45.0,
            'visibility_hours': 3.0,
            'moon_separation_deg': 25.0,
            'recommended_focal_length': 1500.0,
            'surface_brightness': 20.5
        }
    ]
    
    # Test filtering
    print("Testing Advanced Filter System")
    print("=" * 40)
    
    # Apply default filters
    filtered = filter_obj.apply_filters(sample_targets)
    print(f"Default filters: {len(filtered)}/{len(sample_targets)} targets passed")
    
    # Test moon avoidance
    filter_obj.moon_avoidance = True
    filtered = filter_obj.apply_filters(sample_targets)
    print(f"With moon avoidance: {len(filtered)}/{len(sample_targets)} targets passed")
    
    # Test difficulty filtering
    filter_obj.imaging_difficulty = 'beginner'
    filtered = filter_obj.apply_filters(sample_targets)
    print(f"Beginner difficulty: {len(filtered)}/{len(sample_targets)} targets passed")
    
    # Test custom criteria
    filter_obj.add_custom_criteria('constellation', FilterOperator.EQUALS, 'Orion')
    filtered = filter_obj.apply_filters(sample_targets)
    print(f"Orion constellation only: {len(filtered)}/{len(sample_targets)} targets passed")
    
    # Test preset manager
    preset_manager = FilterPresetManager()
    print(f"\nAvailable presets: {preset_manager.list_presets()}")
    
    print("\nAdvanced Filter System implementation complete!")