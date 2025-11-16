from app import create_app

app = create_app('development')
app.config['TESTING'] = True
with app.test_client() as client:
    resp = client.post('/auth/login', data={'username':'admin','password':'password'}, follow_redirects=False)
    print('status', resp.status_code)
    try:
        print('json:', resp.get_json())
    except Exception:
        print('data_text:', resp.get_data(as_text=True)[:200])
    print('headers:', resp.headers)
    print('set-cookie:', resp.headers.get('Set-Cookie'))
