-- MySQL Schema for Agent Software Management System

CREATE DATABASE IF NOT EXISTS agent_management DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE agent_management;

-- 1. RBAC: Roles
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名称',
    permissions JSON DEFAULT NULL COMMENT '权限配置',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. RBAC: Users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    hashed_password VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    full_name VARCHAR(100) COMMENT '姓名',
    role_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB;

-- 3. Dictionary Type (数据字典类型)
CREATE TABLE IF NOT EXISTS dictionary_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL COMMENT '类型名称',
    type_code VARCHAR(50) NOT NULL UNIQUE COMMENT '类型编码',
    description VARCHAR(500) COMMENT '描述',
    status TINYINT(1) DEFAULT 1 COMMENT '状态: 0禁用, 1启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 4. Dictionary Item (数据字典项)
CREATE TABLE IF NOT EXISTS dictionary_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_id INT NOT NULL COMMENT '字典类型ID',
    item_key VARCHAR(100) NOT NULL COMMENT '字典键',
    item_value VARCHAR(500) NOT NULL COMMENT '字典值',
    item_name VARCHAR(200) COMMENT '字典名称',
    sort_order INT DEFAULT 0 COMMENT '排序',
    status TINYINT(1) DEFAULT 1 COMMENT '状态: 0禁用, 1启用',
    remark VARCHAR(500) COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (type_id) REFERENCES dictionary_type(id)
) ENGINE=InnoDB;

-- 5. Agents
CREATE TABLE IF NOT EXISTS agents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_code VARCHAR(50) NOT NULL UNIQUE COMMENT '代理商编号',
    agent_name VARCHAR(100) NOT NULL COMMENT '代理商名称',
    system_type VARCHAR(20) NOT NULL COMMENT '所属系统（从数据字典获取）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 6. Software
CREATE TABLE IF NOT EXISTS software (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '软件名称',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 7. Inventories
CREATE TABLE IF NOT EXISTS inventories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id INT NOT NULL,
    software_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0 COMMENT '库存数量',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_agent_software (agent_id, software_id),
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id)
) ENGINE=InnoDB;

-- 8. Purchase Records
CREATE TABLE IF NOT EXISTS purchase_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id INT NOT NULL,
    software_id INT NOT NULL,
    quantity INT NOT NULL COMMENT '采购数量',
    purchase_date DATE NOT NULL COMMENT '采购日期',
    operator_id INT NOT NULL COMMENT '操作人ID',
    remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- 9. Installation Records
CREATE TABLE IF NOT EXISTS installation_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id INT NOT NULL,
    software_id INT NOT NULL,
    merchant_code VARCHAR(50) NOT NULL COMMENT '商户编号',
    merchant_name VARCHAR(100) NOT NULL COMMENT '商户名称',
    quantity INT NOT NULL COMMENT '安装数量',
    install_date DATE NOT NULL COMMENT '安装日期',
    operator_id INT NOT NULL COMMENT '操作人ID',
    remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- 10. Transfer Records
CREATE TABLE IF NOT EXISTS transfer_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    from_agent_id INT NOT NULL COMMENT '划出方',
    to_agent_id INT NOT NULL COMMENT '划入方',
    software_id INT NOT NULL,
    quantity INT NOT NULL COMMENT '划拨数量',
    transfer_date DATE NOT NULL COMMENT '划拨日期',
    operator_id INT NOT NULL COMMENT '操作人ID',
    remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_agent_id) REFERENCES agents(id),
    FOREIGN KEY (to_agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- 11. Inventory Change Logs (Audit)
CREATE TABLE IF NOT EXISTS inventory_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id INT NOT NULL,
    software_id INT NOT NULL,
    change_type VARCHAR(20) NOT NULL COMMENT '变动类型: purchase/installation/transfer_out/transfer_in',
    before_qty INT NOT NULL COMMENT '变动前数量',
    change_qty INT NOT NULL COMMENT '变动数量',
    after_qty INT NOT NULL COMMENT '变动后数量',
    related_id INT COMMENT '关联业务记录ID',
    operator_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (software_id) REFERENCES software(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- Seed Initial Data

-- Roles
INSERT INTO roles (name, permissions) VALUES 
('管理员', '["*"]'), 
('财务', '["inventory.view", "purchase.view", "purchase.create"]'),
('业务员', '["inventory.view", "installation.create", "transfer.create"]');

-- Admin User (Password: 123456)
INSERT INTO users (username, hashed_password, full_name, role_id) VALUES 
('admin', '$2b$12$eh7Ktw8MFAhZKTp9mg6WfuWA8JaixLMOL9ZNYZyzVO8o4OAOSLoZm', '系统管理员', 1);

-- Dictionary Types
INSERT INTO dictionary_type (type_name, type_code, description) VALUES 
('代理商所属系统', 'SYSTEM_TYPE', '代理商所属系统类型'),
('软件名称', 'SOFTWARE_NAME', '软件名称列表');

-- Dictionary Items - System Types
INSERT INTO dictionary_item (type_id, item_key, item_value, item_name, sort_order) VALUES 
(1, 'V3', 'V3系统', 'V3系统', 1),
(1, 'LTB', 'LTB系统', 'LTB系统', 2);

-- Dictionary Items - Software Names
INSERT INTO dictionary_item (type_id, item_key, item_value, item_name, sort_order) VALUES 
(2, 'HK_CY', '汇客餐饮', '汇客餐饮', 1),
(2, 'HK_LS', '汇客零售', '汇客零售', 2);

-- Software
INSERT INTO software (name) VALUES ('汇客餐饮'), ('汇客零售');
