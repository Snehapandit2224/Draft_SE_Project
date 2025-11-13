import unittest
from unittest.mock import patch, MagicMock
import os
from app import create_app, db
from app.models import Employee, AttritionPrediction, ModelMetrics
from datetime import datetime
import pandas as pd
import numpy as np

class TestMLModelsAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create dummy model and transformer files
        self.model_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, 'attrition_model.pkl')
        self.transformer_path = os.path.join(self.model_dir, 'transformer.pkl')

        with open(self.model_path, 'wb') as f:
            f.write(b'model')
        with open(self.transformer_path, 'wb') as f:
            f.write(b'transformer')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.remove(self.model_path)
        os.remove(self.transformer_path)
        os.rmdir(self.model_dir)

    @patch('joblib.load')
    def test_predict_attrition(self, mock_joblib_load):
        # Mock the model and transformer
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = pd.DataFrame([[0.1, 0.9], [0.8, 0.2]]).to_numpy()
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = pd.DataFrame([[1, 2], [3, 4]]).to_numpy()
        mock_joblib_load.side_effect = [mock_model, mock_transformer]

        # Add a dummy employee
        employee1 = Employee(first_name='John', last_name='Doe', email='john.doe@example.com', department='Engineering', position='Developer', hire_date=datetime(2022, 1, 1))
        employee2 = Employee(first_name='Jane', last_name='Smith', email='jane.smith@example.com', department='HR', position='Manager', hire_date=datetime(2021, 5, 15))
        db.session.add_all([employee1, employee2])
        db.session.commit()

        # Call the predict endpoint
        response = self.client.post('/ml/api/ml/predict')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Successfully predicted attrition', response.json['message'])

        # Check if predictions are saved in the database
        predictions = AttritionPrediction.query.all()
        self.assertEqual(len(predictions), 2)
        self.assertEqual(predictions[0].employee_id, employee1.id)
        self.assertAlmostEqual(predictions[0].attrition_probability, 0.9)
        self.assertEqual(predictions[1].employee_id, employee2.id)
        self.assertAlmostEqual(predictions[1].attrition_probability, 0.2)

    @patch('shap.TreeExplainer')
    @patch('joblib.load')
    def test_get_risk_factors(self, mock_joblib_load, mock_shap_explainer):
        # Mock the model and transformer
        mock_model = MagicMock()
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = np.array([[1, 0, 0, 5.0]]) # Example transformed data
        mock_transformer.named_transformers_ = {'cat': MagicMock()}
        mock_transformer.named_transformers_['cat'].get_feature_names_out.return_value = np.array(['department_Engineering', 'position_Developer', 'status_active'])
        mock_joblib_load.side_effect = [mock_model, mock_transformer]

        # Mock SHAP explainer
        mock_explainer = MagicMock()
        mock_explainer.shap_values.return_value = [np.array([[-0.1, 0.2, -0.3, 0.4]]), np.array([[0.1, -0.2, 0.3, -0.4]])] # SHAP values for two classes
        mock_shap_explainer.return_value = mock_explainer

        # Add a dummy employee
        employee = Employee(first_name='John', last_name='Doe', email='john.doe@example.com', department='Engineering', position='Developer', hire_date=datetime(2020, 1, 1))
        db.session.add(employee)
        db.session.commit()

        # Call the risk factors endpoint
        response = self.client.get(f'/ml/api/ml/risk-factors/{employee.id}')
        self.assertEqual(response.status_code, 200)

        # Verify the response
        data = response.json
        self.assertEqual(data['employee_id'], employee.id)
        risk_factors = data['risk_factors']
        self.assertEqual(len(risk_factors), 4) # Expecting 4 risk factors based on mock data

        # Check if risk factors are sorted by absolute SHAP value
        self.assertGreaterEqual(abs(risk_factors[0][1]), abs(risk_factors[1][1]))
        self.assertGreaterEqual(abs(risk_factors[1][1]), abs(risk_factors[2][1]))
        self.assertGreaterEqual(abs(risk_factors[2][1]), abs(risk_factors[3][1]))

        # Check specific risk factors (based on mock data)
        self.assertIn(['tenure_years', -0.4], risk_factors)
        self.assertIn(['status_active', 0.3], risk_factors)
        self.assertIn(['position_Developer', -0.2], risk_factors)
        self.assertIn(['department_Engineering', 0.1], risk_factors)

    @patch('app.ml_models.api.BackgroundScheduler')
    def test_get_model_metrics_retraining_trigger(self, mock_scheduler):
        # Add some dummy metrics to the database with accuracy below 0.8
        metrics = ModelMetrics(accuracy=0.75, precision=0.70, recall=0.80, timestamp=datetime(2023, 1, 2))
        db.session.add(metrics)
        db.session.commit()

        response = self.client.get('/ml/api/ml/model-metrics')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertAlmostEqual(data['accuracy'], 0.75)

        # Check if the scheduler was called
        mock_scheduler.assert_called_once()
        
    def test_retrain_model_endpoint(self):
        response = self.client.post('/ml/api/ml/retrain')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Model retraining has been triggered', response.json['message'])


    @patch('app.ml_models.training.accuracy_score', return_value=0.75)
    def test_train_attrition_model_retraining_trigger(self, mock_accuracy_score):
        # Add some dummy employees and exit feedback to the database
        employees = [
            Employee(first_name='John', last_name='Doe', email='john.doe@example.com', department='Engineering', position='Developer', hire_date=datetime(2022, 1, 1), is_active=False),
            Employee(first_name='Jane', last_name='Smith', email='jane.smith@example.com', department='HR', position='Manager', hire_date=datetime(2021, 5, 15), is_active=True),
            Employee(first_name='Peter', last_name='Jones', email='peter.jones@example.com', department='Sales', position='Manager', hire_date=datetime(2020, 3, 10), is_active=False),
            Employee(first_name='Mary', last_name='Williams', email='mary.williams@example.com', department='Engineering', position='Developer', hire_date=datetime(2023, 1, 1), is_active=True),
            Employee(first_name='David', last_name='Brown', email='david.brown@example.com', department='Sales', position='Associate', hire_date=datetime(2022, 2, 1), is_active=False),
            Employee(first_name='Susan', last_name='Davis', email='susan.davis@example.com', department='HR', position='Associate', hire_date=datetime(2021, 8, 20), is_active=True),
            Employee(first_name='Michael', last_name='Miller', email='michael.miller@example.com', department='Engineering', position='Manager', hire_date=datetime(2020, 11, 1), is_active=False),
            Employee(first_name='Karen', last_name='Wilson', email='karen.wilson@example.com', department='Sales', position='Manager', hire_date=datetime(2019, 7, 15), is_active=True),
            Employee(first_name='James', last_name='Moore', email='james.moore@example.com', department='Engineering', position='Developer', hire_date=datetime(2022, 4, 1), is_active=False),
            Employee(first_name='Patricia', last_name='Taylor', email='patricia.taylor@example.com', department='HR', position='Manager', hire_date=datetime(2021, 10, 1), is_active=True),
        ]
        db.session.add_all(employees)
        db.session.commit()

        from app.ml_models.training import retrain_model
        retrain_model()

        # Check if new metrics are saved in the database
        metrics = ModelMetrics.query.order_by(ModelMetrics.timestamp.desc()).first()
        self.assertIsNotNone(metrics)
        self.assertAlmostEqual(metrics.accuracy, 0.75)


if __name__ == '__main__':
    unittest.main()
