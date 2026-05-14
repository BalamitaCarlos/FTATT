# app.py - FlairsTech Attendance with Break Management and Activity Monitoring
import pystray
import json
import time
import requests
import threading
import webbrowser
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from pystray import MenuItem as item
import subprocess
import os
import sys
import tkinter as tk
from tkinter import Toplevel, Listbox, Button, Label, SINGLE, messagebox, Frame

class BreakTracker:
    """Tracks break time usage"""
    def __init__(self):
        self.max_break_minutes = 60  # 1 hour per day
        self.used_break_minutes = 0
        self.break_start_time = None
        self.is_on_break = False
        self.break_history = []
        self.last_reset_date = datetime.now().date()
        self.load_break_data()
    
    def load_break_data(self):
        """Load break data from file"""
        try:
            with open('break_data.json', 'r') as f:
                data = json.load(f)
                saved_date = datetime.fromisoformat(data.get('date', '')).date()
                
                # Reset if it's a new day
                if saved_date == datetime.now().date():
                    self.used_break_minutes = data.get('used_minutes', 0)
                    self.break_history = data.get('history', [])
                else:
                    self.reset_daily()
        except:
            self.reset_daily()
    
    def save_break_data(self):
        """Save break data to file"""
        data = {
            'date': datetime.now().date().isoformat(),
            'used_minutes': self.used_break_minutes,
            'history': self.break_history
        }
        with open('break_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def reset_daily(self):
        """Reset break counter for new day"""
        self.used_break_minutes = 0
        self.break_history = []
        self.is_on_break = False
        self.break_start_time = None
        self.save_break_data()
    
    def start_break(self):
        """Start a break"""
        if self.is_on_break:
            return False, "Already on break"
        
        if self.used_break_minutes >= self.max_break_minutes:
            return False, f"Break limit reached ({self.max_break_minutes} minutes used today)"
        
        self.is_on_break = True
        self.break_start_time = datetime.now()
        return True, "Break started"
    
    def end_break(self):
        """End a break and record time"""
        if not self.is_on_break:
            return False, "Not on break"
        
        break_duration = (datetime.now() - self.break_start_time).total_seconds() / 60
        break_duration = min(break_duration, self.get_remaining_minutes())  # Cap at remaining time
        
        self.used_break_minutes += int(break_duration)
        self.break_history.append({
            'start': self.break_start_time.isoformat(),
            'end': datetime.now().isoformat(),
            'duration': int(break_duration)
        })
        
        self.is_on_break = False
        self.break_start_time = None
        self.save_break_data()
        
        return True, f"Break ended. Used {int(break_duration)} minutes"
    
    def get_remaining_minutes(self):
        """Get remaining break minutes"""
        return self.max_break_minutes - self.used_break_minutes
    
    def get_current_break_duration(self):
        """Get current break duration in minutes"""
        if not self.is_on_break:
            return 0
        return int((datetime.now() - self.break_start_time).total_seconds() / 60)

class FlairsTechTray:
    def __init__(self):
        self.icon = None
        self.running = True
        self.config = self.load_config()
        self.token_data = self.load_token()
        self.last_status = None
        self.check_in_time = None
        self.check_out_time = None
        self.break_tracker = BreakTracker()
        
        # Activity monitoring
        self.last_activity_time = time.time()
        self.activity_warnings_sent = 0
        self.activity_check_enabled = True
        
    def load_config(self):
        """Load configuration"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            default_config = {
                "place_id": "",
                "place_name": "Not Set",
                "auto_check_in_time": "08:00",
                "auto_check_out_time": "17:00",
                "enable_auto_check_in": False,
                "enable_auto_check_out": False,
                "notifications": True,
                "all_locations": [],
                "shift_start_time": "09:00",
                "shift_end_time": "18:00"
            }
            with open('config.json', 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def load_token(self):
        """Load authentication token"""
        try:
            with open('token.json', 'r') as f:
                data = json.load(f)
                if data.get('token_expiry', 0) < time.time():
                    return None
                return data
        except FileNotFoundError:
            return None
    
    def is_token_valid(self):
        """Check if token is still valid"""
        if not self.token_data:
            return False
        return self.token_data.get('token_expiry', 0) > time.time()
    
    def create_icon_image(self, checked_in=False, on_break=False):
        """Create system tray icon"""
        img = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(img)
        
        if on_break:
            # Orange pause symbol when on break
            draw.ellipse([8, 8, 56, 56], fill='#FF9800')
            draw.rectangle([22, 20, 28, 44], fill='white')
            draw.rectangle([36, 20, 42, 44], fill='white')
        elif checked_in:
            # Green checkmark when checked in
            draw.ellipse([8, 8, 56, 56], fill='#4CAF50')
            draw.line([20, 32, 28, 40], fill='white', width=4)
            draw.line([28, 40, 44, 24], fill='white', width=4)
        else:
            # Clock when not checked in
            draw.ellipse([8, 8, 56, 56], outline='black', width=3)
            draw.line([32, 32, 32, 16], fill='black', width=3)
            draw.line([32, 32, 44, 32], fill='black', width=3)
        
        return img
    
    def get_headers(self):
        """Get API headers with authentication"""
        if not self.token_data:
            return None
        
        return {
            "authorization": f"Bearer {self.token_data['bearer_token']}",
            "tenant-key": "flairstech",
            "Content-Type": "application/json"
        }
    
    def reset_activity_timer(self):
        """Reset activity timer when user interacts"""
        self.last_activity_time = time.time()
        self.activity_warnings_sent = 0
    
    def check_in(self, icon, item):
        """Perform check-in"""
        self.reset_activity_timer()
        
        if not self.is_token_valid():
            self.show_notification("Token Expired", "Please refresh your token")
            self.refresh_token_simple(icon, item)
            return
        
        if not self.config.get('place_id'):
            self.show_notification("No Location", "Please set your location in config.json or run setup again")
            return
        
        headers = self.get_headers()
        
        payload = {
            "placeId": self.config['place_id'],
            "checkInOutStatusTypeId": 1,
            "longitude": self.config.get('longitude', 0),
            "latitude": self.config.get('latitude', 0)
        }
        
        try:
            response = requests.post(
                "https://apiattendance.flairstech.com/api/CheckInOuts",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                self.check_in_time = datetime.now()
                self.last_status = "checked_in"
                self.activity_check_enabled = True
                location_name = self.config.get('place_name', 'Office')
                self.show_notification(
                    "Checked In Successfully", 
                    f"Location: {location_name}\nTime: {self.check_in_time.strftime('%I:%M %p')}"
                )
                icon.icon = self.create_icon_image(checked_in=True)
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                self.show_notification("Check-in Failed", error_msg)
        except Exception as e:
            self.show_notification("Error", f"Network error: {str(e)}")
    
    def check_out(self, icon, item):
        """Perform check-out"""
        self.reset_activity_timer()
        
        if not self.is_token_valid():
            self.show_notification("Token Expired", "Please refresh your token")
            self.refresh_token_simple(icon, item)
            return
        
        if not self.config.get('place_id'):
            self.show_notification("No Location", "Please set your location in config.json or run setup again")
            return
        
        # End break if on break
        if self.break_tracker.is_on_break:
            self.break_tracker.end_break()
        
        headers = self.get_headers()
        
        payload = {
            "placeId": self.config['place_id'],
            "checkInOutStatusTypeId": 2,
            "longitude": self.config.get('longitude', 0),
            "latitude": self.config.get('latitude', 0)
        }
        
        try:
            response = requests.post(
                "https://apiattendance.flairstech.com/api/CheckInOuts",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                self.check_out_time = datetime.now()
                self.last_status = "checked_out"
                self.activity_check_enabled = False
                
                if self.check_in_time:
                    duration = self.check_out_time - self.check_in_time
                    hours = duration.seconds // 3600
                    minutes = (duration.seconds % 3600) // 60
                    duration_str = f"{hours}h {minutes}m"
                else:
                    duration_str = "Unknown"
                
                location_name = self.config.get('place_name', 'Office')
                self.show_notification(
                    "Checked Out Successfully", 
                    f"Location: {location_name}\nTime: {self.check_out_time.strftime('%I:%M %p')}\nDuration: {duration_str}"
                )
                icon.icon = self.create_icon_image(checked_in=False)
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                self.show_notification("Check-out Failed", error_msg)
        except Exception as e:
            self.show_notification("Error", f"Network error: {str(e)}")
    
    def toggle_break(self, icon, item):
        """Toggle break on/off"""
        self.reset_activity_timer()
        
        if self.last_status != "checked_in":
            messagebox.showwarning(
                "Not Checked In",
                "You must be checked in to take a break"
            )
            return
        
        if self.break_tracker.is_on_break:
            # End break
            success, message = self.break_tracker.end_break()
            if success:
                remaining = self.break_tracker.get_remaining_minutes()
                self.show_notification(
                    "Break Ended",
                    f"{message}\nRemaining break time: {remaining} minutes"
                )
                icon.icon = self.create_icon_image(checked_in=True, on_break=False)
                self.activity_check_enabled = True
        else:
            # Start break
            success, message = self.break_tracker.start_break()
            if success:
                remaining = self.break_tracker.get_remaining_minutes()
                self.show_notification(
                    "Break Started",
                    f"Break time started\nRemaining: {remaining} minutes"
                )
                icon.icon = self.create_icon_image(checked_in=True, on_break=True)
                self.activity_check_enabled = False
            else:
                messagebox.showwarning("Break Limit", message)
        
        # Update menu
        self.icon.menu = self.create_menu()
    
    def show_break_status(self, icon, item):
        """Show break usage status"""
        used = self.break_tracker.used_break_minutes
        remaining = self.break_tracker.get_remaining_minutes()
        
        history_text = ""
        if self.break_tracker.break_history:
            history_text = "\n\nToday's breaks:\n"
            for i, brk in enumerate(self.break_tracker.break_history, 1):
                start = datetime.fromisoformat(brk['start']).strftime('%I:%M %p')
                end = datetime.fromisoformat(brk['end']).strftime('%I:%M %p')
                history_text += f"{i}. {start} - {end} ({brk['duration']} min)\n"
        
        current_break = ""
        if self.break_tracker.is_on_break:
            current_duration = self.break_tracker.get_current_break_duration()
            current_break = f"\n\nCurrent break: {current_duration} minutes"
        
        messagebox.showinfo(
            "Break Status",
            f"Break Time Usage:\n\n"
            f"Used: {used} minutes\n"
            f"Remaining: {remaining} minutes\n"
            f"Daily limit: 60 minutes"
            f"{current_break}"
            f"{history_text}"
        )
    
    def activity_monitor_worker(self):
        """Monitor user activity and check attendance"""
        while self.running:
            # Skip if not checked in or on break
            if self.last_status != "checked_in" or not self.activity_check_enabled or self.break_tracker.is_on_break:
                time.sleep(60)
                continue
            
            idle_time = time.time() - self.last_activity_time
            idle_minutes = idle_time / 60
            
            # First warning at 15 minutes
            if idle_minutes >= 15 and self.activity_warnings_sent == 0:
                self.show_activity_check("First")
                self.activity_warnings_sent = 1
            
            # Second warning at 20 minutes (15 + 5)
            elif idle_minutes >= 20 and self.activity_warnings_sent == 1:
                self.show_activity_check("Second")
                self.activity_warnings_sent = 2
            
            # Final warning at 25 minutes (15 + 5 + 5)
            elif idle_minutes >= 25 and self.activity_warnings_sent == 2:
                self.show_activity_check("Final")
                self.activity_warnings_sent = 3
            
            # Auto check-out at 30 minutes (15 + 5 + 5 + 5)
            elif idle_minutes >= 30 and self.activity_warnings_sent == 3:
                self.auto_checkout_inactive()
                self.activity_warnings_sent = 0
            
            time.sleep(60)  # Check every minute
    
    def show_activity_check(self, warning_type):
        """Show activity check popup"""
        try:
            window = tk.Tk()
            window.title("Activity Check")
            window.geometry("400x250")
            window.attributes('-topmost', True)
            
            # Center window
            window.update_idletasks()
            x = (window.winfo_screenwidth() // 2) - 200
            y = (window.winfo_screenheight() // 2) - 125
            window.geometry(f'400x250+{x}+{y}')
            
            # Warning icon
            canvas = tk.Canvas(window, width=80, height=80, bg='white', highlightthickness=0)
            canvas.pack(pady=20)
            canvas.create_oval(10, 10, 70, 70, fill='#FF9800', outline='')
            canvas.create_text(40, 40, text="!", font=("Arial", 40, "bold"), fill='white')
            
            warning_messages = {
                "First": "You've been inactive for 15 minutes.\nAre you still there?",
                "Second": "Second warning: No activity detected.\nPlease respond!",
                "Final": "FINAL WARNING!\nYou will be checked out in 5 minutes."
            }
            
            Label(
                window,
                text=warning_messages.get(warning_type, "Are you there?"),
                font=("Arial", 12, "bold"),
                justify="center"
            ).pack(pady=10)
            
            Label(
                window,
                text="Click 'Yes, I'm Here' to continue working\nor take a Break if needed.",
                font=("Arial", 10),
                justify="center"
            ).pack(pady=10)
            
            def confirm_presence():
                self.reset_activity_timer()
                self.show_notification("Activity Confirmed", "Welcome back! Timer reset.")
                window.destroy()
            
            def take_break():
                window.destroy()
                self.toggle_break(self.icon, None)
            
            btn_frame = Frame(window)
            btn_frame.pack(pady=20)
            
            Button(
                btn_frame,
                text="Yes, I'm Here",
                font=("Arial", 12, "bold"),
                bg="#4CAF50",
                fg="white",
                padx=20,
                pady=10,
                command=confirm_presence
            ).pack(side='left', padx=10)
            
            Button(
                btn_frame,
                text="Take a Break",
                font=("Arial", 11),
                bg="#FF9800",
                fg="white",
                padx=20,
                pady=10,
                command=take_break
            ).pack(side='left', padx=10)
            
            window.mainloop()
            
        except Exception as e:
            print(f"Error showing activity check: {e}")
    
    def auto_checkout_inactive(self):
        """Automatically check out due to inactivity"""
        self.show_notification(
            "Auto Check-Out",
            "You've been automatically checked out due to inactivity."
        )
        self.check_out(self.icon, None)
    
    def shift_reminder_worker(self):
        """Send shift start/end reminders"""
        while self.running:
            now = datetime.now()
            current_time = now.strftime('%H:%M')
            
            shift_start = self.config.get('shift_start_time', '09:00')
            shift_end = self.config.get('shift_end_time', '18:00')
            
            # Shift start reminder
            if current_time == shift_start and self.last_status != "checked_in":
                self.show_shift_reminder("start")
            
            # Shift end reminder
            elif current_time == shift_end and self.last_status == "checked_in":
                self.show_shift_reminder("end")
            
            time.sleep(60)  # Check every minute
    
    def show_shift_reminder(self, reminder_type):
        """Show shift start/end reminder popup"""
        try:
            window = tk.Tk()
            window.title("Shift Reminder")
            window.geometry("400x300")
            window.attributes('-topmost', True)
            
            # Center window
            window.update_idletasks()
            x = (window.winfo_screenwidth() // 2) - 200
            y = (window.winfo_screenheight() // 2) - 150
            window.geometry(f'400x300+{x}+{y}')
            
            if reminder_type == "start":
                canvas = tk.Canvas(window, width=80, height=80, bg='white', highlightthickness=0)
                canvas.pack(pady=20)
                canvas.create_oval(10, 10, 70, 70, fill='#4CAF50', outline='')
                canvas.create_polygon(30, 25, 30, 55, 55, 40, fill='white')
                
                Label(
                    window,
                    text="Time to Start Your Shift!",
                    font=("Arial", 14, "bold"),
                    fg="#4CAF50"
                ).pack(pady=10)
                
                Label(
                    window,
                    text=f"Your shift starts at {self.config.get('shift_start_time', '09:00')}\n"
                         f"Location: {self.config.get('place_name', 'Office')}",
                    font=("Arial", 10),
                    justify="center"
                ).pack(pady=10)
                
                def check_in_now():
                    window.destroy()
                    self.check_in(self.icon, None)
                
                def take_break_first():
                    window.destroy()
                    messagebox.showinfo("Break", "Please check in first, then you can take a break")
                
                Button(
                    window,
                    text="Check In Now",
                    font=("Arial", 12, "bold"),
                    bg="#4CAF50",
                    fg="white",
                    padx=30,
                    pady=10,
                    command=check_in_now
                ).pack(pady=10)
                
                Button(
                    window,
                    text="Remind Me in 5 Minutes",
                    font=("Arial", 10),
                    command=lambda: [window.destroy(), self.schedule_reminder(5)]
                ).pack(pady=5)
            
            else:  # end
                canvas = tk.Canvas(window, width=80, height=80, bg='white', highlightthickness=0)
                canvas.pack(pady=20)
                canvas.create_oval(10, 10, 70, 70, fill='#FF5722', outline='')
                canvas.create_rectangle(25, 30, 35, 50, fill='white')
                canvas.create_rectangle(45, 30, 55, 50, fill='white')
                
                Label(
                    window,
                    text="Time to End Your Shift!",
                    font=("Arial", 14, "bold"),
                    fg="#FF5722"
                ).pack(pady=10)
                
                Label(
                    window,
                    text=f"Your shift ends at {self.config.get('shift_end_time', '18:00')}\n"
                         f"Don't forget to check out!",
                    font=("Arial", 10),
                    justify="center"
                ).pack(pady=10)
                
                def check_out_now():
                    window.destroy()
                    self.check_out(self.icon, None)
                
                Button(
                    window,
                    text="Check Out Now",
                    font=("Arial", 12, "bold"),
                    bg="#FF5722",
                    fg="white",
                    padx=30,
                    pady=10,
                    command=check_out_now
                ).pack(pady=10)
                
                Button(
                    window,
                    text="Remind Me in 10 Minutes",
                    font=("Arial", 10),
                    command=lambda: [window.destroy(), self.schedule_reminder(10)]
                ).pack(pady=5)
            
            window.mainloop()
            
        except Exception as e:
            print(f"Error showing shift reminder: {e}")
    
    def schedule_reminder(self, minutes):
        """Schedule a reminder after specified minutes"""
        def remind():
            time.sleep(minutes * 60)
            if self.last_status != "checked_in":
                self.show_shift_reminder("start")
            else:
                self.show_shift_reminder("end")
        
        threading.Thread(target=remind, daemon=True).start()
    
    def get_today_status(self):
        """Get today's check-in/out status"""
        if not self.is_token_valid():
            return None
        
        headers = self.get_headers()
        
        try:
            response = requests.get(
                "https://apiattendance.flairstech.com/api/CheckInOuts/GetMyCheckInOutHistoryToday",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('result', {})
            return None
        except Exception:
            return None
    
    def show_status(self, icon, item):
        """Show current status"""
        self.reset_activity_timer()
        status = self.get_today_status()
        
        if not status:
            self.show_notification("Status", "Unable to fetch status. Check your connection.")
            return
        
        check_ins = status.get('checkIns', [])
        check_outs = status.get('checkOuts', [])
        
        if check_ins:
            latest_check_in = check_ins[-1]
            check_in_time = latest_check_in.get('creationTime', 'Unknown')
            location = latest_check_in.get('placeName', 'Unknown')
            
            msg = f"Last Check-in:\n{check_in_time}\nat {location}"
            
            if check_outs:
                latest_check_out = check_outs[-1]
                check_out_time = latest_check_out.get('creationTime', 'Unknown')
                msg += f"\n\nLast Check-out:\n{check_out_time}"
            else:
                msg += "\n\n[STATUS] Currently checked in"
            
            # Add break info
            if self.break_tracker.is_on_break:
                current_break = self.break_tracker.get_current_break_duration()
                msg += f"\n\n[BREAK] On break for {current_break} minutes"
            elif self.break_tracker.used_break_minutes > 0:
                msg += f"\n\nBreak used: {self.break_tracker.used_break_minutes} min"
            
            self.show_notification("Today's Status", msg)
        else:
            self.show_notification("Status", "No check-ins today")
    
    def show_notification(self, title, message):
        """Show Windows notification"""
        if self.config.get('notifications', True):
            try:
                self.icon.notify(message, title)
            except:
                print(f"{title}: {message}")
    
    def switch_location(self, icon, item):
        """Switch to a different location"""
        self.reset_activity_timer()
        
        if not self.config.get('all_locations'):
            self.show_notification("No Locations", "No alternative locations found.\nRun setup again to fetch locations.")
            return
        
        if len(self.config.get('all_locations', [])) == 1:
            self.show_notification("Single Location", "You only have one location configured.")
            return
        
        try:
            window = tk.Tk()
            window.title("Switch Location")
            window.geometry("450x350")
            window.resizable(False, False)
            
            header = Label(
                window,
                text="Select Location:",
                font=("Arial", 14, "bold")
            )
            header.pack(pady=15)
            
            current_label = Label(
                window,
                text=f"Current: {self.config.get('place_name', 'Unknown')}",
                font=("Arial", 10),
                fg="blue"
            )
            current_label.pack(pady=5)
            
            listbox = Listbox(
                window, 
                font=("Arial", 11), 
                selectmode=SINGLE,
                height=10
            )
            listbox.pack(pady=10, padx=20, fill='both', expand=True)
            
            for loc in self.config['all_locations']:
                status = loc.get('status', 'unknown')
                status_text = ""
                if status == 1:
                    status_text = " [APPROVED]"
                elif status == 0:
                    status_text = " [PENDING]"
                
                display_text = f"{loc['name']}{status_text}"
                listbox.insert(tk.END, display_text)
            
            current_id = self.config.get('place_id')
            for i, loc in enumerate(self.config['all_locations']):
                if loc['id'] == current_id:
                    listbox.select_set(i)
                    listbox.see(i)
                    break
            
            def save_selection():
                selection = listbox.curselection()
                if not selection:
                    messagebox.showwarning("No Selection", "Please select a location")
                    return
                
                new_location = self.config['all_locations'][selection[0]]
                
                if new_location['id'] == self.config.get('place_id'):
                    messagebox.showinfo("Same Location", "This location is already selected")
                    window.destroy()
                    return
                
                self.config['place_id'] = new_location['id']
                self.config['place_name'] = new_location['name']
                self.config['latitude'] = new_location.get('latitude', 0)
                self.config['longitude'] = new_location.get('longitude', 0)
                
                try:
                    with open('config.json', 'w') as f:
                        json.dump(self.config, f, indent=2)
                    
                    self.show_notification(
                        "Location Changed", 
                        f"Now using: {new_location['name']}"
                    )
                    
                    self.icon.menu = self.create_menu()
                    
                    messagebox.showinfo(
                        "Success",
                        f"Location changed to:\n{new_location['name']}\n\n"
                        "Your next check-in will use this location."
                    )
                    window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")
            
            button_frame = tk.Frame(window)
            button_frame.pack(pady=15)
            
            Button(
                button_frame,
                text="Switch Location",
                font=("Arial", 11, "bold"),
                bg="#4CAF50",
                fg="white",
                padx=20,
                pady=8,
                command=save_selection
            ).pack(side='left', padx=5)
            
            Button(
                button_frame,
                text="Cancel",
                font=("Arial", 11),
                padx=20,
                pady=8,
                command=window.destroy
            ).pack(side='left', padx=5)
            
            window.update_idletasks()
            width = window.winfo_width()
            height = window.winfo_height()
            x = (window.winfo_screenwidth() // 2) - (width // 2)
            y = (window.winfo_screenheight() // 2) - (height // 2)
            window.geometry(f'{width}x{height}+{x}+{y}')
            
            window.mainloop()
            
        except Exception as e:
            self.show_notification("Error", f"Could not open location switcher: {str(e)}")
    
    def refresh_token_simple(self, icon, item):
        """Simple token refresh"""
        try:
            response = messagebox.askyesno(
                "Refresh Token",
                "This will open the setup wizard.\n\n"
                "You'll need to log in again.\n\n"
                "Continue?",
                icon='question'
            )
            
            if response:
                self.launch_setup_wizard()
        except:
            self.launch_setup_wizard()
    
    def launch_setup_wizard(self):
        """Launch setup wizard"""
        try:
            subprocess.Popen([sys.executable, 'installer.py'])
            self.show_notification(
                "Setup Wizard",
                "Setup wizard opened."
            )
        except Exception as e:
            self.show_notification("Error", f"Could not launch setup wizard: {str(e)}")
    
    def auto_refresh_token_if_needed(self):
        """Automatically prompt for token refresh when expired"""
        try:
            response = messagebox.askyesno(
                "Token Expired",
                "Your authentication token has expired.\n\n"
                "Would you like to refresh it now?",
                icon='warning'
            )
            
            if response:
                self.launch_setup_wizard()
        except:
            self.show_notification("Token Expired", "Please run installer.py to refresh your token")
    
    def check_token_expiry_background(self):
        """Background thread to monitor token expiry"""
        while self.running:
            if self.token_data:
                time_remaining = self.token_data.get('token_expiry', 0) - time.time()
                
                if 0 < time_remaining < 1800:  # 30 minutes
                    minutes_left = int(time_remaining / 60)
                    self.show_notification(
                        "Token Expiring Soon",
                        f"Your token will expire in {minutes_left} minutes."
                    )
                    time.sleep(900)
                
                elif time_remaining <= 0:
                    self.auto_refresh_token_if_needed()
                    time.sleep(3600)
                else:
                    time.sleep(600)
            else:
                time.sleep(60)
    
    def open_web_attendance(self, icon, item):
        """Open web attendance page"""
        webbrowser.open('https://attendance.flairstech.com')
    
    def open_config(self, icon, item):
        """Open config file"""
        try:
            if sys.platform == 'win32':
                os.startfile('config.json')
            else:
                subprocess.call(['open', 'config.json'])
        except Exception as e:
            self.show_notification("Error", f"Could not open config file: {str(e)}")
    
    def auto_check_worker(self):
        """Background worker for auto check-in/out"""
        while self.running:
            if not self.config.get('enable_auto_check_in') and not self.config.get('enable_auto_check_out'):
                time.sleep(60)
                continue
            
            now = datetime.now()
            current_time = now.strftime('%H:%M')
            
            if (self.config.get('enable_auto_check_in') and 
                current_time == self.config.get('auto_check_in_time') and
                self.last_status != 'checked_in'):
                self.check_in(self.icon, None)
            
            if (self.config.get('enable_auto_check_out') and 
                current_time == self.config.get('auto_check_out_time') and
                self.last_status == 'checked_in'):
                self.check_out(self.icon, None)
            
            time.sleep(60)
    
    def update_menu_token_status(self):
        """Periodically update menu"""
        while self.running:
            if self.icon:
                self.icon.menu = self.create_menu()
            time.sleep(300)
    
    def create_menu(self):
        """Create system tray menu"""
        token_status = "Active" if self.is_token_valid() else "Expired"
        
        has_multiple_locations = len(self.config.get('all_locations', [])) > 1
        
        break_status = ""
        if self.break_tracker.is_on_break:
            break_duration = self.break_tracker.get_current_break_duration()
            break_status = f"End Break ({break_duration} min)"
        else:
            remaining = self.break_tracker.get_remaining_minutes()
            break_status = f"Take Break ({remaining} min left)"
        
        menu_items = [
            item('Check In', self.check_in),
            item('Check Out', self.check_out),
            item('Show Status', self.show_status),
            pystray.Menu.SEPARATOR,
            item(break_status, self.toggle_break),
            item('Break Status', self.show_break_status),
            pystray.Menu.SEPARATOR,
        ]
        
        current_location = self.config.get('place_name', 'Not Set')
        menu_items.append(item(f'Location: {current_location}', None, enabled=False))
        
        if has_multiple_locations:
            menu_items.append(item('Switch Location', self.switch_location))
        
        menu_items.append(pystray.Menu.SEPARATOR)
        
        menu_items.extend([
            item(f'Token: {token_status}', None, enabled=False),
            item('Refresh Token', self.refresh_token_simple),
            pystray.Menu.SEPARATOR,
            item('Open Web Attendance', self.open_web_attendance),
            item('Settings', self.open_config),
            pystray.Menu.SEPARATOR,
            item('Exit', self.quit_app)
        ])
        
        return pystray.Menu(*menu_items)
    
    def quit_app(self, icon, item):
        """Exit the application"""
        if self.break_tracker.is_on_break:
            self.break_tracker.end_break()
        
        self.running = False
        icon.stop()
    
    def run(self):
        """Start the system tray application"""
        if not self.is_token_valid():
            print("WARNING: NO VALID TOKEN FOUND")
            print("Please run: python installer.py")
        
        if not self.config.get('place_id'):
            print("WARNING: No location set")
            print("Run: python installer.py")
        
        image = self.create_icon_image()
        self.icon = pystray.Icon(
            "FlairsTech",
            image,
            "FlairsTech Attendance",
            menu=self.create_menu()
        )
        
        # Start background workers
        threading.Thread(target=self.auto_check_worker, daemon=True).start()
        threading.Thread(target=self.check_token_expiry_background, daemon=True).start()
        threading.Thread(target=self.update_menu_token_status, daemon=True).start()
        threading.Thread(target=self.activity_monitor_worker, daemon=True).start()
        threading.Thread(target=self.shift_reminder_worker, daemon=True).start()
        
        # Check if it's a new day and reset break tracker
        def daily_reset_worker():
            while self.running:
                if datetime.now().date() != self.break_tracker.last_reset_date:
                    self.break_tracker.reset_daily()
                    self.break_tracker.last_reset_date = datetime.now().date()
                time.sleep(3600)  # Check every hour
        
        threading.Thread(target=daily_reset_worker, daemon=True).start()
        
        print("")
        print("=" * 60)
        print("FlairsTech Attendance is running!")
        print("=" * 60)
        print("")
        print(f"Location: {self.config.get('place_name', 'Not Set')}")
        print(f"Token Status: {'Valid' if self.is_token_valid() else 'Expired/Missing'}")
        print(f"Shift: {self.config.get('shift_start_time', '09:00')} - {self.config.get('shift_end_time', '18:00')}")
        print(f"Break Time Available: {self.break_tracker.get_remaining_minutes()} minutes")
        print("")
        print("Features:")
        print("- Break Management (1 hour daily)")
        print("- Activity Monitoring (15-minute check)")
        print("- Shift Reminders")
        print("")
        print("=" * 60)
        
        self.icon.run()

if __name__ == '__main__':
    app = FlairsTechTray()
    app.run()