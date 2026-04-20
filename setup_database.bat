@echo off
REM Kapila Invoice Generator - Database Setup Script
REM Run this script to set up the MySQL database

echo ========================================
echo Kapila Invoice - Database Setup
echo ========================================
echo.

REM Check if MySQL is installed
where mysql >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: MySQL is not installed or not in PATH
    echo Please install MySQL and add it to your PATH
    pause
    exit /b 1
)

REM Get database password
set /p DB_PASSWORD=Enter MySQL root password (leave empty if no password):

echo.
echo Creating database...
mysql -u root -p%DB_PASSWORD% < database/schema.sql

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS: Database setup completed!
    echo ========================================
    echo.
    echo Default Login Credentials:
    echo   Username: admin
    echo   Password: admin123
    echo.
    echo Next steps:
    echo   1. Copy .env.example to .env and configure
    echo   2. Install Python dependencies: pip install -r requirements.txt
    echo   3. Run the application: python app.py
    echo   4. Open browser and go to http://localhost:5000
    echo.
) else (
    echo.
    echo ERROR: Database setup failed!
    echo Please check your MySQL connection and try again.
)

pause

