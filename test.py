from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam

model = load_model('fer2013_mini_XCEPTION.102-0.66.hdf5', compile=False)

model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

print("Model loaded successfully!")

import speech_recognition as sr

recognizer = sr.Recognizer()

# Use the microphone as the source
with sr.Microphone() as source:
    print("Say something!")
    audio = recognizer.listen(source)

# Recognize the speech using Google Web Speech API
try:
    print("You said: " + recognizer.recognize_google(audio))
except sr.UnknownValueError:
    print("Sorry, I could not understand the audio.")
except sr.RequestError:
    print("Sorry, the service is down.")
