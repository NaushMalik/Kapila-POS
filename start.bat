@echo off
echo ============================================
echo   KAPILA INVOICE - Quick Start
echo ============================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo ✓ Python found

echo [2/4] Installing dependencies...
pip install -r requirements.txt >nul 2>&1
echo ✓ Dependencies installed

echo [3/4] Starting Kapila Invoice Server...
echo.
echo ============================================
echo   SERVER STARTING...
echo ============================================
echo.
echo Access the app at:
echo   - Local:  http://localhost:5000
echo   - Network: http://YOUR_IP:5000
echo.
echo Default login:
echo   Username: admin
echo   Password: admin123
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

python app.py

pause
