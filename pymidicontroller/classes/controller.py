# controller.py - Complete optimized controller with Note and CC support

from dataclasses import dataclass, field
from time import time, sleep
import mido
import sys

from pymidicontroller.extensions import common
from midi_config import MidiConfig

@dataclass()
class ControlClass:
    """Midi control class values - supports both CC and Note"""
    channel: int
    control: int = None      # For CC messages
    note: int = None         # For Note messages  
    target: all = None
    data: all = 'value'
    message_type: str = 'cc' # 'cc' or 'note'
    
    value: float = 0
    lower_left: int = 0
    upper_right: int = 127

@dataclass
class ControllerExtension:
    """The minimum required values for an extension to work with a Controller class"""
    attributes: dict = field(default_factory = lambda: ({}))
    metadata: dict = field(default_factory = lambda: ({
        'update_frequency': 1,
        'last_exec_time': 0,
        'post_data': None
    }))
    min_value: int = 0
    max_value: int = 255

    def __post_init__(self):    
        execute_function_exists = "execute" in dir(self)
        if not execute_function_exists:
            import sys; sys.exit(f"{type(self)} requires an 'execute' function.")

        update_function_exists = "update" in dir(self)
        if not update_function_exists:
            import sys; sys.exit(f"{type(self)} requires an 'update' function.")

    def set_attribute(self, key, value):
        return self._set_value_in_dict(self.attributes, key, value)

    def set_metadata(self, key, value):
        return self._set_value_in_dict(self.metadata, key, value)

    def get_attribute(self, key):
        return self._get_value_from_dict(self.attributes, key)

    def get_metadata(self, key):
        return self._get_value_from_dict(self.metadata, key)

    def _get_value_from_dict(self, dict, key):
        if key in dict:
            return dict[key]
        else:
            return 0

    def _set_value_in_dict(self, dict, key, value):
        dict[key] = value
        if key in dict and dict[key] == value:
            return True
        else:
            return False

    def update(self, attribute, value):
        return self.set_attribute(attribute, value)

    def invoke(self):
        current_time = time()
        last_post_time = self.get_metadata('last_exec_time')
        update_frequency = self.get_metadata('update_frequency')
        time_check = current_time - last_post_time <= update_frequency
        if not time_check:
            target_execution = self.execute()
            self.set_metadata('last_exec_time', current_time)
            return target_execution
        return False

