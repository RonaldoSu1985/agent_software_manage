@echo off
cd /d "%~dp0backend"
echo 警告：此操作将清空所有业务数据（代理商、库存、采购、安装、调拨记录）！
echo 仅保留初始数据（角色、用户、字典数据、软件）。
set /p "confirm=确定继续吗？(Y/N): "
if /i not "%confirm%"=="Y" (
    echo 操作已取消
    pause
    exit /b
)
echo 正在清理测试数据...
python clean_data.py
echo 清理完成
pause