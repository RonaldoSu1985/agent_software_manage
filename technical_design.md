# 代理商软件库存管理系统 - 技术设计文档

## 1. 技术选型

### 1.1 架构风格
- **架构模式**: 前后端分离架构
- **设计模式**: RESTful API + 微服务思想（单体应用实现）

### 1.2 技术栈

| 分类 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 后端语言 | Python | 3.10+ | 核心业务逻辑开发 |
| 后端框架 | FastAPI | 0.100+ | 高性能异步API框架 |
| 数据库 | MySQL | 8.0+ | 关系型数据库 |
| ORM | SQLAlchemy | 2.0+ | 异步ORM框架 |
| 前端语言 | TypeScript | 5.0+ | 类型安全的前端开发 |
| 前端框架 | React | 18+ | 组件化前端框架 |
| 构建工具 | Vite | 6.0+ | 快速构建工具 |
| UI组件 | Ant Design | 5.0+ | 企业级UI组件库 |
| 状态管理 | React Context | - | 轻量级状态管理 |
| HTTP客户端 | Axios | 1.6+ | HTTP请求库 |
| 认证 | JWT | - | 无状态身份认证 |

---

## 2. 架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend)                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ 登录页  │ │ 库存管理│ │ 采购管理│ │ 安装管理│ │ 用户管理│  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │
│       │           │           │           │           │        │
└───────┼───────────┼───────────┼───────────┼───────────┼────────┘
        │           │           │           │           │
        ▼           ▼           ▼           ▼           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API网关层 (Nginx)                         │
│                        反向代理 / 负载均衡                       │
└───────┬─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                        后端层 (Backend)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Auth API   │  │ Inventory API│  │ Business API │          │
│  │  (认证模块)  │  │   (库存模块)  │  │  (业务模块)   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐          │
│  │   RBAC API   │  │ Dictionary API│  │   Deps       │          │
│  │  (权限模块)  │  │   (字典模块)  │  │  (依赖注入)   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           ▼                                    │
│                  ┌────────────────┐                            │
│                  │   Services     │                            │
│                  │ (业务服务层)   │                            │
│                  └───────┬────────┘                            │
│                           ▼                                    │
│                  ┌────────────────┐                            │
│                  │     CRUD       │                            │
│                  │  (数据访问层)   │                            │
│                  └───────┬────────┘                            │
│                           ▼                                    │
│                  ┌────────────────┐                            │
│                  │  Database      │                            │
│                  │    (MySQL)     │                            │
│                  └────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块划分

| 模块 | 功能说明 | 主要文件 |
|------|----------|----------|
| auth | 用户认证与授权 | `api/v1/endpoints/auth.py`, `services/auth_service.py` |
| rbac | 用户与角色管理 | `api/v1/endpoints/rbac.py`, `models/user.py` |
| inventory | 库存管理 | `api/v1/endpoints/inventory.py`, `services/inventory_service.py` |
| business | 业务操作（采购/安装/划拨） | `api/v1/endpoints/business.py`, `models/business.py` |
| dictionary | 数据字典管理 | `api/v1/endpoints/dictionary.py`, `crud/dictionary.py` |
| common | 通用接口 | `api/v1/endpoints/common.py` |

---

## 3. 目录结构

### 3.1 后端目录结构

```
backend/
├── app/                                    # 应用主目录
│   ├── api/                                # API层
│   │   ├── v1/                             # 版本1 API
│   │   │   ├── endpoints/                  # 端点定义
│   │   │   │   ├── auth.py                 # 认证接口
│   │   │   │   ├── rbac.py                 # 用户/角色管理
│   │   │   │   ├── inventory.py            # 库存查询接口
│   │   │   │   ├── business.py             # 业务操作接口
│   │   │   │   ├── dictionary.py           # 数据字典接口
│   │   │   │   └── common.py               # 通用接口
│   │   │   └── api.py                      # API路由注册
│   │   └── deps.py                         # 依赖注入定义
│   ├── core/                               # 核心配置
│   │   ├── config.py                       # 应用配置
│   │   └── config_test.py                  # 测试配置
│   ├── models/                             # 数据库模型
│   │   ├── database.py                     # 数据库连接
│   │   ├── user.py                         # 用户/角色模型
│   │   ├── dictionary.py                   # 数据字典模型
│   │   └── business.py                     # 业务数据模型
│   ├── schemas/                            # Pydantic Schema
│   │   ├── user.py                         # 用户相关Schema
│   │   ├── token.py                        # Token Schema
│   │   ├── dictionary.py                   # 字典相关Schema
│   │   └── business.py                     # 业务相关Schema
│   ├── services/                           # 业务服务层
│   │   ├── auth_service.py                 # 认证服务
│   │   └── inventory_service.py            # 库存服务
│   ├── crud/                               # 数据访问层
│   │   └── dictionary.py                   # 字典CRUD操作
│   └── main.py                             # 应用入口
├── requirements.txt                         # 依赖清单
└── init.sql                                # 数据库初始化脚本
```

