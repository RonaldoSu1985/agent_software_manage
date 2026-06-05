"""强制清空并重新初始化数据库"""
import pymysql

DB_CONFIG = {
    'host': '192.168.0.118',
    'port': 3306,
    'user': 'agm',
    'password': 'aa111111',
    'database': 'agent_management',
    'charset': 'utf8mb4'
}

# 不连接数据库（连接服务器即可）
SERVER_CONFIG = {
    'host': '192.168.0.118',
    'port': 3306,
    'user': 'agm',
    'password': 'aa111111',
    'charset': 'utf8mb4'
}

try:
    # 1. 先关闭所有连接，删除数据库
    print("Step 1: Drop database...")
    conn = pymysql.connect(**SERVER_CONFIG)
    cursor = conn.cursor()

    # 杀掉所有连接
    cursor.execute("SELECT GROUP_CONCAT(schema_name) FROM information_schema.schemata WHERE schema_name = 'agent_management'")
    if cursor.fetchone()[0]:
        cursor.execute("DROP DATABASE agent_management")
        print("  -> Database dropped")
    else:
        print("  -> Database not exist")

    # 2. 重新创建数据库
    print("\nStep 2: Create database...")
    cursor.execute("CREATE DATABASE agent_management DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print("  -> Database created")
    cursor.close()
    conn.close()

    # 3. 读取并执行 init.sql
    print("\nStep 3: Execute init.sql...")
    with open(r'd:\GeminiProject\deployment_package\backend\init.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 分割 SQL 语句
    statements = []
    current = []
    for line in sql_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        current.append(line)
        if line.endswith(';'):
            stmt = '\n'.join(current).rstrip(';').strip()
            if stmt:
                statements.append(stmt)
            current = []

    # 执行
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    for i, stmt in enumerate(statements, 1):
        try:
            cursor.execute(stmt)
        except Exception as e:
            print(f"  ! Failed at statement {i}: {e}")
            print(f"    SQL: {stmt[:100]}...")

    conn.commit()
    print(f"  -> Executed {len(statements)} statements")

    # 4. 验证结果
    print("\nStep 4: Verify...")
    cursor.execute("SELECT COUNT(*) FROM users")
    print(f"  Users: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM roles")
    print(f"  Roles: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM dictionary_type")
    print(f"  Dictionary types: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM dictionary_item")
    print(f"  Dictionary items: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM agents")
    print(f"  Agents: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM software")
    print(f"  Software: {cursor.fetchone()[0]}")

    cursor.close()
    conn.close()

    print("\n" + "=" * 50)
    print("SUCCESS: Database reset completed!")
    print("=" * 50)
    print("Login: admin / 123456")
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
