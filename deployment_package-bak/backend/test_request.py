import urllib.request
import urllib.parse

data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode()
req = urllib.request.Request(
    'http://localhost:8001/api/v1/auth/login', 
    data=data, 
    headers={'Content-Type': 'application/x-www-form-urlencoded'}, 
    method='POST'
)

try:
    response = urllib.request.urlopen(req, timeout=10)
    print(f"Response status: {response.status}")
    print(f"Response body: {response.read().decode()}")
except Exception as e:
    print(f"Error: {e}")