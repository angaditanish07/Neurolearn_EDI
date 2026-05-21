import logging
import random

import cv2
import numpy as np

from app.ml.loaders import get_emotion_model, get_face_classifier
from app.ml.schemas import EMOTION_LABELS

logger = logging.getLogger(__name__)

MOOD_QUESTIONS = {
    'Angry': ["Take a deep breath. What's one thing you enjoy?", "Want to try a calming video or game?"],
    'Disgust': ["Let's switch the topic! What's your favorite food?", "Would a fun quiz cheer you up?"],
    'Fear': ["You're safe here. Want to talk about what's worrying you?", "Would you like to answer a simple question to distract?"],
    'Happy': ["You're shining! Ready for a fun challenge?", "Let's keep the mood up. Want to try a quiz?"],
    'Sad': ["You're not alone. Want to share something you like?", "Let's try something positive together. OK?"],
    'Surprise': ["Whoa! You seem surprised. Want to explore a fun fact?", "Something amazed you? Let's learn something new!"],
    'Neutral': ["Let's dive into some cool learning. Shall we?", "Feeling calm? Want to try a light question?"],
}

def detect_emotion_from_image(img_rgb, model_path):
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    faces = get_face_classifier().detectMultiScale(gray)
    if len(faces) == 0:
        return None, 'No face detected'

    (x, y, w, h) = sorted(faces, key=lambda a: a[2] * a[3], reverse=True)[0]
    roi_gray = cv2.resize(gray[y:y + h, x:x + w], (64, 64), interpolation=cv2.INTER_AREA)
    roi = roi_gray.astype('float32') / 255.0
    roi = np.expand_dims(np.expand_dims(roi, axis=-1), axis=0)

    model = get_emotion_model(model_path)
    prediction = model.predict(roi, verbose=0)[0]
    label = EMOTION_LABELS[int(np.argmax(prediction))]

    return {
        'emotion': label,
        'mood_question': random.choice(MOOD_QUESTIONS[label]),
    }, None
