import requests

# 首先获取token
login_url = "http://localhost:8000/api/v1/auth/login"
data_url = "http://localhost:8000/api/v1/dictionary/items"

# 登录
try:
    login_data = {
        "username": "admin",
        "password": "123456"
    }
    login_response = requests.post(login_url, data=login_data)
    login_response.raise_for_status()
    print("登录响应:", login_response.json())
    
    token = login_response.json().get('access_token') or login_response.json().get('token')
    print("获取到Token:", token)
    
    # 获取字典数据
    headers = {"Authorization": f"Bearer {token}"}
    data_response = requests.get(data_url, headers=headers, params={"page": 1, "page_size": 10})
    data_response.raise_for_status()
    
    print("\n字典数据响应:")
    print(data_response.json())
    
except Exception as e:
    print(f"错误: {e}")
    if 'response' in dir():
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
