import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os
from sklearn.preprocessing import StandardScaler

def generate_synthetic_data(n_samples=1000):
    """Generate synthetic data for training the model"""
    np.random.seed(42)
    
    
    data = {
        # Reading accuracy features (0-1)
        'reading_accuracy_1': np.random.normal(0.75, 0.15, n_samples),
        'reading_accuracy_2': np.random.normal(0.75, 0.15, n_samples),
        
        # Spelling accuracy features (0-1)
        'spelling_accuracy_1': np.random.normal(0.70, 0.20, n_samples),
        'spelling_accuracy_2': np.random.normal(0.70, 0.20, n_samples),
        
        # Letter recognition accuracy features (0-1)
        'letter_accuracy_1': np.random.normal(0.85, 0.10, n_samples),
        'letter_accuracy_2': np.random.normal(0.85, 0.10, n_samples),
        
        # Word matching accuracy (0-1)
        'word_matching_accuracy': np.random.normal(0.80, 0.15, n_samples),
        
        # Number reading accuracy (0-1)
        'number_reading_accuracy': np.random.normal(0.90, 0.08, n_samples),
        
        # Sentence copying accuracy (0-1)
        'sentence_copying_accuracy': np.random.normal(0.75, 0.15, n_samples),
        
        # Handwriting features with more balanced distributions
        'line_spacing': np.random.normal(0.5, 0.1, n_samples),
        'letter_spacing': np.random.normal(0.3, 0.1, n_samples),
        'slant_angle': np.random.normal(0, 5, n_samples),  # Further reduced variance
        'letter_size_variation': np.random.normal(0.2, 0.05, n_samples),
        'pressure_variation': np.random.normal(0.4, 0.1, n_samples)
    }
    
    # Clip all accuracy features to [0, 1]
    for key in data:
        if 'accuracy' in key:
            data[key] = np.clip(data[key], 0, 1)
    
    # Convert to numpy array
    X = np.column_stack([data[key] for key in data])
    
    # Generate labels with adjusted weights
    weights = {
        'reading_accuracy_1': 0.15,
        'reading_accuracy_2': 0.15,
        'spelling_accuracy_1': 0.15,
        'spelling_accuracy_2': 0.15,
        'letter_accuracy_1': 0.10,
        'letter_accuracy_2': 0.10,
        'word_matching_accuracy': 0.08,
        'number_reading_accuracy': 0.05,
        'sentence_copying_accuracy': 0.05,
        'line_spacing': 0.01,
        'letter_spacing': 0.01,
        'slant_angle': 0.01,  # Further reduced weight
        'letter_size_variation': 0.01,
        'pressure_variation': 0.01
    }
    
    # Calculate risk score with adjusted thresholds
    risk_score = np.zeros(n_samples)
    for i, key in enumerate(data):
        risk_score += weights[key] * (1 - data[key] if 'accuracy' in key else data[key])
    
    # Convert risk score to labels with adjusted thresholds
    y = np.zeros(n_samples, dtype=int)
    y[risk_score > 0.35] = 2  # High Risk
    y[(risk_score > 0.15) & (risk_score <= 0.35)] = 1  # Medium Risk
    y[risk_score <= 0.15] = 0  # Low Risk
    
    return X, y

def train_model():
    """Train the dyslexia screening model"""
    print("Generating synthetic training data...")
    X, y = generate_synthetic_data(n_samples=5000)
    
    # Split data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=300,  # Further increased number of trees
        max_depth=20,      # Further increased depth
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42,
        class_weight='balanced',
        max_features='sqrt'
    )
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Evaluate the model
    train_score = model.score(X_train, y_train)
    val_score = model.score(X_val, y_val)
    
    print(f"Training accuracy: {train_score:.3f}")
    print(f"Validation accuracy: {val_score:.3f}")
    
    # Print feature importance
    feature_importance = dict(zip([
        'reading_accuracy_1', 'reading_accuracy_2',
        'spelling_accuracy_1', 'spelling_accuracy_2',
        'letter_accuracy_1', 'letter_accuracy_2',
        'word_matching_accuracy', 'number_reading_accuracy',
        'sentence_copying_accuracy', 'line_spacing',
        'letter_spacing', 'slant_angle',
        'letter_size_variation', 'pressure_variation'
    ], model.feature_importances_))
    
    print("\nFeature Importance:")
    for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
        print(f"{feature}: {importance:.3f}")
    
    # Save the model
    print("\nSaving model...")
    scaler = StandardScaler()
    scaler.fit(X_train)  # Fit the scaler on training data
    
    model_data = {
        'model': model,
        'scaler': scaler
    }
    joblib.dump(model_data, 'dyslexia_model.joblib')
    print("Model saved successfully!")

if __name__ == '__main__':
    train_model() 