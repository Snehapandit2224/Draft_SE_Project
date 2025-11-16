import requests

url = 'http://127.0.0.1:5000/auth/login'
resp = requests.post(url, data={'username':'admin','password':'password'}, allow_redirects=False)
print('status', resp.status_code)
print('headers:', resp.headers)
print('cookies:', resp.cookies.get_dict())
try:
    print('json:', resp.json())
except Exception:
    print('text:', resp.text[:200])
