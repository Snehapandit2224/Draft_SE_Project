from app import create_app
import json

app = create_app('development')
app.config['TESTING'] = True
with app.test_client() as client:
    print('Testing analytics APIs...\n')
    
    # Test attrition report
    r1 = client.get('/analytics/api/reports/attrition?group_by=department')
    print('attrition report status:', r1.status_code)
    data1 = r1.get_json()
    if data1:
        print('sample rows:', json.dumps(data1[:3], indent=2))
    print()
    
    # Test hotspots
    r2 = client.get('/analytics/api/analytics/hotspots')
    print('hotspots status:', r2.status_code)
    data2 = r2.get_json()
    print('hotspots count:', len(data2) if data2 else 0)
    if data2:
        print('sample:', json.dumps(data2[:2], indent=2))
    print()
    
    # Test exit reasons
    r3 = client.get('/analytics/api/reports/exit-reasons')
    print('exit reasons status:', r3.status_code)
    data3 = r3.get_json()
    if data3:
        print('exit reasons:', json.dumps(data3, indent=2))
