@echo off
echo 正在停止本机服务...


echo 检查端口 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a
    echo 已停止端口 5173 的进程 PID: %%a
)

echo 检查端口 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a
    echo 已停止端口 8000 的进程 PID: %%a
)

echo 本机服务已停止
pause