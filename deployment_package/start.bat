@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "BACKEND_DIR=%~dp0backend"
set "PORT=8888"

cd /d "%BACKEND_DIR%"

echo ==============================================
echo        Agent Software Management System
echo ==============================================
echo.

:: Check Python installation
echo [Step 1/4] Checking Python environment...
python --version 2>NUL
if !errorlevel! neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo Found Python: !PY_VER!
echo.

:: Check if port is available
echo [Step 2/4] Checking port !PORT!...
netstat -ano | findstr ":%PORT%" | findstr "LISTENING" >NUL
if !errorlevel! equ 0 (
    echo WARNING: Port !PORT! is already in use!
    echo Trying to stop the existing process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
        taskkill /f /pid %%a >NUL 2>&1
        if !errorlevel! equ 0 (
            echo Stopped process PID: %%a
        ) else (
            echo Failed to stop process PID: %%a
        )
    )
    timeout /t 2 /nobreak >NUL
)
echo Port !PORT! is available
echo.

:: Install dependencies
echo [Step 3/4] Installing dependencies...
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo ERROR: Failed to install dependencies!
    echo Please check your network connection and try again.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo Dependencies installed successfully
echo.

:: Start the server
echo [Step 4/4] Starting server on port !PORT!...
echo Server will be available at: http://localhost:!PORT!
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --host 0.0.0.0 --port !PORT! --reload

:: If we get here, something went wrong
echo.
echo ERROR: Server stopped unexpectedly!
echo Press any key to exit...
pause >nul