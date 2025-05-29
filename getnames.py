import mido

print("Available MIDI input devices:")
for name in mido.get_input_names():
    print(name)