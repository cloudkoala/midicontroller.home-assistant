#!/usr/bin/env python3
"""
MIDI Note and Control Identifier
Uses your saved MIDI configuration to listen for and identify MIDI messages.
Perfect for figuring out what notes/CCs your buttons and knobs send.
"""

import mido
import time
from midi_config import load_midi_config
from collections import defaultdict
import sys

# MIDI note names for easy reference
NOTE_NAMES = [
    'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'
]

def note_to_name(note_number):
    """Convert MIDI note number to note name (e.g., 60 -> C4)"""
    octave = (note_number // 12) - 1
    note_name = NOTE_NAMES[note_number % 12]
    return f"{note_name}{octave}"

def format_message_info(msg):
    """Format MIDI message information for display"""
    info = {
        'time': time.strftime('%H:%M:%S'),
        'channel': msg.channel + 1,  # Convert to 1-based
        'type': msg.type
    }
    
    if msg.type == 'note_on':
        info.update({
            'note': f"{msg.note} ({note_to_name(msg.note)})",
            'velocity': msg.velocity,
            'description': 'Button Press' if msg.velocity > 0 else 'Button Release'
        })
    elif msg.type == 'note_off':
        info.update({
            'note': f"{msg.note} ({note_to_name(msg.note)})",
            'velocity': msg.velocity,
            'description': 'Button Release'
        })
    elif msg.type == 'control_change':
        info.update({
            'cc': msg.control,
            'value': msg.value,
            'description': 'Knob/Fader/Button'
        })
    elif msg.type == 'program_change':
        info.update({
            'program': msg.program,
            'description': 'Program Change'
        })
    elif msg.type == 'aftertouch':
        info.update({
            'value': msg.value,
            'description': 'Channel Pressure'
        })
    elif msg.type == 'polytouch':
        info.update({
            'note': f"{msg.note} ({note_to_name(msg.note)})",
            'value': msg.value,
            'description': 'Polyphonic Pressure'
        })
    elif msg.type == 'pitchwheel':
        info.update({
            'pitch': msg.pitch,
            'description': 'Pitch Bend'
        })
    
    return info

def print_message(info):
    """Print formatted MIDI message"""
    timestamp = info['time']
    channel = info['channel']
    msg_type = info['type'].replace('_', ' ').title()
    
    if info['type'] in ['note_on', 'note_off']:
        print(f"[{timestamp}] Ch.{channel:2d} | {msg_type:12} | Note: {info['note']:12} | Vel: {info['velocity']:3d} | {info['description']}")
    elif info['type'] == 'control_change':
        print(f"[{timestamp}] Ch.{channel:2d} | {msg_type:12} | CC: {info['cc']:3d}        | Val: {info['value']:3d} | {info['description']}")
    else:
        # Handle other message types
        details = []
        for key, value in info.items():
            if key not in ['time', 'channel', 'type', 'description']:
                details.append(f"{key}: {value}")
        detail_str = " | ".join(details)
        print(f"[{timestamp}] Ch.{channel:2d} | {msg_type:12} | {detail_str:20} | {info.get('description', '')}")

def print_summary(message_counts):
    """Print summary of captured messages"""
    if not message_counts:
        return
    
    print("\n" + "="*80)
    print("SUMMARY OF CAPTURED MESSAGES")
    print("="*80)
    
    # Sort by message type for consistent output
    for msg_type in sorted(message_counts.keys()):
        messages = message_counts[msg_type]
        print(f"\n📋 {msg_type.replace('_', ' ').title()} Messages:")
        
        if msg_type in ['note_on', 'note_off']:
            # Group by note number
            note_groups = defaultdict(list)
            for msg_info in messages:
                note_num = int(msg_info['note'].split()[0])
                note_groups[note_num].append(msg_info)
            
            for note_num in sorted(note_groups.keys()):
                note_name = note_to_name(note_num)
                count = len(note_groups[note_num])
                channels = set(msg['channel'] for msg in note_groups[note_num])
                velocities = set(msg['velocity'] for msg in note_groups[note_num])
                print(f"   Note {note_num:3d} ({note_name:4}) - {count:3d} messages - Ch: {sorted(channels)} - Vel: {sorted(velocities)}")
                
        elif msg_type == 'control_change':
            # Group by CC number
            cc_groups = defaultdict(list)
            for msg_info in messages:
                cc_num = msg_info['cc']
                cc_groups[cc_num].append(msg_info)
            
            for cc_num in sorted(cc_groups.keys()):
                count = len(cc_groups[cc_num])
                channels = set(msg['channel'] for msg in cc_groups[cc_num])
                values = set(msg['value'] for msg in cc_groups[cc_num])
                print(f"   CC {cc_num:3d}           - {count:3d} messages - Ch: {sorted(channels)} - Val: {sorted(values)}")

def main():
    """Main identification loop"""
    print("🎵 MIDI Note and Control Identifier")
    print("This tool will show you exactly what MIDI messages your controller sends.")
    
    # Load MIDI configuration
    midi_config = load_midi_config()
    
    if not midi_config.config_loaded:
        print("❌ MIDI configuration not found!")
        print("Please run 'python midi_setup.py' first to configure your MIDI ports.")
        return
    
    input_port = midi_config.get_input_port()
    print(f"📖 Using configured input port: {input_port}")
    
    # Validate port is still available
    if not midi_config.validate_ports():
        print("❌ Configured MIDI port is not available!")
        print("Please run 'python midi_setup.py' to reconfigure.")
        return
    
    print("\n" + "="*80)
    print("LISTENING FOR MIDI MESSAGES")
    print("="*80)
    print("Time     | Ch | Message Type | Details              | Value | Description")
    print("-" * 80)
    print("🎛️  Start pressing buttons, turning knobs, and moving faders...")
    print("Press Ctrl+C to stop and see summary\n")
    
    message_counts = defaultdict(list)
    
    try:
        with midi_config.open_input() as inport:
            for msg in inport:
                # Skip active sensing and clock messages (too noisy)
                if msg.type in ['active_sensing', 'clock', 'start', 'stop', 'continue']:
                    continue
                
                info = format_message_info(msg)
                print_message(info)
                
                # Store for summary
                message_counts[msg.type].append(info)
                
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping MIDI capture...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return
    
    # Print summary
    print_summary(message_counts)
    
    # Provide helpful tips
    print("\n" + "="*80)
    print("💡 TIPS FOR USING THIS INFORMATION")
    print("="*80)
    print("• Note messages are typically used for buttons (especially in toggle mode)")
    print("• CC messages are typically used for knobs, faders, and momentary buttons")
    print("• For LED feedback, use the same Note/CC number that the button sends")
    print("• Channel numbers should match between your button and LED feedback")
    print("• Velocity 127 usually means 'on' or 'pressed', 0 means 'off' or 'released'")
    
    if message_counts:
        print(f"\n📊 Captured {sum(len(msgs) for msgs in message_counts.values())} total messages")
        print("You can now use these Note/CC numbers in your main.py configuration!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nIdentification cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please check your MIDI controller connection and configuration.")