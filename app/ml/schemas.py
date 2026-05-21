"""Feature schema aligned with train_model.py."""

FEATURE_ORDER = [
    'reading_accuracy_1',
    'reading_accuracy_2',
    'spelling_accuracy_1',
    'spelling_accuracy_2',
    'letter_accuracy_1',
    'letter_accuracy_2',
    'word_matching_accuracy',
    'number_reading_accuracy',
    'sentence_copying_accuracy',
    'line_spacing',
    'letter_spacing',
    'slant_angle',
    'letter_size_variation',
    'pressure_variation',
]

# sklearn model classes: 0=low, 1=medium, 2=high dyslexia risk
ML_CLASS_TO_APP_RISK = {
    0: 1,  # low ML risk -> app "low risk"
    1: 2,  # medium
    2: 3,  # high
}

EMOTION_LABELS = [
    'Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral'
]