### 3.2 前端目录结构

```
frontend/
├── src/                                    # 源代码目录
│   ├── api/                                # API调用封装
│   │   └── index.ts                        # API接口定义
│   ├── components/                         # 公共组件
│   │   └── MainLayout.tsx                  # 主布局组件
│   ├── pages/                              # 页面组件
│   │   ├── LoginPage.tsx                   # 登录页
│   │   ├── InventoryList.tsx               # 库存列表页
│   │   ├── PurchaseList.tsx                # 采购记录页
│   │   ├── InstallList.tsx                 # 安装记录页
│   │   ├── TransferList.tsx                # 划拨记录页
│   │   ├── StockLogs.tsx                   # 库存变动记录页
│   │   ├── DictionaryList.tsx              # 数据字典页
│   │   ├── UserList.tsx                    # 用户管理页
│   │   └── RoleList.tsx                    # 角色管理页
│   ├── styles/                             # 样式文件
│   │   └── responsive.css                  # 响应式样式
│   ├── App.tsx                             # 应用根组件
│   ├── main.tsx                            # 应用入口
│   ├── index.css                           # 全局样式
│   └── App.css                             # 应用样式
├── public/                                 # 静态资源
├── vite.config.ts                          # Vite配置
├── tsconfig.json                           # TypeScript配置
└── package.json                            # 项目配置
```

---

## 4. 关键类与方法设计

### 4.1 后端核心类

#### 4.1.1 数据库模型类

**User 模型** (`models/user.py`)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PRIMARY KEY, AUTO_INCREMENT | 用户ID |
| username | str | UNIQUE, NOT NULL | 用户名 |
| hashed_password | str | NOT NULL | 密码哈希 |
| full_name | str | - | 用户姓名 |
| role_id | int | FOREIGN KEY | 角色ID |
| department | str | - | 部门编码 |
| is_active | bool | DEFAULT True | 是否激活 |
| created_at | datetime | DEFAULT NOW() | 创建时间 |

**Role 模型** (`models/user.py`)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PRIMARY KEY, AUTO_INCREMENT | 角色ID |
| name | str | UNIQUE, NOT NULL | 角色名称 |
| permissions | str | - | 权限列表(JSON) |
| created_at | datetime | DEFAULT NOW() | 创建时间 |

**DictionaryType 模型** (`models/dictionary.py`)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PRIMARY KEY, AUTO_INCREMENT | 类型ID |
| type_name | str | NOT NULL | 类型名称 |
| type_code | str | UNIQUE, NOT NULL | 类型编码 |
| description | str | - | 描述 |
| status | bool | DEFAULT True | 状态 |
| created_at | datetime | DEFAULT NOW() | 创建时间 |
| updated_at | datetime | ON UPDATE NOW() | 更新时间 |

**DictionaryItem 模型** (`models/dictionary.py`)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PRIMARY KEY, AUTO_INCREMENT | 字典项ID |
| type_id | int | FOREIGN KEY | 字典类型ID |
| item_key | str | NOT NULL | 字典键 |
| item_value | str | NOT NULL | 字典值 |
| item_name | str | - | 字典名称 |
| sort_order | int | DEFAULT 0 | 排序号 |
| status | bool | DEFAULT True | 状态 |
| remark | str | - | 备注 |
| created_at | datetime | DEFAULT NOW() | 创建时间 |
| updated_at | datetime | ON UPDATE NOW() | 更新时间 |

**业务数据模型** (`models/business.py`)

