from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 测试密码验证
hashed_password = "$2b$12$zABzJuNTiM6Aj/JOEOog2uM.TCjAz3R.xdS9MDheSCI0LlGAoNhgG"
plain_password = "123456"

result = pwd_context.verify(plain_password, hashed_password)
print(f"密码验证结果: {result}")

# 重新哈希测试
new_hash = pwd_context.hash(plain_password)
print(f"新哈希值: {new_hash}")
print(f"新哈希验证: {pwd_context.verify(plain_password, new_hash)}")
