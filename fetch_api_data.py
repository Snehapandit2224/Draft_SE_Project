from app import create_app
import json

app = create_app('development')
app.config['TESTING'] = True
with app.test_client() as client:
    r1 = client.get('/alerts/api/alerts')
    print('alerts status', r1.status_code)
    try:
        print('alerts json:', json.dumps(r1.get_json(), indent=2)[:1000])
    except Exception:
        print('alerts raw:', r1.get_data(as_text=True)[:1000])

    r2 = client.get('/analytics/api/analytics/hotspots')
    print('\nhotspots status', r2.status_code)
    try:
        print('hotspots json:', json.dumps(r2.get_json(), indent=2)[:1000])
    except Exception:
        print('hotspots raw:', r2.get_data(as_text=True)[:1000])

    r3 = client.get('/analytics/api/reports/attrition')
    print('\nattrition report status', r3.status_code)
    try:
        print('attrition json sample:', json.dumps(r3.get_json()[:5], indent=2))
    except Exception:
        print('attrition raw:', r3.get_data(as_text=True)[:1000])
