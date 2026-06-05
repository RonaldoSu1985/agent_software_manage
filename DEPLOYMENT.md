# 部署说明 (针对端口冲突环境)

本项目的部署配置已针对目标机器（8000 和 5174 端口已占用）进行了调整。

## 已修改配置
1.  **后端端口**: 由 `8000` 修改为 `8001`。
2.  **前端端口**: 由 `5173` 修改为 `5175`。
3.  **前端代理**: `frontend/vite.config.ts` 中的代理目标已指向 `http://localhost:8001`。
4.  **启动脚本**: 更新了 `restart.bat` 和 `stop.bat` 以使用新端口。

## 部署步骤

### 1. 环境准备
确保目标机器已安装：
- **Python 3.10+**
- **Node.js 18+**
- **MySQL 8.0+**

### 2. 数据库配置
1.  在 MySQL 中创建数据库：
    ```sql
    CREATE DATABASE agent_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    ```
2.  修改 `backend/app/core/config.py` 中的 `DATABASE_URL`，确保指向正确的数据库地址、用户名和密码。
3.  初始化表结构：
    ```bash
    cd backend
    pip install -r requirements.txt
    python scripts/init_database.py
    ```

### 3. 安装依赖
```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 4. 启动服务
在项目根目录下，直接双击运行：
- **启动/重启**: `restart.bat`
- **停止**: `stop.bat`

## 访问地址
- **前端页面**: `http://localhost:5175`
- **后端接口**: `http://localhost:8001`
- **API 文档**: `http://localhost:8001/api/v1/docs`

---
*注：如果 `8001` 或 `5175` 端口也被占用，请手动修改 `restart.bat` 中的 `BACKEND_PORT` 和 `FRONTEND_PORT` 变量，并同步修改 `frontend/vite.config.ts` 中的 `target` 端口。*
