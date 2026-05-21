import joblib
import numpy as np

def load_model():
    """Load the trained model"""
    try:
        model = joblib.load('dyslexia_model.joblib')
        print("Model loaded successfully!")
        return model
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None

def create_test_cases():
    """Create sample test cases"""
    # Case 1: Low Risk (Good performance)
    low_risk = {
        'reading_accuracy_1': 0.95,
        'reading_accuracy_2': 0.92,
        'spelling_accuracy_1': 0.90,
        'spelling_accuracy_2': 0.88,
        'letter_accuracy_1': 0.98,
        'letter_accuracy_2': 0.97,
        'word_matching_accuracy': 0.96,
        'number_reading_accuracy': 0.99,
        'sentence_copying_accuracy': 0.94,
        'line_spacing': 0.45,
        'letter_spacing': 0.35,
        'slant_angle': 5,
        'letter_size_variation': 0.15,
        'pressure_variation': 0.35
    }
    
    # Case 2: Medium Risk (Mixed performance)
    medium_risk = {
        'reading_accuracy_1': 0.75,
        'reading_accuracy_2': 0.70,
        'spelling_accuracy_1': 0.65,
        'spelling_accuracy_2': 0.60,
        'letter_accuracy_1': 0.80,
        'letter_accuracy_2': 0.75,
        'word_matching_accuracy': 0.70,
        'number_reading_accuracy': 0.85,
        'sentence_copying_accuracy': 0.65,
        'line_spacing': 0.55,
        'letter_spacing': 0.40,
        'slant_angle': 20,
        'letter_size_variation': 0.25,
        'pressure_variation': 0.45
    }
    
    # Case 3: High Risk (Poor performance)
    high_risk = {
        'reading_accuracy_1': 0.45,
        'reading_accuracy_2': 0.40,
        'spelling_accuracy_1': 0.35,
        'spelling_accuracy_2': 0.30,
        'letter_accuracy_1': 0.50,
        'letter_accuracy_2': 0.45,
        'word_matching_accuracy': 0.40,
        'number_reading_accuracy': 0.55,
        'sentence_copying_accuracy': 0.35,
        'line_spacing': 0.65,
        'letter_spacing': 0.50,
        'slant_angle': 35,
        'letter_size_variation': 0.35,
        'pressure_variation': 0.55
    }
    
    return [low_risk, medium_risk, high_risk]

def test_model():
    """Test the model with sample cases"""
    # Load the model
    model = load_model()
    if model is None:
        return
    
    # Create test cases
    test_cases = create_test_cases()
    risk_levels = ['Low Risk', 'Medium Risk', 'High Risk']
    
    print("\nTesting model with sample cases:")
    print("-" * 50)
    
    for i, case in enumerate(test_cases):
        # Convert case to numpy array
        X = np.array([list(case.values())])
        
        # Make prediction
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        
        print(f"\nTest Case {i+1} ({risk_levels[i]}):")
        print(f"Predicted Risk Level: {risk_levels[prediction]}")
        print("Prediction Probabilities:")
        for j, prob in enumerate(probabilities):
            print(f"- {risk_levels[j]}: {prob:.2%}")
        
        # Print feature importance for this case
        print("\nKey Features Contributing to Risk:")
        feature_importance = dict(zip(case.keys(), model.feature_importances_))
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features[:5]:
            print(f"- {feature}: {importance:.3f}")

if __name__ == '__main__':
    test_model() 