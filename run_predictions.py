from app import create_app
from app.ml_models.api import predict_attrition
import os

# Set the environment variable for development database
os.environ['FLASK_CONFIG'] = 'development'

app = create_app('development')

with app.app_context():
    app.config['TESTING'] = True # Enable testing mode to bypass JWT checks
    with app.test_request_context('/api/ml/predict', method='POST'):
        print("Running attrition prediction...")
        response, status_code = predict_attrition()
        print(f"Prediction complete. Status: {status_code}, Response: {response.get_data(as_text=True)}")
