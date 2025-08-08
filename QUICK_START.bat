@echo off
title Quick Trading Dashboard Start
color 0B

echo 🚀 Quick Trading Dashboard Start
echo.

start "Trading Dashboard" cmd /k "python flask_dashboard.py"
timeout /t 3 /nobreak >nul
start http://localhost:5001

echo ✅ Dashboard launched! Check the new CMD window for alerts. 