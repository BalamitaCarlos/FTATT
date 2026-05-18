@echo off
echo ========================================
echo  FlairsTech Attendance - Build Script
echo ========================================
echo.

echo Checking PyInstaller...
python -m PyInstaller --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller not found! Installing...
    python -m pip install pyinstaller
    echo.
)

echo Cleaning old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec
echo.

echo [1/3] Building Installer...
python -m PyInstaller --name="FlairsTech-Installer" ^
    --onefile ^
    --windowed ^
    --icon=flairstech_logo.png ^
    --add-data="flairstech_logo.png;." ^
    master_installer.py

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Installer build failed!
    pause
    exit /b 1
)
echo OK - Installer built
echo.

echo [2/3] Building Widget...
python -m PyInstaller --name="FlairsTech-Widget" ^
    --onefile ^
    --windowed ^
    --icon=flairstech_logo.png ^
    --add-data="flairstech_logo.png;." ^
    widget.py

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Widget build failed!
    pause
    exit /b 1
)
echo OK - Widget built
echo.

echo [3/3] Building Tray App...
python -m PyInstaller --name="FlairsTech-Attendance" ^
    --onefile ^
    --windowed ^
    --icon=flairstech_logo.png ^
    --add-data="flairstech_logo.png;." ^
    tray_app.py

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Tray app build failed!
    pause
    exit /b 1
)
echo OK - Tray app built
echo.

echo ========================================
echo  BUILD COMPLETE!
echo ========================================
echo.
echo EXE files are in the 'dist' folder:
echo   - FlairsTech-Installer.exe
echo   - FlairsTech-Widget.exe
echo   - FlairsTech-Attendance.exe
echo.
echo Copying logo to dist...
copy flairstech_logo.png dist\
echo.

echo Cleaning up build files...
rmdir /s /q build
del /q *.spec
echo.

echo ========================================
echo  DONE!
echo ========================================
echo.
dir dist
echo.
pause