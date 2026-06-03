# 代理商软件库存管理系统 - 技术设计文档

## 1. 系统架构

### 1.1 架构概述
本系统采用前后端分离架构，前端使用 React + TypeScript，后端使用 FastAPI + MySQL。

### 1.2 技术栈

| 分类 | 技术 | 版本 |
|------|------|------|
| 前端框架 | React | 18.x |
| 前端语言 | TypeScript | 5.x |
| 前端构建工具 | Vite | 8.x |
| UI组件库 | Ant Design | 5.x |
| 后端框架 | FastAPI | 0.104.x |
| 后端语言 | Python | 3.12+ |
| 数据库 | MySQL | 8.0+ |
| ORM | SQLAlchemy | 2.0+ |
| 认证 | JWT | PyJWT |
| 密码哈希 | bcrypt | - |

### 1.3 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端层 (React)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ Login    │ │ Inventory│ │ Purchase │ │ MainLayout       │  │
│  │ Page     │ │ List     │ │ List     │ │ (路由/导航)      │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
│       │            │            │                  │           │
│       └────────────┴────────────┴──────────────────┘           │
│                          │                                   │
└──────────────────────────┼─────────────────────────────────────┘
                           │ HTTP/HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       后端层 (FastAPI)                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API Gateway                          │   │
│  │  /api/v1/auth    /api/v1/inventory    /api/v1/business │   │
│  │  /api/v1/common  /api/v1/rbac        /api/v1/dictionary│   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │                                         │
│  ┌──────────────────┴──────────────────────────────────────┐   │
│  │                    Service Layer                        │   │
│  │  AuthService    InventoryService    BusinessService    │   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │                                         │
│  ┌──────────────────┴──────────────────────────────────────┐   │
│  │                    Data Access Layer                     │   │
│  │              SQLAlchemy Async Session                   │   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │                                         │
└─────────────────────┼─────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      数据层 (MySQL)                           │
│  ┌──────┐ ┌───────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐   │
│  │users │ │ roles │ │ agents   │ │ software  │ │inventory│   │
│  └──────┘ └───────┘ └──────────┘ └───────────┘ └──────────┘   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │purchase_     │ │installation_ │ │transfer_     │            │
│  │records       │ │records       │ │records       │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │inventory_    │ │dictionary_   │ │dictionary_   │            │
│  │logs          │ │type          │ │item          │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 目录结构

