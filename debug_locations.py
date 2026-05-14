# debug_locations.py - Enhanced to find ALL locations including company defaults
import requests
import json

print("=" * 60)
print("  Location API Debug Tool - Enhanced")
print("=" * 60)
print()

# Load token
try:
    with open('token.json', 'r') as f:
        token_data = json.load(f)
        token = token_data.get('bearer_token')
        print(f"[OK] Token loaded (length: {len(token)} chars)")
except Exception as e:
    print(f"[ERROR] Could not load token: {e}")
    exit(1)

headers = {
    "authorization": f"Bearer {token}",
    "tenant-key": "flairstech"
}

# Extended list of endpoints to try
endpoints = [
    ("My Approved Locations (status=1)", 
     "https://apiattendance.flairstech.com/api/Locations/GetMyLocationsFilteredByStatus?pageSize=1000&locationStatus=1"),
    
    ("All My Locations", 
     "https://apiattendance.flairstech.com/api/Locations/GetMyLocations?pageSize=1000"),
    
    ("My Pending Locations (status=0)", 
     "https://apiattendance.flairstech.com/api/Locations/GetMyLocationsFilteredByStatus?pageSize=1000&locationStatus=0"),
    
    ("Company Locations (All)", 
     "https://apiattendance.flairstech.com/api/Locations/GetCompanyLocations?pageSize=1000"),
    
    ("Company Approved Locations", 
     "https://apiattendance.flairstech.com/api/Locations/GetCompanyLocationsFilteredByStatus?pageSize=1000&locationStatus=1"),
    
    ("All Locations (no filter)", 
     "https://apiattendance.flairstech.com/api/Locations?pageSize=1000"),
    
    ("Available Locations for Check-In", 
     "https://apiattendance.flairstech.com/api/Locations/GetAvailableLocations?pageSize=1000"),
    
    ("Locations for Employee", 
     "https://apiattendance.flairstech.com/api/Locations/GetLocationsForEmployee?pageSize=1000"),
]

print()
print("Testing API endpoints...")
print()

all_locations = {}  # Use dict to avoid duplicates by ID

for name, url in endpoints:
    print(f"Testing: {name}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Try to extract items/records
            items = []
            if 'result' in data and isinstance(data['result'], dict):
                items = data['result'].get('records', [])
                if not items:
                    items = data['result'].get('items', [])
            elif 'records' in data:
                items = data['records']
            elif 'result' in data and isinstance(data['result'], list):
                items = data['result']
            elif 'items' in data:
                items = data['items']
            elif isinstance(data, list):
                items = data
            
            print(f"Found {len(items)} locations")
            
            if items:
                for loc in items:
                    loc_id = loc.get('id', '')
                    if loc_id and loc_id not in all_locations:
                        all_locations[loc_id] = loc
                        print(f"  [NEW] {loc.get('name', 'Unnamed')} (ID: {loc_id[:8]}...)")
                    elif loc_id:
                        print(f"  [DUP] {loc.get('name', 'Unnamed')} (already added)")
            
            # Show sample of response structure
            if items:
                print("\nSample location structure:")
                sample = items[0]
                print(json.dumps(sample, indent=2)[:300] + "...")
                
        elif response.status_code == 404:
            print(f"Endpoint not found (404)")
        elif response.status_code == 401:
            print(f"Unauthorized (401) - Token issue")
        elif response.status_code == 403:
            print(f"Forbidden (403) - Permission issue")
        else:
            print(f"Error {response.status_code}")
            print(f"Response: {response.text[:200]}")
        
    except requests.exceptions.Timeout:
        print(f"Timeout")
    except requests.exceptions.ConnectionError:
        print(f"Connection error")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("-" * 60)
    print()

print()
print("=" * 60)
print(f"TOTAL UNIQUE LOCATIONS FOUND: {len(all_locations)}")
print("=" * 60)

if all_locations:
    print()
    print("All unique locations:")
    print()
    
    for i, (loc_id, loc) in enumerate(all_locations.items(), 1):
        status = loc.get('status', loc.get('locationStatus', 'unknown'))
        status_text = ""
        if status == 1:
            status_text = "[APPROVED]"
        elif status == 0:
            status_text = "[PENDING]"
        elif status == 2:
            status_text = "[REJECTED]"
        
        is_company = loc.get('isCompanyLocation', False) or loc.get('isDefault', False)
        type_text = "[COMPANY]" if is_company else "[PERSONAL]"
        
        print(f"{i:2}. {loc.get('name', 'Unnamed'):30} {status_text:12} {type_text}")
        print(f"    ID: {loc_id}")
        print(f"    Address: {loc.get('address', 'N/A')[:50]}")
        print()
    
    # Save to file for inspection
    with open('debug_locations.json', 'w') as f:
        json.dump(list(all_locations.values()), f, indent=2)
    print()
    print("Full data saved to: debug_locations.json")
    
else:
    print()
    print("NO LOCATIONS FOUND!")
    print()
    print("This is unexpected since you mentioned having 9 locations.")
    print("The API structure might be different than expected.")

print()
print("=" * 60)