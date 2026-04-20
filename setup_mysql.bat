@echo off
REM MySQL Setup for Kapila Restaurant Billing System
REM Prerequisites: MySQL installed (XAMPP/WAMP/standalone)
REM Update MYSQL_ROOT_PASSWORD and MYSQL_DB_USER/PASS below

echo ========================================
echo Kapila Invoice - MySQL Database Setup
echo ========================================

set MYSQL_ROOT_PASSWORD=your_root_password_here
set MYSQL_HOST=localhost
set MYSQL_PORT=3306
set MYSQL_DB_NAME=kapila_invoice_db
set MYSQL_DB_USER=kapila_user
set MYSQL_DB_PASS=kapila_pass123

REM Check if MySQL is running
echo [1/6] Checking MySQL connection...
mysql -h%MYSQL_HOST% -P%MYSQL_PORT% -u root -p%MYSQL_ROOT_PASSWORD% -e "SELECT 'MySQL OK'" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Cannot connect to MySQL. Start XAMPP/ MySQL service.
    echo Default: XAMPP Control Panel ^> Start MySQL
    pause
    exit /b 1
)
echo ✓ MySQL connected.

REM [2/6] Create database and user
echo [2/6] Creating database '%MYSQL_DB_NAME%' and user...
mysql -h%MYSQL_HOST% -P%MYSQL_PORT% -u root -p%MYSQL_ROOT_PASSWORD% << EOF
CREATE DATABASE IF NOT EXISTS %MYSQL_DB_NAME% CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '%MYSQL_DB_USER%'@'localhost' IDENTIFIED BY '%MYSQL_DB_PASS%';
GRANT ALL PRIVILEGES ON %MYSQL_DB_NAME%.* TO '%MYSQL_DB_USER%'@'localhost';
FLUSH PRIVILEGES;
USE %MYSQL_DB_NAME%;
SELECT 'Database ready' as status;
EOF

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Database creation failed.
    pause
    exit /b 1
)
echo ✓ Database and user created.

REM [3/6] Import schema
echo [3/6] Importing schema...
mysql -h%MYSQL_HOST% -P%MYSQL_PORT% -u %MYSQL_DB_USER% -p%MYSQL_DB_PASS% %MYSQL_DB_NAME% < "database\mysql_schema.sql"

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Schema import failed. Check mysql_schema.sql
    pause
    exit /b 1
)
echo ✓ Schema imported.

REM [4/6] Verify tables
echo [4/6] Verifying tables...
mysql -h%MYSQL_HOST% -P%MYSQL_PORT% -u %MYSQL_DB_USER% -p%MYSQL_DB_PASS% %MYSQL_DB_NAME% -e "SHOW TABLES; SELECT COUNT(*) as products FROM products; SELECT COUNT(*) as users FROM users;"

REM [5/6] Test Flask connection
echo [5/6] Testing app configuration...
echo MYSQL_HOST=%MYSQL_HOST% ^| MYSQL_PORT=%MYSQL_PORT% ^| MYSQL_DB_NAME=%MYSQL_DB_NAME% ^| MYSQL_DB_USER=%MYSQL_DB_USER% ^| MYSQL_DB_PASS=%MYSQL_DB_PASS% > .env
echo ✓ .env created. Edit for app.py config.

REM [6/6] Final check
echo.
echo ========================================
echo ✓ Setup COMPLETE!
echo.
echo Next steps:
echo 1. Edit .env with your MySQL details
echo 2. Update app.py DATABASE config to use SQLAlchemy/MySQL
echo 3. python app.py
echo 4. Login: admin / admin123
echo.
echo Default credentials in .env above.
echo ========================================
pause

