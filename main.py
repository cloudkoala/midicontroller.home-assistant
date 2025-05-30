# main.py - Complete MIDI controller with ultra-fast LED feedback

from pymidicontroller.classes.controller import Controller
from pymidicontroller.extensions import *
from midi_config import load_midi_config
from instant_feedback import create_instant_feedback_system, create_instant_light_toggle
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

    # Devices - Your existing light controls
    lightbar = homeassistant.Light(entity_id='light.lightbar', client=homeassistant_client)
    tripod = homeassistant.CyncLight(entity_id='light.orange_tripod', client=homeassistant_client)
    rattan = homeassistant.CyncLight(entity_id='light.rattan_floor_lamp', client=homeassistant_client)
    strawberry = homeassistant.CyncLight(entity_id='light.strawberry', client=homeassistant_client)
    jupiter = homeassistant.CyncLight(entity_id='light.jupiter', client=homeassistant_client)
    rice_planet = homeassistant.CyncLight(entity_id='light.rice_planet', client=homeassistant_client)
    pebble_lamp = homeassistant.CyncLight(entity_id='light.pebble_lamp', client=homeassistant_client)
    akari_table_lamp = homeassistant.CyncLight(entity_id='light.akari_table_lamp', client=homeassistant_client)
    office_orb = homeassistant.CyncLight(entity_id='light.office_orb', client=homeassistant_client)
    sunroom_lightbar = homeassistant.Light(entity_id='light.sunroom_lightbar', client=homeassistant_client)
    

    # Light control mappings (CC-based)
    print("🔧 Setting up light controls...")
    # Lightbar - HS channels
    device.register_mapping(1, 77, lightbar, 'brightness_channel', message_type='cc')
    device.register_mapping(1, 13, lightbar, 'hue_channel', message_type='cc')
    device.register_mapping(1, 29, lightbar, 'saturation_channel', message_type='cc')

    # Tripod (Cync light) - RGB channels
    device.register_mapping(1, 14, tripod, 'red_channel', message_type='cc')
    device.register_mapping(1, 30, tripod, 'green_channel', message_type='cc')
    device.register_mapping(1, 50, tripod, 'blue_channel', message_type='cc')
    device.register_mapping(1, 78, tripod, 'brightness_channel', message_type='cc')

    # Rattan (Cync light) - RGB channels
    device.register_mapping(1, 15, rattan, 'red_channel', message_type='cc')
    device.register_mapping(1, 31, rattan, 'green_channel', message_type='cc')
    device.register_mapping(1, 51, rattan, 'blue_channel', message_type='cc')
    device.register_mapping(1, 79, rattan, 'brightness_channel', message_type='cc')

    # Pebble Lamp (Cync light) - RGB channels
    device.register_mapping(1, 16, pebble_lamp, 'red_channel', message_type='cc')
    device.register_mapping(1, 32, pebble_lamp, 'green_channel', message_type='cc')
    device.register_mapping(1, 52, pebble_lamp, 'blue_channel', message_type='cc')
    device.register_mapping(1, 80, pebble_lamp, 'brightness_channel', message_type='cc')
    # Jupiter (Cync light) - RGB channels
    device.register_mapping(1, 17, jupiter, 'red_channel', message_type='cc')
    device.register_mapping(1, 33, jupiter, 'green_channel', message_type='cc')
    device.register_mapping(1, 53, jupiter, 'blue_channel', message_type='cc')  
    device.register_mapping(1, 81, jupiter, 'brightness_channel', message_type='cc')
    # Strawberry (Cync light) - RGB channels
    device.register_mapping(1, 18, strawberry, 'red_channel', message_type='cc')
    device.register_mapping(1, 34, strawberry, 'green_channel', message_type='cc')
    device.register_mapping(1, 54, strawberry, 'blue_channel', message_type='cc')
    device.register_mapping(1, 82, strawberry, 'brightness_channel', message_type='cc')
    # Sunroom Lightbar - HS channels
    device.register_mapping(1, 83, sunroom_lightbar, 'brightness_channel', message_type='cc')
    device.register_mapping(1, 19, sunroom_lightbar, 'hue_channel', message_type='cc')
    device.register_mapping(1, 35, sunroom_lightbar, 'saturation_channel', message_type='cc')




    print("🔧 Setting up INSTANT FEEDBACK switches...")
    
    # Create switches with ultra-fast LED feedback
    wavy_wub_switch, wavy_wub_feedback = create_instant_feedback_system(
        entity_id='switch.wavy_wub',
        client=homeassistant_client,
        controller=device,
        channel=1,
        note=36  # Note 36 (C2)
    )
    
    sunrise_switch, sunrise_feedback = create_instant_feedback_system(
        entity_id='switch.sunrise_lamp',
        client=homeassistant_client,
        controller=device,
        channel=1,
        note=37  # Note 37 (C#2)
    )
    
    lanterns_switch, lanterns_feedback = create_instant_feedback_system(
        entity_id='switch.lanterns',
        client=homeassistant_client,
        controller=device,
        channel=1,
        note=38  # Note 38 (D2)
    )

    print("🔧 Setting up INSTANT FEEDBACK light toggles...")
    
    # Create light toggle with same instant feedback behavior
    office_orb_switch, office_orb_feedback = create_instant_light_toggle(
        entity_id='light.office_orb',
        client=homeassistant_client,
        controller=device,
        channel=1,
        note=40  # Note 40 (E1) as requested
    )

    # Create light toggle for Rice Planet
    rice_planet_switch, rice_planet_feedback = create_instant_light_toggle(
        entity_id='light.rice_planet',
        client=homeassistant_client,
        controller=device,
        channel=1,
        note=41  # Note 41 (F1)
    )

        # Create light toggle with same instant feedback behavior
    akari_table_lamp_switch, akari_table_lamp_feedback = create_instant_light_toggle(
        entity_id='light.akari_table_lamp',
        client=homeassistant_client,
        controller=device,
        channel=1,
        note=42
    )  # Note 42 (F#1)
    

    # Register NOTE mappings for switches
    print("🔧 Registering instant feedback switch mappings...")
    device.register_mapping(1, 36, wavy_wub_switch, message_type='note')
    device.register_mapping(1, 37, sunrise_switch, message_type='note')
    device.register_mapping(1, 38, lanterns_switch, message_type='note')
    device.register_mapping(1, 40, office_orb_switch, message_type='note')
    device.register_mapping(1, 41, rice_planet_switch, message_type='note')  
    device.register_mapping(1, 42, akari_table_lamp_switch, message_type='note')  

    # Register other switches (if you have more)
    # Add more switch mappings as needed...

    # Register feedback systems
    if midi_config.get_output_port():
        print("🔄 Registering LED feedback systems...")
        device.register_feedback(wavy_wub_feedback)
        device.register_feedback(sunrise_feedback)
        device.register_feedback(lanterns_feedback)
        device.register_feedback(office_orb_feedback)
        device.register_feedback(akari_table_lamp_feedback)
        device.register_feedback(rice_planet_feedback)
        print("✅ Ultra-fast LED feedback configured")
    else:
        print("⚠️  No output port - LED feedback disabled")
    
    print("\n" + "="*80)
    print("🎛️  PROFESSIONAL MIDI CONTROLLER READY!")
    print("="*80)
    print("\n🚦 LED FEEDBACK BEHAVIOR:")
    print("   🔴 RED    = Switch is OFF (steady state)")
    print("   🟠 AMBER  = Button pressed - INSTANT response!")
    print("   🟢 GREEN  = Switch is ON (confirmed state)")
    print("\n⚡ PERFORMANCE FEATURES:")
    print("   • Sub-millisecond LED response")
    print("   • 200Hz MIDI polling (5ms intervals)")
    print("   • Ultra-responsive switches (1ms)")
    print("   • Real-time state confirmation")
    print("   • External change detection")
    print("   • Timeout protection (3s)")
    print("\n🎵 SWITCH MAPPINGS (Note-based):")
    print("   • Note 36 (C2)  → wavy_wub")
    print("   • Note 37 (C#2) → sunrise") 
    print("   • Note 38 (D2)  → lanterns")
    print("\n🎛️  LIGHT CONTROLS (CC-based):")
    print("   • Tripod RGB: CC 14,30,50 + Brightness: CC 78")
    print("   • Rattan RGB: CC 15,31,51 + Brightness: CC 79") 
    print("   • Lightbar HSB: CC 13,29,77")
    print("\n💡 READY TO USE!")
    print("   • Press switches for instant amber → final state")
    print("   • Control lights with knobs/faders")
    print("   • LEDs stay in sync with Home Assistant")
    print("\nPress Ctrl+C to stop")
    print("="*80)
    
    device.loop()