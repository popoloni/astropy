"""
Gesture Manager for AstroScope Planner
Handles swipe gestures, pinch-to-zoom, and other touch interactions
"""

from kivy.vector import Vector
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty
import math


class GestureManager(EventDispatcher):
    """Manages gesture recognition and handling for the app"""
    
    # Gesture thresholds
    swipe_threshold = NumericProperty(100)  # Minimum distance for swipe
    swipe_velocity_threshold = NumericProperty(200)  # Minimum velocity
    pinch_threshold = NumericProperty(0.1)  # Minimum scale change for pinch
    tap_threshold = NumericProperty(10)  # Maximum movement for tap
    double_tap_time = NumericProperty(0.3)  # Maximum time between taps
    long_press_time = NumericProperty(0.8)  # Minimum time for long press
    
    # State tracking
    is_swiping = BooleanProperty(False)
    is_pinching = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Touch tracking
        self.touches = {}
        self.last_tap_time = 0
        self.last_tap_pos = None
        self.long_press_event = None
        
        # Gesture callbacks
        self.gesture_callbacks = {
            'swipe_left': [],
            'swipe_right': [],
            'swipe_up': [],
            'swipe_down': [],
            'pinch_in': [],
            'pinch_out': [],
            'double_tap': [],
            'long_press': [],
            'tap': []
        }
    
    def register_gesture(self, gesture_type, callback):
        """Register a callback for a specific gesture"""
        if gesture_type in self.gesture_callbacks:
            self.gesture_callbacks[gesture_type].append(callback)
            Logger.info(f"GestureManager: Registered {gesture_type} callback")
        else:
            Logger.warning(f"GestureManager: Unknown gesture type: {gesture_type}")
    
    def unregister_gesture(self, gesture_type, callback):
        """Unregister a callback for a specific gesture"""
        if gesture_type in self.gesture_callbacks and callback in self.gesture_callbacks[gesture_type]:
            self.gesture_callbacks[gesture_type].remove(callback)
            Logger.info(f"GestureManager: Unregistered {gesture_type} callback")
    
    def on_touch_down(self, touch):
        """Handle touch down events"""
        self.touches[touch.id] = {
            'start_pos': touch.pos,
            'current_pos': touch.pos,
            'start_time': touch.time_start,
            'moved': False
        }
        
        # Schedule long press detection
        if self.long_press_event:
            self.long_press_event.cancel()
        self.long_press_event = Clock.schedule_once(
            lambda dt: self._check_long_press(touch), 
            self.long_press_time
        )
        
        return False
    
    def on_touch_move(self, touch):
        """Handle touch move events"""
        if touch.id not in self.touches:
            return False
        
        touch_data = self.touches[touch.id]
        touch_data['current_pos'] = touch.pos
        
        # Calculate movement distance
        start_pos = Vector(touch_data['start_pos'])
        current_pos = Vector(touch.pos)
        distance = start_pos.distance(current_pos)
        
        if distance > self.tap_threshold:
            touch_data['moved'] = True
            
            # Cancel long press if touch moved
            if self.long_press_event:
                self.long_press_event.cancel()
                self.long_press_event = None
        
        # Handle multi-touch pinch gestures
        if len(self.touches) == 2:
            self._handle_pinch_gesture()
        
        return False
    
    def on_touch_up(self, touch):
        """Handle touch up events"""
        if touch.id not in self.touches:
            return False
        
        touch_data = self.touches[touch.id]
        
        # Cancel long press
        if self.long_press_event:
            self.long_press_event.cancel()
            self.long_press_event = None
        
        # Handle single touch gestures
        if len(self.touches) == 1:
            if not touch_data['moved']:
                self._handle_tap_gesture(touch)
            else:
                self._handle_swipe_gesture(touch, touch_data)
        
        # Clean up
        del self.touches[touch.id]
        
        return False
    
    def _handle_swipe_gesture(self, touch, touch_data):
        """Detect and handle swipe gestures"""
        start_pos = Vector(touch_data['start_pos'])
        end_pos = Vector(touch.pos)
        
        # Calculate swipe vector
        swipe_vector = end_pos - start_pos
        distance = swipe_vector.length()
        
        if distance < self.swipe_threshold:
            return
        
        # Calculate velocity
        duration = touch.time_end - touch_data['start_time']
        if duration <= 0:
            return
        
        velocity = distance / duration
        if velocity < self.swipe_velocity_threshold:
            return
        
        # Determine swipe direction
        angle = math.degrees(math.atan2(swipe_vector.y, swipe_vector.x))
        
        # Normalize angle to 0-360
        if angle < 0:
            angle += 360
        
        # Determine primary direction
        if 315 <= angle or angle < 45:
            direction = 'swipe_right'
        elif 45 <= angle < 135:
            direction = 'swipe_up'
        elif 135 <= angle < 225:
            direction = 'swipe_left'
        else:  # 225 <= angle < 315
            direction = 'swipe_down'
        
        self._trigger_gesture(direction, {
            'start_pos': touch_data['start_pos'],
            'end_pos': touch.pos,
            'distance': distance,
            'velocity': velocity,
            'direction': angle
        })
    
    def _handle_tap_gesture(self, touch):
        """Handle tap and double-tap gestures"""
        current_time = touch.time_end
        
        # Check for double tap
        if (self.last_tap_time and 
            current_time - self.last_tap_time < self.double_tap_time and
            self.last_tap_pos):
            
            # Check if taps are close enough
            last_pos = Vector(self.last_tap_pos)
            current_pos = Vector(touch.pos)
            
            if last_pos.distance(current_pos) < self.tap_threshold * 2:
                self._trigger_gesture('double_tap', {
                    'pos': touch.pos,
                    'time': current_time
                })
                # Reset to prevent triple tap
                self.last_tap_time = 0
                self.last_tap_pos = None
                return
        
        # Single tap
        self._trigger_gesture('tap', {
            'pos': touch.pos,
            'time': current_time
        })
        
        # Store for potential double tap
        self.last_tap_time = current_time
        self.last_tap_pos = touch.pos
    
    def _check_long_press(self, touch):
        """Check if touch qualifies as long press"""
        if touch.id in self.touches and not self.touches[touch.id]['moved']:
            self._trigger_gesture('long_press', {
                'pos': touch.pos,
                'duration': touch.time_end - touch.time_start if hasattr(touch, 'time_end') else self.long_press_time
            })
    
    def _handle_pinch_gesture(self):
        """Handle pinch-to-zoom gestures"""
        if len(self.touches) != 2:
            return
        
        touch_ids = list(self.touches.keys())
        touch1_data = self.touches[touch_ids[0]]
        touch2_data = self.touches[touch_ids[1]]
        
        # Calculate initial and current distances
        start_pos1 = Vector(touch1_data['start_pos'])
        start_pos2 = Vector(touch2_data['start_pos'])
        current_pos1 = Vector(touch1_data['current_pos'])
        current_pos2 = Vector(touch2_data['current_pos'])
        
        start_distance = start_pos1.distance(start_pos2)
        current_distance = current_pos1.distance(current_pos2)
        
        if start_distance == 0:
            return
        
        # Calculate scale factor
        scale_factor = current_distance / start_distance
        
        # Determine pinch direction
        if abs(scale_factor - 1.0) > self.pinch_threshold:
            if scale_factor > 1.0:
                gesture_type = 'pinch_out'
            else:
                gesture_type = 'pinch_in'
            
            center_x = (current_pos1.x + current_pos2.x) / 2
            center_y = (current_pos1.y + current_pos2.y) / 2
            
            self._trigger_gesture(gesture_type, {
                'center': (center_x, center_y),
                'scale_factor': scale_factor,
                'distance': current_distance
            })
    
    def _trigger_gesture(self, gesture_type, data):
        """Trigger callbacks for a specific gesture"""
        Logger.info(f"GestureManager: {gesture_type} detected")
        
        for callback in self.gesture_callbacks[gesture_type]:
            try:
                callback(data)
            except Exception as e:
                Logger.error(f"GestureManager: Error in {gesture_type} callback: {e}")


