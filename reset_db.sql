-- Reset Database to Initial State
-- This script will clear all existing data and restore to initial state

USE agent_management;

-- Disable foreign key checks temporarily
SET FOREIGN_KEY_CHECKS = 0;

-- Truncate all tables (order matters due to foreign keys)
TRUNCATE TABLE inventory_logs;
TRUNCATE TABLE transfer_records;
TRUNCATE TABLE installation_records;
TRUNCATE TABLE purchase_records;
TRUNCATE TABLE inventories;
TRUNCATE TABLE software;
TRUNCATE TABLE agents;
TRUNCATE TABLE dictionary_item;
TRUNCATE TABLE dictionary_type;
TRUNCATE TABLE users;
TRUNCATE TABLE roles;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Re-insert initial data

-- Roles - 只保留管理员角色
INSERT INTO roles (name, permissions) VALUES 
('管理员', '["*"]');

-- Admin User (Password: 123456)
INSERT INTO users (username, hashed_password, full_name, role_id) VALUES 
('admin', '$2b$12$eh7Ktw8MFAhZKTp9mg6WfuWA8JaixLMOL9ZNYZyzVO8o4OAOSLoZm', '系统管理员', 1);

-- Dictionary Types - 添加部门类型
INSERT INTO dictionary_type (type_name, type_code, description) VALUES 
('代理商所属系统', 'SYSTEM_TYPE', '代理商所属系统类型'),
('软件名称', 'SOFTWARE_NAME', '软件名称列表'),
('部门', 'DEPARTMENT', '部门列表');

-- Dictionary Items - System Types
INSERT INTO dictionary_item (type_id, item_key, item_value, item_name, sort_order) VALUES 
(1, 'V3', 'V3系统', 'V3系统', 1),
(1, 'LTB', 'LTB系统', 'LTB系统', 2);

-- Dictionary Items - Software Names
INSERT INTO dictionary_item (type_id, item_key, item_value, item_name, sort_order) VALUES 
(2, 'HK_CY', '汇客餐饮', '汇客餐饮', 1),
(2, 'HK_LS', '汇客零售', '汇客零售', 2);

-- Dictionary Items - Departments (部门数据)
INSERT INTO dictionary_item (type_id, item_key, item_value, item_name, sort_order) VALUES 
(3, 'DEPT_PURCHASE', '采购部', '采购部', 1),
(3, 'DEPT_FINANCE', '财务部', '财务部', 2),
(3, 'DEPT_JINHE', '金合部', '金合部', 3),
(3, 'DEPT_MARKET', '市场品牌部', '市场品牌部', 4),
(3, 'DEPT_PRODUCT', '产品管理部', '产品管理部', 5),
(3, 'DEPT_SALES', '销售部', '销售部', 6),
(3, 'DEPT_SERVICE', '服务部', '服务部', 7),
(3, 'DEPT_OPERATION', '运营部', '运营部', 8),
(3, 'DEPT_SETTLEMENT', '结算部', '结算部', 9),
(3, 'DEPT_RISK', '风控部', '风控部', 10),
(3, 'DEPT_TECH', '技术部', '技术部', 11),
(3, 'DEPT_TEST', '测试部', '测试部', 12),
(3, 'DEPT_OPS', '运维部', '运维部', 13),
(3, 'DEPT_ADMIN', '行政部', '行政部', 14);

-- Software
INSERT INTO software (name) VALUES ('汇客餐饮'), ('汇客零售');

SELECT 'Database reset completed successfully!' AS result;