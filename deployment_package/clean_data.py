#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理测试数据脚本
运行后数据库中只保留初始数据：
- 角色(roles)、用户(users)、字典类型(dictionary_type)、字典项(dictionary_item)、软件(software)
- 清空：代理商(agents)、库存(inventories)、采购记录(purchase_records)、安装记录(installation_records)、调拨记录(transfer_records)、库存日志(inventory_logs)
"""

import asyncio
from sqlalchemy import create_engine, text
from app.core.config import settings

async def clean_test_data():
    # 创建同步连接（简单起见使用同步方式）
    engine = create_engine(settings.DATABASE_URL.replace('aiomysql', 'pymysql'))
    
    with engine.connect() as conn:
        print("开始清理测试数据...")
        
        # 关闭外键约束
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        # 清空业务数据表（按依赖顺序）
        tables_to_clean = [
            'inventory_logs',
            'transfer_records',
            'installation_records', 
            'purchase_records',
            'inventories',
            'agents'
        ]
        
        for table in tables_to_clean:
            conn.execute(text(f"TRUNCATE TABLE {table}"))
            print(f"已清空表: {table}")
        
        # 重置自增ID（可选）
        reset_auto_increment = [
            'agents',
            'inventories',
            'purchase_records',
            'installation_records',
            'transfer_records',
            'inventory_logs'
        ]
        
        for table in reset_auto_increment:
            conn.execute(text(f"ALTER TABLE {table} AUTO_INCREMENT = 1"))
        
        # 重新启用外键约束
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        
        conn.commit()
        print("\n清理完成！数据库中仅保留以下初始数据：")
        print("- 角色(roles): 管理员、财务、业务员")
        print("- 用户(users): admin")
        print("- 字典类型(dictionary_type): 代理商所属系统、软件名称")
        print("- 字典项(dictionary_item): V3系统、LTB系统、汇客餐饮、汇客零售")
        print("- 软件(software): 汇客餐饮、汇客零售")

if __name__ == "__main__":
    asyncio.run(clean_test_data())
