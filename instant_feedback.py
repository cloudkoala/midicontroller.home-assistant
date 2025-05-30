# instant_feedback.py - Complete ultra-fast LED feedback system

import time
from dataclasses import dataclass
from pymidicontroller.classes.controller import ControllerExtension

@dataclass
class InstantFeedbackLight(ControllerExtension):
    """Advanced feedback system with ultra-fast visual response"""
    entity_id: str = None
    client: object = None
    midi_channel: int = 1
    midi_note: int = None
    controller_device: object = None

    def __post_init__(self):
        super().__post_init__()
        if self.client is None:
            import sys; sys.exit('No client registered for InstantFeedbackLight')
        if self.controller_device is None:
            import sys; sys.exit('No controller device registered for InstantFeedbackLight')
        if self.midi_note is None:
            import sys; sys.exit('No MIDI Note specified for InstantFeedbackLight')
        
        self.set_metadata('update_frequency', 0.2)  # Check state frequently
        self.set_metadata('last_ha_state', None)
        self.set_metadata('last_check_time', 0)
        self.set_metadata('pending_change', False)
        self.set_metadata('pending_start_time', 0)
        self.set_metadata('current_led_color', 'unknown')

    def _get_velocity_for_color(self, color):
        """Get velocity values for different LED colors"""
        color_map = {
            'red': 15,      # Off state
            'amber': 63,    # Pending/transitioning state  
            'green': 60,    # On state
            'yellow': 62,   # Alternative pending color
            'off': 0        # LED completely off
        }
        return color_map.get(color, 0)

    def _set_led_color(self, color, reason=""):
        """Set LED to specific color with ultra-fast execution"""
        velocity = self._get_velocity_for_color(color)
        
        # Send MIDI immediately without any error checking delays
        try:
            if self.controller_device.output_device:
                if velocity > 0:
                    msg_type = 'note_on'
                    import mido
                    msg = mido.Message(msg_type, channel=self.midi_channel-1, note=self.midi_note, velocity=velocity)
                else:
                    msg_type = 'note_off'
                    import mido
                    msg = mido.Message(msg_type, channel=self.midi_channel-1, note=self.midi_note, velocity=0)
                
                self.controller_device.output_device.send(msg)
                self.set_metadata('current_led_color', color)
                
                if reason:
                    print(f"💡 LED → {color.upper()}: {self.entity_id} ({reason})")
                return True
        except:
            # Don't let MIDI errors slow us down
            pass
        
        return False

    def button_pressed(self):
        """Called when button is pressed - provides ULTRA-FAST feedback"""
        
        # FIRST: Set LED to amber IMMEDIATELY (no state checking delays)
        self._set_led_color('amber', 'INSTANT button response')
        
        # SECOND: Mark pending and get current state
        self.set_metadata('pending_change', True)
        self.set_metadata('pending_start_time', time.time())
        
        # THIRD: Check what state we're transitioning from/to (for logging only)
        try:
            current_ha_state = self.client.get_state(self.entity_id)
            if current_ha_state == 'on':
                print(f"🎵 Button pressed: {self.entity_id} ON → transitioning to OFF")
            else:
                print(f"🎵 Button pressed: {self.entity_id} OFF → transitioning to ON")
        except:
            # If state check fails, don't let it slow down the LED response
            print(f"🎵 Button pressed: {self.entity_id} → transitioning (state unknown)")
            pass

    def execute(self):
        current_time = time.time()
        last_check = self.get_metadata('last_check_time')
        
        # Check state more frequently when pending change
        check_interval = 0.01 if self.get_metadata('pending_change') else self.get_metadata('update_frequency')
        
        if current_time - last_check < check_interval:
            return False
        
        try:
            current_ha_state = self.client.get_state(self.entity_id)
            last_ha_state = self.get_metadata('last_ha_state')
            pending_change = self.get_metadata('pending_change')
            current_led_color = self.get_metadata('current_led_color')
            
            # Handle state change detection
            if current_ha_state != last_ha_state and current_ha_state is not None:
                if pending_change:
                    # State changed as expected - show final color
                    if current_ha_state == 'on':
                        self._set_led_color('green', 'confirmed ON')
                    else:
                        self._set_led_color('red', 'confirmed OFF')
                    
                    self.set_metadata('pending_change', False)
                    print(f"✅ State change confirmed: {self.entity_id} = {current_ha_state.upper()}")
                    
                else:
                    # State changed without button press (external change)
                    if current_ha_state == 'on':
                        self._set_led_color('green', 'external change - ON')
                    else:
                        self._set_led_color('red', 'external change - OFF')
                    
                    print(f"🔄 External change: {self.entity_id} = {current_ha_state.upper()}")
                
                self.set_metadata('last_ha_state', current_ha_state)
            
            # Handle timeout for pending changes (in case HA doesn't respond)
            elif pending_change:
                pending_duration = current_time - self.get_metadata('pending_start_time')
                if pending_duration > 3.0:  # 3 second timeout
                    print(f"⚠️  Timeout waiting for {self.entity_id} state change - reverting LED")
                    # Revert to actual state
                    if current_ha_state == 'on':
                        self._set_led_color('green', 'timeout - reverting to ON')
                    else:
                        self._set_led_color('red', 'timeout - reverting to OFF')
                    
                    self.set_metadata('pending_change', False)
            
            # Initial state setup (first run)
            elif last_ha_state is None and current_ha_state is not None:
                if current_ha_state == 'on':
                    self._set_led_color('green', 'initial state - ON')
                else:
                    self._set_led_color('red', 'initial state - OFF')
                
                self.set_metadata('last_ha_state', current_ha_state)
                print(f"🔧 Initial state: {self.entity_id} = {current_ha_state.upper()}")
            
            self.set_metadata('last_check_time', current_time)
            
        except Exception as e:
            print(f"❌ Error in InstantFeedbackLight for {self.entity_id}: {e}")
            self.set_metadata('last_check_time', current_time)
        
        return False

