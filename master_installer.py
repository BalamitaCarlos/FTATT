# master_installer.py - FlairsTech Attendance Complete Installer (CHROME FIXED)
import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys
import subprocess
import json
import time
import requests
import threading
import webbrowser
from datetime import datetime
import queue

# FlairsTech Color Palette
COLOR_PURPLE = '#8B5CF6'
COLOR_BLUE = '#3B82F6'
COLOR_DARK_BLUE = '#1E40AF'
COLOR_WHITE = '#FFFFFF'
COLOR_BG = '#F8F9FA'
COLOR_SUCCESS = '#10B981'
COLOR_ERROR = '#EF4444'
COLOR_WARNING = '#F59E0B'

class FlairsTechInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FlairsTech Attendance - Installer")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_WHITE)
        
        if getattr(sys, 'frozen', False):
            self.install_dir = os.path.dirname(sys.executable)
        else:
            self.install_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.token = None
        self.config = {}
        self.locations = []
        self.selected_location = None
        self.selected_location_index = 0
        self.is_processing = False
        
        self.message_queue = queue.Queue()
        
        self.show_welcome_screen()
        self.process_queue()
    
    def process_queue(self):
        """Process messages from background thread safely"""
        try:
            while True:
                msg = self.message_queue.get_nowait()
                msg_type = msg.get('type')
                
                if msg_type == 'progress':
                    self.update_progress_safe(msg.get('text'))
                elif msg_type == 'error':
                    self.show_error(msg.get('text'))
                elif msg_type == 'success':
                    self.fetch_locations()
                elif msg_type == 'timeout':
                    self.show_capture_timeout()
                elif msg_type == 'selenium_install':
                    self.install_selenium()
                elif msg_type == 'selenium_failed':
                    self.show_selenium_install_failed()
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_queue)
    
    def update_progress_safe(self, message):
        """Thread-safe progress update"""
        if hasattr(self, 'progress_label'):
            self.progress_label.config(text=message)
    
    def check_selenium(self):
        """Check if Selenium is installed"""
        try:
            import selenium
            from selenium import webdriver
            return True
        except ImportError:
            return False
    
    def install_selenium(self):
        """Install Selenium automatically"""
        self.show_progress_screen("Installing Dependencies", "Installing Selenium for automatic setup...")
        threading.Thread(target=self._install_selenium_worker, daemon=True).start()
    
    def _install_selenium_worker(self):
        """Background worker to install Selenium - ENHANCED"""
        try:
            print("\n" + "="*60)
            print("INSTALLING SELENIUM & DEPENDENCIES")
            print("="*60)
            
            # Uninstall old version first
            self.message_queue.put({'type': 'progress', 'text': 'Cleaning old installation...'})
            subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "-y", "selenium"],
                capture_output=True,
                timeout=30
            )
            print("✓ Old version removed")
            
            # Install latest Selenium
            self.message_queue.put({'type': 'progress', 'text': 'Installing Selenium...'})
            
            result1 = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "selenium>=4.16.0"],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result1.returncode != 0:
                print(f"✗ Selenium installation failed: {result1.stderr}")
                self.message_queue.put({'type': 'selenium_failed'})
                return
            
            print("✓ Selenium installed")
            
            # Install webdriver-manager as backup
            self.message_queue.put({'type': 'progress', 'text': 'Installing ChromeDriver manager...'})
            
            result2 = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "webdriver-manager"],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result2.returncode == 0:
                print("✓ webdriver-manager installed")
            else:
                print("⚠ webdriver-manager skipped (optional)")
            
            # Verify installation
            self.message_queue.put({'type': 'progress', 'text': 'Verifying installation...'})
            
            try:
                # Force reimport
                if 'selenium' in sys.modules:
                    del sys.modules['selenium']
                
                import selenium
                from selenium import webdriver
                print(f"✓ Selenium version: {selenium.__version__}")
            except Exception as e:
                print(f"✗ Verification failed: {e}")
                self.message_queue.put({'type': 'selenium_failed'})
                return
            
            self.message_queue.put({'type': 'progress', 'text': '✓ All dependencies ready!'})
            time.sleep(1)
            
            # Start automatic capture
            self.message_queue.put({'type': 'progress', 'text': 'Preparing browser...'})
            time.sleep(1)
            self.start_automatic_capture()
        
        except subprocess.TimeoutExpired:
            print("✗ Installation timed out")
            self.message_queue.put({'type': 'selenium_failed'})
        except Exception as e:
            print(f"✗ Installation error: {e}")
            import traceback
            traceback.print_exc()
            self.message_queue.put({'type': 'selenium_failed'})
    
    def show_selenium_install_failed(self):
        """Show error when Selenium install fails"""
        self.is_processing = False
        response = messagebox.askyesno(
            "Installation Failed",
            "Could not install Selenium automatically.\n\n"
            "Would you like to use the manual token entry method instead?\n\n"
            "(It's actually faster and works 100% of the time)",
            icon='warning'
        )
        
        if response:
            self.show_manual_token_entry()
        else:
            self.show_login_screen()
    
    def is_chrome_installed(self):
        """Check if Chrome is installed"""
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                return True, path
        
        return False, None
    
    def get_chrome_driver(self):
        """Get ChromeDriver - COMPLETELY FIXED"""
        print("\n--- ChromeDriver Setup ---")
        
        # Force fresh import
        if 'selenium' in sys.modules:
            del sys.modules['selenium']
        if 'selenium.webdriver' in sys.modules:
            del sys.modules['selenium.webdriver']
        
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=3')
        
        # Find Chrome
        is_installed, chrome_path = self.is_chrome_installed()
        if is_installed and chrome_path:
            options.binary_location = chrome_path
            print(f"✓ Chrome binary: {chrome_path}")
        else:
            raise Exception("Chrome not found!")
        
        # Method 1: Selenium 4.6+ automatic driver management
        try:
            print("Method 1: Selenium Manager (automatic)...")
            driver = webdriver.Chrome(options=options)
            print("✓ SUCCESS: ChromeDriver via Selenium Manager")
            return driver
        except Exception as e1:
            print(f"Method 1 failed: {str(e1)[:100]}")
        
        # Method 2: Try with explicit Service
        try:
            print("Method 2: Explicit Service...")
            from selenium.webdriver.chrome.service import Service
            service = Service()
            driver = webdriver.Chrome(service=service, options=options)
            print("✓ SUCCESS: ChromeDriver via Service")
            return driver
        except Exception as e2:
            print(f"Method 2 failed: {str(e2)[:100]}")
        
        # Method 3: webdriver-manager
        try:
            print("Method 3: webdriver-manager...")
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("✓ SUCCESS: ChromeDriver via webdriver-manager")
            return driver
        except Exception as e3:
            print(f"Method 3 failed: {str(e3)[:100]}")
        
        # All methods failed
        error_msg = (
            "Could not initialize ChromeDriver.\n\n"
            "All methods failed:\n"
            f"1. Selenium Manager: {str(e1)[:50]}\n"
            f"2. Service: {str(e2)[:50]}\n"
            f"3. webdriver-manager: {str(e3)[:50]}\n\n"
            "Try manual method instead."
        )
        raise Exception(error_msg)
    
    def parse_api_response(self, data):
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
    
    def show_welcome_screen(self):
        """Welcome screen"""
        self.clear_screen()
        
        header_frame = tk.Frame(self.root, bg=COLOR_PURPLE, height=150)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        try:
            from PIL import Image, ImageTk
            logo_path = os.path.join(self.install_dir, 'flairstech_logo.png')
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((80, 80), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(header_frame, image=logo_photo, bg=COLOR_PURPLE)
                logo_label.image = logo_photo
                logo_label.pack(pady=15)
        except:
            tk.Label(header_frame, text="⏰", font=('Arial', 48), bg=COLOR_PURPLE, fg=COLOR_WHITE).pack(pady=15)
        
        tk.Label(header_frame, text="FlairsTech Attendance", font=('Arial', 20, 'bold'),
                bg=COLOR_PURPLE, fg=COLOR_WHITE).pack()
        
        content_frame = tk.Frame(self.root, bg=COLOR_WHITE)
        content_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        tk.Label(content_frame, text="Welcome to FlairsTech Attendance Setup",
                font=('Arial', 16, 'bold'), bg=COLOR_WHITE, fg=COLOR_DARK_BLUE).pack(pady=20)
        
        tk.Label(content_frame,
                text="This installer will:\n\n"
                     "✓ Install required dependencies automatically\n"
                     "✓ Set up your attendance tracking\n"
                     "✓ Configure desktop widget\n"
                     "✓ Configure system tray app\n"
                     "✓ Set up break management (60 min/day)\n"
                     "✓ Add to Windows startup (optional)\n\n"
                     "Setup takes about 2-3 minutes.",
                font=('Arial', 11), bg=COLOR_WHITE, fg='#4B5563', justify='left').pack(pady=10)
        
        btn_frame = tk.Frame(content_frame, bg=COLOR_WHITE)
        btn_frame.pack(pady=30)
        
        tk.Button(btn_frame, text="Start Setup", font=('Arial', 14, 'bold'),
                 bg=COLOR_BLUE, fg=COLOR_WHITE, padx=40, pady=15, border=0,
                 cursor='hand2', command=self.check_existing_installation).pack(pady=10)
        
        tk.Label(content_frame, text="Installation Directory:",
                font=('Arial', 9), bg=COLOR_WHITE, fg='#9CA3AF').pack()
        tk.Label(content_frame, text=self.install_dir,
                font=('Arial', 8), bg=COLOR_WHITE, fg='#6B7280').pack()
    
    def check_existing_installation(self):
        """Check if already installed"""
        config_path = os.path.join(self.install_dir, 'config.json')
        token_path = os.path.join(self.install_dir, 'token.json')
        
        if os.path.exists(config_path) and os.path.exists(token_path):
            try:
                with open(token_path, 'r') as f:
                    token_data = json.load(f)
                token_expiry = token_data.get('token_expiry', 0)
                
                if token_expiry < time.time():
                    response = messagebox.askyesno(
                        "Token Expired",
                        "Your authentication token has expired.\n\n"
                        "Would you like to refresh it now?",
                        icon='warning'
                    )
                    if response:
                        self.show_login_screen()
                    else:
                        self.root.quit()
                    return
            except:
                pass
            
            response = messagebox.askyesnocancel(
                "Installation Found",
                "FlairsTech Attendance is already installed.\n\n"
                "What would you like to do?\n\n"
                "• Yes - Reconfigure\n"
                "• No - Refresh token\n"
                "• Cancel - Exit",
                icon='question'
            )
            
            if response is True:
                self.show_login_screen()
            elif response is False:
                self.show_login_screen()
            else:
                self.root.quit()
        else:
            self.show_login_screen()
    
    def show_login_screen(self):
        """Login screen"""
        self.clear_screen()
        self.is_processing = False
        
        header_frame = tk.Frame(self.root, bg=COLOR_PURPLE, height=120)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        try:
            from PIL import Image, ImageTk
            logo_path = os.path.join(self.install_dir, 'flairstech_logo.png')
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((60, 60), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(header_frame, image=logo_photo, bg=COLOR_PURPLE)
                logo_label.image = logo_photo
                logo_label.pack(pady=10)
        except:
            pass
        
        tk.Label(header_frame, text="Login to FlairsTech Attendance",
                font=('Arial', 18, 'bold'), bg=COLOR_PURPLE, fg=COLOR_WHITE).pack()
        
        content_frame = tk.Frame(self.root, bg=COLOR_WHITE)
        content_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        tk.Label(content_frame, text="Fully Automatic Setup",
                font=('Arial', 14, 'bold'), bg=COLOR_WHITE, fg=COLOR_DARK_BLUE).pack(pady=15)
        
        instructions_frame = tk.Frame(content_frame, bg='#EEF2FF', relief='solid', bd=2)
        instructions_frame.pack(fill='x', pady=20)
        
        tk.Label(instructions_frame, text="What will happen:",
                font=('Arial', 11, 'bold'), bg='#EEF2FF', fg=COLOR_PURPLE).pack(anchor='w', padx=20, pady=(15, 10))
        
        steps = [
            "1️⃣ Click the button below",
            "2️⃣ Browser opens automatically (Chrome)",
            "3️⃣ Log in with your Microsoft account",
            "4️⃣ Wait 5-10 seconds while we capture your token",
            "5️⃣ Browser closes automatically - Done!"
        ]
        
        for step in steps:
            tk.Label(instructions_frame, text=step, font=('Arial', 11),
                    bg='#EEF2FF', fg='#4B5563').pack(anchor='w', padx=35, pady=3)
        
        tk.Label(instructions_frame, text="", bg='#EEF2FF').pack(pady=10)
        
        note_frame = tk.Frame(content_frame, bg='#FEF3C7', relief='solid', bd=1)
        note_frame.pack(fill='x', pady=15)
        
        tk.Label(note_frame, text="💡 Tip: If you're already logged in to FlairsTech, it will be instant!",
                font=('Arial', 10, 'bold'), bg='#FEF3C7', fg='#92400E').pack(pady=12)
        
        tk.Button(content_frame, text="🚀 Start Automatic Setup",
                 font=('Arial', 14, 'bold'), bg=COLOR_SUCCESS, fg=COLOR_WHITE,
                 padx=40, pady=15, border=0, cursor='hand2',
                 command=self.start_automatic_capture, activebackground='#059669').pack(pady=25)
        
        manual_label = tk.Label(content_frame, text="Having trouble? Use manual method",
                               font=('Arial', 9, 'underline'), bg=COLOR_WHITE,
                               fg=COLOR_BLUE, cursor='hand2')
        manual_label.pack(pady=10)
        manual_label.bind('<Button-1>', lambda e: self.show_manual_token_entry())
    
    def start_automatic_capture(self):
        """Start automatic token capture"""
        if self.is_processing:
            messagebox.showwarning("Please Wait", "Setup is already in progress.")
            return
        
        if not self.check_selenium():
            response = messagebox.askyesno(
                "Install Dependencies",
                "Selenium is required for automatic setup.\n\n"
                "Would you like to install it now?\n"
                "(This will take about 30-60 seconds)",
                icon='question'
            )
            
            if response:
                self.is_processing = True
                self.install_selenium()
            else:
                self.show_manual_token_entry()
            return
        
        is_installed, chrome_path = self.is_chrome_installed()
        if not is_installed:
            response = messagebox.askyesnocancel(
                "Chrome Not Found",
                "Google Chrome is required for automatic setup.\n\n"
                "• Yes - Download Chrome now\n"
                "• No - Use manual method\n"
                "• Cancel - Go back",
                icon='warning'
            )
            
            if response is True:
                webbrowser.open('https://www.google.com/chrome/')
                messagebox.showinfo("Download Chrome",
                                  "After installing Chrome, restart this installer.")
                self.root.quit()
            elif response is False:
                self.show_manual_token_entry()
            return
        
        self.is_processing = True
        self.show_progress_screen("Starting Browser", "Preparing automatic setup...")
        
        threading.Thread(target=self._automatic_capture_worker, daemon=True).start()
    
    def _automatic_capture_worker(self):
        """Background worker for token capture"""
        driver = None
        try:
            print("\n" + "="*60)
            print("AUTOMATIC TOKEN CAPTURE")
            print("="*60)
            
            try:
                # Force fresh import
                if 'selenium' in sys.modules:
                    del sys.modules['selenium']
                if 'selenium.webdriver' in sys.modules:
                    del sys.modules['selenium.webdriver']
                
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.common.exceptions import WebDriverException, TimeoutException
                print("✓ Selenium imported")
            except ImportError as e:
                print(f"✗ Selenium import failed: {e}")
                self.message_queue.put({'type': 'selenium_install'})
                return
            
            is_installed, chrome_path = self.is_chrome_installed()
            if not is_installed:
                print("✗ Chrome not found")
                self.message_queue.put({
                    'type': 'error',
                    'text': 'Chrome not found!\n\nPlease install Google Chrome.'
                })
                return
            
            print(f"✓ Chrome: {chrome_path}")
            self.message_queue.put({'type': 'progress', 'text': 'Chrome detected!'})
            time.sleep(0.5)
            
            print("\n--- Initializing Chrome ---")
            self.message_queue.put({'type': 'progress', 'text': 'Starting Chrome...'})
            
            try:
                driver = self.get_chrome_driver()
                print("✓ Chrome started")
                self.message_queue.put({'type': 'progress', 'text': '✓ Browser opened!'})
                time.sleep(1)
            except Exception as e:
                print(f"✗ Chrome start failed: {e}")
                error_text = str(e)
                if len(error_text) > 300:
                    error_text = error_text[:300] + "..."
                self.message_queue.put({
                    'type': 'error',
                    'text': f'Could not start Chrome:\n\n{error_text}\n\nTry manual method instead.'
                })
                return
            
            print("\n--- Loading Portal ---")
            self.message_queue.put({'type': 'progress', 'text': 'Opening FlairsTech portal...'})
            
            try:
                driver.set_page_load_timeout(30)
                driver.get("https://attendance.flairstech.com")
                print("✓ Portal loaded")
                self.message_queue.put({'type': 'progress', 'text': '✓ Portal loaded!'})
                time.sleep(2)
            except TimeoutException:
                print("✗ Page load timeout")
                if driver:
                    driver.quit()
                self.message_queue.put({
                    'type': 'error',
                    'text': 'Portal took too long to load.\n\nCheck your internet connection.'
                })
                return
            except Exception as e:
                print(f"✗ Portal load failed: {e}")
                if driver:
                    driver.quit()
                self.message_queue.put({
                    'type': 'error',
                    'text': f'Could not load portal:\n\n{str(e)[:200]}'
                })
                return
            
            print("\n--- Waiting for Token ---")
            self.message_queue.put({'type': 'progress', 'text': '⏳ Please log in...'})
            
            token = None
            timeout = 300
            start_time = time.time()
            check_count = 0
            
            while not token and (time.time() - start_time) < timeout:
                try:
                    token = driver.execute_script("""
                        return localStorage.getItem('access_token') || 
                               sessionStorage.getItem('access_token');
                    """)
                    
                    if token and token.strip():
                        print(f"✓ Token found! ({len(token)} chars)")
                        self.message_queue.put({'type': 'progress', 'text': '✓ Token captured!'})
                        break
                    
                    check_count += 1
                    if check_count % 8 == 0:
                        elapsed = int(time.time() - start_time)
                        remaining = int((timeout - elapsed) / 60)
                        self.message_queue.put({
                            'type': 'progress',
                            'text': f'⏳ Waiting for login... ({remaining} min left)'
                        })
                        print(f"[{elapsed}s] Still waiting...")
                    
                    time.sleep(2)
                
                except WebDriverException:
                    print("✗ Browser closed by user")
                    break
                except Exception as e:
                    print(f"✗ Check error: {e}")
                    time.sleep(2)
            
            if driver:
                try:
                    print("\n--- Closing Browser ---")
                    driver.quit()
                    print("✓ Browser closed")
                except:
                    pass
            
            if token and token.strip():
                print("\n✓✓✓ SUCCESS ✓✓✓")
                self.token = token
                self.message_queue.put({'type': 'success'})
            else:
                print("\n✗ Timeout - no token captured")
                self.message_queue.put({'type': 'timeout'})
        
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            
            self.message_queue.put({
                'type': 'error',
                'text': f'An error occurred:\n\n{str(e)[:200]}\n\nPlease try manual method.'
            })
        finally:
            self.is_processing = False
            print("\n" + "="*60)
            print("WORKER FINISHED")
            print("="*60 + "\n")
    
    def show_capture_timeout(self):
        """Timeout"""
        self.is_processing = False
        response = messagebox.askyesno(
            "Setup Timeout",
            "No login detected within 5 minutes.\n\n"
            "Would you like to try again?",
            icon='warning'
        )
        
        if response:
            self.show_login_screen()
        else:
            self.show_manual_token_entry()
    
    def show_manual_token_entry(self):
        """Manual token entry screen"""
        self.clear_screen()
        self.is_processing = False
        
        header_frame = tk.Frame(self.root, bg=COLOR_BLUE, height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Manual Token Entry", font=('Arial', 16, 'bold'),
                bg=COLOR_BLUE, fg=COLOR_WHITE).pack(pady=25)
        
        content_frame = tk.Frame(self.root, bg=COLOR_WHITE)
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        tk.Button(content_frame, text="📖 Open Detailed Instructions",
                 font=('Arial', 11, 'bold'), bg=COLOR_PURPLE, fg=COLOR_WHITE,
                 padx=20, pady=10, border=0, cursor='hand2',
                 command=self.open_manual_instructions_webpage).pack(pady=10)
        
        instructions = tk.Text(content_frame, height=13, font=('Consolas', 9),
                              wrap='word', bg='#F3F4F6', relief='solid', bd=1)
        instructions.pack(fill='both', expand=True, pady=10)
        
        instructions_text = """
QUICK STEPS:

1. Open https://attendance.flairstech.com and log in

2. Press F12 to open Developer Tools

3. Click "Console" tab

4. Paste this command and press Enter:
   copy(localStorage.getItem('access_token'))

5. Your token is copied! Paste it below.

(The token is usually 500+ characters long and starts with "eyJ")
"""
        
        instructions.insert('1.0', instructions_text)
        instructions.config(state='disabled')
        
        tk.Label(content_frame, text="Paste your token here:",
                font=('Arial', 10, 'bold'), bg=COLOR_WHITE, fg='#374151').pack(pady=(10, 5))
        
        token_entry = tk.Text(content_frame, height=4, font=('Consolas', 9), wrap='word')
        token_entry.pack(fill='x', pady=5)
        
        self.error_label = tk.Label(content_frame, text="", font=('Arial', 9),
                                    bg=COLOR_WHITE, fg=COLOR_ERROR)
        self.error_label.pack(pady=5)
        
        btn_frame = tk.Frame(content_frame, bg=COLOR_WHITE)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="✓ Submit Token", font=('Arial', 11, 'bold'),
                 bg=COLOR_SUCCESS, fg=COLOR_WHITE, padx=30, pady=10, border=0,
                 cursor='hand2',
                 command=lambda: self.validate_manual_token(token_entry.get('1.0', 'end-1c'))).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Back", font=('Arial', 10),
                 bg='#E5E7EB', fg='#374151', padx=20, pady=10, border=0,
                 cursor='hand2', command=self.show_login_screen).pack(side='left', padx=5)
    
    def open_manual_instructions_webpage(self):
        """Open detailed instructions"""
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>FlairsTech - Token Instructions</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 900px;
            margin: 30px auto;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #8B5CF6;
            border-bottom: 3px solid #8B5CF6;
            padding-bottom: 15px;
        }
        .step {
            background: #F3F4F6;
            padding: 20px;
            margin: 20px 0;
            border-left: 5px solid #3B82F6;
            border-radius: 8px;
        }
        .step-number {
            display: inline-block;
            background: #3B82F6;
            color: white;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            text-align: center;
            line-height: 35px;
            font-weight: bold;
            margin-right: 15px;
            font-size: 18px;
        }
        .code-box {
            background: #1F2937;
            color: #10B981;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            cursor: pointer;
            border: 2px solid #374151;
            margin: 10px 0;
            user-select: all;
        }
        .code-box:hover {
            border-color: #10B981;
        }
        .note {
            background: #FEF3C7;
            padding: 15px;
            border-left: 4px solid #F59E0B;
            margin: 15px 0;
            border-radius: 5px;
        }
        .success {
            background: #D1FAE5;
            padding: 15px;
            border-left: 4px solid #10B981;
            margin: 15px 0;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Token Capture - Step by Step</h1>
        
        <div class="step">
            <strong><span class="step-number">1</span> Open Attendance Portal</strong>
            <p>Go to: <a href="https://attendance.flairstech.com" target="_blank" style="color:#3B82F6; font-size:16px;">https://attendance.flairstech.com</a></p>
            <p>Log in with your Microsoft account if needed.</p>
        </div>
        
        <div class="step">
            <strong><span class="step-number">2</span> Open Developer Tools</strong>
            <p>Press <kbd style="background:#E5E7EB; padding:5px 10px; border-radius:5px; font-family:monospace;">F12</kbd> on your keyboard</p>
        </div>
        
        <div class="step">
            <strong><span class="step-number">3</span> Go to Console Tab</strong>
            <p>Click the <strong>"Console"</strong> tab at the top of Developer Tools.</p>
        </div>
        
        <div class="step">
            <strong><span class="step-number">4</span> Run This Command</strong>
            <p>Click the code below to select it, then copy (Ctrl+C):</p>
            <div class="code-box" onclick="this.select(); document.execCommand('copy'); alert('✓ Copied! Now paste in Console and press Enter')">copy(localStorage.getItem('access_token'))</div>
            <p>Paste it in the Console and press Enter.</p>
            <div class="success">
                ✓ You'll see "undefined" - that's perfect! Your token is now copied to clipboard.
            </div>
        </div>
        
        <div class="step">
            <strong><span class="step-number">5</span> Paste in Setup Window</strong>
            <p>Go back to the FlairsTech Setup window and paste the token (Ctrl+V).</p>
        </div>
        
        <div class="note">
            <strong>💡 Important:</strong>
            <ul>
                <li>Token is 500-1000 characters long (very long!)</li>
                <li>Starts with "eyJ"</li>
                <li>If you see "null", refresh the page and try again</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
        
        import tempfile
        temp_file = os.path.join(tempfile.gettempdir(), 'flairstech_instructions.html')
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        webbrowser.open('file://' + temp_file)
        messagebox.showinfo("Instructions Opened",
                           "Instructions have been opened in your browser.\n\n"
                           "Follow the steps, then come back to paste your token.")
    
    def validate_manual_token(self, token):
        """Validate manually entered token"""
        token = token.strip()
        
        if token.lower().startswith('bearer '):
            token = token[7:].strip()
        
        if not token:
            self.error_label.config(text="⚠️ Please paste your token!")
            return
        
        if len(token) < 100:
            self.error_label.config(text=f"⚠️ Token too short! Expected 500+, got {len(token)} chars")
            return
        
        if not token.startswith('eyJ'):
            self.error_label.config(text="⚠️ Invalid format! Token should start with 'eyJ'")
            return
        
        self.token = token
        self.error_label.config(text="")
        self.fetch_locations()
    
    def fetch_locations(self):
        """Fetch user's locations"""
        self.show_progress_screen("Fetching Locations", "Getting your office locations...")
        threading.Thread(target=self._fetch_locations_worker, daemon=True).start()
    
    def _fetch_locations_worker(self):
        """Fetch locations from API"""
        try:
            headers = {
                "authorization": f"Bearer {self.token}",
                "tenant-key": "flairstech"
            }
            
            endpoints = [
                "https://apiattendance.flairstech.com/api/Locations/GetMyLocationsFilteredByStatus?pageSize=1000&locationStatus=1",
                "https://apiattendance.flairstech.com/api/Locations/GetMyLocations?pageSize=1000"
            ]
            
            all_locations = []
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        result = data.get('result', {})
                        
                        if isinstance(result, dict):
                            items = result.get('records', result.get('items', []))
                        elif isinstance(result, list):
                            items = result
                        else:
                            items = []
                        
                        for loc in items:
                            if loc not in all_locations:
                                all_locations.append(loc)
                except:
                    continue
            
            if all_locations:
                self.locations = all_locations
                self.root.after(100, self.show_location_selection)
            else:
                self.root.after(100, lambda: self.show_error(
                    "No locations found.\n\n"
                    "Please add a location at:\n"
                    "https://attendance.flairstech.com"
                ))
        
        except Exception as e:
            self.root.after(100, lambda: self.show_error(f"Network error: {str(e)}"))
    
    def show_location_selection(self):
        """Location selection screen"""
        self.clear_screen()
        self.selected_location_index = 0
        
        header_frame = tk.Frame(self.root, bg=COLOR_PURPLE, height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Select Your Office Location",
                font=('Arial', 16, 'bold'), bg=COLOR_PURPLE, fg=COLOR_WHITE).pack(pady=25)
        
        content_frame = tk.Frame(self.root, bg=COLOR_WHITE)
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        tk.Label(content_frame, text=f"Found {len(self.locations)} location(s)",
                font=('Arial', 11), bg=COLOR_WHITE, fg='#6B7280').pack(pady=10)
        
        list_frame = tk.Frame(content_frame, bg=COLOR_WHITE)
        list_frame.pack(fill='both', expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.location_listbox = tk.Listbox(list_frame, font=('Arial', 11),
                                           yscrollcommand=scrollbar.set, height=10)
        self.location_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.location_listbox.yview)
        
        for loc in self.locations:
            name = loc.get('name', 'Unnamed')
            status = loc.get('status', loc.get('locationStatus', 1))
            status_text = " [APPROVED]" if status == 1 else " [PENDING]"
            self.location_listbox.insert(tk.END, f"  {name}{status_text}")
        
        self.location_listbox.select_set(0)
        
        def on_select(event):
            selection = self.location_listbox.curselection()
            if selection:
                self.selected_location_index = selection[0]
        
        self.location_listbox.bind('<<ListboxSelect>>', on_select)
        
        tk.Button(content_frame, text="Continue", font=('Arial', 12, 'bold'),
                 bg=COLOR_BLUE, fg=COLOR_WHITE, padx=40, pady=12, border=0,
                 cursor='hand2', command=self.validate_and_continue).pack(pady=20)
    
    def validate_and_continue(self):
        """Validate selection and continue"""
        if not hasattr(self, 'selected_location_index'):
            messagebox.showwarning("No Selection", "Please select a location")
            return
        
        if self.selected_location_index < 0 or self.selected_location_index >= len(self.locations):
            messagebox.showwarning("Invalid Selection", "Please select a valid location")
            return
        
        self.selected_location = self.locations[self.selected_location_index]
        self.show_startup_options()
    
    def show_startup_options(self):
        """Ask about Windows startup"""
        self.clear_screen()
        
        header_frame = tk.Frame(self.root, bg=COLOR_BLUE, height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Startup Options", font=('Arial', 16, 'bold'),
                bg=COLOR_BLUE, fg=COLOR_WHITE).pack(pady=25)
        
        content_frame = tk.Frame(self.root, bg=COLOR_WHITE)
        content_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        tk.Label(content_frame, text="Launch FlairsTech on Windows Startup?",
                font=('Arial', 14, 'bold'), bg=COLOR_WHITE, fg=COLOR_DARK_BLUE).pack(pady=20)
        
        tk.Label(content_frame,
                text="If enabled, FlairsTech Attendance will start automatically\n"
                     "when you turn on your computer.\n\nRecommended for daily use.",
                font=('Arial', 11), bg=COLOR_WHITE, fg='#4B5563', justify='center').pack(pady=10)
        
        location_frame = tk.Frame(content_frame, bg='#EEF2FF', relief='solid', bd=1)
        location_frame.pack(fill='x', pady=20)
        
        tk.Label(location_frame, text="📍 Selected Location:",
                font=('Arial', 10, 'bold'), bg='#EEF2FF', fg=COLOR_DARK_BLUE).pack(anchor='w', padx=15, pady=(10, 5))
        
        tk.Label(location_frame, text=self.selected_location.get('name', 'Unknown'),
                font=('Arial', 11), bg='#EEF2FF', fg='#4B5563').pack(anchor='w', padx=25, pady=(0, 10))
        
        self.startup_var = tk.BooleanVar(value=True)
        
        checkbox_frame = tk.Frame(content_frame, bg='#F3F4F6', relief='solid', bd=1)
        checkbox_frame.pack(pady=20, padx=50, fill='x')
        
        tk.Checkbutton(checkbox_frame, text="✓ Launch on Windows startup",
                      font=('Arial', 11), bg='#F3F4F6', variable=self.startup_var,
                      activebackground='#F3F4F6').pack(pady=15, padx=20)
        
        tk.Label(content_frame, text="You can change this later in Windows Startup settings",
                font=('Arial', 9), bg=COLOR_WHITE, fg='#9CA3AF').pack(pady=10)
        
        btn_frame = tk.Frame(content_frame, bg=COLOR_WHITE)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Complete Setup", font=('Arial', 12, 'bold'),
                 bg=COLOR_PURPLE, fg=COLOR_WHITE, padx=40, pady=12, border=0,
                 cursor='hand2', command=self.save_configuration).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Back", font=('Arial', 10),
                 bg='#E5E7EB', fg='#374151', padx=20, pady=10, border=0,
                 cursor='hand2', command=self.show_location_selection).pack(side='left', padx=5)
    
    def save_configuration(self):
        """Save configuration"""
        if not hasattr(self, 'selected_location') or not self.selected_location:
            messagebox.showerror("Error", "No location selected. Please go back.")
            return
        
        self.show_progress_screen("Installing", "Finalizing installation...")
        threading.Thread(target=self._save_config_worker, args=(self.selected_location,), daemon=True).start()
    
    def _save_config_worker(self, location):
        """Save config files"""
        try:
            print("\n" + "="*60)
            print("SAVING CONFIGURATION FILES")
            print("="*60)
            
            token_data = {
                "bearer_token": self.token,
                "token_expiry": int(time.time()) + 43200
            }
            
            config_data = {
                "place_id": location.get('id', ''),
                "place_name": location.get('name', 'Unknown'),
                "latitude": location.get('latitude', 0),
                "longitude": location.get('longitude', 0),
                "auto_check_in_time": "08:00",
                "auto_check_out_time": "17:00",
                "enable_auto_check_in": False,
                "enable_auto_check_out": False,
                "notifications": True,
                "all_locations": self.locations,
                "shift_start_time": "09:00",
                "shift_end_time": "18:00"
            }
            
            break_data = {
                "date": datetime.now().date().isoformat(),
                "used_minutes": 0,
                "history": [],
                "is_on_break": False,
                "break_start_time": None
            }
            
            with open(os.path.join(self.install_dir, 'token.json'), 'w') as f:
                json.dump(token_data, f, indent=2)
            print("✓ token.json saved")
            
            with open(os.path.join(self.install_dir, 'config.json'), 'w') as f:
                json.dump(config_data, f, indent=2)
            print("✓ config.json saved")
            
            with open(os.path.join(self.install_dir, 'break_data.json'), 'w') as f:
                json.dump(break_data, f, indent=2)
            print("✓ break_data.json saved")
            
            if self.startup_var.get():
                self.create_startup_shortcuts()
            
            time.sleep(1)
            self.root.after(100, self.show_completion)
        
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.root.after(100, lambda: self.show_error(f"Installation failed: {str(e)}"))
    
    def create_startup_shortcuts(self):
        """Create Windows startup shortcuts"""
        try:
            if sys.platform != 'win32':
                return
            
            startup_folder = os.path.join(
                os.environ['APPDATA'],
                'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
            )
            
            bat_content = f'''@echo off
cd /d "{self.install_dir}"
start "" pythonw "{os.path.join(self.install_dir, 'run_apps.py')}"
'''
            
            bat_path = os.path.join(startup_folder, 'FlairsTech_Startup.bat')
            with open(bat_path, 'w') as f:
                f.write(bat_content)
            
            print("✓ Startup script created")
        
        except Exception as e:
            print(f"Could not create startup shortcuts: {e}")
    
    def show_completion(self):
        """Installation complete screen"""
        self.clear_screen()
        
        header_frame = tk.Frame(self.root, bg=COLOR_SUCCESS, height=150)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        canvas = tk.Canvas(header_frame, width=80, height=80, bg=COLOR_SUCCESS, highlightthickness=0)
        canvas.pack(pady=20)
        canvas.create_oval(5, 5, 75, 75, fill=COLOR_WHITE, outline='')
        canvas.create_line(20, 40, 35, 55, width=6, fill=COLOR_SUCCESS, smooth=True)
        canvas.create_line(35, 55, 60, 25, width=6, fill=COLOR_SUCCESS, smooth=True)
        
        tk.Label(header_frame, text="Installation Complete!", font=('Arial', 18, 'bold'),
                bg=COLOR_SUCCESS, fg=COLOR_WHITE).pack()
        
        content_frame = tk.Frame(self.root, bg=COLOR_WHITE)
        content_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        tk.Label(content_frame,
                text="✓ Token saved (valid for 12 hours)\n"
                     "✓ Location configured\n"
                     "✓ Break tracker initialized\n"
                     "✓ Settings saved\n"
                     "✓ Startup shortcuts created",
                font=('Arial', 12), bg=COLOR_WHITE, fg='#059669', justify='left').pack(pady=20)
        
        tk.Label(content_frame, text="FlairsTech Attendance is ready to use!",
                font=('Arial', 14, 'bold'), bg=COLOR_WHITE, fg=COLOR_DARK_BLUE).pack(pady=10)
        
        info_frame = tk.Frame(content_frame, bg='#F3F4F6', relief='solid', bd=1)
        info_frame.pack(fill='x', pady=20)
        
        tk.Label(info_frame, text="ℹ️ How to Run",
                font=('Arial', 11, 'bold'), bg='#F3F4F6', fg=COLOR_DARK_BLUE).pack(anchor='w', padx=15, pady=(10, 5))
        
        info_text = [
            "• Run: python run_apps.py",
            "• Or double-click run_apps.bat",
            "• Config files saved in: " + self.install_dir[:40],
            "• Token expires every 12 hours",
            "• To refresh token: Run this installer again"
        ]
        
        for info in info_text:
            tk.Label(info_frame, text=info, font=('Arial', 9),
                    bg='#F3F4F6', fg='#4B5563', justify='left').pack(anchor='w', padx=25, pady=2)
        
        tk.Label(info_frame, text="", bg='#F3F4F6').pack(pady=5)
        
        btn_frame = tk.Frame(content_frame, bg=COLOR_WHITE)
        btn_frame.pack(pady=20, fill='x')
        
        tk.Button(btn_frame, text="✓ Done", font=('Arial', 14, 'bold'),
                 bg=COLOR_PURPLE, fg=COLOR_WHITE, padx=40, pady=18, border=0,
                 cursor='hand2', command=self.root.quit,
                 activebackground='#7C3AED').pack(pady=10)
    
    def show_progress_screen(self, title, message):
        """Show progress screen"""
        self.clear_screen()
        
        header_frame = tk.Frame(self.root, bg=COLOR_BLUE, height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=title, font=('Arial', 16, 'bold'),
                bg=COLOR_BLUE, fg=COLOR_WHITE).pack(pady=25)
        
        content_frame = tk.Frame(self.root, bg=COLOR_WHITE)
        content_frame.pack(fill='both', expand=True, padx=40, pady=50)
        
        self.progress_label = tk.Label(content_frame, text=message,
                                       font=('Arial', 12), bg=COLOR_WHITE, fg='#4B5563')
        self.progress_label.pack(pady=20)
        
        self.progress_bar = ttk.Progressbar(content_frame, length=400, mode='indeterminate')
        self.progress_bar.pack(pady=20)
        self.progress_bar.start()
    
    def show_error(self, message):
        """Show error screen"""
        self.is_processing = False
        self.clear_screen()
        
        header_frame = tk.Frame(self.root, bg=COLOR_ERROR, height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Setup Error", font=('Arial', 16, 'bold'),
                bg=COLOR_ERROR, fg=COLOR_WHITE).pack(pady=25)
        
        content_frame = tk.Frame(self.root, bg=COLOR_WHITE)
        content_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        tk.Label(content_frame, text=message, font=('Arial', 11),
                bg=COLOR_WHITE, fg='#4B5563', wraplength=500, justify='center').pack(pady=30)
        
        btn_frame = tk.Frame(content_frame, bg=COLOR_WHITE)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Try Again", font=('Arial', 11, 'bold'),
                 bg=COLOR_BLUE, fg=COLOR_WHITE, padx=30, pady=10, border=0,
                 cursor='hand2', command=self.show_login_screen).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Exit", font=('Arial', 10),
                 bg='#E5E7EB', fg='#374151', padx=20, pady=10, border=0,
                 cursor='hand2', command=self.root.quit).pack(side='left', padx=5)
    
    def clear_screen(self):
        """Clear all widgets"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def run(self):
        """Start installer"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.mainloop()


if __name__ == '__main__':
    installer = FlairsTechInstaller()
    installer.run()