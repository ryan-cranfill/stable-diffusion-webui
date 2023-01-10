import os
from pathlib import Path
from PIL import Image

from src.utils import encode_pil_to_base64

TARGET_WIDTH = 512
TARGET_HEIGHT = 512

TARGET_SIZE = (TARGET_WIDTH, TARGET_HEIGHT)
IMAGE_OPTIONS = list(Path('/Users/ryan/Downloads/stained-glass-cats/donkey1_upscayled/').glob('*.png'))
SHARED_SETTINGS_MEM_NAME = 'settings'

THIS_FILE = Path(__file__).resolve()
SRC_DIR = THIS_FILE.parent
ROOT_DIR = SRC_DIR.parent
CHECKPOINT_DIR = ROOT_DIR / 'models/Stable-diffusion'

DEFAULT_IMG_PATH = SRC_DIR / 'garfield.jpg'
DEFAULT_IMG = Image.open(DEFAULT_IMG_PATH)

# Need to manually remove these keys from the request, because they are not in the processing class
REMOVE_FROM_REQ_KEYS = ['script_name']

# Use most recent checkpoint
DEFAULT_CHECKPOINT_PATH = sorted(CHECKPOINT_DIR.glob('*.ckpt'), key=lambda x: os.path.getmtime(x))[-1]

DEFAULT_SHARED_SETTINGS = {
    'generation_settings': {
        "batch_size": 1,
        "n_iter": 1,
        "steps": 20,
        "cfg_scale": 7.5,
        "width": TARGET_WIDTH,
        "height": TARGET_HEIGHT,
        "resize_mode": 0,
        "denoising_strength": 0.75,
        # 'prompt': 'jon and garfield at the kitchen table by jim davis',
        "sampler_index": "DPM++ SDE Karras",
        "seed": -1,
        "subseed": -1,
        "subseed_strength": 0,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
    },
    'source_img_1': encode_pil_to_base64(DEFAULT_IMG),
    'source_img_2': encode_pil_to_base64(DEFAULT_IMG),
    'source_img_3': encode_pil_to_base64(DEFAULT_IMG),
    'prompt_1': 'jon and garfield at the kitchen table by jim davis',
    'prompt_2': 'an orange cat wearing a tophat by jim davis',
    'prompt_3': 'the sun and the stars by jim davis',
    # When a new initial image or prompt get added, flip this to True
    # Defaults to true, so that the first time the app is run, it will generate a new image
    '1_changed': True,
    '2_changed': True,
    '3_changed': True,
}

img2img_params = {
  "init_images": [
    "string"
  ],
  "resize_mode": 0,
  "denoising_strength": 0.75,
  "mask": "string",
  "mask_blur": 4,
  "inpainting_fill": 0,
  "inpaint_full_res": True,
  "inpaint_full_res_padding": 0,
  "inpainting_mask_invert": 0,
  "initial_noise_multiplier": 0,
  "prompt": "",
  "styles": [
    "string"
  ],
  "seed": -1,
  "subseed": -1,
  "subseed_strength": 0,
  "seed_resize_from_h": -1,
  "seed_resize_from_w": -1,
  "sampler_name": "string",
  "batch_size": 1,
  "n_iter": 1,
  "steps": 50,
  "cfg_scale": 7,
  "width": 512,
  "height": 512,
  "restore_faces": False,
  "tiling": False,
  "negative_prompt": "string",
  "eta": 0,
  "s_churn": 0,
  "s_tmax": 0,
  "s_tmin": 0,
  "s_noise": 1,
  "override_settings": {},
  "override_settings_restore_afterwards": True,
  "sampler_index": "Euler",
  "include_init_images": True,
}