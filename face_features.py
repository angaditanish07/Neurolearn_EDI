'''import cv2
import mediapipe as mp

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False)

# Webcam
cap = cv2.VideoCapture(0)

# Color & Organs
colors = {
    "Left Eye": (255, 0, 0),
    "Right Eye": (0, 255, 0),
    "Nose": (0, 0, 255),
    "Mouth": (255, 255, 0),
    "Left Ear": (255, 0, 255),
    "Right Ear": (0, 255, 255),
    "Chin": (200, 100, 100)
}

organs = {
    "Left Eye": 33,
    "Right Eye": 263,
    "Nose": 1,
    "Mouth": 13,
    "Left Ear": 234,
    "Right Ear": 454,
    "Chin": 152
}

# Alternate arrow direction toggle
flip_dir = {
    "Left Eye": (-80, -30),
    "Right Eye": (80, -30),
    "Nose": (0, -60),
    "Mouth": (-80, 50),
    "Left Ear": (-100, -10),
    "Right Ear": (100, -10),
    "Chin": (0, 80)
}

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # REMOVE MIRROR EFFECT (don't flip)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image)

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    h, w, _ = image.shape

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for organ, idx in organs.items():
                pt = face_landmarks.landmark[idx]
                x, y = int(pt.x * w), int(pt.y * h)

                dx, dy = flip_dir[organ]
                label_x, label_y = x + dx, y + dy

                color = colors[organ]
                cv2.circle(image, (x, y), 5, color, -1)
                cv2.arrowedLine(image, (label_x, label_y), (x, y), color, 2, tipLength=0.3)
                cv2.putText(image, organ, (label_x, label_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

    cv2.imshow("Face Organs Learner", image)

    if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()'''
import cv2
import mediapipe as mp

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False)

# Webcam
cap = cv2.VideoCapture(0)

# Color & Organs
colors = {
    "Left Eye": (255, 0, 0),
    "Right Eye": (0, 255, 0),
    "Nose": (0, 0, 255),
    "Mouth": (255, 255, 0),
    "Left Ear": (255, 0, 255),
    "Right Ear": (0, 255, 255),
    "Chin": (200, 100, 100)
}

organs = {
    "Left Eye": 33,
    "Right Eye": 263,
    "Nose": 1,
    "Mouth": 13,
    "Left Ear": 234,
    "Right Ear": 454,
    "Chin": 152
}

# Alternate arrow direction toggle
flip_dir = {
    "Left Eye": (-80, -30),
    "Right Eye": (80, -30),
    "Nose": (0, -60),
    "Mouth": (-80, 50),
    "Left Ear": (-100, -10),
    "Right Ear": (100, -10),
    "Chin": (0, 80)
}

# Function to calculate distance between two points
def calculate_distance(pt1, pt2):
    return ((pt2.x - pt1.x) ** 2 + (pt2.y - pt1.y) ** 2) ** 0.5

# Function to adjust font size based on distance between eyes
def adjust_font_size(distance):
    max_distance = 0.2  # Maximum distance between eyes (for the smallest font size)
    min_distance = 0.05  # Minimum distance between eyes (for the largest font size)

    # Calculate font size in a dynamic range between 1 and 3
    if distance > max_distance:
        font_size = 1
    elif distance < min_distance:
        font_size = 3
    else:
        # Interpolate font size based on distance
        font_size = 3 - (distance - min_distance) / (max_distance - min_distance) * 2
    
    return font_size
#Frame capture and prcessing of each frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert image to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image)

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    h, w, _ = image.shape

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Extract points for left and right eyes
            left_eye = face_landmarks.landmark[organs["Left Eye"]]
            right_eye = face_landmarks.landmark[organs["Right Eye"]]
            
            # Calculate the distance between the eyes
            distance = calculate_distance(left_eye, right_eye)
            
            # Adjust font size based on the distance between eyes
            font_size = adjust_font_size(distance)

            # Draw the organs and labels with dynamic font size
            for organ, idx in organs.items():
                pt = face_landmarks.landmark[idx]
                x, y = int(pt.x * w), int(pt.y * h)

                dx, dy = flip_dir[organ]
                label_x, label_y = x + dx, y + dy

                color = colors[organ]
                cv2.circle(image, (x, y), 5, color, -1)
                cv2.arrowedLine(image, (label_x, label_y), (x, y), color, 2, tipLength=0.3)
                cv2.putText(image, organ, (label_x, label_y - 10), cv2.FONT_HERSHEY_SIMPLEX, font_size, color, 2)

    cv2.imshow("Face Organs Learner", image)

    if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()




