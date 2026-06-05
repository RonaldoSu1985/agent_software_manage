import os
import sys

# 清理测试数据脚本
def clean_test_data():
    print("==============================================")
    print("    代理商软件库存管理系统 - 数据清理脚本")
    print("==============================================")
    print()
    print("注意：此脚本用于清理测试数据")
    print("请确保已备份重要数据")
    print()
    
    confirm = input("确定要继续吗？(y/N): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        sys.exit(0)
    
    # 这里可以添加实际的数据清理逻辑
    print("正在清理测试数据...")
    print("数据清理完成")

if __name__ == "__main__":
    clean_test_data()