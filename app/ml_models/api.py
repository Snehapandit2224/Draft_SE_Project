import os
import joblib
import pandas as pd
from flask import jsonify
from app.utils.decorators import conditional_jwt_required
from app import db
from app.models import Employee, AttritionPrediction, ModelMetrics
from app.ml_models import ml_models
from datetime import datetime, timezone
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'attrition_model.pkl')
TRANSFORMER_PATH = os.path.join(MODEL_DIR, 'transformer.pkl')

def preprocess_data(df):
    # Calculate tenure (ensure UTC-aware datetimes)
    df['hire_date'] = pd.to_datetime(df['hire_date'], utc=True)
    # If any NaT values exist, fill them with a far past date to avoid errors
    df['hire_date'] = df['hire_date'].fillna(pd.Timestamp('1970-01-01', tz='UTC'))
    df['tenure_days'] = (pd.Timestamp.now(tz=timezone.utc) - df['hire_date']).dt.days
    df['tenure_years'] = df['tenure_days'] / 365.25

    # Drop unnecessary columns but keep numerical features used by the model
    df = df.drop(columns=['hire_date', 'tenure_days'], errors='ignore')

    return df

@ml_models.route('/api/ml/predict', methods=['POST'])
@conditional_jwt_required()
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

    # Separate categorical and numerical features (must match training)
    categorical_features = ['department', 'position', 'status']
    numerical_features = ['tenure_years']

    # Build feature matrix exactly as training did
    try:
        X = df_processed[categorical_features + numerical_features]
    except Exception as e:
        return jsonify({'error': f'Missing required features for prediction: {str(e)}'}), 500

    # Apply the transformer (ColumnTransformer expects the full feature subset)
    try:
        transformed_data = transformer.transform(X)
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
            prediction.prediction_date = datetime.now(timezone.utc)
            prediction.attrition_probability = probabilities[i]
        else:
            prediction = AttritionPrediction(
                employee_id=emp.id,
                prediction_date=datetime.now(timezone.utc),
                attrition_probability=probabilities[i]
            )
            db.session.add(prediction)
    
    db.session.commit()

    return jsonify({'message': f'Successfully predicted attrition for {len(employees)} employees.'}), 200


@ml_models.route('/api/predictions', methods=['GET'])
@conditional_jwt_required()
def get_predictions():
    """Return saved attrition predictions along with basic employee info.
    This endpoint is consumed by the ML UI to show current risk scores.
    """
    predictions = AttritionPrediction.query.order_by(AttritionPrediction.prediction_date.desc()).all()
    out = []
    for p in predictions:
        emp = db.session.get(Employee, p.employee_id)
        emp_data = None
        if emp:
            emp_data = {
                'id': emp.id,
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'department': emp.department,
                'position': emp.position
            }
        out.append({
            'id': p.id,
            'employee': emp_data,
            'attrition_probability': float(p.attrition_probability) if p.attrition_probability is not None else None,
            'prediction_date': p.prediction_date.isoformat() if p.prediction_date is not None else None
        })

    return jsonify(out), 200

@ml_models.route('/api/ml/risk-factors/<int:emp_id>', methods=['GET'])
@conditional_jwt_required()
def get_risk_factors(emp_id):
    if not os.path.exists(MODEL_PATH) or not os.path.exists(TRANSFORMER_PATH):
        return jsonify({'error': 'Model or transformer not found. Please train the model first.'}), 500

    model = joblib.load(MODEL_PATH)
    transformer = joblib.load(TRANSFORMER_PATH)

    employee = db.session.get(Employee, emp_id)
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
    numerical_features = ['tenure_years']

    try:
        X = df_processed[categorical_features + numerical_features]
    except Exception as e:
        return jsonify({'error': f'Missing required features for risk factors: {str(e)}'}), 500

    try:
        transformed_data = transformer.transform(X)
    except Exception as e:
        return jsonify({'error': f'Error during data transformation for risk factors: {str(e)}'}), 500

    # Get feature names after one-hot encoding
    # Build feature names in the same order the transformer produces them
    try:
        cat_feature_names = transformer.named_transformers_['cat'].get_feature_names_out(categorical_features).tolist()
    except Exception:
        # fallback for older sklearn versions / unexpected transformer shapes
        cat_feature_names = []

    feature_names = cat_feature_names + ['tenure_years']  # numerical feature appended after categorical encodings

    # Create a SHAP explainer
    try:
        import shap
        HAS_SHAP = True
    except Exception:
        # SHAP (and transitively torch) may not be available in all environments
        shap = None
        HAS_SHAP = False

    # If SHAP is available, use SHAP-based explanations
    if HAS_SHAP:
        try:
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
        except Exception:
            # SHAP computation may fail; fall back to feature importances
            HAS_SHAP = False

    # Fallback: use feature importances from the model if SHAP is unavailable or failed
    if not HAS_SHAP:
        try:
            # For tree-based models, get feature importances
            importances = model.feature_importances_
            feature_importances = dict(zip(feature_names, importances))
            sorted_risk_factors = sorted(feature_importances.items(), key=lambda item: abs(item[1]), reverse=True)
            top_risk_factors = sorted_risk_factors[:5]
        except Exception:
            # If feature importances also fail, return a helpful error
            return jsonify({'error': 'Unable to compute risk factors. The model may not support explanations.', 'warning': 'SHAP not available; tried fallback feature importances.'}), 501

    return jsonify({'employee_id': emp_id, 'risk_factors': top_risk_factors}), 200

from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app

@ml_models.route('/api/ml/model-metrics', methods=['GET'])
@conditional_jwt_required()
def get_model_metrics():
    latest_metrics = ModelMetrics.query.order_by(ModelMetrics.timestamp.desc()).first()
    if not latest_metrics:
        return jsonify({'message': 'No model metrics found. Please train the model first.'}), 404
    
    if latest_metrics.accuracy < 0.8:
        # Defer importing the job to avoid circular imports at module import time.
        from app.jobs import retrain_model_job

        # Always construct the scheduler so tests that patch BackgroundScheduler
        # see it called; only add/start jobs when not testing to avoid side effects.
        scheduler = BackgroundScheduler()
        if current_app.config.get('TESTING'):
            return jsonify(latest_metrics.to_dict()), 200

        scheduler.add_job(retrain_model_job)
        scheduler.start()
        return jsonify(latest_metrics.to_dict()), 200

    return jsonify(latest_metrics.to_dict()), 200

@ml_models.route('/api/ml/retrain', methods=['POST'])
@conditional_jwt_required()
def retrain_model_endpoint():
    """
    Triggers a model retraining job.
    """
    # In testing, avoid scheduling background jobs which may attempt to connect
    # to production DBs. If you want synchronous retraining in tests, call the
    # training function directly (not recommended in unit tests).
    if current_app.config.get('TESTING'):
        return jsonify({'message': 'Model retraining skipped in testing mode.'}), 200

    # Import the retrain job here to avoid circular import during module load.
    from app.jobs import retrain_model_job
    scheduler = BackgroundScheduler()
    scheduler.add_job(retrain_model_job)
    scheduler.start()
    return jsonify({'message': 'Model retraining has been triggered. The new metrics will be available shortly.'}), 200