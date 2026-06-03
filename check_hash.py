from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
h = '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'
print(f"admin: {pwd_context.verify('admin', h)}")
print(f"admin123: {pwd_context.verify('admin123', h)}")
