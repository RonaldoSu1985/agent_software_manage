"""检查数据库当前内容"""
import pymysql

DB_CONFIG = {
    'host': '192.168.6.10',
    'port': 37061,
    'user': 'product',
    'password': 'product123',
    'database': 'agent_management',
    'charset': 'utf8mb4'
}

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 查看所有表
    print("=" * 50)
    print("TABLES IN DATABASE:")
    print("=" * 50)
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for t in tables:
        print(f"  - {t[0]}")

    # 查看每个表的数据量
    print("\n" + "=" * 50)
    print("ROW COUNTS:")
    print("=" * 50)
    for t in tables:
        table_name = t[0]
        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
        count = cursor.fetchone()[0]
        print(f"  {table_name}: {count} rows")

    # 查看用户
    print("\n" + "=" * 50)
    print("USERS:")
    print("=" * 50)
    cursor.execute("SELECT id, username, full_name, department FROM users")
    for u in cursor.fetchall():
        print(f"  ID={u[0]}, Username={u[1]}, Name={u[2]}, Dept={u[3]}")

    # 查看代理商
    print("\n" + "=" * 50)
    print("AGENTS:")
    print("=" * 50)
    cursor.execute("SELECT id, agent_name, contact_person, phone FROM agents LIMIT 10")
    for a in cursor.fetchall():
        print(f"  ID={a[0]}, Name={a[1]}, Contact={a[2]}, Phone={a[3]}")

    # 查看字典
    print("\n" + "=" * 50)
    print("DICTIONARY ITEMS:")
    print("=" * 50)
    cursor.execute("""
        SELECT t.type_name, i.item_name, i.item_code
        FROM dictionary_item i
        JOIN dictionary_type t ON i.type_id = t.id
        ORDER BY t.type_name, i.sort_order
    """)
    for d in cursor.fetchall():
        print(f"  {d[0]}: {d[1]} ({d[2]})")

    cursor.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
