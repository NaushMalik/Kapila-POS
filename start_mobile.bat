@echo off
echo ========================================
echo   KAPILA INVOICE - MOBILE ACCESS
echo ========================================
echo.

REM Kill any existing ngrok processes
taskkill /F /IM ngrok.exe 2>nul
echo [OK] Cleaned up old processes

REM Start Flask in a new window
echo [1] Starting Flask server...
start "KapilaInvoice - Flask" cmd /k "cd /d %~dp0 && python app.py"

echo Waiting for Flask to start...
timeout /t 6 /nobreak >nul

REM Start ngrok tunnel in a new window
echo [2] Starting tunnel...
start "KapilaInvoice - Tunnel" cmd /k "cd /d %~dp0 && ngrok http 5001"

echo.
echo ========================================
echo   INSTRUCTIONS:
echo ========================================
echo 1. Look at the "KapilaInvoice - Tunnel" window
echo 2. Copy the https:// URL shown there
echo 3. Open that URL on your MOBILE PHONE
echo 4. Login: admin / admin123
echo.
echo IMPORTANT: Keep BOTH windows open!
echo ========================================

pause

