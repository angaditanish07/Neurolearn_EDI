import cv2
import numpy as np
import random
import time
from tensorflow.keras.models import load_model

# Load the model
model = load_model('fer2013_mini_XCEPTION.102-0.66.hdf5', compile=False)

# Emotion labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Mood-based supportive questions
mood_questions = {
    'Angry': ["Take a deep breath. What's one thing you enjoy?", "Want to try a calming video or game?"],
    'Disgust': ["Let’s switch the topic! What’s your favorite food?", "Would a fun quiz cheer you up?"],
    'Fear': ["You're safe here. Want to talk about what’s worrying you?", "Would you like to answer a simple question to distract?"],
    'Happy': ["You're shining! Ready for a fun challenge?", "Let's keep the mood up. Want to try a quiz?"],
    'Sad': ["You're not alone. Want to share something you like?", "Let’s try something positive together. OK?"],
    'Surprise': ["Whoa! You seem surprised. Want to explore a fun fact?", "Something amazed you? Let’s learn something new!"],
    'Neutral': ["Let’s dive into some cool learning. Shall we?", "Feeling calm? Want to try a light question?"]
}

# Academic questions to follow up
academic_questions = [
    "What is 5 + 3?",
    "Can you name one planet in the solar system?",
    "What comes after the letter 'D'?",
    "How many sides does a triangle have?",
    "Spell the word 'sun'."
]

import cv2
import numpy as np
import random
import time
from tensorflow.keras.models import load_model

# Load the model
model = load_model('fer2013_mini_XCEPTION.102-0.66.hdf5', compile=False)

# Emotion labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Mood-based supportive questions
mood_questions = {
    'Angry': ["Take a deep breath. What's one thing you enjoy?", "Want to try a calming video or game?"],
    'Disgust': ["Let’s switch the topic! What’s your favorite food?", "Would a fun quiz cheer you up?"],
    'Fear': ["You're safe here. Want to talk about what’s worrying you?", "Would you like to answer a simple question to distract?"],
    'Happy': ["You're shining! Ready for a fun challenge?", "Let's keep the mood up. Want to try a quiz?"],
    'Sad': ["You're not alone. Want to share something you like?", "Let’s try something positive together. OK?"],
    'Surprise': ["Whoa! You seem surprised. Want to explore a fun fact?", "Something amazed you? Let’s learn something new!"],
    'Neutral': ["Let’s dive into some cool learning. Shall we?", "Feeling calm? Want to try a light question?"]
}

# Academic questions
academic_questions = [
    "What is 5 + 3?",
    "Can you name one planet in the solar system?",
    "What comes after the letter 'D'?",
    "How many sides does a triangle have?",
    "Spell the word 'sun'."
]

# Video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

frame_count = 0
last_mood = ""
last_mood_question = ""
last_academic_question = ""
last_question_time = 0
QUESTION_INTERVAL = 5  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    frame_count += 1
    if frame_count % 5 == 0:
        faces = face_classifier.detectMultiScale(gray)

        if len(faces) > 0:
            (x, y, w, h) = sorted(faces, key=lambda a: a[2]*a[3], reverse=True)[0]
            roi_gray = gray[y:y+h, x:x+w]
            roi_gray = cv2.resize(roi_gray, (64, 64), interpolation=cv2.INTER_AREA)

            if np.sum([roi_gray]) != 0:
                roi = roi_gray.astype('float') / 255.0
                roi = np.expand_dims(roi, axis=0)
                roi = np.expand_dims(roi, axis=-1)

                prediction = model.predict(roi)[0]
                label = emotion_labels[np.argmax(prediction)]
                last_mood = label

                # Draw rectangle and label
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

                # Change questions only after interval
                current_time = time.time()
                if current_time - last_question_time > QUESTION_INTERVAL:
                    last_mood_question = random.choice(mood_questions[label])
                    last_academic_question = random.choice(academic_questions)
                    last_question_time = current_time

    # Display the questions
    if last_mood_question:
        cv2.putText(frame, last_mood_question, (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    if last_academic_question:
        cv2.putText(frame, "Q: " + last_academic_question, (10, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow('Personalized Learning (Special Kids)', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.1)  # Reduce CPU usage

cap.release()
cv2.destroyAllWindows()








