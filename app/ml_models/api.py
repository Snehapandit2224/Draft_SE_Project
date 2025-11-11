import os
import joblib
import pandas as pd
from flask import jsonify
from app import db
from app.models import Employee, AttritionPrediction
from app.ml_models import ml_models
from datetime import datetime
import shap

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

    # Separate categorical and numerical features
    categorical_features = ['department', 'position', 'status']
    
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

@ml_models.route('/api/ml/risk-factors/<int:emp_id>', methods=['GET'])
def get_risk_factors(emp_id):
    if not os.path.exists(MODEL_PATH) or not os.path.exists(TRANSFORMER_PATH):
        return jsonify({'error': 'Model or transformer not found. Please train the model first.'}), 500

    model = joblib.load(MODEL_PATH)
    transformer = joblib.load(TRANSFORMER_PATH)

    employee = Employee.query.get(emp_id)
    if not employee:
        return jsonify({'error': 'Employee not found.'}), 404

    employee_data = {
        'id': employee.id,
        'department': employee.department,
        'position': employee.position,
        'hire_date': employee.hire_date,
        'status': employee.status
    }
    df = pd.DataFrame([employee_data])
    df_processed = preprocess_data(df.copy())

    categorical_features = ['department', 'position', 'status']
    
    try:
        transformed_data = transformer.transform(df_processed[categorical_features])
    except Exception as e:
        return jsonify({'error': f'Error during data transformation for risk factors: {str(e)}'}), 500

    # Get feature names after one-hot encoding
    feature_names = transformer.named_transformers_['cat'].get_feature_names_out(categorical_features).tolist()
    feature_names.append('tenure_years') # Add numerical feature

    # Create a SHAP explainer
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(transformed_data)

    # For binary classification, shap_values will be a list of two arrays.
    # We are interested in the SHAP values for the positive class (attrition).
    if isinstance(shap_values, list):
        shap_values = shap_values[1] # Assuming index 1 is the positive class

    # Map SHAP values to feature names
    feature_shap_values = dict(zip(feature_names, shap_values[0]))

    # Sort by absolute SHAP value to get top risk factors
    sorted_risk_factors = sorted(feature_shap_values.items(), key=lambda item: abs(item[1]), reverse=True)

    # Return top N risk factors (e.g., top 5)
    top_risk_factors = sorted_risk_factors[:5]

    return jsonify({'employee_id': emp_id, 'risk_factors': top_risk_factors}), 200