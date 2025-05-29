import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()  # loads from .env by default

api_key = os.getenv("API_KEY")

# Your credentials
homeassistant_uri = "http://homeassistant.local:8123"
homeassistant_token = api_key

headers = {
    'Authorization': f'Bearer {homeassistant_token}', 
    'Content-Type': 'application/json'
}

# Your Cync light entity
entity_id = 'light.orange_tripod'

def get_state():
    """Get current state of the light"""
    response = requests.get(f'{homeassistant_uri}/api/states/{entity_id}', headers=headers)
    if response.status_code == 200:
        state = response.json()
        attrs = state['attributes']
        print(f"\nCurrent state of {entity_id}:")
        print(f"  State: {state['state']}")
        print(f"  Brightness: {attrs.get('brightness', 'N/A')}")
        print(f"  Color mode: {attrs.get('color_mode', 'N/A')}")
        print(f"  RGB color: {attrs.get('rgb_color', 'N/A')}")
        print(f"  HS color: {attrs.get('hs_color', 'N/A')}")
        print(f"  Color temp: {attrs.get('color_temp_kelvin', 'N/A')}K")
        print(f"  Supported modes: {attrs.get('supported_color_modes', [])}")
        return state
    else:
        print(f"Error getting state: {response.status_code}")
        return None

def test_command(data, description):
    """Test a specific command"""
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"Sending: {json.dumps(data, indent=2)}")
    
    response = requests.post(
        f'{homeassistant_uri}/api/services/light/turn_on',
        headers=headers,
        data=json.dumps(data)
    )
    
    print(f"Response: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    
    time.sleep(2)  # Wait for the change to take effect
    get_state()  # Check new state

# Start testing
print("Starting Cync light debug test...")
get_state()

# Test 1: Turn on with brightness only
test_command(
    {'entity_id': entity_id, 'brightness': 255},
    "Turn on with max brightness"
)

# Test 2: Set color temperature (to see if it switches modes)
test_command(
    {'entity_id': entity_id, 'brightness': 255, 'color_temp_kelvin': 4000},
    "Set color temperature to 4000K"
)

# Test 3: Set RGB color
test_command(
    {'entity_id': entity_id, 'brightness': 255, 'rgb_color': [255, 0, 0]},
    "Set RGB to red [255, 0, 0]"
)

# Test 4: Try without brightness
test_command(
    {'entity_id': entity_id, 'rgb_color': [0, 255, 0]},
    "Set RGB to green [0, 255, 0] without brightness"
)

# Test 5: Try HS color
test_command(
    {'entity_id': entity_id, 'brightness': 255, 'hs_color': [240, 100]},
    "Set HS to blue [240, 100]"
)

# Test 6: Try XY color (some lights prefer this)
test_command(
    {'entity_id': entity_id, 'brightness': 255, 'xy_color': [0.3, 0.3]},
    "Set XY color"
)

# Test 7: Turn off then on with color
print(f"\n{'='*50}")
print("Testing: Turn off, then on with color")
requests.post(
    f'{homeassistant_uri}/api/services/light/turn_off',
    headers=headers,
    data=json.dumps({'entity_id': entity_id})
)
time.sleep(2)

test_command(
    {'entity_id': entity_id, 'brightness': 255, 'rgb_color': [255, 255, 0]},
    "Turn on with yellow [255, 255, 0]"
)

print("\n" + "="*50)
print("Debug test complete!")