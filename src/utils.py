import io
import base64
from io import BytesIO

import numpy as np
from PIL import Image, PngImagePlugin


def encode_pil_to_base64(image, as_string=True):
    with io.BytesIO() as output_bytes:

        # Copy any text-only metadata
        use_metadata = False
        metadata = PngImagePlugin.PngInfo()
        for key, value in image.info.items():
            if isinstance(key, str) and isinstance(value, str):
                metadata.add_text(key, value)
                use_metadata = True

        image.save(
            output_bytes, "PNG", pnginfo=(metadata if use_metadata else None)
        )
        bytes_data = output_bytes.getvalue()
    b64_encoded_data = base64.b64encode(bytes_data)
    if as_string:
        return b64_encoded_data.decode("utf-8")
    return base64.b64encode(bytes_data)


def decode_image(encoding):
    if isinstance(encoding, str):
        if encoding.startswith("data:image/"):
            encoding = encoding.split(";")[1].split(",")[1]
        return Image.open(BytesIO(base64.b64decode(encoding)))
    elif isinstance(encoding, Image.Image):
        return encoding
    elif isinstance(encoding, np.ndarray):
        return Image.fromarray(encoding)
    else:
        raise TypeError("Unknown type for encoding")
