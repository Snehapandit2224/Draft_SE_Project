
import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from app import db
from app.models import Employee, ModelMetrics
from datetime import datetime, timezone

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'attrition_model.pkl')
TRANSFORMER_PATH = os.path.join(MODEL_DIR, 'transformer.pkl')

def preprocess_data(df):
    # Calculate tenure
    df['hire_date'] = pd.to_datetime(df['hire_date'])
    df['tenure_days'] = (datetime.now(timezone.utc) - df['hire_date'].dt.tz_localize('UTC')).dt.days
    df['tenure_years'] = df['tenure_days'] / 365.25

    # Drop unnecessary columns
    df = df.drop(columns=['hire_date', 'tenure_days'])

    return df

def retrain_model():
    """
    Retrains the attrition prediction model and saves it to disk.
    """
    # Fetch all employees
    employees = Employee.query.all()
    if not employees:
        print("No employees found to retrain the model.")
        return

    # Create a DataFrame from the employee data
    employee_data = [{
        'id': emp.id,
        'department': emp.department,
        'position': emp.position,
        'hire_date': emp.hire_date,
        'status': emp.status,
        'is_active': emp.is_active
    } for emp in employees]
    df = pd.DataFrame(employee_data)

    # Define target variable
    df['attrition'] = df['is_active'].apply(lambda x: 0 if x else 1)
    df = df.drop(columns=['is_active'])

    # Preprocess the data
    df_processed = preprocess_data(df.copy())

    # Separate features and target
    X = df_processed.drop('attrition', axis=1)
    y = df_processed['attrition']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Define categorical and numerical features
    categorical_features = ['department', 'position', 'status']
    numerical_features = ['tenure_years']

    # Create a column transformer for preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
            ('num', 'passthrough', numerical_features)
        ])

    # Fit and transform the training data
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)

    # Train the model
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train_transformed, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test_transformed)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)

    # Save the new metrics
    new_metrics = ModelMetrics(
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(new_metrics)
    db.session.commit()

    # Save the model and transformer
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(preprocessor, TRANSFORMER_PATH)

    print(f"Model retrained. Accuracy: {accuracy:.2f}, Precision: {precision:.2f}, Recall: {recall:.2f}")
