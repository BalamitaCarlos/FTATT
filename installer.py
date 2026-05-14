# installer.py - Complete Automated Setup (With Selenium Auto-Capture & Multi-Location Support) - FIXED
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import time
import requests
import webbrowser
import os
import sys
import subprocess

class SetupWizard:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("FlairsTech Attendance - Setup")
        self.window.geometry("600x500")
        self.window.resizable(False, False)
        
        self.token = None
        self.locations = []
        self.selected_location = None
        
        self.create_welcome_screen()
        
    def create_welcome_screen(self):
        """Welcome screen"""
        self.clear_window()
        
        # Header
        header = tk.Label(
            self.window, 
            text="Welcome to FlairsTech Attendance",
            font=("Arial", 20, "bold"),
            fg="#4CAF50"
        )
        header.pack(pady=30)
        
        # Description
        desc = tk.Label(
            self.window,
            text="This setup will take 2 minutes.\n\n"
                 "You'll need to:\n"
                 "1. Log in once to your attendance account\n"
                 "2. Select your office location\n"
                 "3. That's it!\n\n"
                 "After setup, everything works automatically.",
            font=("Arial", 11),
            justify="center"
        )
        desc.pack(pady=20)
        
        # Start button
        start_btn = tk.Button(
            self.window,
            text="Start Setup",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=15,
            command=self.choose_method
        )
        start_btn.pack(pady=30)
        
        # Info
        info = tk.Label(
            self.window,
            text="No technical knowledge required!\n"
                 "Just log in and we'll handle the rest.",
            font=("Arial", 10),
            fg="gray"
        )
        info.pack(pady=20)
    
    def choose_method(self):
        """Choose between automatic and manual method"""
        self.clear_window()
        
        header = tk.Label(
            self.window,
            text="Choose Setup Method",
            font=("Arial", 18, "bold")
        )
        header.pack(pady=30)
        
        # Check if selenium is available
        selenium_available = self.check_selenium()
        
        # Automatic method box
        auto_frame = tk.Frame(self.window, bg='#e8f5e9', relief='raised', borderwidth=2)
        auto_frame.pack(pady=10, padx=40, fill='x')
        
        auto_label = tk.Label(
            auto_frame,
            text="[RECOMMENDED] Fully Automatic",
            font=("Arial", 14, "bold"),
            bg='#e8f5e9',
            fg='#2e7d32'
        )
        auto_label.pack(pady=10)
        
        auto_desc = tk.Label(
            auto_frame,
            text="• Just log in\n"
                 "• Token captured automatically\n"
                 "• Takes 1 minute" +
                 ("\n• Selenium installed ✓" if selenium_available else "\n• Will install Selenium first"),
            font=("Arial", 10),
            bg='#e8f5e9',
            justify="left"
        )
        auto_desc.pack(pady=5)
        
        auto_btn = tk.Button(
            auto_frame,
            text="Use Automatic Method",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10,
            command=self.prepare_selenium_method
        )
        auto_btn.pack(pady=15)
        
        # Manual method box
        manual_frame = tk.Frame(self.window, bg='#e3f2fd', relief='raised', borderwidth=2)
        manual_frame.pack(pady=10, padx=40, fill='x')
        
        manual_label = tk.Label(
            manual_frame,
            text="Manual Copy-Paste",
            font=("Arial", 14, "bold"),
            bg='#e3f2fd',
            fg='#1565c0'
        )
        manual_label.pack(pady=10)
        
        manual_desc = tk.Label(
            manual_frame,
            text="• Log in and copy token\n"
                 "• Works 100% of the time\n"
                 "• Takes 2 minutes\n"
                 "• No extra installation needed",
            font=("Arial", 10),
            bg='#e3f2fd',
            justify="left"
        )
        manual_desc.pack(pady=5)
        
        manual_btn = tk.Button(
            manual_frame,
            text="Use Manual Method",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=10,
            command=self.start_manual_method
        )
        manual_btn.pack(pady=15)
    
    def check_selenium(self):
        """Check if selenium is installed"""
        try:
            import selenium
            from selenium import webdriver
            return True
        except ImportError:
            return False
    
    def prepare_selenium_method(self):
        """Check and install Selenium if needed"""
        if self.check_selenium():
            # Selenium already installed
            self.start_selenium_method()
        else:
            # Need to install Selenium
            self.install_selenium()
    
    def install_selenium(self):
        """Install Selenium and webdriver-manager"""
        self.clear_window()
        
        header = tk.Label(
            self.window,
            text="Installing Selenium",
            font=("Arial", 18, "bold")
        )
        header.pack(pady=30)
        
        desc = tk.Label(
            self.window,
            text="Installing required packages for automatic capture...\n"
                 "This will take about 30 seconds.",
            font=("Arial", 11),
            justify="center"
        )
        desc.pack(pady=20)
        
        self.progress_bar = ttk.Progressbar(
            self.window,
            length=400,
            mode='indeterminate'
        )
        self.progress_bar.pack(pady=20)
        self.progress_bar.start()
        
        self.status_text = tk.Text(
            self.window,
            height=10,
            width=60,
            font=("Consolas", 9)
        )
        self.status_text.pack(pady=20)
        
        # Install in background
        threading.Thread(target=self.run_selenium_install, daemon=True).start()
    
    def run_selenium_install(self):
        """Actually install selenium"""
        try:
            self.update_status("Installing Selenium...")
            
            # Install selenium
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "selenium"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.update_status("[OK] Selenium installed")
            else:
                self.update_status(f"[ERROR] {result.stderr}")
                raise Exception("Selenium installation failed")
            
            self.update_status("\nInstalling WebDriver Manager...")
            
            # Install webdriver-manager
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "webdriver-manager"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.update_status("[OK] WebDriver Manager installed")
            else:
                self.update_status("[WARNING] WebDriver Manager installation failed")
                self.update_status("          (Automatic ChromeDriver download may not work)")
            
            self.update_status("\n" + "=" * 50)
            self.update_status("Installation Complete!")
            self.update_status("=" * 50)
            
            time.sleep(2)
            self.window.after(100, self.start_selenium_method)
            
        except subprocess.TimeoutExpired:
            self.update_status("\n[ERROR] Installation timed out")
            self.update_status("\nTrying manual method instead...")
            time.sleep(2)
            self.window.after(100, self.start_manual_method)
            
        except Exception as e:
            self.update_status(f"\n[ERROR] {str(e)}")
            self.update_status("\nTrying manual method instead...")
            time.sleep(2)
            self.window.after(100, self.start_manual_method)
    
    def start_selenium_method(self):
        """Start automated selenium capture"""
        self.clear_window()
        
        header = tk.Label(
            self.window,
            text="Automatic Token Capture",
            font=("Arial", 18, "bold")
        )
        header.pack(pady=30)
        
        self.status_label = tk.Label(
            self.window,
            text="Starting Chrome browser...",
            font=("Arial", 11)
        )
        self.status_label.pack(pady=20)
        
        self.progress_bar = ttk.Progressbar(
            self.window,
            length=400,
            mode='indeterminate'
        )
        self.progress_bar.pack(pady=20)
        self.progress_bar.start()
        
        self.status_text = tk.Text(
            self.window,
            height=10,
            width=60,
            font=("Consolas", 9)
        )
        self.status_text.pack(pady=20)
        
        # Start selenium capture in background
        threading.Thread(target=self.run_selenium_capture, daemon=True).start()
    
    def run_selenium_capture(self):
        """Run selenium to capture token"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            # Try to use webdriver-manager for automatic ChromeDriver
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                use_manager = True
                self.update_status("[INFO] Using automatic ChromeDriver management")
            except ImportError:
                use_manager = False
                self.update_status("[INFO] WebDriver Manager not available")
                self.update_status("       Looking for manually installed ChromeDriver...")
            
            self.update_status("\n[1/4] Starting Chrome browser...")
            
            # Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Try to start Chrome
            try:
                if use_manager:
                    # Use webdriver-manager (automatic)
                    self.update_status("    Downloading/updating ChromeDriver...")
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    # Try manual ChromeDriver
                    driver = webdriver.Chrome(options=chrome_options)
                    
            except Exception as e:
                self.update_status(f"\n[ERROR] Could not start Chrome: {str(e)}")
                self.update_status("\nPossible solutions:")
                self.update_status("1. Make sure Google Chrome is installed")
                self.update_status("2. Install ChromeDriver automatically:")
                self.update_status("   pip install webdriver-manager")
                self.update_status("\nSwitching to manual method...")
                time.sleep(3)
                self.window.after(100, self.start_manual_method)
                return
            
            self.update_status("[OK] Chrome started successfully\n")
            
            # Open attendance page
            self.update_status("[2/4] Opening FlairsTech Attendance...")
            driver.get("https://attendance.flairstech.com")
            
            self.update_status("[OK] Page loaded\n")
            self.update_status("=" * 50)
            self.update_status("  PLEASE LOG IN NOW")
            self.update_status("=" * 50)
            self.update_status("Log in with your Microsoft account in the browser")
            self.update_status("This window will update automatically...\n")
            
            # Wait for login
            self.update_status("[3/4] Waiting for login...")
            
            token = None
            timeout = 300  # 5 minutes
            start_time = time.time()
            dots = 0
            
            while not token and (time.time() - start_time) < timeout:
                try:
                    # Try to get token from localStorage
                    token = driver.execute_script(
                        "return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');"
                    )
                    
                    if token:
                        self.update_status("\n[OK] Login detected!")
                        self.update_status(f"[OK] Token captured! (Length: {len(token)} chars)\n")
                        break
                    
                    # Show progress dots
                    if dots % 15 == 0:  # Every 30 seconds
                        elapsed = int(time.time() - start_time)
                        remaining = int((timeout - elapsed) / 60)
                        self.update_status(f"    Still waiting... ({remaining} minutes remaining)")
                    dots += 1
                    
                    time.sleep(2)
                    
                except Exception:
                    time.sleep(2)
            
            driver.quit()
            
            if token:
                self.token = token
                self.update_status("[4/4] Closing browser...\n")
                self.update_status("=" * 50)
                self.update_status("  SUCCESS!")
                self.update_status("=" * 50)
                time.sleep(1)
                self.window.after(100, self.fetch_locations)
            else:
                self.update_status("\n[TIMEOUT] Could not detect login within 5 minutes")
                self.update_status("\nDon't worry! Trying manual method instead...")
                time.sleep(2)
                self.window.after(100, self.start_manual_method)
                
        except ImportError as e:
            self.update_status(f"[ERROR] Selenium not available: {str(e)}")
            self.update_status("\nThis shouldn't happen after installation!")
            self.update_status("Switching to manual method...")
            time.sleep(2)
            self.window.after(100, self.start_manual_method)
            
        except Exception as e:
            self.update_status(f"[ERROR] {str(e)}")
            self.update_status("\nSwitching to manual method...")
            time.sleep(2)
            self.window.after(100, self.start_manual_method)
    
    def start_manual_method(self):
        """Start manual token entry method"""
        self.clear_window()
        
        header = tk.Label(
            self.window,
            text="Manual Token Entry",
            font=("Arial", 18, "bold")
        )
        header.pack(pady=20)
        
        desc = tk.Label(
            self.window,
            text="We'll open a webpage with step-by-step instructions.\n"
                 "Just follow along - it's easy!",
            font=("Arial", 11),
            justify="center"
        )
        desc.pack(pady=10)
        
        # Open browser button
        browser_btn = tk.Button(
            self.window,
            text="Open Instructions Page",
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            padx=30,
            pady=15,
            command=self.open_manual_instructions
        )
        browser_btn.pack(pady=20)
        
        # Token input
        tk.Label(
            self.window,
            text="After copying your token, paste it here:",
            font=("Arial", 10)
        ).pack(pady=10)
        
        self.token_entry = tk.Entry(
            self.window,
            font=("Courier New", 10),
            width=50
        )
        self.token_entry.pack(pady=10)
        
        # Bind Enter key
        self.token_entry.bind('<Return>', lambda e: self.validate_manual_token())
        
        # Submit button
        submit_btn = tk.Button(
            self.window,
            text="Submit Token",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=10,
            command=self.validate_manual_token
        )
        submit_btn.pack(pady=20)
        
        self.error_label = tk.Label(
            self.window,
            text="",
            font=("Arial", 10),
            fg="red"
        )
        self.error_label.pack(pady=5)
    
    def open_manual_instructions(self):
        """Open instruction page in browser"""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Token Instructions</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 700px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #4CAF50; }
        .step {
            background: #f9f9f9;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #4CAF50;
            border-radius: 4px;
        }
        .step-number {
            display: inline-block;
            background: #4CAF50;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            font-weight: bold;
            margin-right: 10px;
        }
        code {
            background: #f4f4f4;
            padding: 3px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        .button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px 5px;
        }
        .code-box {
            width: 100%;
            padding: 10px;
            font-family: 'Courier New', monospace;
            background: #2d2d2d;
            color: #f8f8f8;
            border-radius: 5px;
            cursor: pointer;
            border: none;
            resize: none;
            box-sizing: border-box;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Get Your Token - Easy Method</h1>
        
        <div class="step">
            <strong><span class="step-number">1</span> Open Attendance Site</strong>
            <p><a href="https://attendance.flairstech.com" target="_blank" class="button">Open Attendance</a></p>
            <p>Log in if needed</p>
        </div>
        
        <div class="step">
            <strong><span class="step-number">2</span> Open Developer Tools</strong>
            <p>Press <code>F12</code> on your keyboard</p>
        </div>
        
        <div class="step">
            <strong><span class="step-number">3</span> Go to Console</strong>
            <p>Click the "Console" tab at the top</p>
        </div>
        
        <div class="step">
            <strong><span class="step-number">4</span> Copy and Run This Code</strong>
            <p>Click the code below to copy it, then paste in Console and press Enter:</p>
            <textarea readonly onclick="this.select(); document.execCommand('copy'); alert('Copied! Now paste in Console and press Enter');" 
                      class="code-box" rows="2">copy(localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || 'NOT_FOUND')</textarea>
        </div>
        
        <div class="step">
            <strong><span class="step-number">5</span> Paste in Setup Window</strong>
            <p>Your token is now copied! Go back to the setup window and paste it (Ctrl+V).</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Save to temp file
        temp_file = os.path.join(os.path.dirname(__file__), 'token_instructions.html')
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Open in browser
        webbrowser.open('file://' + os.path.abspath(temp_file))
        
        messagebox.showinfo(
            "Instructions Opened",
            "Instructions page opened in your browser.\n\n"
            "Follow the steps, then paste your token here."
        )
    
    def validate_manual_token(self):
        """Validate manually entered token"""
        token = self.token_entry.get().strip()
        
        # Clean token
        if token.lower().startswith('bearer '):
            token = token[7:].strip()
        
        # Validate
        if not token:
            self.error_label.config(text="Please enter your token!")
            return
        
        if len(token) < 100:
            self.error_label.config(text=f"Token too short! Expected 500+, got {len(token)} characters")
            return
        
        if not token.startswith('eyJ'):
            self.error_label.config(text="Invalid token format! Should start with 'eyJ'")
            return
        
        # Token is valid
        self.token = token
        self.error_label.config(text="")
        self.fetch_locations()
    
    def fetch_locations(self):
        """Fetch user's locations automatically"""
        self.clear_window()
        
        header = tk.Label(
            self.window,
            text="Step 2: Getting Your Locations",
            font=("Arial", 18, "bold")
        )
        header.pack(pady=30)
        
        status = tk.Label(
            self.window,
            text="Fetching your approved office locations...",
            font=("Arial", 11)
        )
        status.pack(pady=20)
        
        progress = ttk.Progressbar(
            self.window,
            length=400,
            mode='indeterminate'
        )
        progress.pack(pady=20)
        progress.start()
        
        # Fetch in background
        threading.Thread(target=self.get_locations_api, daemon=True).start()
    
    def get_locations_api(self):
        """Call API to get ALL locations - FIXED to work with 'records' key"""
        try:
            headers = {
                "authorization": f"Bearer {self.token}",
                "tenant-key": "flairstech"
            }
            
            # Try different endpoints (only the ones that work based on debug)
            location_endpoints = [
                {
                    "name": "My Approved Locations",
                    "url": "https://apiattendance.flairstech.com/api/Locations/GetMyLocationsFilteredByStatus",
                    "params": {"pageSize": 10000, "locationStatus": 1}
                },
                {
                    "name": "My All Locations",
                    "url": "https://apiattendance.flairstech.com/api/Locations/GetMyLocations",
                    "params": {"pageSize": 10000}
                },
                {
                    "name": "My Pending Locations",
                    "url": "https://apiattendance.flairstech.com/api/Locations/GetMyLocationsFilteredByStatus",
                    "params": {"pageSize": 10000, "locationStatus": 0}
                },
            ]
            
            all_locations = {}  # Use dict with ID as key to avoid duplicates
            
            for endpoint_info in location_endpoints:
                try:
                    response = requests.get(
                        endpoint_info['url'],
                        headers=headers,
                        params=endpoint_info['params'],
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract locations from response
                        items = []
                        
                        # THE FIX: Look for 'records' in result.records
                        if 'result' in data and isinstance(data['result'], dict):
                            items = data['result'].get('records', [])
                            # Fallback to 'items' if records not found
                            if not items:
                                items = data['result'].get('items', [])
                        
                        # Fallback: records directly
                        elif 'records' in data:
                            items = data['records']
                        
                        # Fallback: items directly  
                        elif 'items' in data:
                            items = data['items']
                        
                        # Fallback: result as list
                        elif 'result' in data and isinstance(data['result'], list):
                            items = data['result']
                        
                        # Fallback: data itself as list
                        elif isinstance(data, list):
                            items = data
                        
                        # Add unique locations
                        for loc in items:
                            loc_id = loc.get('id', '')
                            if loc_id and loc_id not in all_locations:
                                # Normalize location data
                                normalized_loc = {
                                    'id': loc.get('id', ''),
                                    'name': loc.get('name', 'Unnamed Location'),
                                    'latitude': loc.get('latitude', 0),
                                    'longitude': loc.get('longitude', 0),
                                    'locationStatus': loc.get('status', loc.get('locationStatus', 1)),
                                    'address': loc.get('address', ''),
                                    'radius': loc.get('radius', 0),
                                    'isCompany': False
                                }
                                all_locations[loc_id] = normalized_loc
                    
                    # Skip 404s silently (endpoint doesn't exist)
                    elif response.status_code == 404:
                        continue
                        
                except Exception:
                    # Skip failed endpoints silently
                    continue
            
            # Convert dict to list
            self.locations = list(all_locations.values())
            
            # Sort: Approved first, then alphabetically
            self.locations.sort(key=lambda x: (
                x.get('locationStatus', 1) != 1,  # Approved first
                x.get('name', '').lower()          # Then alphabetically
            ))
            
            if self.locations:
                self.window.after(100, self.show_location_selection)
            else:
                self.window.after(100, self.show_no_locations_screen)
                
        except Exception as e:
            self.window.after(100, lambda: self.show_error(f"Network Error: {str(e)}"))
    
    def show_no_locations_screen(self):
        """Show screen when no locations are found"""
        self.clear_window()
        
        header = tk.Label(
            self.window,
            text="No Locations Found",
            font=("Arial", 18, "bold"),
            fg="#ff9800"
        )
        header.pack(pady=30)
        
        desc = tk.Label(
            self.window,
            text="We couldn't find any office locations in your account.\n\n"
                 "This might be because:\n"
                 "• You haven't added any locations yet\n"
                 "• Your locations are pending approval\n"
                 "• You need to add locations in the web portal\n\n"
                 "What would you like to do?",
            font=("Arial", 11),
            justify="center"
        )
        desc.pack(pady=20)
        
        # Option 1: Open web portal
        web_btn = tk.Button(
            self.window,
            text="Open Web Portal to Add Location",
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            padx=30,
            pady=15,
            command=lambda: [webbrowser.open("https://attendance.flairstech.com/my-locations"), 
                            messagebox.showinfo("Next Steps", 
                                              "After adding a location in the web portal:\n\n"
                                              "1. Wait for approval (if needed)\n"
                                              "2. Come back and click 'Retry'\n\n"
                                              "Or you can enter your location ID manually.")]
        )
        web_btn.pack(pady=10)
        
        # Option 2: Manual entry
        manual_btn = tk.Button(
            self.window,
            text="Enter Location ID Manually",
            font=("Arial", 11),
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=10,
            command=self.show_manual_location_entry
        )
        manual_btn.pack(pady=10)
        
        # Option 3: Retry
        retry_btn = tk.Button(
            self.window,
            text="Retry Fetching Locations",
            font=("Arial", 11),
            padx=30,
            pady=10,
            command=self.fetch_locations
        )
        retry_btn.pack(pady=10)
        
        # Option 4: Skip for now
        skip_btn = tk.Button(
            self.window,
            text="Skip - I'll Add It Later",
            font=("Arial", 9),
            command=self.save_without_location
        )
        skip_btn.pack(pady=20)
    
    def show_manual_location_entry(self):
        """Allow manual location ID entry"""
        self.clear_window()
        
        header = tk.Label(
            self.window,
            text="Enter Location ID Manually",
            font=("Arial", 18, "bold")
        )
        header.pack(pady=30)
        
        desc = tk.Label(
            self.window,
            text="You can find your location ID in the web portal:\n"
                 "1. Go to 'My Locations'\n"
                 "2. Look at the URL when viewing a location\n"
                 "3. Copy the ID from the URL",
            font=("Arial", 10),
            justify="center"
        )
        desc.pack(pady=20)
        
        tk.Label(
            self.window,
            text="Location ID:",
            font=("Arial", 11)
        ).pack(pady=10)
        
        self.location_id_entry = tk.Entry(
            self.window,
            font=("Arial", 12),
            width=40
        )
        self.location_id_entry.pack(pady=10)
        
        tk.Label(
            self.window,
            text="Location Name (optional):",
            font=("Arial", 11)
        ).pack(pady=10)
        
        self.location_name_entry = tk.Entry(
            self.window,
            font=("Arial", 12),
            width=40
        )
        self.location_name_entry.pack(pady=10)
        
        submit_btn = tk.Button(
            self.window,
            text="Save Location",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=10,
            command=self.save_manual_location
        )
        submit_btn.pack(pady=20)
        
        back_btn = tk.Button(
            self.window,
            text="Back",
            font=("Arial", 10),
            command=self.show_no_locations_screen
        )
        back_btn.pack(pady=5)
        
        self.error_label = tk.Label(
            self.window,
            text="",
            font=("Arial", 10),
            fg="red"
        )
        self.error_label.pack(pady=5)
    
    def save_manual_location(self):
        """Save manually entered location"""
        location_id = self.location_id_entry.get().strip()
        location_name = self.location_name_entry.get().strip()
        
        if not location_id:
            self.error_label.config(text="Please enter a location ID!")
            return
        
        if not location_name:
            location_name = f"Office Location {location_id}"
        
        # Create a location object
        self.selected_location = {
            'id': location_id,
            'name': location_name,
            'latitude': 0,
            'longitude': 0,
            'locationStatus': 1,
            'address': ''
        }
        
        self.locations = [self.selected_location]
        
        # Save configuration
        self.clear_window()
        
        header = tk.Label(
            self.window,
            text="Saving Configuration...",
            font=("Arial", 18, "bold")
        )
        header.pack(pady=50)
        
        progress = ttk.Progressbar(
            self.window,
            length=400,
            mode='indeterminate'
        )
        progress.pack(pady=20)
        progress.start()
        
        threading.Thread(target=self.save_files, daemon=True).start()
    
    def save_without_location(self):
        """Save config without location (user will add later)"""
        self.selected_location = {
            'id': '',
            'name': 'Not Set',
            'latitude': 0,
            'longitude': 0,
            'locationStatus': 0,
            'address': ''
        }
        
        self.locations = [self.selected_location]
        
        messagebox.showwarning(
            "No Location Set",
            "You'll need to add your location later in config.json\n\n"
            "The app won't work until you add a valid location ID."
        )
        
        self.clear_window()
        
        header = tk.Label(
            self.window,
            text="Saving Configuration...",
            font=("Arial", 18, "bold")
        )
        header.pack(pady=50)
        
        progress = ttk.Progressbar(
            self.window,
            length=400,
            mode='indeterminate'
        )
        progress.pack(pady=20)
        progress.start()
        
        threading.Thread(target=self.save_files, daemon=True).start()
    
    def show_location_selection(self):
        """Show location selection screen"""
        self.clear_window()
        
        header = tk.Label(
            self.window,
            text=f"Step 3: Select Your Office ({len(self.locations)} found)",
            font=("Arial", 18, "bold")
        )
        header.pack(pady=20)
        
        desc = tk.Label(
            self.window,
            text="Select your primary office location.\n"
                 "All locations will be saved to config for easy switching later.",
            font=("Arial", 10),
            justify="center"
        )
        desc.pack(pady=10)
        
        # Location list with status indicators
        frame = tk.Frame(self.window)
        frame.pack(pady=20, fill='both', expand=True, padx=40)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')
        
        self.location_listbox = tk.Listbox(
            frame,
            font=("Arial", 10),
            height=10,
            yscrollcommand=scrollbar.set
        )
        self.location_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.location_listbox.yview)
        
        # Add locations with status
        for loc in self.locations:
            name = loc.get('name', 'Unnamed Location')
            status = loc.get('locationStatus', 1)
            
            # Format display name with status
            status_text = ""
            if status == 1:
                status_text = " [APPROVED]"
            elif status == 0:
                status_text = " [PENDING]"
            elif status == 2:
                status_text = " [REJECTED]"
            
            display_name = f"{name}{status_text}"
            self.location_listbox.insert(tk.END, display_name)
        
        # Select first approved location by default
        approved_index = -1
        for i, loc in enumerate(self.locations):
            if loc.get('locationStatus', 1) == 1:
                approved_index = i
                break
        
        if approved_index >= 0:
            self.location_listbox.select_set(approved_index)
        elif self.locations:
            self.location_listbox.select_set(0)
        
        # Note about pending locations
        if any(loc.get('locationStatus', 0) == 0 for loc in self.locations):
            note = tk.Label(
                self.window,
                text="Note: Pending locations may not work until approved",
                font=("Arial", 9),
                fg="orange"
            )
            note.pack(pady=5)
        
        # Continue button
        continue_btn = tk.Button(
            self.window,
            text="Continue",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=10,
            command=self.save_configuration
        )
        continue_btn.pack(pady=15)
    
    def save_configuration(self):
        """Save token and config"""
        selection = self.location_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a location")
            return
        
        self.selected_location = self.locations[selection[0]]
        
        # Show saving screen
        self.clear_window()
        
        header = tk.Label(
            self.window,
            text="Finalizing Setup...",
            font=("Arial", 18, "bold")
        )
        header.pack(pady=50)
        
        progress = ttk.Progressbar(
            self.window,
            length=400,
            mode='indeterminate'
        )
        progress.pack(pady=20)
        progress.start()
        
        status = tk.Label(
            self.window,
            text="Saving configuration...",
            font=("Arial", 11)
        )
        status.pack(pady=20)
        
        # Save in background
        threading.Thread(target=self.save_files, daemon=True).start()
    
    def save_files(self):
        """Save token and config files"""
        try:
            # Save token
            token_data = {
                "bearer_token": self.token,
                "token_expiry": int(time.time()) + 43200  # 12 hours
            }
            with open('token.json', 'w') as f:
                json.dump(token_data, f, indent=2)
            
            # Prepare all locations for config
            all_locations_data = []
            for loc in self.locations:
                loc_data = {
                    "id": loc.get('id', ''),
                    "name": loc.get('name', 'Unnamed'),
                    "latitude": loc.get('latitude', 0),
                    "longitude": loc.get('longitude', 0),
                    "status": loc.get('locationStatus', loc.get('status', 'unknown')),
                    "address": loc.get('address', '')
                }
                all_locations_data.append(loc_data)
            
            # Save config with primary location and all locations
            config_data = {
                "place_id": self.selected_location.get('id', ''),
                "place_name": self.selected_location.get('name', 'Unknown'),
                "latitude": self.selected_location.get('latitude', 0),
                "longitude": self.selected_location.get('longitude', 0),
                "auto_check_in_time": "08:00",
                "auto_check_out_time": "17:00",
                "enable_auto_check_in": False,
                "enable_auto_check_out": False,
                "notifications": True,
                "all_locations": all_locations_data
            }
            
            with open('config.json', 'w') as f:
                json.dump(config_data, f, indent=2)
            
            time.sleep(1)
            self.window.after(100, self.show_completion)
            
        except Exception as e:
            self.window.after(100, lambda: self.show_error(f"Save Error: {str(e)}"))
    
    def show_completion(self):
        """Show completion screen"""
        self.clear_window()
        
        # Success checkmark using canvas
        canvas = tk.Canvas(self.window, width=100, height=100, bg='white', highlightthickness=0)
        canvas.pack(pady=30)
        canvas.create_oval(10, 10, 90, 90, fill='#4CAF50', outline='')
        canvas.create_line(30, 50, 45, 65, width=6, fill='white', smooth=True)
        canvas.create_line(45, 65, 70, 35, width=6, fill='white', smooth=True)
        
        header = tk.Label(
            self.window,
            text="Setup Complete!",
            font=("Arial", 20, "bold"),
            fg="#4CAF50"
        )
        header.pack(pady=10)
        
        desc = tk.Label(
            self.window,
            text=f"[OK] Token saved (valid for 12 hours)\n"
                 f"[OK] Location set: {self.selected_location.get('name', 'Unknown')}\n"
                 f"[OK] {len(self.locations)} location(s) saved to config\n"
                 f"[OK] Configuration complete\n\n"
                 f"You're ready to use the app!",
            font=("Arial", 12),
            justify="center"
        )
        desc.pack(pady=20)
        
        # Launch app button
        launch_btn = tk.Button(
            self.window,
            text="Launch FlairsTech Attendance",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=15,
            command=self.launch_app
        )
        launch_btn.pack(pady=20)
        
        close_btn = tk.Button(
            self.window,
            text="Close Setup",
            font=("Arial", 11),
            command=self.window.quit
        )
        close_btn.pack(pady=10)
    
    def launch_app(self):
        """Launch the main app"""
        try:
            if sys.platform == 'win32':
                # Windows - use pythonw to run without console
                subprocess.Popen(['pythonw', 'app.py'], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # Linux/Mac
                subprocess.Popen(['python', 'app.py'])
            
            messagebox.showinfo(
                "App Launched",
                "FlairsTech Attendance is now running!\n\n"
                "Look for the clock icon in your system tray."
            )
            self.window.quit()
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch app: {str(e)}\n\nRun manually: python app.py")
    
    def show_error(self, message=None):
        """Show error screen"""
        self.clear_window()
        
        header = tk.Label(
            self.window,
            text="Setup Error",
            font=("Arial", 18, "bold"),
            fg="red"
        )
        header.pack(pady=30)
        
        if message:
            msg = tk.Label(
                self.window,
                text=message,
                font=("Arial", 11),
                wraplength=500
            )
            msg.pack(pady=20)
        
        retry_btn = tk.Button(
            self.window,
            text="Try Again",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            padx=30,
            pady=10,
            command=self.create_welcome_screen
        )
        retry_btn.pack(pady=20)
        
        close_btn = tk.Button(
            self.window,
            text="Exit",
            font=("Arial", 11),
            command=self.window.quit
        )
        close_btn.pack(pady=10)
    
    def clear_window(self):
        """Clear all widgets"""
        for widget in self.window.winfo_children():
            widget.destroy()
    
    def update_status(self, text):
        """Update status text"""
        try:
            self.status_text.insert(tk.END, text + "\n")
            self.status_text.see(tk.END)
            self.window.update()
        except:
            pass
    
    def run(self):
        """Run the setup wizard"""
        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        self.window.mainloop()

if __name__ == '__main__':
    wizard = SetupWizard()
    wizard.run()