import sys
sys.path.append('.')

from app.services.auth_service import verify_password, get_password_hash

# 测试密码验证
print("测试密码验证...")

# 从数据库中获取的哈希值
hashed_password = "$2b$12$eh7Ktw8MFAhZKTp9mg6WfuWA8JaixLMOL9ZNYZyzVO8o4OAOSLoZm"

# 测试密码 "123456"
result = verify_password("123456", hashed_password)
print(f"密码 '123456' 验证结果: {result}")

# 测试其他密码
result2 = verify_password("admin", hashed_password)
print(f"密码 'admin' 验证结果: {result2}")

# 生成新的哈希值
new_hash = get_password_hash("123456")
print(f"\n新生成的密码哈希: {new_hash}")
print(f"新哈希验证结果: {verify_password('123456', new_hash)}")
