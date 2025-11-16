from app import create_app, db

app = create_app('development')
with app.app_context():
    app.config['TESTING'] = True
    # Call the predict endpoint function directly
    from app.ml_models.api import predict_attrition
    from app.jobs import check_attrition_hotspots
    print('Running predictions...')
    # Use test request context to satisfy decorators
    with app.test_request_context('/api/ml/predict', method='POST'):
        resp = predict_attrition()
        print('predict response:', resp)

    print('Triggering hotspot check...')
    check_attrition_hotspots(app)

    # show counts
    from app.models import AttritionPrediction, AttritionAlert
    print('Predictions count:', AttritionPrediction.query.count())
    print('Alerts count:', AttritionAlert.query.count())
