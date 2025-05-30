# Simplified main.py for testing button presses WITHOUT LED feedback

from pymidicontroller.classes.controller import Controller
from pymidicontroller.extensions import *
from midi_config import load_midi_config
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

# Load MIDI configuration
print("🎵 Loading MIDI configuration...")
midi_config = load_midi_config()

if not midi_config.config_loaded:
    print("❌ MIDI configuration not found!")
    print("Please run: python midi_setup.py")
    exit(1)

print(f"✅ Using MIDI Input: {midi_config.get_input_port()}")
# TEMPORARILY DISABLE OUTPUT FOR TESTING
print("⚠️  LED feedback DISABLED for testing")

# Home Assistant setup
homeassistant_uri = "http://homeassistant.local:8123"
homeassistant_token = api_key

if __name__ == '__main__':
    # Create the MIDI Controller
    device = Controller()
    
    # TEMPORARILY override output to None to disable LED feedback
    device.output_device = None

    # Home Assistant integration
    homeassistant_client = homeassistant.Client(homeassistant_uri, homeassistant_token)

    # Only create switches for testing
    print("🔧 Setting up switches for testing...")
    wavy_wub = homeassistant.Switch(entity_id='switch.wavy_wub', client=homeassistant_client)
    sunrise = homeassistant.Switch(entity_id='switch.sunrise_lamp', client=homeassistant_client)
    lanterns = homeassistant.Switch(entity_id='switch.lanterns', client=homeassistant_client)

    # Register switch mappings - use the CC/Note numbers you discovered
    # Update these based on what your midi_identifier.py script showed
    print("🔧 Registering button mappings...")
    device.register_mapping(1, 36, wavy_wub)    # Update with your actual CC/Note numbers
    device.register_mapping(1, 37, sunrise)     # Update with your actual CC/Note numbers
    device.register_mapping(1, 38, lanterns)    # Update with your actual CC/Note numbers

    # NO LED FEEDBACK FOR NOW - just test button presses
    
    print("\n🧪 TESTING MODE - Button Presses Only")
    print("🎛️  Try pressing your buttons - they should control Home Assistant")
    print("💡 LED feedback is DISABLED for this test")
    print("📊 Watch the console for button press detection")
    print("\nPress Ctrl+C to stop")
    
    # Add some debug output to see if buttons are being pressed
    class DebugSwitch(homeassistant.Switch):
        def execute(self):
            result = super().execute()
            if self.get_metadata('post_flag'):
                print(f"🔥 Button pressed! Toggling {self.entity_id}")
            return result
    
    # Replace switches with debug versions
    wavy_wub = DebugSwitch(entity_id='switch.wavy_wub', client=homeassistant_client)
    sunrise = DebugSwitch(entity_id='switch.sunrise_lamp', client=homeassistant_client)
    lanterns = DebugSwitch(entity_id='switch.lanterns', client=homeassistant_client)
    
    # Re-register with debug switches
    device.controls.clear()  # Clear previous mappings
    device.register_mapping(1, 36, wavy_wub)
    device.register_mapping(1, 37, sunrise)
    device.register_mapping(1, 38, lanterns)
    
    device.loop()