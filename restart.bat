@echo off
chcp 65001 >nul
echo.
echo ==================== 项目重启脚本 ====================
echo.

set "BACKEND_DIR=d:\GeminiProject\backend"
set "FRONTEND_DIR=d:\GeminiProject\frontend"
set "BACKEND_PORT=8001"
set "FRONTEND_PORT=5175"

echo [1/4] 停止正在运行的服务...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%BACKEND_PORT%"') do (
    if not "%%a"=="0" (
        taskkill /f /pid %%a >nul 2>&1
        echo       已停止后端服务 (PID: %%a)
    )
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%FRONTEND_PORT%"') do (
    if not "%%a"=="0" (
        taskkill /f /pid %%a >nul 2>&1
        echo       已停止前端服务 (PID: %%a)
    )
)

timeout /t 2 /nobreak >nul

echo.
echo [2/4] 启动后端服务...
start "Backend - FastAPI" /d "%BACKEND_DIR%" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT% --reload"

timeout /t 3 /nobreak >nul

echo.
echo [3/4] 启动前端服务...
start "Frontend - React" /d "%FRONTEND_DIR%" cmd /k "npm run dev -- --host 0.0.0.0 --port %FRONTEND_PORT%"

timeout /t 2 /nobreak >nul

echo.
echo [4/4] 服务启动完成！
echo.
echo         后端服务: http://localhost:%BACKEND_PORT%
echo         前端服务: http://localhost:%FRONTEND_PORT%
echo.
echo 按任意键退出...
pause >nul