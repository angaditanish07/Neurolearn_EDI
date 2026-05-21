import cv2
import mediapipe as mp
import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# MediaPipe Hands setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

# Finger tips index (for each finger)
finger_tips = [8, 12, 16, 20]
thumb_tip = 4
spoken_numbers = set()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    h, w, _ = img.shape

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    fingers_up = 0

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                lm_list.append((int(lm.x * w), int(lm.y * h)))

            # Check for fingers
            if lm_list:
                # Thumb
                if lm_list[thumb_tip][0] > lm_list[thumb_tip - 1][0]:
                    fingers_up += 1
                # Other fingers
                for tip in finger_tips:
                    if lm_list[tip][1] < lm_list[tip - 2][1]:
                        fingers_up += 1

            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Display number
    cv2.rectangle(img, (20, 250), (200, 450), (255, 204, 102), -1)
    cv2.putText(img, f'{fingers_up}', (70, 400), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 5)

    # Speak the number once
    if fingers_up not in spoken_numbers and fingers_up > 0:
        engine.say(str(fingers_up))
        engine.runAndWait()
        spoken_numbers.clear()
        spoken_numbers.add(fingers_up)

    # Reset if no hand
    if not results.multi_hand_landmarks:
        spoken_numbers.clear()

    cv2.imshow("Finger Counter", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
