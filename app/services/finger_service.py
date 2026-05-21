import logging

from app.ml.loaders import get_hands_detector

logger = logging.getLogger(__name__)

FINGER_TIPS = [8, 12, 16, 20]
THUMB_TIP = 4


def _landmarks_to_pixels(hand_landmarks, width, height):
    return [
        (int(lm.x * width), int(lm.y * height))
        for lm in hand_landmarks.landmark
    ]


def _count_fingers_one_hand(lm_list, is_right_hand):
    """Count raised fingers for one hand (palm facing camera)."""
    if len(lm_list) < 21:
        return 0

    fingers_up = 0

    # Thumb: direction depends on handedness
    if is_right_hand:
        if lm_list[THUMB_TIP][0] > lm_list[THUMB_TIP - 1][0]:
            fingers_up += 1
    else:
        if lm_list[THUMB_TIP][0] < lm_list[THUMB_TIP - 1][0]:
            fingers_up += 1

    # Other fingers: tip above pip (smaller y)
    for tip in FINGER_TIPS:
        if lm_list[tip][1] < lm_list[tip - 2][1]:
            fingers_up += 1

    return fingers_up


def count_fingers_in_image(img_rgb):
    hands = get_hands_detector()
    if hands is None:
        return None, 'Hand detection unavailable (install mediapipe)'

    h, w = img_rgb.shape[:2]
    if h < 10 or w < 10:
        return None, 'Invalid image'

    results = hands.process(img_rgb)

    if not results.multi_hand_landmarks:
        return {
            'success': True,
            'total_fingers': 0,
            'hand_counts': [],
        }, None

    hand_counts = []
    for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
        lm_list = _landmarks_to_pixels(hand_landmarks, w, h)
        is_right = True
        if results.multi_handedness and idx < len(results.multi_handedness):
            label = results.multi_handedness[idx].classification[0].label
            is_right = label == 'Right'
        hand_counts.append(_count_fingers_one_hand(lm_list, is_right))

    return {
        'success': True,
        'total_fingers': sum(hand_counts),
        'hand_counts': hand_counts,
    }, None
