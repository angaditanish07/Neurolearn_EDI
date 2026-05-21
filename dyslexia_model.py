import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import shap
import joblib
import json
from datetime import datetime

class DyslexiaScreeningModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = [
            'reading_time', 'reading_accuracy', 'spelling_time',
            'spelling_accuracy', 'letter_recognition_time',
            'letter_recognition_accuracy', 'error_count',
            'reversal_errors', 'omission_errors', 'substitution_errors'
        ]
        
    def preprocess_features(self, features):
        """Preprocess the input features"""
        features_array = np.array([features])
        return self.scaler.transform(features_array)
    
    def predict(self, features):
        """Make prediction and generate explanations"""
        processed_features = self.preprocess_features(features)
        prediction = self.model.predict(processed_features)[0]
        probability = self.model.predict_proba(processed_features)[0]
        
        # Generate SHAP explanations
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(processed_features)[0]
        
        # Create feature importance dictionary
        feature_importance = dict(zip(self.feature_names, shap_values))
        
        return {
            'prediction': prediction,
            'probability': probability.tolist(),
            'feature_importance': feature_importance
        }
    
    def save_model(self, path='dyslexia_model.joblib'):
        """Save the model and scaler"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler
        }
        joblib.dump(model_data, path)
    
    def load_model(self, path='dyslexia_model.joblib'):
        """Load the model and scaler"""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']

# Initialize the model
dyslexia_model = DyslexiaScreeningModel()

# Load pre-trained model if available
try:
    dyslexia_model.load_model()
except:
    print("No pre-trained model found. Please train the model first.") 