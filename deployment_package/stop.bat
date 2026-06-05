@echo off
echo ==============================================
echo        代理商软件库存管理系统 - 停止脚本
echo ==============================================
echo.
echo 正在停止服务（端口：8888）...
set "found=0"
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8888" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a
    echo 已停止进程 PID: %%a
    set "found=1"
)
if %found% equ 0 (
    echo 未找到运行在端口 8888 的服务
) else (
    echo.
    echo 服务已停止
)
pause