@echo off
chcp 65001 >nul

echo ==============================================
echo   Update Admin Password
echo ==============================================
echo.

:: Find MySQL
set "MYSQL_PATH="
set "COMMON_PATHS=C:\Program Files\MySQL\MySQL Server 8.0\bin,C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin,C:\Program Files\MySQL\MySQL Server 5.7\bin,C:\Program Files (x86)\MySQL\MySQL Server 5.7\bin,D:\Program Files\MySQL\MySQL Server 8.0\bin,C:\mysql\bin"

for %%p in ("%COMMON_PATHS:,=" "%") do (
    if exist "%%~p\mysql.exe" (
        set "MYSQL_PATH=%%~p\mysql.exe"
        goto :FOUND
    )
)

:FOUND
if not defined MYSQL_PATH (
    echo MySQL not found!
    set /p "MYSQL_PATH=Enter full path to mysql.exe: "
)

echo Updating admin password to: 123456
"!MYSQL_PATH!" -h 192.168.0.118 -u agm -paa111111 agent_management -e "UPDATE users SET hashed_password='$2b$12$Q6r//78ftYMOjWW0FlSPq.90rM3djLgJjoF75BNNRGJTEZ5d./TV6' WHERE username='admin';"

if !errorlevel! equ 0 (
    echo SUCCESS: Password updated!
) else (
    echo ERROR: Update failed!
)
pause