### 2.1 后端目录结构

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py          # 认证相关接口
│   │   │   │   ├── inventory.py      # 库存相关接口
│   │   │   │   ├── business.py       # 业务操作接口（采购/安装/划拨）
│   │   │   │   ├── common.py         # 通用接口（软件/代理商列表）
│   │   │   │   ├── rbac.py           # 用户/角色管理接口
│   │   │   │   └── dictionary.py     # 数据字典接口
│   │   │   └── api.py                # 路由注册
│   │   └── deps.py                   # 依赖注入（数据库会话、当前用户）
│   ├── core/
│   │   ├── config.py                 # 配置管理
│   │   └── config_test.py            # 测试配置
│   ├── models/
│   │   ├── database.py               # 数据库连接配置
│   │   ├── business.py               # 业务模型（代理商、软件、库存等）
│   │   ├── user.py                   # 用户模型（用户、角色）
│   │   └── dictionary.py             # 数据字典模型
│   ├── schemas/
│   │   ├── business.py               # 业务相关数据结构
│   │   ├── user.py                   # 用户相关数据结构
│   │   ├── token.py                  # Token相关数据结构
│   │   └── dictionary.py             # 数据字典相关数据结构
│   ├── services/
│   │   ├── auth_service.py           # 认证服务
│   │   └── inventory_service.py      # 库存服务
│   └── main.py                       # 应用入口
├── scripts/
│   ├── init_dictionary.py            # 数据字典初始化脚本
│   ├── init_users.py                 # 用户初始化脚本
│   ├── init_database.py              # 数据库初始化脚本
│   ├── init_test_data.py             # 测试数据初始化脚本
│   └── clear_test_data.py            # 测试数据清理脚本
├── requirements.txt                  # 依赖清单
└── init.sql                          # MySQL数据库初始化脚本
```

### 2.2 前端目录结构

```
frontend/
├── public/                           # 静态资源
├── src/
│   ├── api/
│   │   └── index.ts                  # API请求封装（Axios）
│   ├── components/
│   │   └── MainLayout.tsx            # 主布局组件
│   ├── pages/
│   │   ├── LoginPage.tsx             # 登录页面
│   │   ├── InventoryList.tsx         # 代理商库存管理页面
│   │   ├── PurchaseList.tsx          # 代理商采购记录页面
│   │   ├── InstallList.tsx           # 代理商安装记录页面
│   │   ├── TransferList.tsx          # 代理商划拨记录页面
│   │   ├── StockLogs.tsx             # 代理商库存记录页面
│   │   ├── DictionaryList.tsx        # 数据字典管理页面
│   │   ├── UserList.tsx              # 用户管理页面
│   │   └── RoleList.tsx              # 角色管理页面
│   ├── App.tsx                       # 应用组件（路由配置）
│   ├── main.tsx                      # 应用入口
│   └── index.css                     # 全局样式
├── package.json                      # 依赖配置
├── vite.config.ts                    # Vite配置
└── tsconfig.json                     # TypeScript配置
```

---

## 3. 关键类与方法设计

### 3.1 后端API接口

#### 3.1.1 认证接口 (`auth.py`)

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /api/v1/auth/login | 用户登录 |
| POST | /api/v1/auth/logout | 用户登出 |
| GET | /api/v1/auth/me | 获取当前用户信息 |

#### 3.1.2 库存接口 (`inventory.py`)

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /api/v1/inventory/list | 查询库存列表 |
| GET | /api/v1/inventory/logs | 查询库存变动日志 |

#### 3.1.3 业务接口 (`business.py`)

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /api/v1/business/purchase | 创建采购记录 |
| POST | /api/v1/business/install | 创建安装记录 |
| POST | /api/v1/business/transfer | 创建划拨记录 |

#### 3.1.4 通用接口 (`common.py`)

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /api/v1/common/software | 获取软件列表 |
| GET | /api/v1/common/agents | 获取代理商列表 |

#### 3.1.5 RBAC接口 (`rbac.py`)

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /api/v1/users | 查询用户列表 |
| POST | /api/v1/users | 创建用户 |
| GET | /api/v1/users/{id} | 获取用户详情 |
| PUT | /api/v1/users/{id} | 更新用户 |
| DELETE | /api/v1/users/{id} | 删除用户 |
| GET | /api/v1/roles | 查询角色列表 |
| POST | /api/v1/roles | 创建角色 |
| GET | /api/v1/roles/{id} | 获取角色详情 |
| PUT | /api/v1/roles/{id} | 更新角色 |
| DELETE | /api/v1/roles/{id} | 删除角色 |

#### 3.1.6 数据字典接口 (`dictionary.py`)

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /api/v1/dictionary/types | 获取字典类型列表 |
| POST | /api/v1/dictionary/types | 创建字典类型 |
| GET | /api/v1/dictionary/types/{type_id} | 获取字典类型详情 |
| PUT | /api/v1/dictionary/types/{type_id} | 更新字典类型 |
| DELETE | /api/v1/dictionary/types/{type_id} | 删除字典类型 |
| GET | /api/v1/dictionary/items | 获取字典项列表 |
| POST | /api/v1/dictionary/items | 创建字典项 |
| GET | /api/v1/dictionary/items/{item_id} | 获取字典项详情 |
| PUT | /api/v1/dictionary/items/{item_id} | 更新字典项 |
| DELETE | /api/v1/dictionary/items/{item_id} | 删除字典项 |
| GET | /api/v1/dictionary/items/export | 导出字典项 |
| GET | /api/v1/dictionary/by_type/{type_code} | 按类型编码获取字典项 |

### 3.2 服务层方法

#### 3.2.1 AuthService (`services/auth_service.py`)

| 方法 | 参数 | 返回值 | 功能 |
|------|------|--------|------|
| authenticate_user | db, username, password | User | 验证用户身份 |
| create_access_token | data, expires_delta | str | 生成JWT Token |
| get_password_hash | password | str | 密码哈希 |
| verify_password | plain_password, hashed_password | bool | 验证密码 |

#### 3.2.2 InventoryService (`services/inventory_service.py`)

| 方法 | 参数 | 返回值 | 功能 |
|------|------|--------|------|
| get_or_create_agent | db, agent_code, agent_name, system_type | Agent | 获取或创建代理商 |
| get_or_create_software | db, name | Software | 获取或创建软件 |
| get_inventory | db, agent_id, software_id | Inventory | 获取库存记录 |
| add_purchase | db, agent_id, software_id, quantity, purchase_date, operator_id, remark | PurchaseRecord | 添加采购记录 |
| add_installation | db, agent_id, software_id, quantity, merchant_code, merchant_name, install_date, operator_id, remark | InstallationRecord | 添加安装记录 |
| add_transfer | db, from_agent_id, to_agent_id, software_id, quantity, transfer_date, operator_id, remark | TransferRecord | 添加划拨记录 |
| update_inventory | db, agent_id, software_id, delta | Inventory | 更新库存数量 |
| add_inventory_log | db, agent_id, software_id, change_type, before_qty, change_qty, after_qty, related_id, operator_id | InventoryLog | 添加库存变动日志 |

### 3.3 数据模型

#### 3.3.1 用户模型 (`models/user.py`)

**User 类**
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PrimaryKey | 用户ID |
| username | String(50) | Unique, NotNull | 用户名 |
| hashed_password | String | NotNull | 密码哈希 |
| full_name | String(100) | - | 姓名 |
| role_id | Integer | ForeignKey | 角色ID |
| is_active | Boolean | Default=True | 是否激活 |
| created_at | DateTime | Default=now() | 创建时间 |

**Role 类**
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PrimaryKey | 角色ID |
| name | String(50) | Unique, NotNull | 角色名称 |
| permissions | Text | - | 权限列表(JSON) |
| created_at | DateTime | Default=now() | 创建时间 |

#### 3.3.2 业务模型 (`models/business.py`)

**Agent 类**
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PrimaryKey | 代理商ID |
| agent_code | String(50) | Unique, NotNull | 代理商编号 |
| agent_name | String(100) | NotNull | 代理商名称 |
| system_type | String(20) | NotNull | 所属系统（从数据字典获取） |
| created_at | DateTime | Default=now() | 创建时间 |

**Software 类**
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PrimaryKey | 软件ID |
| name | String(50) | Unique, NotNull | 软件名称 |
| created_at | DateTime | Default=now() | 创建时间 |

**Inventory 类**
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PrimaryKey | 库存ID |
| agent_id | Integer | ForeignKey, NotNull | 代理商ID |
| software_id | Integer | ForeignKey, NotNull | 软件ID |
| quantity | Integer | Default=0, NotNull | 库存数量 |
| updated_at | DateTime | Default=now() | 更新时间 |

**PurchaseRecord 类**
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PrimaryKey | 采购记录ID |
| agent_id | Integer | ForeignKey, NotNull | 代理商ID |
| software_id | Integer | ForeignKey, NotNull | 软件ID |
| quantity | Integer | NotNull | 采购数量 |
| purchase_date | Date | NotNull | 采购日期 |
| operator_id | Integer | ForeignKey, NotNull | 操作人ID |
| remark | Text | - | 备注 |
| created_at | DateTime | Default=now() | 创建时间 |

**InstallationRecord 类**
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PrimaryKey | 安装记录ID |
| agent_id | Integer | ForeignKey, NotNull | 代理商ID |
| software_id | Integer | ForeignKey, NotNull | 软件ID |
| merchant_code | String(50) | NotNull | 商户编号 |
| merchant_name | String(100) | NotNull | 商户名称 |
| quantity | Integer | NotNull | 安装数量 |
| install_date | Date | NotNull | 安装日期 |
| operator_id | Integer | ForeignKey, NotNull | 操作人ID |
| remark | Text | - | 备注 |
| created_at | DateTime | Default=now() | 创建时间 |

**TransferRecord 类**
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PrimaryKey | 划拨记录ID |
| from_agent_id | Integer | ForeignKey, NotNull | 划出代理商ID |
| to_agent_id | Integer | ForeignKey, NotNull | 划入代理商ID |
| software_id | Integer | ForeignKey, NotNull | 软件ID |
| quantity | Integer | NotNull | 划拨数量 |
| transfer_date | Date | NotNull | 划拨日期 |
| operator_id | Integer | ForeignKey, NotNull | 操作人ID |
| remark | Text | - | 备注 |
| created_at | DateTime | Default=now() | 创建时间 |

**InventoryLog 类**
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PrimaryKey | 日志ID |
| agent_id | Integer | ForeignKey, NotNull | 代理商ID |
| software_id | Integer | ForeignKey, NotNull | 软件ID |
| change_type | String(20) | NotNull | 变动类型 |
| before_qty | Integer | NotNull | 变动前数量 |
| change_qty | Integer | NotNull | 变动数量 |
| after_qty | Integer | NotNull | 变动后数量 |
| related_id | Integer | - | 关联记录ID |
| operator_id | Integer | ForeignKey, NotNull | 操作人ID |
| created_at | DateTime | Default=now() | 创建时间 |

#### 3.3.3 数据字典模型 (`models/dictionary.py`)

**DictionaryType 类**
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PrimaryKey | 类型ID |
| type_name | String(100) | NotNull | 类型名称 |
| type_code | String(50) | Unique, NotNull | 类型编码 |
| description | String(500) | - | 描述 |
| status | Integer | Default=1 | 状态 |
| created_at | DateTime | Default=now() | 创建时间 |
| updated_at | DateTime | Default=now() | 更新时间 |

**DictionaryItem 类**
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PrimaryKey | 字典项ID |
| type_id | Integer | ForeignKey, NotNull | 字典类型ID |
| item_key | String(100) | NotNull | 字典键 |
| item_value | String(500) | NotNull | 字典值 |
| item_name | String(200) | - | 字典名称 |
| sort_order | Integer | Default=0 | 排序号 |
| status | Integer | Default=1 | 状态 |
| remark | String(500) | - | 备注 |
| created_at | DateTime | Default=now() | 创建时间 |
| updated_at | DateTime | Default=now() | 更新时间 |

---

## 4. 数据库与数据结构

### 4.1 数据库配置

**数据库连接信息**：
- 主机：192.168.6.10
- 端口：37061
- 用户名：product
- 密码：product123
- 数据库名：agent_management

**连接字符串**：
```python
mysql+aiomysql://product:product123@192.168.6.10:37061/agent_management?charset=utf8mb4
```

### 4.2 数据库表结构

#### 4.2.1 users 表

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role_id INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);
```

