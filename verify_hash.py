from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# 新生成的密码哈希
new_hash = "$2b$12$Q6r//78ftYMOjWW0FlSPq.90rM3djLgJjoF75BNNRGJTEZ5d./TV6"
# init.sql 中的旧密码哈希
old_hash = "$2b$12$eh7Ktw8MFAhZKTp9mg6WfuWA8JaixLMOL9ZNYZyzVO8o4OAOSLoZm"

print("=== 验证密码 123456 ===")
print("新哈希验证结果:", pwd_context.verify("123456", new_hash))
print("旧哈希验证结果:", pwd_context.verify("123456", old_hash))

# 生成几个新的密码哈希
print("\n=== 生成新的密码哈希 ===")
for i in range(3):
    h = pwd_context.hash("123456")
    print(f"哈希 {i+1}: {h}")
    print(f"  验证: {pwd_context.verify('123456', h)}")