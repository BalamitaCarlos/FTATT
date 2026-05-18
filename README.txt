FlairsTech Attendance - Quick Start Guide
==========================================

FIRST TIME SETUP:
1. Run: python master_installer.py
2. Follow the setup wizard (2-3 minutes)
3. Done!

DAILY USE:
Run: python run_apps.py

This starts:
- System tray app (check your taskbar)
- Desktop widget (top-right corner)

FILES:
- master_installer.py = Setup wizard
- widget.py = Desktop widget
- tray_app.py = System tray app
- run_apps.py = Launcher
- config.json = Your settings (auto-created)
- token.json = Your auth token (auto-created)
- break_data.json = Break tracking (auto-created)

TOKEN EXPIRES EVERY 12 HOURS:
When expired, run master_installer.py again to refresh.

TROUBLESHOOTING:
- Widget shows "offline"? Check internet connection.
- Tray not showing? Look for Python icon in hidden icons.
- Token expired? Re-run installer.

SUPPORT:
Check console output for error messages.