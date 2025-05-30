from pymidicontroller.classes.controller import ControllerExtension
from pymidicontroller.extensions.common import translate
from dataclasses import dataclass
import requests
import json
import time

@dataclass()
class Client:
    uri: str
    token: str

    def get_state(self, entity_id):
        """Get the current state of a Home Assistant entity"""
        headers = {
            'Authorization': f'Bearer {self.token}', 
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get(f'{self.uri}/api/states/{entity_id}', headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get('state')
            else:
                print(f"Error getting state for {entity_id}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception getting state for {entity_id}: {e}")
            return None
        
    def post_data(self, data, domain, service):
        headers = {
            'Authorization': f'Bearer {self.token}', 
            'Content-Type': 'application/json'
        }
        print(f"Sending: {json.dumps(data)}")
        response = requests.post(f'{self.uri}/api/services/{domain}/{service}', headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
        return response.status_code == 200
    
@dataclass
class FeedbackLight(ControllerExtension):
    """Monitors Home Assistant entity state and controls MIDI feedback LED using Note messages for toggle buttons"""
    entity_id: str = None
    client: Client = None
    midi_channel: int = 1
    midi_note: int = None
    controller_device: object = None
    led_color: str = 'red'

    def __post_init__(self):
        super().__post_init__()
        if self.client is None:
            import sys; sys.exit('No client registered for FeedbackLight')
        if self.controller_device is None:
            import sys; sys.exit('No controller device registered for FeedbackLight')
        if self.midi_note is None:
            import sys; sys.exit('No MIDI Note specified for FeedbackLight')
        
        self.set_metadata('update_frequency', 1.0)  # Check every second
        self.set_metadata('last_state', None)
        self.set_metadata('last_check_time', 0)

    def _get_velocity_for_color(self, on=True):
        """Get the correct velocity value for LED color from Launch Control XL manual"""
        if not on:
            return 0  # LED off
        
        # Values from the official manual (page 4)
        color_map = {
            'red': 15,      # 0Fh - Red Full
            'green': 60,    # 3Ch - Green Full  
            'amber': 63,    # 3Fh - Amber Full
            'yellow': 62    # 3Eh - Yellow Full
        }
        return color_map.get(self.led_color, 15)

    def execute(self):
        current_time = time.time()
        last_check = self.get_metadata('last_check_time')
        
        if current_time - last_check < self.get_metadata('update_frequency'):
            return False
            
        try:
            current_state = self.client.get_state(self.entity_id)
            last_state = self.get_metadata('last_state')
            
            if current_state != last_state and current_state is not None:
                if current_state == 'on':
                    velocity = self._get_velocity_for_color(True)
                    success = self.controller_device.send_note(self.midi_channel, self.midi_note, velocity)
                    if success:
                        print(f"✓ LED ON ({self.led_color}, Note {self.midi_note}) for {self.entity_id}")
                else:
                    success = self.controller_device.send_note(self.midi_channel, self.midi_note, 0)
                    if success:
                        print(f"✓ LED OFF (Note {self.midi_note}) for {self.entity_id}")
                
                if success:
                    self.set_metadata('last_state', current_state)
            
            self.set_metadata('last_check_time', current_time)
            
        except Exception as e:
            print(f"Error in FeedbackLight for {self.entity_id}: {e}")
            self.set_metadata('last_check_time', current_time)
        
        return False

    
@dataclass()
class Light(ControllerExtension):
    entity_id: str = None
    client: Client = None

    def __post_init__(self):
        super().__post_init__()
        if self.client == None:
            import sys; sys.exit('No client registered')
        self.set_metadata('update_frequency', 1)
        self.set_attribute('colour_mode', 'hs')
        self.set_metadata('init', True)

    def update(self, attribute, value):
        self.set_metadata('post_flag', True)
        super().update(attribute, value)

    def execute(self):
        if not self.get_metadata('init'):
            self.first_run()
        
        post_flag = self.get_metadata('post_flag')
        if post_flag:
            transition = self.get_metadata('update_frequency')
            brightness = translate(self.get_attribute('brightness_channel'),0,127,0,255)

            data = {}
            data['brightness'] = round(brightness)
            data['transition'] = transition
            data['entity_id'] = self.entity_id

            colour_mode = self.get_attribute('colour_mode')
            if colour_mode == 'rgb':
                red = translate(self.get_attribute('red_channel'),0,127,0,255)
                green = translate(self.get_attribute('green_channel'),0,127,0,255)
                blue = translate(self.get_attribute('blue_channel'),0,127,0,255)
                data['rgb_color'] = [
                    round(red), 
                    round(green), 
                    round(blue)
                ]

            elif colour_mode == 'hs':
                hue = translate(self.get_attribute('hue_channel'),0,127,0,360)
                saturation = translate(self.get_attribute('saturation_channel'),0,127,0,100)
                data['hs_color'] = [
                    round(hue), 
                    round(saturation)
                ]
                
            post_data = self.client.post_data(data, 'light', 'turn_on')
            self.set_metadata('post_flag', not post_data)
            return not post_data
        return False

    def change_colour_mode(self):
        current_colour_mode = self.get_attribute('colour_mode')
        colour_modes = ['hs', 'rgb']

        current_colour_mode_index = colour_modes.index(current_colour_mode)
        new_colour_mode = colour_modes[(current_colour_mode_index + 1) % len(colour_modes)]
        self.set_attribute('colour_mode', new_colour_mode)
        print(f"Color mode for {self.entity_id} set to: {new_colour_mode}")


@dataclass()
class CyncLight(Light):
    """Special handling for Cync lights that don't accept brightness with RGB"""
    
    def __post_init__(self):
        super().__post_init__()
        self.set_attribute('colour_mode', 'rgb')
        self.set_metadata('last_brightness', 255)
        self.set_metadata('last_color', [255, 255, 255])
        
    def execute(self):
        if not self.get_metadata('init'):
            self.first_run()
        
        post_flag = self.get_metadata('post_flag')
        if not post_flag:
            return False
        
        # Get current values
        brightness = translate(self.get_attribute('brightness_channel'), 0, 127, 0, 255)
        red = translate(self.get_attribute('red_channel'), 0, 127, 0, 255)
        green = translate(self.get_attribute('green_channel'), 0, 127, 0, 255)
        blue = translate(self.get_attribute('blue_channel'), 0, 127, 0, 255)
        
        current_brightness = round(brightness)
        current_color = [round(red), round(green), round(blue)]
        
        last_brightness = self.get_metadata('last_brightness')
        last_color = self.get_metadata('last_color')
        
        # For Cync: Send color and brightness separately
        success = True
        
        # If color changed, send color WITHOUT brightness first
        if current_color != last_color:
            color_data = {
                'entity_id': self.entity_id,
                'rgb_color': current_color
                # NO brightness here!
            }
            print(f"Cync: Setting color to {current_color}")
            success = self.client.post_data(color_data, 'light', 'turn_on')
            if success:
                self.set_metadata('last_color', current_color)
                time.sleep(0.1)  # Small delay between commands
        
        # Then send brightness separately if it changed
        if current_brightness != last_brightness and success:
            brightness_data = {
                'entity_id': self.entity_id,
                'brightness': current_brightness
                # NO color here!
            }
            print(f"Cync: Setting brightness to {current_brightness}")
            success = self.client.post_data(brightness_data, 'light', 'turn_on')
            if success:
                self.set_metadata('last_brightness', current_brightness)
        
        self.set_metadata('post_flag', not success)
        return not success


@dataclass
class Switch(ControllerExtension):
    entity_id: str = None
    client: Client = None

    def __post_init__(self):
        super().__post_init__()
        self.set_metadata('update_frequency', 0.005)
        if self.client is None:
            import sys; sys.exit('No client registered')
        self.set_attribute('button_state', 0)

    def update(self, attribute, value):
        last_button_state = self.get_attribute('button_state') or 0
        button_state = 1 if value > 0 else 0

        # Detect rising edge (press)
        if last_button_state == 0 and button_state == 1:
            self.set_metadata('post_flag', True)

        self.set_attribute('button_state', button_state)
        super().update(attribute, value)

    def execute(self):
        if self.get_metadata('post_flag'):
            data = {'entity_id': self.entity_id}
            success = self.client.post_data(data, 'switch', 'toggle')
            self.set_metadata('post_flag', False)
            return not success
        return False
    
@dataclass
class ToggleSwitch(ControllerExtension):
    """Handles toggle note-based switches - simpler than momentary switches"""
    entity_id: str = None
    client: Client = None

    def __post_init__(self):
        super().__post_init__()
        self.set_metadata('update_frequency', 0.1)  # Fast response for user actions
        if self.client is None:
            import sys; sys.exit('No client registered')
        self.set_attribute('last_note_state', 0)

    def update(self, attribute, value):
        # For toggle buttons, we get note on/off messages
        # Note on (value > 0) = button pressed down
        # Note off (value = 0) = button released
        last_state = self.get_attribute('last_note_state') or 0
        current_state = 1 if value > 0 else 0

        # Only trigger on note ON (button press), not note OFF (release)
        if last_state == 0 and current_state == 1:
            self.set_metadata('post_flag', True)

        self.set_attribute('last_note_state', current_state)
        super().update(attribute, value)

    def execute(self):
        if self.get_metadata('post_flag'):
            data = {'entity_id': self.entity_id}
            success = self.client.post_data(data, 'switch', 'toggle')
            self.set_metadata('post_flag', False)
            return not success
        return False