# 代理商软件管理系统

## 项目结构
- `backend/`: FastAPI + SQLAlchemy (MySQL)
- `frontend/`: React + Vite + Ant Design

## 启动步骤

### 1. 数据库准备
- 创建 MySQL 数据库 `agent_management`。
- 执行 `backend/init.sql` 初始化表结构和基础数据。

### 2. 后端启动
```bash
cd backend
pip install -r requirements.txt
# 修改 app/core/config.py 中的 DATABASE_URL
uvicorn app.main:app --reload
```

### 3. 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 功能说明
- **RBAC**: 内置管理员账号 `admin` / `admin123`。
- **库存管理**: 支持 V3/LTB 系统下的软件库存查询。
- **业务操作**:
  - 新增采购：增加库存。
  - 商户安装：扣减库存。
  - 库存划拨：代理商之间转移库存。
- **审计日志**: 记录所有库存变动明细。
