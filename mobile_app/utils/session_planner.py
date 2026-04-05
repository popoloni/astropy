"""
Advanced Session Planning and Management System
Comprehensive observation session planning with optimization and export
"""

import json
import os
from datetime import datetime, timedelta, time
from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import math
import tempfile

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class SessionPriority(Enum):
    """Session priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SessionType(Enum):
    """Types of observing sessions"""
    VISUAL = "visual"
    IMAGING = "imaging"
    MIXED = "mixed"
    SURVEY = "survey"
    SPECIFIC_TARGET = "specific_target"


class WeatherCondition(Enum):
    """Weather condition categories"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNUSABLE = "unusable"


class OptimizationStrategy(Enum):
    """Session optimization strategies"""
    MAXIMIZE_TARGETS = "maximize_targets"
    MAXIMIZE_QUALITY = "maximize_quality"
    BALANCED = "balanced"
    TIME_EFFICIENT = "time_efficient"
    PRIORITY_BASED = "priority_based"


@dataclass
class SessionTarget:
    """Individual target in a session"""
    name: str
    object_type: str
    ra: float
    dec: float
    magnitude: float
    size: float
    constellation: str
    priority: SessionPriority
    estimated_time: int  # minutes
    optimal_start_time: Optional[datetime] = None
    optimal_end_time: Optional[datetime] = None
    altitude_at_start: float = 0.0
    altitude_at_end: float = 0.0
    notes: str = ""
    equipment_notes: str = ""
    completed: bool = False
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    success_rating: Optional[int] = None  # 1-5 scale
    weather_impact: Optional[str] = None


@dataclass
class SessionConditions:
    """Observing conditions for a session"""
    date: datetime
    location_lat: float
    location_lon: float
    location_name: str
    moon_phase: float  # 0-1
    moon_illumination: float  # 0-100%
    astronomical_twilight_start: datetime
    astronomical_twilight_end: datetime
    weather_forecast: WeatherCondition
    seeing_forecast: float  # arcseconds
    transparency_forecast: float  # 0-10 scale
    wind_speed: float  # km/h
    temperature: float  # Celsius
    humidity: float  # percentage


@dataclass
class SessionPlan:
    """Complete observation session plan"""
    session_id: str
    name: str
    date: datetime
    duration: int  # minutes
    session_type: SessionType
    conditions: SessionConditions
    targets: List[SessionTarget]
    optimization_strategy: OptimizationStrategy
    created_at: datetime
    modified_at: datetime
    notes: str = ""
    equipment_list: List[str] = field(default_factory=list)
    backup_targets: List[SessionTarget] = field(default_factory=list)
    session_statistics: Dict[str, Any] = field(default_factory=dict)