# Enhanced Switch class that triggers instant feedback
class InstantResponseSwitch:
    """Switch that provides ultra-fast LED feedback on button press"""
    
    def __init__(self, entity_id, client, feedback_light=None):
        self.entity_id = entity_id
        self.client = client
        self.feedback_light = feedback_light
        self.switch = self._create_switch()
    
    def _create_switch(self):
        """Create the underlying switch with enhanced behavior"""
        from pymidicontroller.extensions import homeassistant
        
        class EnhancedSwitch(homeassistant.Switch):
            def __init__(self, entity_id, client, feedback_callback=None):
                super().__init__(entity_id=entity_id, client=client)
                self.feedback_callback = feedback_callback
                self.set_metadata('update_frequency', 0.0001)  # Ultra responsive
            
            def update(self, attribute, value):
                timestamp = time.strftime('%H:%M:%S')
                
                if value > 0:  # Button pressed
                    print(f"[{timestamp}] 🎵 PRESSED: {self.entity_id}")
                    
                    # Trigger instant LED feedback IMMEDIATELY - before ANY other processing
                    if self.feedback_callback:
                        self.feedback_callback()
                    
                    # Call parent update method AFTER LED feedback
                    result = super().update(attribute, value)
                    return result
                
                else:  # Button released
                    print(f"[{timestamp}] 🎵 RELEASED: {self.entity_id}")
                    # Call parent update method
                    result = super().update(attribute, value)
                    return result
            
            def execute(self):
                if self.get_metadata('post_flag'):
                    timestamp = time.strftime('%H:%M:%S')
                    print(f"[{timestamp}] 🔥 TOGGLING {self.entity_id}")
                result = super().execute()
                return result
        
        # Create switch with feedback callback
        callback = self.feedback_light.button_pressed if self.feedback_light else None
        return EnhancedSwitch(self.entity_id, self.client, callback)
    
    def get_switch(self):
        """Get the underlying switch object for registration"""
        return self.switch

# Convenience function for easy setup
def create_instant_feedback_system(entity_id, client, controller, channel, note):
    """Create a complete instant feedback system for a switch"""
    
    # Create the feedback light
    feedback = InstantFeedbackLight(
        entity_id=entity_id,
        client=client,
        midi_channel=channel,
        midi_note=note,
        controller_device=controller
    )
    
    # Create the enhanced switch with instant feedback
    switch_system = InstantResponseSwitch(
        entity_id=entity_id,
        client=client,
        feedback_light=feedback
    )
    
    return switch_system.get_switch(), feedback