#### 4.2.2 roles 表

```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    permissions TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.3 dictionary_type 表

```sql
CREATE TABLE dictionary_type (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(100) NOT NULL,
    type_code VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(500),
    status TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 4.2.4 dictionary_item 表

```sql
CREATE TABLE dictionary_item (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    type_id INTEGER NOT NULL,
    item_key VARCHAR(100) NOT NULL,
    item_value VARCHAR(500) NOT NULL,
    item_name VARCHAR(200),
    sort_order INTEGER DEFAULT 0,
    status TINYINT(1) DEFAULT 1,
    remark VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (type_id) REFERENCES dictionary_type(id)
);
```

#### 4.2.5 agents 表

```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    agent_code VARCHAR(50) UNIQUE NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    system_type VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.6 software 表

```sql
CREATE TABLE software (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.7 inventories 表

```sql
CREATE TABLE inventories (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    agent_id INTEGER NOT NULL,
    software_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 0 NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE(agent_id, software_id),
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id)
);
```

#### 4.2.8 purchase_records 表

```sql
CREATE TABLE purchase_records (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    agent_id INTEGER NOT NULL,
    software_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    purchase_date DATE NOT NULL,
    operator_id INTEGER NOT NULL,
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
);
```

#### 4.2.9 installation_records 表

```sql
CREATE TABLE installation_records (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    agent_id INTEGER NOT NULL,
    software_id INTEGER NOT NULL,
    merchant_code VARCHAR(50) NOT NULL,
    merchant_name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    install_date DATE NOT NULL,
    operator_id INTEGER NOT NULL,
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
);
```

#### 4.2.10 transfer_records 表

```sql
CREATE TABLE transfer_records (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    from_agent_id INTEGER NOT NULL,
    to_agent_id INTEGER NOT NULL,
    software_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    transfer_date DATE NOT NULL,
    operator_id INTEGER NOT NULL,
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_agent_id) REFERENCES agents(id),
    FOREIGN KEY (to_agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
);
```

#### 4.2.11 inventory_logs 表

```sql
CREATE TABLE inventory_logs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    agent_id INTEGER NOT NULL,
    software_id INTEGER NOT NULL,
    change_type VARCHAR(20) NOT NULL,
    before_qty INTEGER NOT NULL,
    change_qty INTEGER NOT NULL,
    after_qty INTEGER NOT NULL,
    related_id INTEGER,
    operator_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
);
```

---

## 5. API接口详细设计

### 5.1 认证接口

#### 5.1.1 POST /api/v1/auth/login

**请求体**：
```json
{
    "username": "admin",
    "password": "123456"
}
```

**响应体**：
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "username": "admin",
        "full_name": "系统管理员",
        "role_id": 1,
        "role_name": "管理员"
    }
}
```

### 5.2 库存接口

#### 5.2.1 GET /api/v1/inventory/list

**查询参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| system_type | string | 否 | 代理商所属系统 |
| agent_code | string | 否 | 代理商编号 |
| agent_name | string | 否 | 代理商名称 |
| software_name | string | 否 | 软件名称 |

**响应体**：
```json
[
    {
        "id": 1,
        "agent": {
            "id": 1,
            "agent_code": "000001",
            "agent_name": "阿灿一代",
            "system_type": "V3系统"
        },
        "software": {
            "id": 1,
            "name": "汇客餐饮"
        },
        "quantity": 100,
        "updated_at": "2024-01-01T10:00:00"
    }
]
```

#### 5.2.2 GET /api/v1/inventory/logs

**查询参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| agent_id | int | 否 | 代理商ID |
| software_id | int | 否 | 软件ID |
| change_type | string | 否 | 变动类型 |
| system_type | string | 否 | 代理商所属系统 |
| agent_code | string | 否 | 代理商编号 |
| agent_name | string | 否 | 代理商名称 |
| software_name | string | 否 | 软件名称 |
| start_date | string | 否 | 开始日期(YYYY-MM-DD) |
| end_date | string | 否 | 结束日期(YYYY-MM-DD) |

**响应体**：
```json
[
    {
        "id": 1,
        "agent": {
            "id": 1,
            "agent_code": "000001",
            "agent_name": "阿灿一代",
            "system_type": "V3系统"
        },
        "software": {
            "id": 1,
            "name": "汇客餐饮"
        },
        "change_type": "purchase",
        "before_qty": 0,
        "change_qty": 100,
        "after_qty": 100,
        "related_id": 1,
        "operator_id": "admin",
        "created_at": "2024-01-01T10:00:00",
        "related_system_type": null,
        "related_agent_code": null,
        "related_agent_name": null,
        "merchant_code": null,
        "merchant_name": null,
        "remark": null
    }
]
```

### 5.3 业务接口

#### 5.3.1 POST /api/v1/business/purchase

**请求体**：
```json
{
    "system_type": "V3系统",
    "agent_code": "000001",
    "agent_name": "阿灿一代",
    "software_name": "汇客餐饮",
    "quantity": 100,
    "purchase_date": "2024-01-01",
    "remark": "测试采购"
}
```

**响应体**：
```json
{
    "message": "采购记录已保存",
    "id": 1
}
```

#### 5.3.2 POST /api/v1/business/install

**请求体**：
```json
{
    "system_type": "V3系统",
    "agent_code": "000001",
    "agent_name": "阿灿一代",
    "software_name": "汇客餐饮",
    "merchant_code": "M001",
    "merchant_name": "商户A",
    "quantity": 10,
    "install_date": "2024-01-01",
    "remark": "测试安装"
}
```

**响应体**：
```json
{
    "message": "安装记录已保存",
    "id": 1
}
```

#### 5.3.3 POST /api/v1/business/transfer

**请求体**：
```json
{
    "from_system_type": "V3系统",
    "from_agent_code": "000001",
    "from_agent_name": "阿灿一代",
    "to_system_type": "LTB系统",
    "to_agent_code": "000101",
    "to_agent_name": "阿灿二代",
    "software_name": "汇客餐饮",
    "quantity": 10,
    "transfer_date": "2024-01-01",
    "remark": "测试划拨"
}
```

**响应体**：
```json
{
    "message": "划拨记录已保存",
    "id": 1
}
```

### 5.4 通用接口

#### 5.4.1 GET /api/v1/common/software

**响应体**：
```json
[
    {
        "id": 1,
        "name": "汇客餐饮"
    },
    {
        "id": 2,
        "name": "汇客零售"
    }
]
```

#### 5.4.2 GET /api/v1/common/agents

**响应体**：
```json
[
    {
        "id": 1,
        "agent_code": "000001",
        "agent_name": "阿灿一代",
        "system_type": "V3系统"
    }
]
```

### 5.5 RBAC接口

#### 5.5.1 GET /api/v1/users

**响应体**：
```json
[
    {
        "id": 1,
        "username": "admin",
        "full_name": "系统管理员",
        "role_id": 1,
        "role_name": "管理员",
        "is_active": true,
        "created_at": "2024-01-01T10:00:00"
    }
]
```

#### 5.5.2 POST /api/v1/users

**请求体**：
```json
{
    "username": "user1",
    "password": "password123",
    "full_name": "用户1",
    "role_id": 2
}
```

#### 5.5.3 GET /api/v1/roles

**响应体**：
```json
[
    {
        "id": 1,
        "name": "管理员",
        "permissions": ["*"]
    },
    {
        "id": 2,
        "name": "财务",
        "permissions": ["inventory.view", "purchase.view", "purchase.create"]
    }
]
```

#### 5.5.4 POST /api/v1/roles

**请求体**：
```json
{
    "name": "新角色",
    "permissions": ["inventory.view"]
}
```

### 5.6 数据字典接口

#### 5.6.1 GET /api/v1/dictionary/items

**查询参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type_code | string | 否 | 字典类型编码 |
| item_name | string | 否 | 字典项名称 |
| item_key | string | 否 | 字典项KEY |
| status | bool | 否 | 状态 |

**响应体**：
```json
[
    {
        "id": 1,
        "type_id": 1,
        "type_name": "代理商所属系统",
        "type_code": "SYSTEM_TYPE",
        "item_key": "V3",
        "item_value": "V3系统",
        "item_name": "V3系统",
        "sort_order": 1,
        "status": true,
        "remark": null,
        "created_at": "2024-01-01T10:00:00"
    }
]
```

#### 5.6.2 POST /api/v1/dictionary/items

**请求体**：
```json
{
    "type_id": 1,
    "item_key": "NEW_KEY",
    "item_value": "新值",
    "item_name": "新名称",
    "sort_order": 1,
    "status": true,
    "remark": "备注"
}
```

#### 5.6.3 GET /api/v1/dictionary/by_type/{type_code}

**路径参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| type_code | string | 字典类型编码 |

**响应体**：
```json
[
    {
        "item_key": "V3",
        "item_value": "V3系统",
        "item_name": "V3系统"
    },
    {
        "item_key": "LTB",
        "item_value": "LTB系统",
        "item_name": "LTB系统"
    }
]
```

#### 5.6.4 GET /api/v1/dictionary/items/export

**查询参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type_code | string | 否 | 字典类型编码 |

**响应体**：CSV文件流

---

## 6. 主业务流程与调用链

### 6.1 采购流程调用链

```
前端 PurchaseList.tsx
    │
    ▼ POST /api/v1/business/purchase