| 模型 | 说明 | 关键字段 |
|------|------|----------|
| Agent | 代理商信息 | agent_code, agent_name, system_type |
| Software | 软件信息 | name |
| Inventory | 库存信息 | agent_id, software_id, quantity |
| PurchaseRecord | 采购记录 | agent_id, software_id, quantity, purchase_date |
| InstallationRecord | 安装记录 | agent_id, software_id, merchant_code, quantity |
| TransferRecord | 划拨记录 | from_agent_id, to_agent_id, software_id, quantity |
| InventoryLog | 库存变动日志 | agent_id, software_id, change_type, before_qty, change_qty, after_qty |

#### 4.1.2 Service 类

**AuthService** (`services/auth_service.py`)

| 方法 | 功能 | 参数 | 返回值 |
|------|------|------|--------|
| create_access_token | 生成JWT Token | data: dict, expires_delta: timedelta | str (token) |
| verify_password | 验证密码 | plain_password: str, hashed_password: str | bool |
| get_password_hash | 加密密码 | password: str | str (hash) |

**InventoryService** (`services/inventory_service.py`)

| 方法 | 功能 | 参数 | 返回值 |
|------|------|------|--------|
| purchase | 采购入库 | db, agent_id, software_id, quantity, operator_id | InventoryLog |
| install | 安装出库 | db, agent_id, software_id, merchant_code, merchant_name, quantity, operator_id | InventoryLog |
| transfer | 划拨操作 | db, from_agent_id, to_agent_id, software_id, quantity, operator_id | (from_log, to_log) |

### 4.2 前端核心组件

**MainLayout** (`components/MainLayout.tsx`)

| 属性 | 类型 | 说明 |
|------|------|------|
| children | ReactNode | 子组件内容 |

**页面组件** (`pages/*.tsx`)

| 组件 | 功能 | 主要交互 |
|------|------|----------|
| LoginPage | 用户登录 | 表单提交、Token存储 |
| InventoryList | 库存列表 | 查询、查看变动记录 |
| PurchaseList | 采购记录 | 查询、新增采购 |
| InstallList | 安装记录 | 查询、新增安装 |
| TransferList | 划拨记录 | 查询、新增划拨 |
| StockLogs | 库存变动日志 | 查询、导出 |
| DictionaryList | 数据字典 | CRUD操作 |
| UserList | 用户管理 | CRUD操作 |
| RoleList | 角色管理 | CRUD操作、权限配置 |

---

## 5. 数据库与数据结构设计

### 5.1 数据库表结构

#### 5.1.1 用户表 (users)

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role_id INT,
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);
```

#### 5.1.2 角色表 (roles)

```sql
CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    permissions TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.1.3 字典类型表 (dictionary_type)

```sql
CREATE TABLE dictionary_type (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(100) NOT NULL,
    type_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    status BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
);
```

#### 5.1.4 字典项表 (dictionary_item)

```sql
CREATE TABLE dictionary_item (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type_id INT NOT NULL,
    item_key VARCHAR(100) NOT NULL,
    item_value VARCHAR(255) NOT NULL,
    item_name VARCHAR(100),
    sort_order INT DEFAULT 0,
    status BOOLEAN DEFAULT TRUE,
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (type_id) REFERENCES dictionary_type(id)
);
```

#### 5.1.5 代理商表 (agents)

