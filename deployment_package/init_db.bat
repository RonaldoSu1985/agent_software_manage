@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==============================================
echo        Agent Software Management System
echo        Database Initialization Script
echo ==============================================
echo.
echo Database Configuration:
echo   Host: 192.168.0.118
echo   Port: 3306
echo   Database: agent_management
echo   Username: agm
echo   Password: aa111111
echo.

:: Try to find mysql in common locations
set "MYSQL_PATH="
set "COMMON_PATHS=C:\Program Files\MySQL\MySQL Server 8.0\bin,C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin,C:\Program Files\MySQL\MySQL Server 5.7\bin,C:\Program Files (x86)\MySQL\MySQL Server 5.7\bin,D:\Program Files\MySQL\MySQL Server 8.0\bin,D:\Program Files (x86)\MySQL\MySQL Server 8.0\bin,C:\mysql\bin,D:\mysql\bin"

for %%p in ("%COMMON_PATHS:,=" "%") do (
    if exist "%%~p\mysql.exe" (
        set "MYSQL_PATH=%%~p\mysql.exe"
        goto :FOUND
    )
)

:FOUND
if defined MYSQL_PATH (
    echo Found MySQL at: !MYSQL_PATH!
) else (
    echo MySQL not found in common locations!
    echo.
    set /p "MYSQL_PATH=Enter full path to mysql.exe: "

    if not exist "!MYSQL_PATH!" (
        echo Error: Path not found: !MYSQL_PATH!
        pause
        exit /b 1
    )
)

echo.
echo Step 1: Drop and recreate database...
"!MYSQL_PATH!" -h 192.168.0.118 -u agm -paa111111 -e "DROP DATABASE IF EXISTS agent_management; CREATE DATABASE agent_management DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

if !errorlevel! neq 0 (
    echo ERROR: Failed to create database!
    pause
    exit /b 1
)

echo.
echo Step 2: Initialize schema and seed data...
"!MYSQL_PATH!" -h 192.168.0.118 -u agm -paa111111 agent_management ^< backend\init.sql

if !errorlevel! equ 0 (
    echo.
    echo ==============================================
    echo SUCCESS: Database initialization completed!
    echo ==============================================
    echo.
    echo Default admin account:
    echo   Username: admin
    echo   Password: 123456
    echo.
    echo Initial data includes:
    echo   - 1 admin role with all permissions
    echo   - 1 admin user (admin/123456)
    echo   - 14 departments
    echo   - 2 system types (V3, LTB)
    echo   - 2 software (汇客餐饮, 汇客零售)
) else (
    echo.
    echo ERROR: Database initialization failed!
    echo Possible reasons:
    echo 1. MySQL server is not running
    echo 2. Incorrect database credentials
    echo 3. Network issue connecting to 192.168.0.118
)

echo.
pause