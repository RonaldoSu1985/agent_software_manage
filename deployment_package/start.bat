@echo off
cd /d "%~dp0backend"
echo 正在安装依赖...
pip install -r requirements.txt
echo 依赖安装完成
echo 启动开发服务（端口：8888）...
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
pause