import base64
import logging
from io import BytesIO

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def process_base64_image(base64_string):
    if 'data:image' in base64_string:
        base64_string = base64_string.split(',')[1]
    img_data = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_data))
    return np.array(img)
