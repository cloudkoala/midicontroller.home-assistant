from pymidicontroller.classes.controller import Controller
from pymidicontroller.extensions import *
import mido
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # loads from .env by default
api_key = os.getenv("API_KEY")

input_names = mido.get_input_names()
my_midi_controller = input_names[1]  # Automatically pick the first one
print(f"Selected MIDI input: {my_midi_controller}")


# my_midi_controller = mido.get_input_names(0)
homeassistant_uri = "http://homeassistant.local:8123"
homeassistant_token = api_key

if __name__ == '__main__':
    # Match MIDI device name
    device_name = None
    for name in mido.get_input_names():
        if name.startswith(my_midi_controller):
            device_name = name
            break

    if not device_name:
        raise RuntimeError("MIDI device not found. Check name with mido.get_input_names()")

    # Create the MIDI Controller
    device = Controller(device_name)

    # Home Assistant integration
    homeassistant_client = homeassistant.Client(homeassistant_uri, homeassistant_token)

    # Devices
    # Regular lights work normally
    lightbar = homeassistant.Light(entity_id='light.lightbar', client=homeassistant_client)
    
    # Cync lights need special handling
    tripod = homeassistant.CyncLight(entity_id='light.orange_tripod', client=homeassistant_client)
    rattan = homeassistant.CyncLight(entity_id='light.rattan_floor_lamp', client=homeassistant_client)
    
    # If you have other Cync lights, add them as CyncLight objects:
    # pebble = homeassistant.CyncLight(entity_id='light.pebble_lamp', client=homeassistant_client)
    # jupiter = homeassistant.CyncLight(entity_id='light.jupiter', client=homeassistant_client)
    

    # Switches
    sunrise = homeassistant.Switch(entity_id='switch.sunrise_lamp', client=homeassistant_client)
    lanterns = homeassistant.Switch(entity_id='switch.lanterns', client=homeassistant_client)
    # spotify = homeassistant.Media(entity_id='media_player.spotify', client=homeassistant_client)
    wavy_wub = homeassistant.Switch(entity_id='switch.wavy_wub', client=homeassistant_client)


    circadian_lighting = homeassistant.Switch(entity_id='switch.circadian_lighting_circadian_lighting', client=homeassistant_client)
    cycle_color_mode = arbitrary.Toggle(func=tripod.change_colour_mode)

    # Volume controls
    # master_volume = volumemixer.Device()
    # spotify_volume = volumemixer.Application(application='Spotify.exe')
    # discord_volume = volumemixer.Application(application='Discord.exe')
    # tarkov_volume = volumemixer.Application(application='EscapeFromTarkov.exe')
    # r6_volume = volumemixer.Application(application='RainbowSix.exe')

    # Controller mappings
    # Tripod (Cync light) - RGB channels
    device.register_mapping(1, 14, tripod, 'red_channel')
    device.register_mapping(1, 30, tripod, 'green_channel')
    device.register_mapping(1, 50, tripod, 'blue_channel')
    device.register_mapping(1, 78, tripod, 'brightness_channel')

    # Tripod (Cync light) - RGB channels
    device.register_mapping(1, 15, rattan, 'red_channel')
    device.register_mapping(1, 31, rattan, 'green_channel')
    device.register_mapping(1, 51, rattan, 'blue_channel')
    device.register_mapping(1, 79, rattan, 'brightness_channel')

    # Lightbar - HS channels
    device.register_mapping(1, 77, lightbar, 'brightness_channel')
    device.register_mapping(1, 13, lightbar, 'hue_channel')
    device.register_mapping(1, 29, lightbar, 'saturation_channel')


    # Switches
    # device.register_mapping(1, 26, cycle_color_mode)
    # device.register_mapping(1, 31, circadian_lighting)
    device.register_mapping(1, 43, wavy_wub)
    device.register_mapping(1, 42, sunrise)
    device.register_mapping(1, 41, lanterns)

    # Volume (commented out)
    # device.register_mapping(1, 11, master_volume)
    # device.register_mapping(1, 3, spotify_volume)
    # device.register_mapping(1, 4, discord_volume)
    # device.register_mapping(1, 5, tarkov_volume)
    # device.register_mapping(1, 5, r6_volume)

    print("MIDI Controller Ready!")
    print(f"Orange Tripod: Using CyncLight class (sends color and brightness separately)")
    print(f"Lightbar: Using standard Light class")
    print("\nNote: Cync lights require color to be sent WITHOUT brightness, then brightness separately.")
    
    device.loop()