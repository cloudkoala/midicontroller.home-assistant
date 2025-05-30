# midi_config.py - Configuration loader module

import json
import os
from typing import Optional, Tuple
import mido

CONFIG_FILE = "midi_config.json"

class MidiConfig:
    """MIDI Configuration Manager"""
    
    def __init__(self):
        self.input_port = None
        self.output_port = None
        self.config_loaded = False
        self.load_config()
    
    def load_config(self) -> bool:
        """Load MIDI configuration from file"""
        if not os.path.exists(CONFIG_FILE):
            print(f"⚠️  MIDI configuration file '{CONFIG_FILE}' not found!")
            print("Please run 'python midi_setup.py' first to configure your MIDI ports.")
            return False
        
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            self.input_port = config.get('midi_input_port')
            self.output_port = config.get('midi_output_port')
            
            if not self.input_port:
                print("❌ No input port configured!")
                return False
            
            print(f"📖 Loaded MIDI config - Input: {self.input_port}, Output: {self.output_port or 'None'}")
            self.config_loaded = True
            return True
            
        except Exception as e:
            print(f"❌ Error loading MIDI configuration: {e}")
            return False
    
    def get_input_port(self) -> Optional[str]:
        """Get configured input port"""
        return self.input_port if self.config_loaded else None
    
    def get_output_port(self) -> Optional[str]:
        """Get configured output port"""
        return self.output_port if self.config_loaded else None
    
    def validate_ports(self) -> bool:
        """Validate that configured ports are still available"""
        if not self.config_loaded:
            return False
        
        available_inputs = mido.get_input_names()
        available_outputs = mido.get_output_names()
        
        if self.input_port not in available_inputs:
            print(f"❌ Configured input port '{self.input_port}' is not available!")
            print(f"Available inputs: {available_inputs}")
            return False
        
        if self.output_port and self.output_port not in available_outputs:
            print(f"❌ Configured output port '{self.output_port}' is not available!")
            print(f"Available outputs: {available_outputs}")
            return False
        
        return True
    
    def open_input(self):
        """Open the configured input port"""
        if not self.config_loaded or not self.input_port:
            raise RuntimeError("No input port configured")
        
        if not self.validate_ports():
            raise RuntimeError("Configured ports are not available")
        
        return mido.open_input(self.input_port)
    
    def open_output(self):
        """Open the configured output port"""
        if not self.config_loaded:
            raise RuntimeError("No configuration loaded")
        
        if not self.output_port:
            print("⚠️  No output port configured - LED feedback disabled")
            return None
        
        if not self.validate_ports():
            raise RuntimeError("Configured ports are not available")
        
        return mido.open_output(self.output_port)

# Convenience functions for backward compatibility
def get_midi_ports() -> Tuple[Optional[str], Optional[str]]:
    """Get configured MIDI input and output ports"""
    config = MidiConfig()
    return config.get_input_port(), config.get_output_port()

def load_midi_config() -> MidiConfig:
    """Load and return MIDI configuration"""
    return MidiConfig()