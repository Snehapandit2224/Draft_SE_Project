from app import create_app
import json

app = create_app('development')
app.config['TESTING'] = True
with app.test_client() as client:
    # Check total employees
    r1 = client.get('/employees/api/employees')
    data1 = r1.get_json()
    total = len(data1.get('employees', [])) if data1 else 0
    print(f'Total employees: {total}')
    
    # Check active employees only
    r2 = client.get('/employees/api/employees?status=active')
    data2 = r2.get_json()
    active = len(data2.get('employees', [])) if data2 else 0
    print(f'Active employees: {active}')
    
    # Check terminated employees
    r3 = client.get('/employees/api/employees?status=terminated')
    data3 = r3.get_json()
    terminated = len(data3.get('employees', [])) if data3 else 0
    print(f'Terminated employees: {terminated}')
    
    # Print first few active employees
    if data2 and data2.get('employees'):
        print('\nFirst 5 active employees:')
        for emp in data2['employees'][:5]:
            print(f"  - {emp['first_name']} {emp['last_name']} (ID: {emp['id']}, is_active: {emp.get('is_active', '?')})")