@dataclass()
class Controller:
    """High-performance MIDI controller with automatic configuration and dual message support"""
    name: str = None
    controls: list[ControlClass] = field(default_factory=list)
    feedback_extensions: list[ControllerExtension] = field(default_factory=list)
    update_rate: float = 0.005  # 200Hz for ultra-responsive performance

    is_connected: bool = False
    initialized: bool = False
    output_device: mido.ports.BaseOutput = None
    midi_config: MidiConfig = None

    def __post_init__(self):
        """Load MIDI configuration on initialization"""
        self.midi_config = MidiConfig()
        if not self.midi_config.config_loaded:
            print("❌ MIDI configuration not loaded!")
            print("Please run 'python midi_setup.py' to configure your MIDI ports.")
            sys.exit(1)
        
        if not self.name:
            self.name = self.midi_config.get_input_port()

    def init(self):
        """Initialize MIDI connections using configured ports"""
        try:
            midi_device = self.midi_config.open_input()
            print(f'✅ MIDI input opened: {self.midi_config.get_input_port()}')
            
            self.output_device = self.midi_config.open_output()
            if self.output_device:
                print(f'✅ MIDI output opened: {self.midi_config.get_output_port()}')
            else:
                print('⚠️  No MIDI output configured - LED feedback disabled')
            
            self.initialized = True
            self.is_connected = True
            print(f'🎛️  Controller ready!')
            return midi_device
            
        except Exception as e:
            print(f"❌ Failed to initialize MIDI: {e}")
            return None

    def check_connection(self):
        """Check if MIDI connections are still valid"""
        if self.initialized and self.midi_config.validate_ports():
            self.is_connected = True
        else:
            self.is_connected = False
            self.initialized = False

    def get_controls(self):
        return self.controls

    def register_mapping(self, channel, control_or_note, target, data=None, message_type='cc'):
        """Register mapping for CC or Note messages"""
        if message_type == 'note':
            cc = ControlClass(channel=channel, note=control_or_note, target=target, data=data, message_type='note')
            print(f"✅ Registered Note mapping: Ch.{channel} Note.{control_or_note} → {type(target).__name__}")
        else:
            cc = ControlClass(channel=channel, control=control_or_note, target=target, data=data, message_type='cc')
            print(f"✅ Registered CC mapping: Ch.{channel} CC.{control_or_note} → {type(target).__name__}")
        
        self.controls.append(cc)

    def register_feedback(self, feedback_extension):
        """Register a feedback extension that will be executed in the main loop"""
        self.feedback_extensions.append(feedback_extension)
        print(f"✅ Registered feedback for {getattr(feedback_extension, 'entity_id', 'unknown')}")

    def send_note(self, channel, note, velocity):
        """Send MIDI Note On/Off message to control LEDs"""
        if self.output_device is None:
            return False
        
        try:
            if velocity > 0:
                msg = mido.Message('note_on', channel=channel-1, note=note, velocity=velocity)
            else:
                msg = mido.Message('note_off', channel=channel-1, note=note, velocity=0)
            
            self.output_device.send(msg)
            return True
        except Exception as e:
            print(f"❌ Error sending MIDI Note (ch:{channel}, note:{note}, vel:{velocity}): {e}")
            return False

    def send_cc(self, channel, control, value):
        """Send MIDI Control Change message"""
        if self.output_device is None:
            return False
        
        try:
            msg = mido.Message('control_change', channel=channel-1, control=control, value=value)
            self.output_device.send(msg)
            return True
        except Exception as e:
            print(f"❌ Error sending MIDI CC (ch:{channel}, cc:{control}, val:{value}): {e}")
            return False

    def update_control(self, channel, control, value):
        """Handle CC messages"""
        channel = channel + 1
        for cc in self.get_controls():
            if cc.message_type == 'cc' and cc.channel == channel and cc.control == control:
                if cc.data == None:
                    cc.data = 'value'
                cc.target.update(cc.data, value)

    def update_note(self, channel, note, velocity):
        """Handle Note On/Off messages"""
        channel = channel + 1
        for cc in self.get_controls():
            if cc.message_type == 'note' and cc.channel == channel and cc.note == note:
                if cc.data == None:
                    cc.data = 'value'
                cc.target.update(cc.data, velocity)

    def loop(self):
        """Ultra-high performance main loop with 200Hz polling"""
        midi_device = None

        while True:
            try:
                self.check_connection()
                while not self.is_connected:
                    midi_device = self.init()
                    if midi_device is None:
                        print("❌ Failed to connect to MIDI device. Retrying in 2 seconds...")
                        sleep(2)

                # Handle incoming MIDI messages - PROCESS ALL for zero latency
                for message in midi_device.iter_pending():
                    formatted_message = vars(message)
                    
                    if formatted_message['type'] == 'control_change':
                        control = formatted_message['control']
                        value = formatted_message['value']
                        channel = formatted_message['channel']
                        self.update_control(channel, control, value)
                    
                    elif formatted_message['type'] in ['note_on', 'note_off']:
                        note = formatted_message['note']
                        velocity = formatted_message['velocity']
                        channel = formatted_message['channel']
                        # For note_off, set velocity to 0
                        if formatted_message['type'] == 'note_off':
                            velocity = 0
                        self.update_note(channel, note, velocity)
                
                # Execute control extensions
                ignore_list = []
                for cc in self.get_controls():
                    target = cc.target
                    if target not in ignore_list:
                        target.invoke()
                        ignore_list.append(target)

                # Execute feedback extensions
                feedback_ignore_list = []
                for feedback_ext in self.feedback_extensions:
                    if feedback_ext not in feedback_ignore_list:
                        try:
                            feedback_ext.invoke()
                            feedback_ignore_list.append(feedback_ext)
                        except Exception as e:
                            print(f"❌ Error in feedback extension: {e}")

                # Ultra-fast loop for maximum responsiveness
                sleep(self.update_rate)  # 5ms = 200Hz
                
            except KeyboardInterrupt:
                print('\n🛑 Shutting down...')
                self.cleanup()
                sys.exit()
            except Exception as e:
                print(f"❌ Error in controller loop: {e}")
                sleep(1)

    def cleanup(self):
        """Clean up MIDI connections"""
        try:
            if self.output_device:
                self.output_device.close()
                print("✅ MIDI output closed")
        except Exception as e:
            print(f"Error closing MIDI output: {e}")