```sql
CREATE TABLE agents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_code VARCHAR(50) UNIQUE NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    system_type VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.1.6 软件表 (software)

```sql
CREATE TABLE software (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.1.7 库存表 (inventory)

```sql
CREATE TABLE inventory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_id INT NOT NULL,
    software_id INT NOT NULL,
    quantity INT DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    UNIQUE KEY (agent_id, software_id)
);
```

#### 5.1.8 采购记录表 (purchase_records)

```sql
CREATE TABLE purchase_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_id INT NOT NULL,
    software_id INT NOT NULL,
    quantity INT NOT NULL,
    purchase_date DATE NOT NULL,
    operator_id INT,
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
);
```

#### 5.1.9 安装记录表 (installation_records)

```sql
CREATE TABLE installation_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_id INT NOT NULL,
    software_id INT NOT NULL,
    merchant_code VARCHAR(50),
    merchant_name VARCHAR(100),
    quantity INT NOT NULL,
    install_date DATE NOT NULL,
    operator_id INT,
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
);
```

#### 5.1.10 划拨记录表 (transfer_records)

```sql
CREATE TABLE transfer_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    from_agent_id INT NOT NULL,
    to_agent_id INT NOT NULL,
    software_id INT NOT NULL,
    quantity INT NOT NULL,
    transfer_date DATE NOT NULL,
    operator_id INT,
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_agent_id) REFERENCES agents(id),
    FOREIGN KEY (to_agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
);
```

#### 5.1.11 库存变动日志表 (inventory_logs)

```sql
CREATE TABLE inventory_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_id INT NOT NULL,
    software_id INT NOT NULL,
    change_type VARCHAR(20) NOT NULL,
    before_qty INT NOT NULL,
    change_qty INT NOT NULL,
    after_qty INT NOT NULL,
    related_id INT,
    operator_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
);
```

### 5.2 API响应结构

**通用响应格式**

```json
{
    "code": 200,
    "message": "success",
    "data": {}
}
```

**分页响应格式**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [],
        "total": 100,
        "page": 1,
        "size": 10
    }
}
```

---

## 6. API 接口设计

### 6.1 认证接口

| API路径 | HTTP方法 | Controller文件 | 功能描述 |
|---------|----------|----------------|----------|
| `/api/v1/auth/login` | POST | `auth.py` | 用户登录 |
| `/api/v1/auth/logout` | POST | `auth.py` | 用户登出 |

**登录请求**

```json
POST /api/v1/auth/login
{
    "username": "string",
    "password": "string"
}
```

**登录响应**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "access_token": "string",
        "token_type": "bearer",
        "username": "string",
        "role_name": "string",
        "permissions": ["string"]
    }
}
```

### 6.2 用户管理接口

| API路径 | HTTP方法 | Controller文件 | 功能描述 |
|---------|----------|----------------|----------|
| `/api/v1/users` | GET | `rbac.py` | 获取用户列表 |
| `/api/v1/users/{user_id}` | GET | `rbac.py` | 获取单个用户 |
| `/api/v1/users` | POST | `rbac.py` | 创建用户 |
| `/api/v1/users/{user_id}` | PUT | `rbac.py` | 更新用户 |
| `/api/v1/users/{user_id}` | DELETE | `rbac.py` | 删除用户 |

**创建用户请求**

```json
POST /api/v1/users
{
    "username": "string",
    "password": "string",
    "full_name": "string",
    "role_id": "integer",
    "department": "string"
}
```

**用户响应**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "integer",
        "username": "string",
        "full_name": "string",
        "role_id": "integer",
        "role_name": "string",
        "department": "string",
        "department_name": "string",
        "is_active": "boolean",
        "created_at": "datetime"
    }
}
```

### 6.3 角色管理接口

| API路径 | HTTP方法 | Controller文件 | 功能描述 |
|---------|----------|----------------|----------|
| `/api/v1/roles` | GET | `rbac.py` | 获取角色列表 |
| `/api/v1/roles/{role_id}` | GET | `rbac.py` | 获取单个角色 |
| `/api/v1/roles` | POST | `rbac.py` | 创建角色 |
| `/api/v1/roles/{role_id}` | PUT | `rbac.py` | 更新角色 |
| `/api/v1/roles/{role_id}` | DELETE | `rbac.py` | 删除角色 |

**角色响应**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "integer",
        "name": "string",
        "permissions": ["string"],
        "created_at": "datetime"
    }
}
```

### 6.4 库存管理接口

| API路径 | HTTP方法 | Controller文件 | 功能描述 |
|---------|----------|----------------|----------|
| `/api/v1/inventory` | GET | `inventory.py` | 获取库存列表 |
| `/api/v1/inventory/{inventory_id}` | GET | `inventory.py` | 获取库存详情 |

