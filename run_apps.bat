@echo off
title FlairsTech Attendance
echo Starting FlairsTech Attendance...
echo.

if not exist config.json (
    echo Config not found! Run FlairsTech-Installer.exe first.
    pause
    exit
)

echo Starting system tray...
start  FlairsTech-Attendance.exe
timeout t 2 nobreak nul

echo Starting widget...
start  FlairsTech-Widget.exe

echo.
echo Apps started!
echo - Check system tray for icon
echo - Check top-right for widget
echo.
timeout t 3