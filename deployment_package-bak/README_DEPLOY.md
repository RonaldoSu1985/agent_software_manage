# 代理商管理系统 部署说明

本包已完成前端编译和后端整合，可直接在安装了 Python 3.10+ 的 Windows 环境下运行。

## 部署步骤

### 1. 准备数据库
*   确保目标机器已安装 MySQL 8.0+。
*   创建一个名为 `agent_management` 的数据库。
*   如果需要初始化表结构和数据，请进入 `backend` 目录，参考 `init.sql` 或运行 `scripts` 中的脚本。
*   **重要：** 请修改 `backend/app/core/config.py` 中的 `DATABASE_URL`，确保指向目标机器的 MySQL 服务。

### 2. 安装环境依赖
*   双击运行根目录下的 `install.bat`。
*   该脚本会自动安装后端运行所需的 Python 库。

### 3. 启动系统
*   双击运行根目录下的 `start.bat`。
*   系统启动后，可通过浏览器访问：`http://localhost:8000`。

## 目录结构
*   `backend/`: 后端源码及配置文件。
*   `frontend/`: 前端编译后的静态文件（由后端自动托管）。
*   `install.bat`: 依赖安装脚本。
*   `start.bat`: 一键启动脚本。

## 注意事项
*   如果访问不到前端页面，请确认 `frontend` 目录是否存在且包含 `index.html`。
*   如果 API 报错，请确认数据库连接配置是否正确。
