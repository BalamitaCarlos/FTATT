# tray_app.py - Fixed System Tray with Proper Icon
import pystray
import json
import time
import requests
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw
from pystray import MenuItem as item
import threading

# Set working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

print("=" * 60)
print("FlairsTech Attendance - System Tray")
print("=" * 60)
print(f"Working directory: {SCRIPT_DIR}")
print()

def get_file_path(filename):
    return os.path.join(SCRIPT_DIR, filename)

def parse_api_response(data):
    """Parse API response - handles both dict and list formats"""
    result = data.get('result', {})
    
    check_ins = []
    check_outs = []
    
    if isinstance(result, dict):
        check_ins = result.get('checkIns', [])
        check_outs = result.get('checkOuts', [])
    elif isinstance(result, list):
        for record in result:
            status_type = record.get('checkInOutStatusTypeId', 0)
            if status_type == 1:
                check_ins.append(record)
            elif status_type == 2:
                check_outs.append(record)
    
    return check_ins, check_outs

class FlairsTechTray:
    def __init__(self):
        self.icon = None
        self.running = True
        self.config = self.load_config()
        self.token_data = self.load_token()
        self.checked_in = False
        self.last_status = "Starting..."
        
        print(f"Config loaded: {self.config.get('place_name', 'Unknown')}")
        print(f"Token valid: {self.token_data is not None}")
        print()
    
    def load_config(self):
        try:
            with open(get_file_path('config.json'), 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Config error: {e}")
            return {}
    
    def load_token(self):
        try:
            with open(get_file_path('token.json'), 'r') as f:
                data = json.load(f)
                if data.get('token_expiry', 0) > time.time():
                    return data
        except Exception as e:
            print(f"Token error: {e}")
        return None
    
    def create_icon_image(self):
        """Create icon - try logo first, fallback to generated"""
        logo_path = get_file_path('flairstech_logo.png')
        
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                # Resize to proper tray icon size
                img = img.resize((64, 64), Image.Resampling.LANCZOS)
                print("✓ Using FlairsTech logo")
                return img
            except Exception as e:
                print(f"Logo load error: {e}, using fallback")
        
        # Fallback: generate icon
        img = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw FlairsTech "F"
        draw.rectangle([10, 10, 54, 54], fill='#8B5CF6', outline='#6D28D9', width=2)
        
        # Draw "F" letter
        # Vertical line
        draw.rectangle([20, 20, 26, 44], fill='white')
        # Top horizontal
        draw.rectangle([20, 20, 40, 26], fill='white')
        # Middle horizontal
        draw.rectangle([20, 30, 35, 36], fill='white')
        
        print("✓ Using generated icon")
        return img
    
    def check_status(self):
        """Check attendance status from API"""
        if not self.token_data:
            self.last_status = "No Token"
            return "No Token"
        
        try:
            headers = {
                "authorization": f"Bearer {self.token_data['bearer_token']}",
                "tenant-key": "flairstech"
            }
            
            response = requests.get(
                "https://apiattendance.flairstech.com/api/CheckInOuts/GetMyCheckInOutHistoryToday",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                check_ins, check_outs = parse_api_response(data)
                
                if check_ins and len(check_ins) > len(check_outs):
                    self.checked_in = True
                    
                    # Get check-in time
                    last_checkin = check_ins[-1]
                    checkin_time_str = last_checkin.get('creationTime', '')
                    
                    try:
                        checkin_time = datetime.fromisoformat(
                            checkin_time_str.replace('Z', '+00:00').split('.')[0]
                        )
                        time_str = checkin_time.strftime('%I:%M %p')
                        self.last_status = f"✓ Checked In ({time_str})"
                    except:
                        self.last_status = "✓ Checked In"
                    
                    return self.last_status
                else:
                    self.checked_in = False
                    self.last_status = "○ Not Checked In"
                    return self.last_status
            elif response.status_code == 401:
                self.last_status = "Token Expired"
                return "Token Expired"
            else:
                self.last_status = f"API Error ({response.status_code})"
                return self.last_status
        except requests.exceptions.Timeout:
            self.last_status = "Connection Timeout"
            return self.last_status
        except Exception as e:
            self.last_status = "Offline"
            print(f"Status check error: {e}")
            return "Offline"
    
    def check_in(self, icon, item):
        """Check in"""
        if not self.token_data:
            icon.notify("No token available. Run Setup.", "FlairsTech")
            return
        
        if self.checked_in:
            icon.notify("Already checked in!", "FlairsTech")
            return
        
        headers = {
            "authorization": f"Bearer {self.token_data['bearer_token']}",
            "tenant-key": "flairstech",
            "Content-Type": "application/json"
        }
        
        payload = {
            "placeId": self.config.get('place_id', ''),
            "checkInOutStatusTypeId": 1,
            "longitude": self.config.get('longitude', 0),
            "latitude": self.config.get('latitude', 0)
        }
        
        try:
            print("Checking in...")
            response = requests.post(
                "https://apiattendance.flairstech.com/api/CheckInOuts",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✓ Check-in successful")
                self.checked_in = True
                icon.notify("Checked in successfully!", "FlairsTech Attendance")
                self.update_menu(icon)
            else:
                error = response.json().get('error', {}).get('message', 'Unknown error')
                print(f"✗ Check-in failed: {error}")
                icon.notify(f"Check-in failed: {error}", "FlairsTech")
        except Exception as e:
            print(f"✗ Check-in error: {e}")
            icon.notify(f"Error: {str(e)}", "FlairsTech")
    
    def check_out(self, icon, item):
        """Check out"""
        if not self.token_data:
            icon.notify("No token available. Run Setup.", "FlairsTech")
            return
        
        if not self.checked_in:
            icon.notify("Not checked in!", "FlairsTech")
            return
        
        headers = {
            "authorization": f"Bearer {self.token_data['bearer_token']}",
            "tenant-key": "flairstech",
            "Content-Type": "application/json"
        }
        
        payload = {
            "placeId": self.config.get('place_id', ''),
            "checkInOutStatusTypeId": 2,
            "longitude": self.config.get('longitude', 0),
            "latitude": self.config.get('latitude', 0)
        }
        
        try:
            print("Checking out...")
            response = requests.post(
                "https://apiattendance.flairstech.com/api/CheckInOuts",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✓ Check-out successful")
                self.checked_in = False
                icon.notify("Checked out successfully!", "FlairsTech Attendance")
                self.update_menu(icon)
            else:
                error = response.json().get('error', {}).get('message', 'Unknown error')
                print(f"✗ Check-out failed: {error}")
                icon.notify(f"Check-out failed: {error}", "FlairsTech")
        except Exception as e:
            print(f"✗ Check-out error: {e}")
            icon.notify(f"Error: {str(e)}", "FlairsTech")
    
    def refresh_status(self, icon, item):
        """Refresh status"""
        print("Refreshing status...")
        status = self.check_status()
        icon.notify(f"Status: {status}", "FlairsTech Attendance")
        self.update_menu(icon)
    
    def update_menu(self, icon):
        """Update menu dynamically"""
        icon.menu = self.create_menu()
    
    def exit_app(self, icon, item):
        """Exit application"""
        print("Exiting...")
        self.running = False
        icon.stop()
    
    def create_menu(self):
        """Create system tray menu"""
        location_name = self.config.get('place_name', 'Not Set')[:25]
        
        return pystray.Menu(
            item('FlairsTech Attendance', None, enabled=False),
            item(f'Status: {self.last_status}', None, enabled=False),
            item(f'Location: {location_name}', None, enabled=False),
            item('─' * 30, None, enabled=False),
            item('Check In', self.check_in, enabled=not self.checked_in),
            item('Check Out', self.check_out, enabled=self.checked_in),
            item('Refresh Status', self.refresh_status),
            item('─' * 30, None, enabled=False),
            item('Exit', self.exit_app)
        )
    
    def periodic_refresh(self):
        """Refresh status every 60 seconds"""
        while self.running:
            time.sleep(60)
            if self.running and self.icon:
                print("Auto-refreshing status...")
                self.check_status()
                try:
                    self.icon.update_menu()
                except:
                    pass
    
    def run(self):
        """Run the tray application"""
        icon_image = self.create_icon_image()
        
        self.icon = pystray.Icon(
            "FlairsTech",
            icon_image,
            "FlairsTech Attendance",
            self.create_menu()
        )
        
        # Start periodic refresh in background
        refresh_thread = threading.Thread(target=self.periodic_refresh, daemon=True)
        refresh_thread.start()
        
        # Check initial status
        print("Checking initial status...")
        self.check_status()
        
        print("=" * 60)
        print("System tray icon started!")
        print("Right-click the icon in your system tray to use it.")
        print("=" * 60)
        print()
        
        self.icon.run()

if __name__ == '__main__':
    try:
        app = FlairsTechTray()
        app.run()
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")