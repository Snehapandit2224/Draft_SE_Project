from app import create_app
import json

app = create_app('development')
app.config['TESTING'] = True
with app.test_client() as client:
    r = client.get('/ml/api/predictions')
    print('status', r.status_code)
    try:
        print('json:', json.dumps(r.get_json()[:10], indent=2))
    except Exception:
        print('raw:', r.get_data(as_text=True)[:1000])
