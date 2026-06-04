@echo off
chcp 65001 >nul
echo.
echo ==================== 代理商管理系统 环境安装脚本 ====================
echo.

echo [1/2] 正在安装 Python 依赖库...
cd /d "%~dp0backend"
python -m pip install -r requirements.txt

echo.
echo [2/2] 环境准备完成！
echo.
echo 如果您是第一次部署，请先安装 MySQL 并运行 backend/scripts 目录下的初始化脚本。
echo.
pause
