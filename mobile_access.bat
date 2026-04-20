@echo off
echo ========================================
echo   KAPILA INVOICE - MOBILE ACCESS
echo ========================================
echo.
echo Step 1: Installing localtunnel (one time only)
echo.
call npm install -g localtunnel
echo.
echo Step 2: Starting Flask server...
echo.
start "Flask" cmd /k "python app.py"
echo.
echo Waiting for Flask to start...
timeout /t 5 /nobreak >nul
echo.
echo Step 3: Creating public link...
echo.
echo Open a NEW command window and run:
echo    lt --port 5001
echo.
echo Or use this alternative:
echo    npx localtunnel --port 5001
echo.
echo ========================================
echo Once you see your URL (like xxx.loca.lt)
echo Open that on your MOBILE PHONE
echo ========================================
echo.
pause