后端 business.py:create_purchase()
    │
    ├─► InventoryService.get_or_create_agent()
    │       └─► 数据库: SELECT/INSERT agents
    │
    ├─► InventoryService.get_or_create_software()
    │       └─► 数据库: SELECT/INSERT software
    │
    ├─► InventoryService.add_purchase()
    │       └─► 数据库: INSERT purchase_records
    │
    ├─► InventoryService.update_inventory()
    │       └─► 数据库: INSERT/UPDATE inventories
    │
    └─► InventoryService.add_inventory_log()
            └─► 数据库: INSERT inventory_logs
```

### 6.2 安装流程调用链

```
前端 InstallList.tsx
    │
    ▼ POST /api/v1/business/install
后端 business.py:create_installation()
    │
    ├─► InventoryService.get_or_create_agent()
    │       └─► 数据库: SELECT/INSERT agents
    │
    ├─► InventoryService.get_or_create_software()
    │       └─► 数据库: SELECT/INSERT software
    │
    ├─► InventoryService.add_installation()
    │       └─► 数据库: INSERT installation_records
    │
    ├─► InventoryService.update_inventory() (-quantity)
    │       └─► 数据库: UPDATE inventories
    │
    └─► InventoryService.add_inventory_log()
            └─► 数据库: INSERT inventory_logs
