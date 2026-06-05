"""
使用 PyMySQL 直接更新 admin 用户的密码哈希
"""
import pymysql

# 数据库连接信息
DB_CONFIG = {
    'host': '192.168.0.118',
    'port': 3306,
    'user': 'agm',
    'password': 'aa111111',
    'database': 'agent_management',
    'charset': 'utf8mb4'
}

# 密码 123456 的正确 bcrypt 哈希
NEW_PASSWORD_HASH = '$2b$12$Q6r//78ftYMOjWW0FlSPq.90rM3djLgJjoF75BNNRGJTEZ5d./TV6'

try:
    # 连接数据库
    print("Connecting to database...")
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 查询 admin 用户
    print("Checking admin user...")
    cursor.execute("SELECT id, username, hashed_password FROM users WHERE username = 'admin'")
    user = cursor.fetchone()

    if user:
        print(f"Found admin user (ID: {user[0]})")
        print(f"Current hash: {user[2][:30]}...")

        # 更新密码
        print("Updating password...")
        cursor.execute(
            "UPDATE users SET hashed_password = %s WHERE username = 'admin'",
            (NEW_PASSWORD_HASH,)
        )
        conn.commit()

        # 验证更新
        cursor.execute("SELECT hashed_password FROM users WHERE username = 'admin'")
        updated = cursor.fetchone()
        print(f"New hash: {updated[0][:30]}...")

        print("\nSUCCESS: Admin password updated to: 123456")
    else:
        print("ERROR: Admin user not found!")

    cursor.close()
    conn.close()
    print("\nDatabase connection closed.")

except pymysql.MySQLError as e:
    print(f"\nERROR: {e}")
    print("\nPlease check:")
    print("1. MySQL server is running")
    print("2. Network connection to 192.168.0.118 is available")
    print("3. Database credentials are correct")
    print("4. Database 'agent_management' exists")
except Exception as e:
    print(f"\nUnexpected ERROR: {e}")