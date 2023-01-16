import io
import time
import qrcode
import base64
import numpy as np
from PIL import Image, PngImagePlugin, ImageDraw
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask, SolidFillColorMask

from src.settings import SHM_NAMES, TARGET_WIDTH, QR_CODE_HEIGHT
from src.sharing import SharedDict, SharedMemManager


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


def decode_image(encoding) -> Image.Image:
    if isinstance(encoding, str):
        if encoding.startswith("data:image/"):
            encoding = encoding.split(";")[1].split(",")[1]
        img = Image.open(io.BytesIO(base64.b64decode(encoding)))
    elif isinstance(encoding, Image.Image):
        img = encoding
    elif isinstance(encoding, np.ndarray):
        img = Image.fromarray(encoding)
    else:
        raise TypeError("Unknown type for encoding")

    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def connect_to_shared(silent=False):
    print('Connecting to shared memory...') if not silent else None
    connected_to_shared = False
    shared_settings, shared_mem_manager = None, None
    while not connected_to_shared:
        try:
            shared_settings = SharedDict(is_client=True)
            print("Connected to shared settings") if not silent else None
            shared_mem_manager = SharedMemManager(SHM_NAMES, is_client=True)
            print('connected to shared memory manager') if not silent else None
            connected_to_shared = True
        except Exception as e:
            print(e)
            print('Waiting for shared memory to be available and server to start...')
            time.sleep(1)
    print('connected to shared memory') if not silent else None
    return shared_settings, shared_mem_manager


def make_banner(url, text: str = None):
    # Make a black banner with the url in white text
    img = Image.new('RGB', (TARGET_WIDTH, QR_CODE_HEIGHT), color = (0, 0, 0))
    d = ImageDraw.Draw(img)

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(url)
    # qr_img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())
    qr_img = qr.make_image(fill_color="white", back_color="black", module_drawer=RoundedModuleDrawer())
    # qr_img = qr.make_image(image_factory=StyledPilImage, color_mask=RadialGradiantColorMask(), module_drawer=RoundedModuleDrawer())
    # qr_img = qrcode.make(url,)

    # Resize the QR code to fit the banner
    qr_img.thumbnail((TARGET_WIDTH, QR_CODE_HEIGHT))
    # Paste the QR code on the right side of the banner
    img.paste(qr_img, (TARGET_WIDTH - QR_CODE_HEIGHT, 0))

    # d.text((10,10), url, fill=(255,255,255))
    if text:
        d.text((10, 30), text, fill=(255, 255, 255))
    return img