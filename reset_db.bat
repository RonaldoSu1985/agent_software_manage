@echo off
chcp 65001
echo ==============================================
echo Agent Software Management System - Database Reset
echo ==============================================
echo WARNING: This will clear ALL existing data!
echo Press Ctrl+C to cancel or any key to continue...
pause >nul

echo.
echo Connecting to database...
mysql -h 192.168.0.118 -u agm -paa111111 agent_management < "%~dp0reset_db.sql"

if %ERRORLEVEL% equ 0 (
    echo.
    echo SUCCESS: Database reset completed successfully!
    echo Default admin account: username=admin, password=123456
) else (
    echo.
    echo ERROR: Database reset failed!
    echo Please check MySQL connection settings.
)

echo.
pause