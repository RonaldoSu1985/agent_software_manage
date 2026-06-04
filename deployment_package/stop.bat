@echo off
echo 正在停止服务（端口：8888）...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8888" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a
    echo 已停止进程 PID: %%a
)
echo 服务已停止
pause