# widget.py - Production Version with Fixed API Parsing
import tkinter as tk
from tkinter import messagebox
import json
import time
import requests
import threading
from datetime import datetime
import subprocess
import sys
import os

COLOR_PURPLE = '#8B5CF6'
COLOR_BLUE = '#3B82F6'
COLOR_DARK_BLUE = '#1E40AF'
COLOR_LIGHT_BLUE = '#60A5FA'
COLOR_WHITE = '#FFFFFF'
COLOR_BG_DARK = '#1E293B'
COLOR_SUCCESS = '#10B981'
COLOR_WARNING = '#F59E0B'
COLOR_ERROR = '#EF4444'

# Set working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

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

class AttendanceWidget:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("FlairsTech Attendance")
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
        
        width = 320
        height = 400
        x = self.window.winfo_screenwidth() - width - 20
        y = 100
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        self.window.bind('<Button-1>', self.start_move)
        self.window.bind('<B1-Motion>', self.on_move)
        
        if not self.check_files():
            return
        
        self.config = self.load_config()
        self.token_data = self.load_token()
        self.break_data = self.load_break_data()
        
        self.checked_in = False
        self.actual_check_in_time = None
        self.actual_check_out_time = None
        
        self.create_ui()
        self.start_updates()
    
    def check_files(self):
        """Check required files"""
        config_path = get_file_path('config.json')
        token_path = get_file_path('token.json')
        
        if not os.path.exists(config_path) or not os.path.exists(token_path):
            messagebox.showerror(
                "Setup Required",
                f"Config files missing!\n\nSearched in:\n{SCRIPT_DIR}\n\nRun the installer."
            )
            sys.exit(1)
        return True
    
    def load_config(self):
        try:
            with open(get_file_path('config.json'), 'r') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Config Error", f"Could not load config:\n{e}")
            sys.exit(1)
    
    def load_token(self):
        try:
            with open(get_file_path('token.json'), 'r') as f:
                data = json.load(f)
                if data.get('token_expiry', 0) > time.time():
                    return data
        except:
            pass
        return None
    
    def load_break_data(self):
        try:
            with open(get_file_path('break_data.json'), 'r') as f:
                data = json.load(f)
                if data.get('date') == datetime.now().date().isoformat():
                    return data
        except:
            pass
        
        return {
            'date': datetime.now().date().isoformat(),
            'used_minutes': 0,
            'history': [],
            'is_on_break': False,
            'break_start_time': None
        }
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")
    
    def create_ui(self):
        main_frame = tk.Frame(self.window, bg=COLOR_BG_DARK, relief='raised', bd=2)
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header = tk.Frame(main_frame, bg=COLOR_PURPLE, height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="FlairsTech Attendance", bg=COLOR_PURPLE, fg=COLOR_WHITE,
                font=('Arial', 11, 'bold')).pack(side='left', padx=15, pady=10)
        
        close_btn = tk.Button(header, text="✕", bg=COLOR_PURPLE, fg=COLOR_WHITE,
                             bd=0, font=('Arial', 14, 'bold'), cursor='hand2',
                             command=self.minimize_widget, activebackground=COLOR_ERROR)
        close_btn.pack(side='right', padx=10)
        
        # Time
        self.time_label = tk.Label(main_frame, text="--:--:--", bg=COLOR_BG_DARK,
                                   fg=COLOR_LIGHT_BLUE, font=('Arial', 32, 'bold'))
        self.time_label.pack(pady=15)
        
        # Check-in time
        self.checkin_time_label = tk.Label(main_frame, text="Not Checked In",
                                           bg=COLOR_BG_DARK, fg='#94A3B8', font=('Arial', 9))
        self.checkin_time_label.pack(pady=2)
        
        # Status
        self.status_label = tk.Label(main_frame, text="● Connecting...",
                                     bg=COLOR_BG_DARK, fg=COLOR_WARNING, font=('Arial', 10, 'bold'))
        self.status_label.pack(pady=5)
        
        # Location
        location_name = self.config.get('place_name', 'Unknown')[:28]
        self.location_label = tk.Label(main_frame, text=f"📍 {location_name}",
                                       bg=COLOR_BG_DARK, fg='#94A3B8', font=('Arial', 8))
        self.location_label.pack(pady=2)
        
        # Separator
        tk.Frame(main_frame, bg='#334155', height=1).pack(fill='x', padx=20, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg=COLOR_BG_DARK)
        btn_frame.pack(pady=8)
        
        tk.Button(btn_frame, text="Check In", bg=COLOR_SUCCESS, fg=COLOR_WHITE,
                 font=('Arial', 10, 'bold'), bd=0, padx=22, pady=10, cursor='hand2',
                 command=self.check_in, activebackground='#059669').grid(row=0, column=0, padx=5)
        
        tk.Button(btn_frame, text="Check Out", bg=COLOR_ERROR, fg=COLOR_WHITE,
                 font=('Arial', 10, 'bold'), bd=0, padx=20, pady=10, cursor='hand2',
                 command=self.check_out, activebackground='#DC2626').grid(row=0, column=1, padx=5)
        
        # Break button
        self.break_btn = tk.Button(main_frame, text="☕ Take a Break",
                                   bg=COLOR_WARNING, fg=COLOR_WHITE,
                                   font=('Arial', 11, 'bold'), bd=0, padx=30, pady=12,
                                   cursor='hand2', command=self.toggle_break,
                                   activebackground='#D97706')
        self.break_btn.pack(pady=10, padx=20, fill='x')
        
        # Break time
        remaining = 60 - self.break_data.get('used_minutes', 0)
        self.break_label = tk.Label(main_frame, text=f"Break: {remaining}/60 min left",
                                    bg=COLOR_BG_DARK, fg='#94A3B8', font=('Arial', 9))
        self.break_label.pack(pady=5)
        
        # Bottom buttons
        bottom_frame = tk.Frame(main_frame, bg=COLOR_BG_DARK)
        bottom_frame.pack(pady=10)
        
        tk.Button(bottom_frame, text="🔄 Refresh", bg=COLOR_BLUE, fg=COLOR_WHITE,
                 font=('Arial', 9, 'bold'), bd=0, padx=15, pady=6, cursor='hand2',
                 command=self.force_update, activebackground=COLOR_DARK_BLUE).pack(side='left', padx=5)
        
        tk.Button(bottom_frame, text="⚙ Setup", bg='#475569', fg=COLOR_WHITE,
                 font=('Arial', 9), bd=0, padx=15, pady=6, cursor='hand2',
                 command=self.open_setup, activebackground='#334155').pack(side='left', padx=5)
    
    def fetch_live_data(self):
        """Fetch status from API"""
        if not self.token_data:
            self.status_label.config(text="● No Token", fg=COLOR_ERROR)
            return False
        
        if self.token_data.get('token_expiry', 0) < time.time():
            self.status_label.config(text="● Token Expired", fg=COLOR_ERROR)
            return False
        
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
                    
                    last_checkin = check_ins[-1]
                    checkin_time_str = last_checkin.get('creationTime', '')
                    
                    try:
                        self.actual_check_in_time = datetime.fromisoformat(
                            checkin_time_str.replace('Z', '+00:00').split('.')[0]
                        )
                        time_str = self.actual_check_in_time.strftime('%I:%M %p')
                        self.checkin_time_label.config(text=f"Checked in at {time_str}", fg=COLOR_SUCCESS)
                    except:
                        self.actual_check_in_time = datetime.now()
                        self.checkin_time_label.config(text="Checked in", fg=COLOR_SUCCESS)
                    
                    self.status_label.config(text="● Checked In", fg=COLOR_SUCCESS)
                    self.actual_check_out_time = None
                else:
                    self.checked_in = False
                    self.actual_check_in_time = None
                    self.status_label.config(text="● Not Checked In", fg='#94A3B8')
                    self.checkin_time_label.config(text="No check-ins today", fg='#94A3B8')
                
                # Update break data
                self.break_data = self.load_break_data()
                used = self.break_data.get('used_minutes', 0)
                remaining = 60 - used
                is_on_break = self.break_data.get('is_on_break', False)
                
                if is_on_break:
                    self.break_btn.config(text="⏸ End Break", bg=COLOR_ERROR)
                    self.break_label.config(text=f"Break: {remaining}/60 min (ON BREAK)")
                else:
                    self.break_btn.config(text="☕ Take a Break", bg=COLOR_WARNING)
                    self.break_label.config(text=f"Break: {remaining}/60 min left")
                
                return True
            elif response.status_code == 401:
                self.status_label.config(text="● Token Expired", fg=COLOR_ERROR)
                return False
            else:
                self.status_label.config(text="● API Error", fg=COLOR_ERROR)
                return False
        except:
            self.status_label.config(text="● Connection Error", fg=COLOR_ERROR)
            return False
    
    def update_time_display(self):
        """Update timer"""
        if self.checked_in and self.actual_check_in_time:
            elapsed = datetime.now() - self.actual_check_in_time
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            seconds = int(elapsed.total_seconds() % 60)
            self.time_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}", fg=COLOR_SUCCESS)
        else:
            self.time_label.config(text="--:--:--", fg=COLOR_LIGHT_BLUE)
        
        self.window.after(1000, self.update_time_display)
    
    def update_status_periodic(self):
        """Periodic refresh"""
        self.fetch_live_data()
        self.window.after(30000, self.update_status_periodic)
    
    def force_update(self):
        """Manual refresh"""
        self.status_label.config(text="● Refreshing...", fg=COLOR_BLUE)
        self.window.update()
        success = self.fetch_live_data()
        if success:
            messagebox.showinfo("Refreshed", "Status updated")
        else:
            messagebox.showwarning("Failed", "Could not connect")
    
    def check_in(self):
        """Check in"""
        if not self.token_data:
            messagebox.showwarning("No Token", "Run Setup first")
            return
        
        if self.checked_in:
            messagebox.showinfo("Already Checked In", "You're already checked in")
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
            response = requests.post(
                "https://apiattendance.flairstech.com/api/CheckInOuts",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Checked in successfully!")
                time.sleep(1)
                self.fetch_live_data()
            else:
                error = response.json().get('error', {}).get('message', 'Unknown error')
                messagebox.showerror("Failed", error)
        except Exception as e:
            messagebox.showerror("Error", f"Network error:\n{str(e)}")
    
    def check_out(self):
        """Check out"""
        if not self.checked_in:
            messagebox.showwarning("Not Checked In", "Check in first")
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
            response = requests.post(
                "https://apiattendance.flairstech.com/api/CheckInOuts",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Checked out successfully!")
                time.sleep(1)
                self.fetch_live_data()
            else:
                error = response.json().get('error', {}).get('message', 'Unknown error')
                messagebox.showerror("Failed", error)
        except Exception as e:
            messagebox.showerror("Error", f"Network error:\n{str(e)}")
    
    def toggle_break(self):
        """Toggle break"""
        if not self.checked_in:
            messagebox.showwarning("Not Checked In", "Check in first")
            return
        
        try:
            break_path = get_file_path('break_data.json')
            with open(break_path, 'r') as f:
                break_data = json.load(f)
            
            if break_data.get('is_on_break', False):
                # End break
                break_start = datetime.fromisoformat(break_data['break_start_time'])
                duration = int((datetime.now() - break_start).total_seconds() / 60)
                
                break_data['used_minutes'] = break_data.get('used_minutes', 0) + duration
                break_data['is_on_break'] = False
                break_data['break_start_time'] = None
                
                with open(break_path, 'w') as f:
                    json.dump(break_data, f, indent=2)
                
                remaining = 60 - break_data['used_minutes']
                self.break_label.config(text=f"Break: {remaining}/60 min left")
                self.break_btn.config(text="☕ Take a Break", bg=COLOR_WARNING)
                
                messagebox.showinfo("Break Ended", f"Used {duration} minutes.\nRemaining: {remaining} min")
            else:
                # Start break
                used = break_data.get('used_minutes', 0)
                if used >= 60:
                    messagebox.showwarning("Limit Reached", "You've used all 60 minutes today")
                    return
                
                break_data['is_on_break'] = True
                break_data['break_start_time'] = datetime.now().isoformat()
                break_data['date'] = datetime.now().date().isoformat()
                
                with open(break_path, 'w') as f:
                    json.dump(break_data, f, indent=2)
                
                remaining = 60 - used
                self.break_btn.config(text="⏸ End Break", bg=COLOR_ERROR)
                self.break_label.config(text=f"Break: {remaining}/60 min (ON BREAK)")
                
                messagebox.showinfo("Break Started", f"You have {remaining} minutes remaining")
        except Exception as e:
            messagebox.showerror("Error", f"Break error:\n{str(e)}")
    
    def open_setup(self):
        """Open setup"""
        installer_path = get_file_path('FlairsTech-Installer.exe')
        if os.path.exists(installer_path):
            subprocess.Popen([installer_path])
            messagebox.showinfo("Setup Opened", "After setup, restart widget")
        else:
            messagebox.showerror("Not Found", "Installer not found")
    
    def minimize_widget(self):
        """Minimize to restore button"""
        self.window.withdraw()
        
        restore = tk.Tk()
        restore.title("FlairsTech")
        restore.geometry("140x50+1740+10")
        restore.attributes('-topmost', True)
        
        tk.Button(restore, text="📊 Show Widget",
                 command=lambda: [restore.destroy(), self.window.deiconify()],
                 bg=COLOR_PURPLE, fg=COLOR_WHITE, font=('Arial', 10, 'bold'),
                 bd=0, cursor='hand2').pack(expand=True, fill='both')
    
    def start_updates(self):
        """Start updates"""
        self.fetch_live_data()
        self.update_time_display()
        self.update_status_periodic()
    
    def run(self):
        """Run widget"""
        self.window.mainloop()

if __name__ == '__main__':
    try:
        widget = AttendanceWidget()
        widget.run()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Widget failed:\n\n{str(e)}")