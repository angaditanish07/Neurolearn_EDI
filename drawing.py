import cv2
import mediapipe as mp
import numpy as np
import math
import random
import time

# MediaPipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)

# Constants
RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]
NOSE_TIP_IDX = 1
EAR_THRESHOLD = 0.23
CONSEC_FRAMES = 3

# Encouraging messages=
ENCOURAGING_MESSAGES = [
    "Amazing work! 🌟",
    "You're an artist! ",
    "Fantastic drawing! 👏",
    "Brilliant job! ⭐",
    "You're so creative! 🎯",
    "Wonderful drawing! 🌈",
    "You're getting better! 🚀",
    "That's beautiful! 💫",
    "Keep up the great work! 🎉",
    "You're a star! ⭐"
]

# Game Word List with hint images
WORDS = ["Flower", "Boat", "Smiley Face", "Balloon"]
HINT_IMAGES = {
    "Flower": "static/flower.jpeg",   # Add your hint images here
    "Boat": "static/boat.jpg",
    "Smiley Face": "static/smiley.webp",
   
  
    "Balloon": "static/balloon.png"
}

current_word = random.choice(WORDS)
last_word_time = time.time()
celebration_start = 0
celebration_active = False
celebration_message = ""

# Drawing and blink state
canvas = None
drawing_mode = False
blink_frame_count = 0
blink_active = False

# Distance and EAR calculation
def euclidean_dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def calculate_ear(landmarks, eye_idx, w, h):
    points = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in eye_idx]
    A = euclidean_dist(points[1], points[5])
    B = euclidean_dist(points[2], points[4])
    C = euclidean_dist(points[0], points[3])
    return (A + B) / (2.0 * C) if C else 0

# Load hint images (ensure they are in the same directory)
def load_hint_image(word):
    return cv2.imread(HINT_IMAGES.get(word, ""))

# Webcam setup
cap = cv2.VideoCapture(0)

def show_celebration(frame, message):
    """Display celebration effect with message"""
    h, w = frame.shape[:2]
    
    # Create a semi-transparent overlay
    overlay = frame.copy()
    
    # Add colorful particles
    for _ in range(50):
        x = random.randint(0, w-1)
        y = random.randint(0, h-1)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        cv2.circle(overlay, (x, y), random.randint(2, 5), color, -1)
    
    # Add the message with a nice background
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(message, font, 2, 4)[0]
    text_x = (w - text_size[0]) // 2
    text_y = (h + text_size[1]) // 2
    
    # Add background rectangle for text
    cv2.rectangle(overlay, 
                 (text_x - 20, text_y - text_size[1] - 20),
                 (text_x + text_size[0] + 20, text_y + 20),
                 (255, 255, 255),
                 -1)
    
    # Add text
    cv2.putText(overlay, message, (text_x, text_y), font, 2, (0, 0, 255), 4)
    
    # Blend the overlay with the original frame
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    if canvas is None:
        canvas = np.zeros_like(frame)

    # Word refresh every 40 seconds
    if time.time() - last_word_time > 40:
        filename = f"{current_word.replace(' ', '_')}_drawing.png"
        cv2.imwrite(filename, canvas)
        print(f"✅ Drawing saved as '{filename}'")
        
        # Start celebration
        celebration_start = time.time()
        celebration_active = True
        celebration_message = random.choice(ENCOURAGING_MESSAGES)
        
        canvas = np.zeros_like(frame)
        current_word = random.choice(WORDS)
        last_word_time = time.time()

    # Show celebration for 3 seconds
    if celebration_active:
        if time.time() - celebration_start < 3:
            show_celebration(frame, celebration_message)
        else:
            celebration_active = False

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    # Load the hint image
    hint_image = load_hint_image(current_word)
    if hint_image is not None:
        hint_image = cv2.resize(hint_image, (300, 300))  # Increased from 150x150 to 300x300
        frame[10:310, 10:310] = hint_image  # Adjusted position for larger image

    if result.multi_face_landmarks:
        landmarks = result.multi_face_landmarks[0].landmark
        ear = calculate_ear(landmarks, RIGHT_EYE_IDX, w, h)

        if ear < EAR_THRESHOLD:
            blink_frame_count += 1
        else:
            if blink_frame_count >= CONSEC_FRAMES and not blink_active:
                drawing_mode = not drawing_mode
                blink_active = True
            blink_frame_count = 0
            blink_active = False

        nose = landmarks[NOSE_TIP_IDX]
        nose_x, nose_y = int(nose.x * w), int(nose.y * h)
        cv2.circle(frame, (nose_x, nose_y), 6, (255, 0, 0), -1)

        if drawing_mode:
            cv2.circle(canvas, (nose_x, nose_y), 6, (0, 255, 255), -1)  # Bright yellow brush
            cv2.putText(frame, f"Drawing: {current_word}", (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 4)  # Increased font size and thickness
        else:
            cv2.putText(frame, f"Paused - Draw: {current_word}", (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 4)  # Increased font size and thickness

    combined = cv2.addWeighted(frame, 0.8, canvas, 0.5, 0)
    cv2.imshow("NeuroDraw – Blink Challenge", combined)

    key = cv2.waitKey(1)
    if key == ord('s'):
        cv2.imwrite("manual_save.png", canvas)
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()




