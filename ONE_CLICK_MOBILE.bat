@echo off
title Kapila Invoice - Starting...
echo.
echo ========================================
echo   KAPILA INVOICE - ONE CLICK MOBILE ACCESS
echo ========================================
echo.

echo [1/3] Checking Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org
    pause
    exit
)
echo [OK] Node.js found

echo.
echo [2/3] Starting Flask server...
start "Flask Server" cmd /k "python app.py"
timeout /t 4 /nobreak >nul

echo.
echo [3/3] Creating public link...
echo.
echo ========================================
echo   WAIT FOR YOUR PUBLIC URL BELOW:
echo ========================================
echo.
npx --yes localtunnel --port 5001

