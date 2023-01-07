import torch
from PIL import Image
import numpy as np
import base64
from io import BytesIO
import SharedArray as sa
from screeninfo import get_monitors

from webui import shared
import modules.images as images
from modules import sd_models
from modules.api.api import decode_base64_to_file, decode_base64_to_image, validate_sampler_name, encode_pil_to_base64
from modules.api.models import StableDiffusionImg2ImgProcessingAPI, ImageToImageResponse
from modules.processing import StableDiffusionProcessingTxt2Img, StableDiffusionProcessingImg2Img, process_images

from src.utils import make_shared_mem
from src.settings import TARGET_SIZE, IMAGE_OPTIONS, SharedSettingsManager, DEFAULT_GENERATION_SETTINGS, DEFAULT_IMG


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


req = StableDiffusionImg2ImgProcessingAPI()
print(req)
for k, v in DEFAULT_GENERATION_SETTINGS.items():
    setattr(req, k, v)

req.init_images = [DEFAULT_IMG]
print(req)


def img2imgapi(img2imgreq: StableDiffusionImg2ImgProcessingAPI):
    init_images = img2imgreq.init_images
    # if init_images is None:
    #     raise HTTPException(status_code=404, detail="Init image not found")

    mask = img2imgreq.mask
    if mask:
        mask = decode_image(mask)

    populate = img2imgreq.copy(update={  # Override __init__ params
        "sampler_name": validate_sampler_name(img2imgreq.sampler_name or img2imgreq.sampler_index),
        "do_not_save_samples": True,
        "do_not_save_grid": True,
        "mask": mask
    }
    )
    if populate.sampler_name:
        populate.sampler_index = None  # prevent a warning later on

    args = vars(populate)
    args.pop('include_init_images',
             None)  # this is meant to be done by "exclude": True in model, but it's for a reason that I cannot determine.

    print(args)
    # with api.queue_lock:
    p = StableDiffusionProcessingImg2Img(sd_model=shared.sd_model, **args)
    p.init_images = [decode_image(x) for x in init_images]

    shared.state.begin()
    processed = process_images(p)
    shared.state.end()

    for i in processed.images:
        i.show()

    b64images = list(map(encode_pil_to_base64, processed.images))

    if not img2imgreq.include_init_images:
        img2imgreq.init_images = None
        img2imgreq.mask = None

    return ImageToImageResponse(images=b64images, parameters=vars(img2imgreq), info=processed.js())


# settings = SharedSettingsManager(is_client=True)
#
#
# monitors = get_monitors()
# print('monitors:', monitors)
#
# img_dim = np.zeros((*TARGET_SIZE, 3), dtype=np.uint8).shape
# print('img_dim:', img_dim)
#
#
# changes = np.zeros(len(monitors), dtype=np.int8)
# changes_shared_mem = make_shared_mem('changes', changes.shape, dtype=changes.dtype)
#
# shared_mem_names = [f"img_{i}" for i in range(len(monitors))]
# shared_mems = [make_shared_mem(name, img_dim, dtype=np.uint8) for name in shared_mem_names]

print(shared.refresh_checkpoints())
sd_models.load_model()
print(img2imgapi(req))


# some of those options should not be changed at all because they would break the model, so I removed them from options.
# opt_C = 4
# opt_f = 8


# def reset_processor(p: StableDiffusionProcessingImg2Img, init_images):
#     p.init_images = init_images
#
#     imgs = []
#     for image in p.init_images:
#         if isinstance(image, Image.Image):
#             image = images.flatten(image, '#ffffff')
#             image = np.array(image).astype(np.float32) / 255.0
#             image = np.moveaxis(image, 2, 0)
#
#         imgs.append(image)
#
#     if len(imgs) == 1:
#         batch_images = np.expand_dims(imgs[0], axis=0).repeat(p.batch_size, axis=0)
#
#     elif len(imgs) <= p.batch_size:
#         p.batch_size = len(imgs)
#         batch_images = np.array(imgs)
#     else:
#         raise RuntimeError(f"bad number of images passed: {len(imgs)}; expecting {p.batch_size} or less")
#
#     image = torch.from_numpy(batch_images)
#     image = 2. * image - 1.
#     image = image.to(shared.device)
#
#     p.init_latent = p.sd_model.get_first_stage_encoding(p.sd_model.encode_first_stage(image))
#
#     if p.resize_mode == 3:
#         p.init_latent = torch.nn.functional.interpolate(p.init_latent,
#                                                            size=(p.height // opt_f, p.width // opt_f),
#                                                            mode="bilinear")
#
#     p.image_conditioning = p.img2img_image_conditioning(image, p.init_latent, None)



