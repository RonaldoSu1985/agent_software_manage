@echo off
cd /d "%~dp0backend"
echo ==============================================
echo    代理商软件库存管理系统 - 生产环境启动脚本
echo ==============================================
echo.
echo 启动生产服务（端口：8888）...
echo 服务地址: http://localhost:8888
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8888