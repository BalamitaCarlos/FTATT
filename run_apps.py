# run_apps.py - Launch Both Apps
import subprocess
import sys
import os
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

print("=" * 60)
print("   FlairsTech Attendance Launcher")
print("=" * 60)
print(f"Directory: {SCRIPT_DIR}")
print()

# Check files
required = ['widget.py', 'tray_app.py', 'config.json', 'token.json']
missing = [f for f in required if not os.path.exists(f)]

if missing:
    print("ERROR: Missing files:")
    for f in missing:
        print(f"  ✗ {f}")
    print("\nRun master_installer.py first!")
    input("\nPress Enter to exit...")
    sys.exit(1)

print("✓ All files found")
print()

# Start tray app (no console)
print("Starting system tray...")
tray_process = subprocess.Popen(
    [sys.executable, 'tray_app.py'],
    cwd=SCRIPT_DIR,
    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
)
print("✓ Tray started")
time.sleep(2)

# Start widget
print("Starting desktop widget...")
widget_process = subprocess.Popen(
    [sys.executable, 'widget.py'],
    cwd=SCRIPT_DIR
)
print("✓ Widget started")

print()
print("=" * 60)
print("Both apps running!")
print("=" * 60)