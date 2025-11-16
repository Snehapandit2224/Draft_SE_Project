from app import create_app

app = create_app('development')
with app.app_context():
    # Enable TESTING so `conditional_jwt_required` bypasses JWT checks for this local run
    app.config['TESTING'] = True
    # Use a test request context so route decorators that inspect request behave normally
    with app.test_request_context('/api/ml/predict', method='POST'):
        from app.ml_models.api import predict_attrition
        resp = predict_attrition()

        # Route functions may return (Response, status) or a Response
        if isinstance(resp, tuple):
            response_obj, status = resp
            try:
                print('Status:', status)
                print('JSON:', response_obj.get_json())
            except Exception:
                print('Response (raw):', response_obj)
        else:
            try:
                print('Status (default):', resp.status_code)
                print('JSON:', resp.get_json())
            except Exception:
                print('Response (raw):', resp)
print('PREDICT_DONE')
