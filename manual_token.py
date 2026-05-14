import json
import time

print("")
print("=" * 60)
print("       Manual Token Entry")
print("=" * 60)
print("")
print("STEP BY STEP:")
print("")
print("1. Open Chrome")
print("2. Go to: https://attendance.flairstech.com")
print("3. Log in normally (if not already logged in)")
print("4. Press F12 (opens DevTools)")
print("5. Click 'Network' tab at the top")
print("6. Refresh the page (F5)")
print("7. Click on ANY request in the list")
print("8. Look for 'Request Headers' on the right side")
print("9. Scroll down to find a line like:")
print("   authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6...")
print("10. RIGHT-CLICK on that long token and click 'Copy value'")
print("")
print("=" * 60)
print("")

token = input("Paste the FULL token here (including 'Bearer' if present): ").strip()

# Clean up the token
if token.startswith('Bearer '):
    token = token[7:].strip()
elif token.startswith('bearer '):
    token = token[7:].strip()

# Validate
if len(token) < 100:
    print("")
    print("ERROR: That token looks too short!")
    print("Expected length: 500+ characters")
    print("You have: " + str(len(token)) + " characters")
    print("")
    print("Make sure you copied the ENTIRE token after 'Bearer'")
    exit(1)

# Save
token_data = {
    "bearer_token": token,
    "token_expiry": int(time.time()) + 43200
}

with open('token.json', 'w') as f:
    json.dump(token_data, f, indent=2)

print("")
print("SUCCESS! Token saved to token.json")
print("")
print("Token preview: " + token[:50] + "...")
print("Token length: " + str(len(token)) + " characters")
print("Expires in: 12 hours")
print("")
print("=" * 60)
print("Next step: Run this command:")
print("  python get_locations.py")
print("=" * 60)
print("")