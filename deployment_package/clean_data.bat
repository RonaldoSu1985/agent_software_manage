@echo off
cd /d "%~dp0"
echo ==============================================
echo        代理商软件库存管理系统 - 数据清理
echo ==============================================
echo.
echo 注意：此脚本用于清理测试数据
echo 请确保已备份重要数据
echo.
python clean_data.py
pause