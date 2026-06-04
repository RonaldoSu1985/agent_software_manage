@echo off
chcp 65001 >nul
echo.
echo ==================== 代理商管理系统 启动脚本 ====================
echo.

set "BACKEND_DIR=%~dp0backend"
set "FRONTEND_DIR=%~dp0frontend"
set "PORT=8080"

echo [1/2] 正在检查端口 %PORT%...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT%"') do (
    if not "%%a"=="0" (
        echo 正在停止占用端口的旧服务 (PID: %%a)...
        taskkill /f /pid %%a >nul 2>&1
    )
)

echo.
echo [2/2] 正在启动后端服务 (包含前端静态资源)...
echo 系统将运行在: http://localhost:%PORT%
echo.

cd /d "%BACKEND_DIR%"
python -m uvicorn app.main:app --host 0.0.0.0 --port %PORT%

pause
