import unittest
from unittest.mock import patch, MagicMock
import os
from app import create_app, db
from app.models import Employee, AttritionPrediction
from datetime import datetime
import pandas as pd

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

if __name__ == '__main__':
    unittest.main()
