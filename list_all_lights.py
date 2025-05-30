import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()  # loads from .env by default
api_key = os.getenv("API_KEY")

# Your credentials
homeassistant_uri = "http://homeassistant.local:8123"
homeassistant_token = api_key

headers = {'Authorization': f'Bearer {homeassistant_token}'}

print("Fetching all lights...\n")

response = requests.get(f'{homeassistant_uri}/api/states', headers=headers)
if response.status_code == 200:
    states = response.json()
    lights = [s for s in states if s['entity_id'].startswith('light.')]
    
    print(f"Found {len(lights)} lights:\n")
    
    for light in lights:
        entity_id = light['entity_id']
        attrs = light['attributes']
        friendly_name = attrs.get('friendly_name', 'Unknown')
        
        print(f"{entity_id}")
        print(f"  Name: {friendly_name}")
        print(f"  State: {light['state']}")
        print(f"  Supported modes: {attrs.get('supported_color_modes', [])}")
        print(f"  Current mode: {attrs.get('color_mode', 'N/A')}")
        
        # Check if it's a Cync light
        if 'cync' in entity_id.lower() or 'cync' in friendly_name.lower():
            print("  *** This appears to be a Cync light ***")
        
        print()
else:
    print(f"Error: {response.status_code}")

