@echo off
echo Building complete bundle...

pyinstaller --name="FlairsTech-Complete" ^
    --onefile ^
    --windowed ^
    --icon=flairstech_logo.png ^
    --add-data="flairstech_logo.png;." ^
    --add-data="widget.py;." ^
    --add-data="tray_app.py;." ^
    --hidden-import=pystray ^
    --hidden-import=PIL ^
    --hidden-import=requests ^
    master_installer.py

echo Done! Check dist folder.
pause