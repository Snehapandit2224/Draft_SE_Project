from app import create_app
import json

app = create_app('development')
app.config['TESTING'] = True
with app.test_client() as client:
    # Test risk factors for an employee (should now use feature importances as fallback)
    emp_id = 35  # Use an employee ID we know exists
    r = client.get(f'/ml/api/ml/risk-factors/{emp_id}')
    print('status:', r.status_code)
    try:
        data = r.get_json()
        print('risk_factors response:', json.dumps(data, indent=2))
    except Exception as e:
        print('error:', e)
        print('raw:', r.get_data(as_text=True)[:500])
