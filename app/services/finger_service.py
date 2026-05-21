import logging

from app.ml.loaders import get_hands_detector

logger = logging.getLogger(__name__)

FINGER_TIPS = [8, 12, 16, 20]
THUMB_TIP = 4


def count_fingers_in_image(img_rgb):
    hands = get_hands_detector()
    if hands is None:
        return None, 'Hand detection unavailable'

    h, w = img_rgb.shape[:2]
    results = hands.process(img_rgb)

    if not results.multi_hand_landmarks:
        return {
            'success': True,
            'total_fingers': 0,
            'hand_counts': [],
        }, None

    hand_counts = []
    for hand_landmarks in results.multi_hand_landmarks:
        lm_list = [
            (int(lm.x * w), int(lm.y * h))
            for lm in hand_landmarks.landmark
        ]
        fingers_up = 0
        if lm_list:
            if lm_list[THUMB_TIP][0] > lm_list[THUMB_TIP - 1][0]:
                fingers_up += 1
            for tip in FINGER_TIPS:
                if lm_list[tip][1] < lm_list[tip - 2][1]:
                    fingers_up += 1
        hand_counts.append(fingers_up)

    return {
        'success': True,
        'total_fingers': sum(hand_counts),
        'hand_counts': hand_counts,
    }, None
