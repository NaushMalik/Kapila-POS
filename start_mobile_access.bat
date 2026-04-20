@echo off
echo ========================================
echo   KAPILA INVOICE - MOBILE ACCESS
echo ========================================
echo.

echo Starting Flask server...
start "Flask" cmd /k "python app.py"

echo Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo Starting tunnel...
echo.
echo ========================================
echo   COPY THIS URL TO YOUR MOBILE:
echo ========================================
echo.

cd /d "%~dp0"
cloudflared.exe tunnel --url http://localhost:5001

pause