class SessionOptimizer:
    """Optimize target scheduling within a session"""
    
    def __init__(self):
        self.min_altitude = 30.0  # degrees
        self.max_airmass = 2.0
        self.setup_time = 15  # minutes
        self.target_change_time = 5  # minutes
    
    def optimize_session(self, targets: List[SessionTarget], conditions: SessionConditions, 
                        strategy: OptimizationStrategy) -> List[SessionTarget]:
        """Optimize target order and timing"""
        
        # Calculate visibility windows for all targets
        for target in targets:
            self._calculate_visibility_window(target, conditions)
        
        # Apply optimization strategy
        if strategy == OptimizationStrategy.MAXIMIZE_TARGETS:
            return self._maximize_targets_strategy(targets, conditions)
        elif strategy == OptimizationStrategy.MAXIMIZE_QUALITY:
            return self._maximize_quality_strategy(targets, conditions)
        elif strategy == OptimizationStrategy.PRIORITY_BASED:
            return self._priority_based_strategy(targets, conditions)
        elif strategy == OptimizationStrategy.TIME_EFFICIENT:
            return self._time_efficient_strategy(targets, conditions)
        else:  # BALANCED
            return self._balanced_strategy(targets, conditions)
    
    def _calculate_visibility_window(self, target: SessionTarget, conditions: SessionConditions):
        """Calculate optimal visibility window for target"""
        # Simplified calculation - in real implementation would use proper astronomical calculations
        session_start = conditions.astronomical_twilight_end
        session_end = conditions.astronomical_twilight_start + timedelta(days=1)
        
        # For demonstration, use simplified altitude calculation
        # Real implementation would use astropy coordinates and observer location
        optimal_time = session_start + timedelta(hours=4)  # Simplified
        
        target.optimal_start_time = optimal_time - timedelta(minutes=target.estimated_time//2)
        target.optimal_end_time = optimal_time + timedelta(minutes=target.estimated_time//2)
        target.altitude_at_start = 45.0  # Simplified
        target.altitude_at_end = 50.0   # Simplified
    
    def _maximize_targets_strategy(self, targets: List[SessionTarget], 
                                 conditions: SessionConditions) -> List[SessionTarget]:
        """Strategy to observe maximum number of targets"""
        # Sort by estimated time (shortest first) and priority
        priority_order = {
            SessionPriority.CRITICAL: 4,
            SessionPriority.HIGH: 3,
            SessionPriority.MEDIUM: 2,
            SessionPriority.LOW: 1
        }
        sorted_targets = sorted(targets, key=lambda t: (t.estimated_time, -priority_order.get(t.priority, 2)))
        return self._schedule_targets(sorted_targets, conditions)
    
    def _maximize_quality_strategy(self, targets: List[SessionTarget], 
                                 conditions: SessionConditions) -> List[SessionTarget]:
        """Strategy to maximize observation quality"""
        # Sort by altitude and seeing conditions
        sorted_targets = sorted(targets, key=lambda t: -t.altitude_at_start)
        return self._schedule_targets(sorted_targets, conditions)
    
    def _priority_based_strategy(self, targets: List[SessionTarget], 
                               conditions: SessionConditions) -> List[SessionTarget]:
        """Strategy based on target priorities"""
        priority_order = {
            SessionPriority.CRITICAL: 4,
            SessionPriority.HIGH: 3,
            SessionPriority.MEDIUM: 2,
            SessionPriority.LOW: 1
        }
        sorted_targets = sorted(targets, key=lambda t: priority_order.get(t.priority, 2), reverse=True)
        return self._schedule_targets(sorted_targets, conditions)
    
    def _time_efficient_strategy(self, targets: List[SessionTarget], 
                               conditions: SessionConditions) -> List[SessionTarget]:
        """Strategy to minimize setup and transition times"""
        # Group by constellation/region and sort by RA
        targets_by_region = {}
        for target in targets:
            region = target.constellation
            if region not in targets_by_region:
                targets_by_region[region] = []
            targets_by_region[region].append(target)
        
        # Sort within each region by RA
        sorted_targets = []
        for region_targets in targets_by_region.values():
            region_targets.sort(key=lambda t: t.ra)
            sorted_targets.extend(region_targets)
        
        return self._schedule_targets(sorted_targets, conditions)
    
    def _balanced_strategy(self, targets: List[SessionTarget], 
                         conditions: SessionConditions) -> List[SessionTarget]:
        """Balanced strategy considering multiple factors"""
        # Score targets based on multiple criteria
        scored_targets = []
        for target in targets:
            score = self._calculate_target_score(target, conditions)
            scored_targets.append((score, target))
        
        # Sort by score (highest first)
        scored_targets.sort(key=lambda x: -x[0])
        sorted_targets = [target for _, target in scored_targets]
        
        return self._schedule_targets(sorted_targets, conditions)
    
    def _calculate_target_score(self, target: SessionTarget, conditions: SessionConditions) -> float:
        """Calculate composite score for target"""
        score = 0.0
        
        # Priority weight
        priority_weights = {
            SessionPriority.CRITICAL: 10.0,
            SessionPriority.HIGH: 7.5,
            SessionPriority.MEDIUM: 5.0,
            SessionPriority.LOW: 2.5
        }
        score += priority_weights[target.priority]
        
        # Altitude bonus
        if target.altitude_at_start > 60:
            score += 5.0
        elif target.altitude_at_start > 45:
            score += 3.0
        elif target.altitude_at_start > 30:
            score += 1.0
        
        # Time efficiency bonus (shorter observations get slight bonus)
        if target.estimated_time < 30:
            score += 2.0
        elif target.estimated_time < 60:
            score += 1.0
        
        return score
    
    def _schedule_targets(self, targets: List[SessionTarget], 
                         conditions: SessionConditions) -> List[SessionTarget]:
        """Schedule targets with proper timing"""
        scheduled = []
        current_time = conditions.astronomical_twilight_end + timedelta(minutes=self.setup_time)
        session_end = conditions.astronomical_twilight_start + timedelta(days=1)
        
        for target in targets:
            # Check if target fits in remaining time
            required_time = target.estimated_time + self.target_change_time
            if current_time + timedelta(minutes=required_time) <= session_end:
                target.optimal_start_time = current_time
                target.optimal_end_time = current_time + timedelta(minutes=target.estimated_time)
                scheduled.append(target)
                current_time = target.optimal_end_time + timedelta(minutes=self.target_change_time)
        
        return scheduled


class SessionManager:
    """Manage observation sessions"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.expanduser("~"), ".astroscope", "sessions")
        self.optimizer = SessionOptimizer()
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for complex objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, (SessionType, OptimizationStrategy, SessionPriority, WeatherCondition)):
            return obj.value
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    def _session_to_dict(self, session: SessionPlan) -> Dict:
        """Convert session to dictionary for JSON serialization"""
        session_dict = {
            'session_id': session.session_id,
            'name': session.name,
            'date': session.date.isoformat(),
            'duration': session.duration,
            'session_type': session.session_type.value,
            'optimization_strategy': session.optimization_strategy.value,
            'created_at': session.created_at.isoformat(),
            'modified_at': session.modified_at.isoformat(),
            'notes': session.notes,
            'equipment_list': session.equipment_list,
            'session_statistics': session.session_statistics,
            'conditions': self._conditions_to_dict(session.conditions),
            'targets': [self._target_to_dict(t) for t in session.targets],
            'backup_targets': [self._target_to_dict(t) for t in session.backup_targets]
        }
        return session_dict
    
    def _conditions_to_dict(self, conditions: SessionConditions) -> Dict:
        """Convert conditions to dictionary"""
        return {
            'date': conditions.date.isoformat(),
            'location_lat': conditions.location_lat,
            'location_lon': conditions.location_lon,
            'location_name': conditions.location_name,
            'moon_phase': conditions.moon_phase,
            'moon_illumination': conditions.moon_illumination,
            'astronomical_twilight_start': conditions.astronomical_twilight_start.isoformat(),
            'astronomical_twilight_end': conditions.astronomical_twilight_end.isoformat(),
            'weather_forecast': conditions.weather_forecast.value,
            'seeing_forecast': conditions.seeing_forecast,
            'transparency_forecast': conditions.transparency_forecast,
            'wind_speed': conditions.wind_speed,
            'temperature': conditions.temperature,
            'humidity': conditions.humidity
        }
    
    def _target_to_dict(self, target: SessionTarget) -> Dict:
        """Convert target to dictionary"""
        return {
            'name': target.name,
            'object_type': target.object_type,
            'ra': target.ra,
            'dec': target.dec,
            'magnitude': target.magnitude,
            'size': target.size,
            'constellation': target.constellation,
            'priority': target.priority.value,
            'estimated_time': target.estimated_time,
            'optimal_start_time': target.optimal_start_time.isoformat() if target.optimal_start_time else None,
            'optimal_end_time': target.optimal_end_time.isoformat() if target.optimal_end_time else None,
            'altitude_at_start': target.altitude_at_start,
            'altitude_at_end': target.altitude_at_end,
            'notes': target.notes,
            'equipment_notes': target.equipment_notes,
            'completed': target.completed,
            'actual_start_time': target.actual_start_time.isoformat() if target.actual_start_time else None,
            'actual_end_time': target.actual_end_time.isoformat() if target.actual_end_time else None,
            'success_rating': target.success_rating,
            'weather_impact': target.weather_impact
        }
    
    def create_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def save_session(self, session: SessionPlan) -> bool:
        """Save session to disk"""
        try:
            session.modified_at = datetime.now()
            session_file = os.path.join(self.data_dir, f"{session.session_id}.json")
            
            # Convert to dict for JSON serialization
            session_dict = self._session_to_dict(session)
            
            with open(session_file, 'w') as f:
                json.dump(session_dict, f, indent=2, default=self._json_serializer)
            
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[SessionPlan]:
        """Load session from disk"""
        try:
            session_file = os.path.join(self.data_dir, f"{session_id}.json")
            if not os.path.exists(session_file):
                return None
            
            with open(session_file, 'r') as f:
                session_dict = json.load(f)
            
            # Reconstruct objects
            return self._dict_to_session_plan(session_dict)
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all saved sessions"""
        sessions = []
        try:
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    session_id = filename[:-5]  # Remove .json
                    session = self.load_session(session_id)
                    if session:
                        sessions.append({
                            'session_id': session.session_id,
                            'name': session.name,
                            'date': session.date,
                            'duration': session.duration,
                            'target_count': len(session.targets),
                            'session_type': session.session_type.value,
                            'created_at': session.created_at
                        })
        except Exception as e:
            print(f"Error listing sessions: {e}")
        
        return sorted(sessions, key=lambda x: x['date'], reverse=True)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            session_file = os.path.join(self.data_dir, f"{session_id}.json")
            if os.path.exists(session_file):
                os.remove(session_file)
                return True
            return False
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    

    
    def _dict_to_session_plan(self, session_dict: Dict) -> SessionPlan:
        """Convert dictionary to SessionPlan object"""
        # Convert conditions
        conditions_dict = session_dict['conditions']
        conditions = self._dict_to_conditions(conditions_dict)
        
        # Convert targets
        targets = []
        for target_dict in session_dict['targets']:
            targets.append(self._dict_to_target(target_dict))
        
        # Convert backup targets
        backup_targets = []
        for target_dict in session_dict.get('backup_targets', []):
            backup_targets.append(self._dict_to_target(target_dict))
        
        # Create session plan
        session_type = SessionType(session_dict['session_type'])
        optimization_strategy = OptimizationStrategy(session_dict['optimization_strategy'])
        
        return SessionPlan(
            session_id=session_dict['session_id'],
            name=session_dict['name'],
            date=datetime.fromisoformat(session_dict['date']),
            duration=session_dict['duration'],
            session_type=session_type,
            conditions=conditions,
            targets=targets,
            optimization_strategy=optimization_strategy,
            created_at=datetime.fromisoformat(session_dict['created_at']),
            modified_at=datetime.fromisoformat(session_dict['modified_at']),
            notes=session_dict.get('notes', ''),
            equipment_list=session_dict.get('equipment_list', []),
            backup_targets=backup_targets,
            session_statistics=session_dict.get('session_statistics', {})
        )
    
    def _dict_to_conditions(self, conditions_dict: Dict) -> SessionConditions:
        """Convert dictionary to SessionConditions object"""
        return SessionConditions(
            date=datetime.fromisoformat(conditions_dict['date']),
            location_lat=conditions_dict['location_lat'],
            location_lon=conditions_dict['location_lon'],
            location_name=conditions_dict['location_name'],
            moon_phase=conditions_dict['moon_phase'],
            moon_illumination=conditions_dict['moon_illumination'],
            astronomical_twilight_start=datetime.fromisoformat(conditions_dict['astronomical_twilight_start']),
            astronomical_twilight_end=datetime.fromisoformat(conditions_dict['astronomical_twilight_end']),
            weather_forecast=WeatherCondition(conditions_dict['weather_forecast']),
            seeing_forecast=conditions_dict['seeing_forecast'],
            transparency_forecast=conditions_dict['transparency_forecast'],
            wind_speed=conditions_dict['wind_speed'],
            temperature=conditions_dict['temperature'],
            humidity=conditions_dict['humidity']
        )
    
    def _dict_to_target(self, target_dict: Dict) -> SessionTarget:
        """Convert dictionary to SessionTarget object"""
        return SessionTarget(
            name=target_dict['name'],
            object_type=target_dict['object_type'],
            ra=target_dict['ra'],
            dec=target_dict['dec'],
            magnitude=target_dict['magnitude'],
            size=target_dict['size'],
            constellation=target_dict['constellation'],
            priority=SessionPriority(target_dict['priority']),
            estimated_time=target_dict['estimated_time'],
            optimal_start_time=datetime.fromisoformat(target_dict['optimal_start_time']) if target_dict['optimal_start_time'] else None,
            optimal_end_time=datetime.fromisoformat(target_dict['optimal_end_time']) if target_dict['optimal_end_time'] else None,
            altitude_at_start=target_dict['altitude_at_start'],
            altitude_at_end=target_dict['altitude_at_end'],
            notes=target_dict['notes'],
            equipment_notes=target_dict['equipment_notes'],
            completed=target_dict['completed'],
            actual_start_time=datetime.fromisoformat(target_dict['actual_start_time']) if target_dict['actual_start_time'] else None,
            actual_end_time=datetime.fromisoformat(target_dict['actual_end_time']) if target_dict['actual_end_time'] else None,
            success_rating=target_dict['success_rating'],
            weather_impact=target_dict['weather_impact']
        )


class SessionPlanner:
    """Advanced observation session planning"""
    
    def __init__(self, session_manager: SessionManager = None):
        self.session_manager = session_manager or SessionManager()
        self.optimizer = SessionOptimizer()
    
    def create_session(self, date: datetime, duration: int, priorities: List[str],
                      targets: List[Dict], location: Dict, session_type: SessionType = SessionType.MIXED,
                      optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED) -> SessionPlan:
        """Generate optimized observation session"""
        
        # Create session ID and basic info
        session_id = self.session_manager.create_session_id()
        session_name = f"Observing Session {date.strftime('%Y-%m-%d')}"
        
        # Create session conditions
        conditions = self._create_session_conditions(date, location)
        
        # Convert targets to SessionTarget objects
        session_targets = self._convert_targets(targets, priorities)
        
        # Optimize target scheduling
        optimized_targets = self.optimizer.optimize_session(
            session_targets, conditions, optimization_strategy
        )
        
        # Create backup targets (targets that didn't fit in main schedule)
        backup_targets = [t for t in session_targets if t not in optimized_targets]
        
        # Calculate session statistics
        statistics = self._calculate_session_statistics(optimized_targets, conditions)
        
        # Create session plan
        session = SessionPlan(
            session_id=session_id,
            name=session_name,
            date=date,
            duration=duration,
            session_type=session_type,
            conditions=conditions,
            targets=optimized_targets,
            optimization_strategy=optimization_strategy,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            backup_targets=backup_targets,
            session_statistics=statistics
        )
        
        return session
    
    def _create_session_conditions(self, date: datetime, location: Dict) -> SessionConditions:
        """Create session conditions from date and location"""
        # Simplified conditions - real implementation would fetch weather data
        return SessionConditions(
            date=date,
            location_lat=location.get('latitude', 0.0),
            location_lon=location.get('longitude', 0.0),
            location_name=location.get('name', 'Unknown'),
            moon_phase=0.3,  # Simplified
            moon_illumination=30.0,
            astronomical_twilight_start=date.replace(hour=5, minute=30),
            astronomical_twilight_end=date.replace(hour=20, minute=30),
            weather_forecast=WeatherCondition.GOOD,
            seeing_forecast=2.5,
            transparency_forecast=7.0,
            wind_speed=15.0,
            temperature=10.0,
            humidity=65.0
        )
    
    def _convert_targets(self, targets: List[Dict], priorities: List[str]) -> List[SessionTarget]:
        """Convert target dictionaries to SessionTarget objects"""
        session_targets = []
        
        for i, target in enumerate(targets):
            # Determine priority
            if i < len(priorities):
                priority_str = priorities[i].lower()
                priority = SessionPriority(priority_str) if priority_str in [p.value for p in SessionPriority] else SessionPriority.MEDIUM
            else:
                priority = SessionPriority.MEDIUM
            
            # Estimate observation time based on object type and magnitude
            estimated_time = self._estimate_observation_time(target)
            
            session_target = SessionTarget(
                name=target.get('name', 'Unknown'),
                object_type=target.get('object_type', 'Unknown'),
                ra=target.get('ra', 0.0),
                dec=target.get('dec', 0.0),
                magnitude=target.get('magnitude', 10.0),
                size=target.get('size', 5.0),
                constellation=target.get('constellation', 'Unknown'),
                priority=priority,
                estimated_time=estimated_time
            )
            
            session_targets.append(session_target)
        
        return session_targets
    
    def _estimate_observation_time(self, target: Dict) -> int:
        """Estimate observation time for target"""
        base_time = 30  # minutes
        
        # Adjust based on object type
        obj_type = target.get('object_type', '').lower()
        if 'galaxy' in obj_type:
            base_time = 45
        elif 'nebula' in obj_type:
            base_time = 60
        elif 'cluster' in obj_type:
            base_time = 20
        elif 'planetary' in obj_type:
            base_time = 30
        
        # Adjust based on magnitude (fainter = more time)
        magnitude = target.get('magnitude', 10.0)
        if magnitude > 12:
            base_time *= 1.5
        elif magnitude > 10:
            base_time *= 1.2
        elif magnitude < 6:
            base_time *= 0.8
        
        return int(base_time)
    
    def _calculate_session_statistics(self, targets: List[SessionTarget], 
                                    conditions: SessionConditions) -> Dict[str, Any]:
        """Calculate session statistics"""
        if not targets:
            return {}
        
        total_time = sum(t.estimated_time for t in targets)
        target_types = {}
        priority_counts = {}
        
        for target in targets:
            # Count by type
            obj_type = target.object_type
            target_types[obj_type] = target_types.get(obj_type, 0) + 1
            
            # Count by priority
            priority = target.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            'total_targets': len(targets),
            'total_observation_time': total_time,
            'average_time_per_target': total_time / len(targets),
            'target_types': target_types,
            'priority_distribution': priority_counts,
            'session_efficiency': (total_time / conditions.duration) * 100 if hasattr(conditions, 'duration') else 0
        }
    
    def export_session(self, session: SessionPlan, format: str = 'pdf', 
                      output_path: str = None) -> str:
        """Export session plan for field use"""
        
        if format.lower() == 'pdf':
            return self._export_pdf(session, output_path)
        elif format.lower() == 'json':
            return self._export_json(session, output_path)
        elif format.lower() == 'txt':
            return self._export_text(session, output_path)
        elif format.lower() == 'html':
            return self._export_html(session, output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_pdf(self, session: SessionPlan, output_path: str = None) -> str:
        """Export session as PDF"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF export")
        
        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), f"{session.session_id}.pdf")
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph(f"Observation Session Plan", title_style))
        story.append(Paragraph(f"{session.name}", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Session Info
        session_info = [
            ['Date:', session.date.strftime('%Y-%m-%d')],
            ['Duration:', f"{session.duration} minutes"],
            ['Session Type:', session.session_type.value.title()],
            ['Location:', session.conditions.location_name],
            ['Optimization:', session.optimization_strategy.value.replace('_', ' ').title()],
            ['Total Targets:', str(len(session.targets))],
        ]
        
        info_table = Table(session_info, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Conditions
        story.append(Paragraph("Observing Conditions", styles['Heading3']))
        conditions_info = [
            ['Moon Phase:', f"{session.conditions.moon_illumination:.0f}% illuminated"],
            ['Weather:', session.conditions.weather_forecast.value.title()],
            ['Seeing:', f"{session.conditions.seeing_forecast:.1f} arcsec"],
            ['Transparency:', f"{session.conditions.transparency_forecast:.0f}/10"],
            ['Temperature:', f"{session.conditions.temperature:.0f}°C"],
            ['Wind:', f"{session.conditions.wind_speed:.0f} km/h"],
        ]
        
        conditions_table = Table(conditions_info, colWidths=[2*inch, 3*inch])
        conditions_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(conditions_table)
        story.append(Spacer(1, 20))
        
        # Target Schedule
        story.append(Paragraph("Target Schedule", styles['Heading3']))
        
        target_data = [['Time', 'Target', 'Type', 'Mag', 'Size', 'Priority', 'Notes']]
        
        for target in session.targets:
            start_time = target.optimal_start_time.strftime('%H:%M') if target.optimal_start_time else 'TBD'
            target_data.append([
                start_time,
                target.name,
                target.object_type,
                f"{target.magnitude:.1f}",
                f"{target.size:.1f}'",
                target.priority.value.title(),
                target.notes[:20] + '...' if len(target.notes) > 20 else target.notes
            ])
        
        target_table = Table(target_data, colWidths=[0.8*inch, 2*inch, 1*inch, 0.6*inch, 0.6*inch, 0.8*inch, 1.2*inch])
        target_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(target_table)
        
        # Backup Targets
        if session.backup_targets:
            story.append(Spacer(1, 20))
            story.append(Paragraph("Backup Targets", styles['Heading3']))
            
            backup_data = [['Target', 'Type', 'Mag', 'Priority']]
            for target in session.backup_targets[:10]:  # Limit to 10 backup targets
                backup_data.append([
                    target.name,
                    target.object_type,
                    f"{target.magnitude:.1f}",
                    target.priority.value.title()
                ])
            
            backup_table = Table(backup_data, colWidths=[2.5*inch, 1.5*inch, 0.8*inch, 1*inch])
            backup_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(backup_table)
        
        # Equipment List
        if session.equipment_list:
            story.append(Spacer(1, 20))
            story.append(Paragraph("Equipment Checklist", styles['Heading3']))
            for item in session.equipment_list:
                story.append(Paragraph(f"☐ {item}", styles['Normal']))
        
        # Notes
        if session.notes:
            story.append(Spacer(1, 20))
            story.append(Paragraph("Session Notes", styles['Heading3']))
            story.append(Paragraph(session.notes, styles['Normal']))
        
        doc.build(story)
        return output_path
    
    def _export_json(self, session: SessionPlan, output_path: str = None) -> str:
        """Export session as JSON"""
        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), f"{session.session_id}.json")
        
        # Use session manager's save functionality
        temp_session_file = os.path.join(self.session_manager.data_dir, f"{session.session_id}.json")
        self.session_manager.save_session(session)
        
        # Copy to desired output path if different
        if output_path != temp_session_file:
            import shutil
            shutil.copy2(temp_session_file, output_path)
        
        return output_path
    
    def _export_text(self, session: SessionPlan, output_path: str = None) -> str:
        """Export session as plain text"""
        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), f"{session.session_id}.txt")
        
        with open(output_path, 'w') as f:
            f.write(f"OBSERVATION SESSION PLAN\n")
            f.write(f"=" * 50 + "\n\n")
            
            f.write(f"Session: {session.name}\n")
            f.write(f"Date: {session.date.strftime('%Y-%m-%d')}\n")
            f.write(f"Duration: {session.duration} minutes\n")
            f.write(f"Type: {session.session_type.value.title()}\n")
            f.write(f"Location: {session.conditions.location_name}\n")
            f.write(f"Optimization: {session.optimization_strategy.value.replace('_', ' ').title()}\n\n")
            
            f.write(f"OBSERVING CONDITIONS\n")
            f.write(f"-" * 20 + "\n")
            f.write(f"Moon: {session.conditions.moon_illumination:.0f}% illuminated\n")
            f.write(f"Weather: {session.conditions.weather_forecast.value.title()}\n")
            f.write(f"Seeing: {session.conditions.seeing_forecast:.1f} arcsec\n")
            f.write(f"Transparency: {session.conditions.transparency_forecast:.0f}/10\n")
            f.write(f"Temperature: {session.conditions.temperature:.0f}°C\n")
            f.write(f"Wind: {session.conditions.wind_speed:.0f} km/h\n\n")
            
            f.write(f"TARGET SCHEDULE ({len(session.targets)} targets)\n")
            f.write(f"-" * 30 + "\n")
            for i, target in enumerate(session.targets, 1):
                start_time = target.optimal_start_time.strftime('%H:%M') if target.optimal_start_time else 'TBD'
                f.write(f"{i:2d}. {start_time} - {target.name}\n")
                f.write(f"     Type: {target.object_type}, Mag: {target.magnitude:.1f}, Size: {target.size:.1f}'\n")
                f.write(f"     Priority: {target.priority.value.title()}, Time: {target.estimated_time} min\n")
                if target.notes:
                    f.write(f"     Notes: {target.notes}\n")
                f.write("\n")
            
            if session.backup_targets:
                f.write(f"BACKUP TARGETS ({len(session.backup_targets)} targets)\n")
                f.write(f"-" * 20 + "\n")
                for target in session.backup_targets:
                    f.write(f"• {target.name} ({target.object_type}, mag {target.magnitude:.1f})\n")
                f.write("\n")
            
            if session.equipment_list:
                f.write(f"EQUIPMENT CHECKLIST\n")
                f.write(f"-" * 20 + "\n")
                for item in session.equipment_list:
                    f.write(f"☐ {item}\n")
                f.write("\n")
            
            if session.notes:
                f.write(f"SESSION NOTES\n")
                f.write(f"-" * 15 + "\n")
                f.write(f"{session.notes}\n")
        
        return output_path
    
    def _export_html(self, session: SessionPlan, output_path: str = None) -> str:
        """Export session as HTML"""
        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), f"{session.session_id}.html")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{session.name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .section {{ margin-bottom: 25px; }}
        .section h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .priority-high {{ background-color: #ffebee; }}
        .priority-medium {{ background-color: #fff3e0; }}
        .priority-low {{ background-color: #e8f5e8; }}
        .priority-critical {{ background-color: #ffcdd2; }}
        .equipment {{ list-style-type: none; }}
        .equipment li:before {{ content: "☐ "; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Observation Session Plan</h1>
        <h2>{session.name}</h2>
    </div>
    
    <div class="section">
        <h2>Session Information</h2>
        <table>
            <tr><td><strong>Date</strong></td><td>{session.date.strftime('%Y-%m-%d')}</td></tr>
            <tr><td><strong>Duration</strong></td><td>{session.duration} minutes</td></tr>
            <tr><td><strong>Session Type</strong></td><td>{session.session_type.value.title()}</td></tr>
            <tr><td><strong>Location</strong></td><td>{session.conditions.location_name}</td></tr>
            <tr><td><strong>Optimization</strong></td><td>{session.optimization_strategy.value.replace('_', ' ').title()}</td></tr>
            <tr><td><strong>Total Targets</strong></td><td>{len(session.targets)}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Observing Conditions</h2>
        <table>
            <tr><td><strong>Moon Phase</strong></td><td>{session.conditions.moon_illumination:.0f}% illuminated</td></tr>
            <tr><td><strong>Weather</strong></td><td>{session.conditions.weather_forecast.value.title()}</td></tr>
            <tr><td><strong>Seeing</strong></td><td>{session.conditions.seeing_forecast:.1f} arcsec</td></tr>
            <tr><td><strong>Transparency</strong></td><td>{session.conditions.transparency_forecast:.0f}/10</td></tr>
            <tr><td><strong>Temperature</strong></td><td>{session.conditions.temperature:.0f}°C</td></tr>
            <tr><td><strong>Wind</strong></td><td>{session.conditions.wind_speed:.0f} km/h</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Target Schedule</h2>
        <table>
            <tr>
                <th>Time</th>
                <th>Target</th>
                <th>Type</th>
                <th>Magnitude</th>
                <th>Size</th>
                <th>Priority</th>
                <th>Duration</th>
                <th>Notes</th>
            </tr>
        """
        
        for target in session.targets:
            start_time = target.optimal_start_time.strftime('%H:%M') if target.optimal_start_time else 'TBD'
            priority_class = f"priority-{target.priority.value}"
            html_content += f"""
            <tr class="{priority_class}">
                <td>{start_time}</td>
                <td>{target.name}</td>
                <td>{target.object_type}</td>
                <td>{target.magnitude:.1f}</td>
                <td>{target.size:.1f}'</td>
                <td>{target.priority.value.title()}</td>
                <td>{target.estimated_time} min</td>
                <td>{target.notes}</td>
            </tr>
            """
        
        html_content += """
        </table>
    </div>
        """
        
        if session.backup_targets:
            html_content += """
    <div class="section">
        <h2>Backup Targets</h2>
        <table>
            <tr>
                <th>Target</th>
                <th>Type</th>
                <th>Magnitude</th>
                <th>Priority</th>
            </tr>
            """
            
            for target in session.backup_targets:
                priority_class = f"priority-{target.priority.value}"
                html_content += f"""
            <tr class="{priority_class}">
                <td>{target.name}</td>
                <td>{target.object_type}</td>
                <td>{target.magnitude:.1f}</td>
                <td>{target.priority.value.title()}</td>
            </tr>
                """
            
            html_content += """
        </table>
    </div>
            """
        
        if session.equipment_list:
            html_content += """
    <div class="section">
        <h2>Equipment Checklist</h2>
        <ul class="equipment">
            """
            for item in session.equipment_list:
                html_content += f"<li>{item}</li>"
            html_content += """
        </ul>
    </div>
            """
        
        if session.notes:
            html_content += f"""
    <div class="section">
        <h2>Session Notes</h2>
        <p>{session.notes}</p>
    </div>
            """
        
        html_content += """
</body>
</html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        return output_path


# Example usage and testing
if __name__ == "__main__":
    # Create sample data
    sample_targets = [
        {
            'name': 'M31 Andromeda Galaxy',
            'object_type': 'galaxy',
            'ra': 10.68,
            'dec': 41.27,
            'magnitude': 3.4,
            'size': 190.0,
            'constellation': 'Andromeda'
        },
        {
            'name': 'M42 Orion Nebula',
            'object_type': 'nebula',
            'ra': 83.82,
            'dec': -5.39,
            'magnitude': 4.0,
            'size': 85.0,
            'constellation': 'Orion'
        },
        {
            'name': 'M45 Pleiades',
            'object_type': 'cluster',
            'ra': 56.75,
            'dec': 24.12,
            'magnitude': 1.6,
            'size': 110.0,
            'constellation': 'Taurus'
        }
    ]
    
    sample_location = {
        'latitude': 40.7128,
        'longitude': -74.0060,
        'name': 'New York, NY'
    }
    
    # Create session planner
    planner = SessionPlanner()
    
    # Create session
    session_date = datetime(2024, 3, 15, 20, 0)
    priorities = ['high', 'medium', 'low']
    
    session = planner.create_session(
        date=session_date,
        duration=240,  # 4 hours
        priorities=priorities,
        targets=sample_targets,
        location=sample_location,
        session_type=SessionType.MIXED,
        optimization_strategy=OptimizationStrategy.BALANCED
    )
    
    # Add equipment list
    session.equipment_list = [
        'Telescope',
        'Mount',
        'Eyepieces (25mm, 10mm, 6mm)',
        'Red flashlight',
        'Star charts',
        'Notebook and pen',
        'Warm clothing',
        'Thermos with hot drink'
    ]
    
    session.notes = "Clear night expected. Focus on galaxies early in the session when they're highest."
    
    # Save session
    planner.session_manager.save_session(session)
    print(f"Session saved: {session.session_id}")
    
    # Export in different formats
    try:
        pdf_path = planner.export_session(session, 'pdf')
        print(f"PDF exported: {pdf_path}")
    except ImportError:
        print("PDF export requires ReportLab library")
    
    txt_path = planner.export_session(session, 'txt')
    print(f"Text exported: {txt_path}")
    
    html_path = planner.export_session(session, 'html')
    print(f"HTML exported: {html_path}")
    
    # List sessions
    sessions = planner.session_manager.list_sessions()
    print(f"Total sessions: {len(sessions)}")
    
    print("Session planning system test completed successfully!")