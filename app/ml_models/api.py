import os
import joblib
import pandas as pd
from flask import jsonify
from app import db
from app.models import Employee, AttritionPrediction
from app.ml_models import ml_models
from datetime import datetime

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'attrition_model.pkl')
TRANSFORMER_PATH = os.path.join(MODEL_DIR, 'transformer.pkl')

def preprocess_data(df):
    # Calculate tenure
    df['hire_date'] = pd.to_datetime(df['hire_date'])
    df['tenure_days'] = (datetime.now() - df['hire_date']).dt.days
    df['tenure_years'] = df['tenure_days'] / 365.25

    # Drop unnecessary columns
    df = df.drop(columns=['hire_date', 'tenure_days'])

    return df

@ml_models.route('/api/ml/predict', methods=['POST'])
def predict_attrition():
    # Load the trained model and transformer
    if not os.path.exists(MODEL_PATH) or not os.path.exists(TRANSFORMER_PATH):
        return jsonify({'error': 'Model or transformer not found. Please train the model first.'}), 500

    model = joblib.load(MODEL_PATH)
    transformer = joblib.load(TRANSFORMER_PATH)

    # Fetch all active employees
    employees = Employee.query.filter_by(is_active=True).all()
    if not employees:
        return jsonify({'message': 'No active employees to predict.'}), 200

    # Create a DataFrame from the employee data
    employee_data = [{
        'id': emp.id,
        'department': emp.department,
        'position': emp.position,
        'hire_date': emp.hire_date,
        'status': emp.status
    } for emp in employees]
    df = pd.DataFrame(employee_data)

    # Preprocess the data
    df_processed = preprocess_data(df.copy())
    print(f"df_processed: {df_processed}")

    # Separate categorical and numerical features
    categorical_features = ['department', 'position', 'status']
    print(f"categorical_features: {categorical_features}")
    
    # Apply the transformer
    try:
        transformed_data = transformer.transform(df_processed[categorical_features])
    except Exception as e:
        return jsonify({'error': f'Error during data transformation: {str(e)}'}), 500

    # Predict attrition probability
    try:
        probabilities = model.predict_proba(transformed_data)[:, 1]
    except Exception as e:
        return jsonify({'error': f'Error during prediction: {str(e)}'}), 500

    # Save predictions to the database
    for i, emp in enumerate(employees):
        prediction = AttritionPrediction.query.filter_by(employee_id=emp.id).first()
        if prediction:
            prediction.prediction_date = datetime.utcnow()
            prediction.attrition_probability = probabilities[i]
        else:
            prediction = AttritionPrediction(
                employee_id=emp.id,
                prediction_date=datetime.utcnow(),
                attrition_probability=probabilities[i]
            )
            db.session.add(prediction)
    
    db.session.commit()

    return jsonify({'message': f'Successfully predicted attrition for {len(employees)} employees.'}), 200
