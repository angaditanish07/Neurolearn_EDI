import logging
from io import BytesIO

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def analyze_handwriting(image_data):
    """Extract handwriting features (already normalized 0-1)."""
    try:
        if isinstance(image_data, bytes):
            image = np.array(Image.open(BytesIO(image_data)))
        else:
            image = np.array(image_data)

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return {}

        features = {}
        lines = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 20:
                lines.append((y, y + h))
        lines.sort()

        line_spacing = 0.0
        if len(lines) > 1:
            spacings = []
            for i in range(len(lines) - 1):
                spacing = lines[i + 1][0] - lines[i][1]
                if spacing > 0:
                    spacings.append(spacing)
            if spacings:
                line_spacing = min(1.0, (sum(spacings) / len(spacings)) / 50.0)
        features['line_spacing'] = line_spacing

        letter_contours = [cnt for cnt in contours if 10 < cv2.boundingRect(cnt)[2] < 50]
        letter_spacing = 0.0
        if len(letter_contours) > 1:
            letter_positions = sorted(cv2.boundingRect(cnt)[0] for cnt in letter_contours)
            spacings = []
            for i in range(len(letter_positions) - 1):
                spacing = letter_positions[i + 1] - letter_positions[i]
                if 5 < spacing < 30:
                    spacings.append(spacing)
            if spacings:
                letter_spacing = min(1.0, (sum(spacings) / len(spacings)) / 20.0)
        features['letter_spacing'] = letter_spacing

        angles = []
        for cnt in contours:
            if len(cnt) > 5:
                try:
                    _, _, angle = cv2.fitEllipse(cnt)
                    if angle > 90:
                        angle = angle - 180
                    angles.append(abs(angle))
                except cv2.error:
                    pass
        if angles:
            slant_angle = sum(angles) / len(angles)
            features['slant_angle'] = 1.0 - (abs(slant_angle - 90) / 90.0)
        else:
            features['slant_angle'] = 0.5

        sizes = [cv2.boundingRect(cnt)[2] * cv2.boundingRect(cnt)[3] for cnt in letter_contours]
        if sizes and np.mean(sizes) > 0:
            size_variation = np.std(sizes) / np.mean(sizes)
            features['letter_size_variation'] = max(0, min(1, 1.0 - size_variation))
        else:
            features['letter_size_variation'] = 0.5

        pressure_values = []
        for cnt in letter_contours:
            mask = np.zeros_like(gray)
            cv2.drawContours(mask, [cnt], 0, 255, -1)
            pressure_values.append(np.mean(gray[mask == 255]))
        if pressure_values and np.mean(pressure_values) > 0:
            pv = np.std(pressure_values) / np.mean(pressure_values)
            features['pressure_variation'] = max(0, min(1, 1.0 - pv))
        else:
            features['pressure_variation'] = 0.5

        return features
    except Exception as e:
        logger.error('Error analyzing handwriting: %s', e)
        return {}
