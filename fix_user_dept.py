"""为 users 表添加 department 列"""
import pymysql

DB_CONFIG = {
    'host': '192.168.0.118',
    'port': 3306,
    'user': 'agm',
    'password': 'aa111111',
    'database': 'agent_management',
    'charset': 'utf8mb4'
}

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 检查列是否存在
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_schema = 'agent_management'
        AND table_name = 'users'
        AND column_name = 'department'
    """)
    exists = cursor.fetchone()[0]

    if exists:
        print("department column already exists, dropping first...")
        cursor.execute("ALTER TABLE users DROP COLUMN department")

    # 添加 department 列
    print("Adding department column...")
    cursor.execute("""
        ALTER TABLE users
        ADD COLUMN department VARCHAR(50) NULL AFTER full_name
    """)
    conn.commit()
    print("  -> department column added")

    # 同时检查并添加其他可能缺失的列
    print("\nChecking other columns...")

    columns_to_check = [
        ('created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP'),
    ]

    for col_name, col_type, col_extra in columns_to_check:
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = 'agent_management'
            AND table_name = 'users'
            AND column_name = %s
        """, (col_name,))
        if not cursor.fetchone()[0]:
            print(f"  Adding {col_name}...")
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type} {col_extra}")
            conn.commit()

    # 更新 admin 用户的部门
    print("\nUpdating admin user department...")
    cursor.execute("UPDATE users SET department = 'PRODUCT' WHERE username = 'admin'")
    conn.commit()

    # 验证表结构
    print("\nFinal users table structure:")
    cursor.execute("DESCRIBE users")
    for col in cursor.fetchall():
        print(f"  {col[0]:25s} {col[1]:30s} NULL={'YES' if col[2]=='YES' else 'NO'}")

    cursor.close()
    conn.close()
    print("\nSUCCESS: All fixes applied!")
    print("You can now login with admin / 123456")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