**库存列表响应**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [
            {
                "id": "integer",
                "agent_code": "string",
                "agent_name": "string",
                "system_type": "string",
                "software_name": "string",
                "quantity": "integer"
            }
        ],
        "total": "integer"
    }
}
```

### 6.5 业务操作接口

| API路径 | HTTP方法 | Controller文件 | 功能描述 |
|---------|----------|----------------|----------|
| `/api/v1/business/purchase` | POST | `business.py` | 新增采购 |
| `/api/v1/business/purchase/list` | GET | `business.py` | 获取采购记录 |
| `/api/v1/business/install` | POST | `business.py` | 新增安装 |
| `/api/v1/business/install/list` | GET | `business.py` | 获取安装记录 |
| `/api/v1/business/transfer` | POST | `business.py` | 新增划拨 |
| `/api/v1/business/transfer/list` | GET | `business.py` | 获取划拨记录 |
| `/api/v1/business/stock-logs` | GET | `business.py` | 获取库存变动日志 |

**采购请求**

```json
POST /api/v1/business/purchase
{
    "agent_id": "integer",
    "software_id": "integer",
    "quantity": "integer",
    "purchase_date": "date",
    "remark": "string"
}
```

### 6.6 数据字典接口

| API路径 | HTTP方法 | Controller文件 | 功能描述 |
|---------|----------|----------------|----------|
| `/api/v1/dictionary/types` | GET | `dictionary.py` | 获取字典类型列表 |
| `/api/v1/dictionary/types` | POST | `dictionary.py` | 创建字典类型 |
| `/api/v1/dictionary/items` | GET | `dictionary.py` | 获取字典项列表 |
| `/api/v1/dictionary/items` | POST | `dictionary.py` | 创建字典项 |
| `/api/v1/dictionary/items/{item_id}` | PUT | `dictionary.py` | 更新字典项 |
| `/api/v1/dictionary/items/{item_id}` | DELETE | `dictionary.py` | 删除字典项 |
| `/api/v1/dictionary/items/type/{type_code}` | GET | `dictionary.py` | 根据类型获取字典项 |

---

## 7. 主业务流程与调用链

### 7.1 登录流程

```
前端 LoginPage ──POST──> /api/v1/auth/login ──> auth.py ──> auth_service.py
                                                               │
                                                               ▼
                                                      验证用户名密码
                                                               │
                                                               ▼
                                                      生成JWT Token
                                                               │
                                                               ▼
                                                         返回用户信息
```

**调用链**

| 步骤 | 文件 | 方法 | 说明 |
|------|------|------|------|
| 1 | `auth.py` | `login()` | 接收登录请求 |
| 2 | `auth_service.py` | `verify_password()` | 验证密码 |
| 3 | `auth_service.py` | `create_access_token()` | 生成Token |
| 4 | `auth.py` | 返回响应 | 返回用户信息和Token |

### 7.2 采购流程

```
前端 PurchaseList ──POST──> /api/v1/business/purchase ──> business.py
                                                               │
                                                               ▼
                                                     inventory_service.py
                                                               │
                                                               ├── 创建采购记录
                                                               ├── 更新库存(+数量)
                                                               └── 记录库存变动日志
```

**调用链**

| 步骤 | 文件 | 方法 | 说明 |
|------|------|------|------|
| 1 | `business.py` | `create_purchase()` | 接收采购请求 |
| 2 | `inventory_service.py` | `purchase()` | 执行采购业务逻辑 |
| 3 | `models/business.py` | `PurchaseRecord` | 创建采购记录 |
| 4 | `models/business.py` | `Inventory` | 更新库存数量 |
| 5 | `models/business.py` | `InventoryLog` | 记录变动日志 |

### 7.3 安装流程

```
前端 InstallList ──POST──> /api/v1/business/install ──> business.py
                                                               │
                                                               ▼
                                                     inventory_service.py
                                                               │
                                                               ├── 验证库存充足
                                                               ├── 创建安装记录
                                                               ├── 更新库存(-数量)
                                                               └── 记录库存变动日志
```

**调用链**

| 步骤 | 文件 | 方法 | 说明 |
|------|------|------|------|
| 1 | `business.py` | `create_installation()` | 接收安装请求 |
| 2 | `inventory_service.py` | `install()` | 执行安装业务逻辑 |
| 3 | `models/business.py` | `Inventory` | 验证并更新库存 |
| 4 | `models/business.py` | `InstallationRecord` | 创建安装记录 |
| 5 | `models/business.py` | `InventoryLog` | 记录变动日志 |

### 7.4 划拨流程

```
前端 TransferList ──POST──> /api/v1/business/transfer ──> business.py
                                                               │
                                                               ▼
                                                     inventory_service.py
                                                               │
                                                               ├── 验证划出方库存充足
                                                               ├── 创建划拨记录
                                                               ├── 更新划出方库存(-数量)
                                                               ├── 更新划入方库存(+数量)
                                                               └── 记录双方库存变动日志