```

### 6.3 划拨流程调用链

```
前端 TransferList.tsx
    │
    ▼ POST /api/v1/business/transfer
后端 business.py:create_transfer()
    │
    ├─► InventoryService.get_or_create_agent() [划出方]
    │       └─► 数据库: SELECT/INSERT agents
    │
    ├─► InventoryService.get_or_create_agent() [划入方]
    │       └─► 数据库: SELECT/INSERT agents
    │
    ├─► InventoryService.get_or_create_software()
    │       └─► 数据库: SELECT/INSERT software
    │
    ├─► InventoryService.add_transfer()
    │       └─► 数据库: INSERT transfer_records
    │
    ├─► InventoryService.update_inventory() [划出方, -quantity]
    │       └─► 数据库: UPDATE inventories
    │
    ├─► InventoryService.update_inventory() [划入方, +quantity]
    │       └─► 数据库: INSERT/UPDATE inventories
    │
    ├─► InventoryService.add_inventory_log() [划出记录]
    │       └─► 数据库: INSERT inventory_logs (transfer_out)
    │
    └─► InventoryService.add_inventory_log() [划入记录]
            └─► 数据库: INSERT inventory_logs (transfer_in)
```

---

## 7. 安全设计

### 7.1 认证机制

- **JWT Token**：使用JSON Web Token进行身份认证
- **Token有效期**：默认30分钟
- **密码哈希**：使用bcrypt进行密码加密存储

### 7.2 权限控制

- **RBAC模型**：基于角色的访问控制
- **权限验证**：每个API接口都需要验证当前用户是否具有相应权限
- **权限粒度**：支持到操作级别的权限控制（如 inventory.view, purchase.create）

### 7.3 安全防护

- **CORS配置**：允许前端域名访问
- **请求限制**：可配置请求频率限制
- **SQL注入防护**：使用ORM参数化查询
- **XSS防护**：前端使用React自动转义

---

## 8. 部署与集成方案

### 8.1 开发环境

**后端启动**：
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**前端启动**：
```bash
cd frontend
npm install
npm run dev
```

### 8.2 生产环境

**后端配置**：
- 使用Gunicorn作为WSGI服务器
- 配置环境变量（数据库连接、JWT密钥等）
- 启用HTTPS

**前端配置**：
- 构建生产版本：`npm run build`
- 使用Nginx作为静态文件服务器
- 配置反向代理到后端API

### 8.3 数据库初始化

**使用SQL文件初始化**：
```bash
mysql -h 192.168.6.10 -P 37061 -u product -pproduct123 < init.sql
```

**使用Python脚本初始化**：
```bash
cd backend
python scripts/init_database.py
python scripts/init_users.py
python scripts/init_dictionary.py
```

---

## 9. 代码安全性

### 9.1 注意事项

1. **密码安全**：
   - 密码必须经过bcrypt哈希后存储
   - 禁止明文存储密码
   - 禁止在日志中打印密码

2. **JWT安全**：
   - JWT密钥必须安全存储（使用环境变量）
   - Token必须通过HTTPS传输
   - 设置合理的Token过期时间

3. **SQL注入防护**：
   - 所有数据库查询必须使用参数化查询
   - 禁止拼接SQL语句

4. **XSS防护**：
   - 前端使用React自动转义
   - 对用户输入进行验证和过滤

5. **权限验证**：
   - 每个接口都必须验证用户权限
   - 禁止直接访问未授权的资源

6. **敏感信息保护**：
   - 禁止在响应中返回敏感信息（如密码哈希）
   - 日志中禁止记录敏感数据
