import requests
import json

# Load your token
with open('token.json', 'r') as f:
    token_data = json.load(f)
    token = token_data.get('bearer_token', '')

if not token:
    print("❌ No token found. You need to login first.")
    print("We'll get to that in the next step.")
    exit()

# Get your locations
headers = {
    "authorization": f"Bearer {token}",
    "tenant-key": "flairstech"
}

response = requests.get(
    "https://apiattendance.flairstech.com/api/Locations/GetMyLocationsFilteredByStatus?pageSize=1000&PageSize=1&locationStatus=1",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    locations = data.get('result', {}).get('items', [])
    
    print("\n🗺️  YOUR APPROVED LOCATIONS:\n")
    for loc in locations:
        print(f"Name: {loc['name']}")
        print(f"PlaceId: {loc['id']}")
        print(f"Coordinates: {loc['latitude']}, {loc['longitude']}")
        print("-" * 50)
else:
    print(f"❌ Error: {response.status_code}")
    print("You need to get your token first (next step)")