class SwipeableWidget:
    """Mixin class to add swipe gesture support to widgets"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gesture_manager = GestureManager()
        
        # Bind touch events
        self.bind(on_touch_down=self.gesture_manager.on_touch_down)
        self.bind(on_touch_move=self.gesture_manager.on_touch_move)
        self.bind(on_touch_up=self.gesture_manager.on_touch_up)
    
    def register_swipe_callback(self, direction, callback):
        """Register a swipe callback"""
        self.gesture_manager.register_gesture(f'swipe_{direction}', callback)
    
    def register_gesture_callback(self, gesture_type, callback):
        """Register any gesture callback"""
        self.gesture_manager.register_gesture(gesture_type, callback)


# Common gesture patterns for astronomy apps
class AstronomyGestures:
    """Common gesture patterns for astronomy applications"""
    
    @staticmethod
    def setup_screen_navigation(screen, app):
        """Setup standard screen navigation gestures"""
        if hasattr(screen, 'gesture_manager'):
            # Swipe right to go back
            screen.gesture_manager.register_gesture('swipe_right', 
                lambda data: app.go_back() if hasattr(app, 'go_back') else None)
            
            # Swipe left for next screen (if applicable)
            screen.gesture_manager.register_gesture('swipe_left',
                lambda data: app.go_forward() if hasattr(app, 'go_forward') else None)
            
            # Double tap to refresh
            screen.gesture_manager.register_gesture('double_tap',
                lambda data: app.refresh_data() if hasattr(app, 'refresh_data') else None)
    
    @staticmethod
    def setup_list_gestures(list_widget, callbacks):
        """Setup gestures for list widgets"""
        if hasattr(list_widget, 'gesture_manager'):
            # Swipe up/down for scrolling (handled by ScrollView)
            # Long press for context menu
            if 'long_press' in callbacks:
                list_widget.gesture_manager.register_gesture('long_press', callbacks['long_press'])
            
            # Double tap for quick action
            if 'double_tap' in callbacks:
                list_widget.gesture_manager.register_gesture('double_tap', callbacks['double_tap'])
    
    @staticmethod
    def setup_target_gestures(target_widget, callbacks):
        """Setup gestures for target widgets"""
        if hasattr(target_widget, 'gesture_manager'):
            # Swipe right to add to planned
            if 'add_to_planned' in callbacks:
                target_widget.gesture_manager.register_gesture('swipe_right', callbacks['add_to_planned'])
            
            # Swipe left to remove/skip
            if 'remove' in callbacks:
                target_widget.gesture_manager.register_gesture('swipe_left', callbacks['remove'])
            
            # Long press for details
            if 'show_details' in callbacks:
                target_widget.gesture_manager.register_gesture('long_press', callbacks['show_details'])