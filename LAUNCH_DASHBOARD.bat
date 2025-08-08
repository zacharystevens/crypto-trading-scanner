@echo off
title Trading Dashboard Launcher
color 0A

echo.
echo ========================================
echo    🚀 TRADING DASHBOARD LAUNCHER
echo ========================================
echo.

:: We're already in the correct directory
echo 📁 Working directory: %CD%
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo ✅ Python found
echo.

:: Check if required files exist
if not exist "flask_dashboard.py" (
    echo ❌ ERROR: flask_dashboard.py not found
    echo Please make sure you're in the correct directory
    pause
    exit /b 1
)

echo ✅ Trading dashboard files found
echo.

:: Install dependencies if needed
echo 📦 Checking dependencies...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Some dependencies may not be installed, but continuing...
) else (
    echo ✅ Dependencies check complete
)
echo.

:: Wait a moment for user to read
echo 🚀 Starting Trading Dashboard...
echo.
echo 📊 Features that will be available:
echo    • Top 100 coins monitoring
echo    • Real-time EMA/SMA crossover alerts
echo    • 3-second audio beeps
echo    • Professional popup notifications
echo    • Audio on/off toggle
echo    • Enhanced charts with SMA lines
echo.
echo ⏳ Starting in 3 seconds...
timeout /t 3 /nobreak >nul

:: Start the Flask dashboard in a new window
echo 🌐 Launching Trading Dashboard...
start "Trading Dashboard" cmd /k "python flask_dashboard.py"

:: Wait a moment for the server to start
echo ⏳ Waiting for server to start...
timeout /t 5 /nobreak >nul

:: Open browser to the dashboard
echo 🌐 Opening browser to dashboard...
start http://localhost:5001

echo.
echo ========================================
echo    ✅ LAUNCH COMPLETE!
echo ========================================
echo.
echo 📊 Dashboard URL: http://localhost:5001
echo 🎛️ Audio toggle: Use API endpoints
echo 📱 Popup alerts: Will appear automatically
echo 🔊 Audio alerts: ON by default
echo.
echo 💡 Tips:
echo    • Keep the CMD window open for alerts
echo    • Audio alerts can be toggled via API
echo    • Popup notifications have close buttons
echo    • Monitor top 100 coins automatically
echo.
echo Press any key to close this launcher...
pause >nul 