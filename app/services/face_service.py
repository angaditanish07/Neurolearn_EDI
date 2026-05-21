import logging

from app.ml.loaders import get_face_mesh

logger = logging.getLogger(__name__)

ORGANS = {
    'Left Eye': 33,
    'Right Eye': 263,
    'Nose': 1,
    'Mouth': 13,
    'Left Ear': 234,
    'Right Ear': 454,
    'Chin': 152,
}


def extract_face_landmarks(img_rgb):
    face_mesh = get_face_mesh()
    if face_mesh is None:
        return None, 'Face mesh unavailable'

    results = face_mesh.process(img_rgb)
    if not results.multi_face_landmarks:
        return None, 'No face detected'

    h, w = img_rgb.shape[:2]
    face_landmarks = results.multi_face_landmarks[0]
    face_points = {}
    for organ, idx in ORGANS.items():
        pt = face_landmarks.landmark[idx]
        # Normalized 0–1 coords; client maps to on-screen video (object-fit: cover)
        face_points[organ] = {
            'x': round(float(pt.x), 4),
            'y': round(float(pt.y), 4),
        }

    return {
        'success': True,
        'face_data': [face_points],
        'frame_width': w,
        'frame_height': h,
    }, None
