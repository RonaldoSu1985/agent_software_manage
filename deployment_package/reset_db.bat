@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==============================================
echo   Agent Software Management System - Reset
echo ==============================================
echo WARNING: This will CLEAR ALL existing data!
echo Press Ctrl+C to cancel or any key to continue...
pause >nul

echo.
echo Database Configuration:
echo   Host: 192.168.0.118
echo   Database: agent_management
echo.

:: Try to find mysql in common locations
set "MYSQL_PATH="
set "COMMON_PATHS=^
C:\Program Files\MySQL\MySQL Server 8.0\bin^
C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin^
C:\Program Files\MySQL\MySQL Server 5.7\bin^
C:\Program Files (x86)\MySQL\MySQL Server 5.7\bin^
D:\Program Files\MySQL\MySQL Server 8.0\bin^
D:\Program Files (x86)\MySQL\MySQL Server 8.0\bin"

for %%p in (%COMMON_PATHS%) do (
    if exist "%%p\mysql.exe" (
        set "MYSQL_PATH=%%p\mysql.exe"
        goto :FOUND
    )
)

:FOUND
if defined MYSQL_PATH (
    echo Found MySQL at: !MYSQL_PATH!
) else (
    echo MySQL not found in common locations!
    set /p "MYSQL_PATH=Enter full path to mysql.exe: "
    
    if not exist "!MYSQL_PATH!" (
        echo Error: Path not found!
        pause
        exit /b 1
    )
)

echo.
echo Resetting database...
"!MYSQL_PATH!" -h 192.168.0.118 -u agm -paa111111 agent_management < backend\init.sql

if !errorlevel! equ 0 (
    echo.
    echo SUCCESS: Database reset completed!
    echo Default admin account: username=admin, password=123456
) else (
    echo.
    echo ERROR: Database reset failed!
)

pause