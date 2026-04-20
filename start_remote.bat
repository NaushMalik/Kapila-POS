@echo off
echo ========================================
echo   Kapila Invoice - Remote Access Setup
echo ========================================
echo.

REM Check if ngrok exists
if exist "ngrok\ngrok.exe" (
    echo [OK] ngrok found
    goto :start_services
)

echo [STEP 1] Downloading ngrok...
echo This may take a minute depending on your internet speed...
echo.

REM Download ngrok
powershell -Command "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip' -OutFile 'ngrok.zip'"

if not exist "ngrok.zip" (
    echo [ERROR] Failed to download ngrok
    pause
    exit /b 1
)

echo [STEP 2] Extracting ngrok...
powershell -Command "Expand-Archive -Path 'ngrok.zip' -DestinationPath 'ngrok' -Force"

if not exist "ngrok\ngrok.exe" (
    echo [ERROR] Failed to extract ngrok
    pause
    exit /b 1
)

del ngrok.zip
echo [OK] ngrok installed successfully
echo.

:start_services
echo [STEP 3] Starting Flask server...
echo The app will run on port 5001
echo.

REM Start Flask in background
start "KapilaInvoice" cmd /k "python app.py"

REM Wait for Flask to start
timeout /t 5 /nobreak >nul

echo [STEP 4] Starting ngrok tunnel...
echo.
echo ========================================
echo   IMPORTANT: Copy this URL:
echo ========================================
echo.

REM Start ngrok and capture the URL
cd ngrok
start "ngrok" cmd /k "ngrok http 5001 --log=stdout | findstr /C:""url=ngrok"" /C:""https://"""

echo.
echo ========================================
echo   INSTRUCTIONS:
echo ========================================
echo 1. The above URL is your public link
echo 2. Open this URL on your mobile phone
echo 3. You can access from anywhere!
echo 4. Keep this window open
echo.
echo NOTE: Each time you restart ngrok,
echo you'll get a NEW URL.
echo ========================================
echo.

pause

