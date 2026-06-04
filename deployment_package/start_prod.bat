@echo off
cd /d "%~dp0backend"
echo 启动生产服务（端口：8888）...
uvicorn app.main:app --host 0.0.0.0 --port 8888
pause