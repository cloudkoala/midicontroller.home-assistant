# Main.py with instant LED feedback system

from pymidicontroller.classes.controller import Controller
from pymidicontroller.extensions import *
from midi_config import load_midi_config
from instant_feedback import create_instant_feedback_system
from datetime import datetime
import os
import time
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
print(f"✅ Using MIDI Output: {midi_config.get_output_port() or 'None'}")

# Home Assistant setup
homeassistant_uri = "http://homeassistant.local:8123"
homeassistant_token = api_key

if __name__ == '__main__':
    # Create the MIDI Controller
    device = Controller()

    # Home Assistant integration
    homeassistant_client = homeassistant.Client(homeassistant_uri, homeassistant_token)

    print("🔧 Setting up INSTANT FEEDBACK switches...")
    
    # Create switches with instant LED feedback
    wavy_wub_switch, wavy_wub_feedback = create_instant_feedback_system(
        entity_id='switch.wavy_wub',
        client=homeassistant_client,
        controller=device,
        channel=1,
        note=36
    )
    
    sunrise_switch, sunrise_feedback = create_instant_feedback_system(
        entity_id='switch.sunrise_lamp',
        client=homeassistant_client,
        controller=device,
        channel=1,
        note=37
    )
    
    lanterns_switch, lanterns_feedback = create_instant_feedback_system(
        entity_id='switch.lanterns',
        client=homeassistant_client,
        controller=device,
        channel=1,
        note=38
    )

    # Register NOTE mappings
    print("🔧 Registering instant feedback mappings...")
    device.register_mapping(1, 36, wavy_wub_switch, message_type='note')
    device.register_mapping(1, 37, sunrise_switch, message_type='note')
    device.register_mapping(1, 38, lanterns_switch, message_type='note')

    # Register feedback systems
    if midi_config.get_output_port():
        print("🔄 Registering LED feedback systems...")
        device.register_feedback(wavy_wub_feedback)
        device.register_feedback(sunrise_feedback)
        device.register_feedback(lanterns_feedback)
        print("✅ Instant LED feedback configured")
    else:
        print("⚠️  No output port - LED feedback disabled")
    
    print("\n🎛️  INSTANT FEEDBACK MIDI Controller Ready!")
    print("\n🚦 LED Behavior:")
    print("   🔴 RED    = Switch is OFF")
    print("   🟠 AMBER  = Button pressed (transitioning)")
    print("   🟢 GREEN  = Switch is ON")
    print("   🟡 YELLOW = Pending state change")
    print("\n⚡ Features:")
    print("   • INSTANT LED response on button press")
    print("   • Real-time state confirmation")
    print("   • External change detection")
    print("   • Timeout protection")
    print("\n🎵 Button mappings:")
    print("   • Note 36 (C2)  → wavy_wub")
    print("   • Note 37 (C#2) → sunrise") 
    print("   • Note 38 (D2)  → lanterns")
    print("\n💡 Press any button and watch the instant LED response!")
    print("Press Ctrl+C to stop")
    
    device.loop()