```

**调用链**

| 步骤 | 文件 | 方法 | 说明 |
|------|------|------|------|
| 1 | `business.py` | `create_transfer()` | 接收划拨请求 |
| 2 | `inventory_service.py` | `transfer()` | 执行划拨业务逻辑 |
| 3 | `models/business.py` | `Inventory` | 验证划出方库存 |
| 4 | `models/business.py` | `TransferRecord` | 创建划拨记录 |
| 5 | `models/business.py` | `Inventory` | 更新双方库存 |
| 6 | `models/business.py` | `InventoryLog` | 记录双方变动日志 |

---

## 8. 部署与集成方案

### 8.1 依赖与环境

**后端依赖** (`requirements.txt`)

```txt
fastapi==0.100.0
uvicorn==0.23.2
sqlalchemy==2.0.20
pydantic==2.4.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pymysql==1.1.0
python-dotenv==1.0.0
```

**前端依赖** (`package.json`)

```json
{
    "dependencies": {
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "react-router-dom": "^6.15.0",
        "antd": "^5.9.0",
        "axios": "^1.6.0",
        "@ant-design/icons": "^5.2.6"
    },
    "devDependencies": {
        "@types/react": "^18.2.21",
        "@types/react-dom": "^18.2.7",
        "@vitejs/plugin-react": "^4.3.1",
        "typescript": "^5.2.2",
        "vite": "^6.4.0",
        "tailwindcss": "^3.3.3",
        "postcss": "^8.4.29",
        "autoprefixer": "^10.4.15"
    }
}
```

### 8.2 配置与运行

**后端配置** (`core/config.py`)

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接地址 | mysql+pymysql://user:pass@localhost:3306/db |
| SECRET_KEY | JWT密钥 | - |
| ALGORITHM | JWT算法 | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token过期时间(分钟) | 30 |

**启动方式**

**开发环境**

```bash
# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端
cd frontend
npm install
npm run dev
```

**生产环境**

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm install
npm run build
```

---

## 9. 代码安全性

### 9.1 注意事项

| 风险类型 | 风险描述 | 关联模块 |
|----------|----------|----------|
| 认证绕过 | 未授权访问受保护资源 | auth, deps |
| SQL注入 | 通过输入注入恶意SQL | 所有数据库操作 |
| 密码泄露 | 明文存储或传输密码 | auth_service |
| XSS攻击 | 前端未过滤用户输入 | 前端所有页面 |
| CSRF攻击 | 跨站请求伪造 | 表单提交接口 |
| 敏感信息泄露 | 日志或响应中包含敏感数据 | 所有API |
| 越权访问 | 用户访问非授权数据 | rbac, business |

### 9.2 解决方案

| 风险类型 | 解决方案 | 实施位置 |
|----------|----------|----------|
| 认证绕过 | 使用JWT Token验证，依赖注入检查权限 | `api/deps.py` |
| SQL注入 | 使用SQLAlchemy ORM，禁止拼接SQL | 所有CRUD操作 |
| 密码泄露 | 使用bcrypt加密存储，HTTPS传输 | `services/auth_service.py` |
| XSS攻击 | 使用Ant Design自动转义，手动过滤富文本 | 前端组件 |
| CSRF攻击 | 使用JWT Token认证，无需额外CSRF防护 | 全局 |
| 敏感信息泄露 | 配置日志脱敏，响应中不返回密码等敏感字段 | `schemas/*`, 日志配置 |
| 越权访问 | 在Service层验证用户权限，检查数据归属 | `services/*` |

**安全配置要点**

1. **JWT密钥管理**: 使用环境变量存储密钥，禁止硬编码
2. **密码策略**: 强制密码复杂度要求，定期更换密码
3. **HTTPS**: 生产环境强制使用HTTPS
4. **输入验证**: 使用Pydantic进行严格的输入验证
5. **日志审计**: 记录关键操作日志，便于安全审计
6. **权限最小化**: 遵循最小权限原则，按需分配角色权限