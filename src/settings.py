import os
import sys
import json
import numpy as np
import SharedArray as sa
from pathlib import Path
from PIL import Image

from src.utils import make_shared_mem

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

# Use most recent checkpoint
DEFAULT_CHECKPOINT_PATH = sorted(CHECKPOINT_DIR.glob('*.ckpt'), key=lambda x: os.path.getmtime(x))[-1]

DEFAULT_GENERATION_SETTINGS = {
    "batch_size": 1,
    "n_iter": 1,
    "steps": 20,
    "cfg_scale": 7.5,
    "width": TARGET_WIDTH,
    "height": TARGET_HEIGHT,
    "resize_mode": 0,
    "denoising_strength": 0.75,
    'prompt': 'jon and garfield at the kitchen table by jim davis',
    "sampler_index": "DPM++ SDE Karras",
    "seed": -1,
    "subseed": -1,
    "subseed_strength": 0,
    "seed_resize_from_h": -1,
    "seed_resize_from_w": -1,
}


class SharedSettingsManager:
    def __init__(self, is_client=True, shm_size=1024*10):
        self.is_client = is_client
        if not is_client:
            dummy_arr = np.array([' ' * shm_size])
            self.shared = make_shared_mem(SHARED_SETTINGS_MEM_NAME, dummy_arr.shape, dtype=dummy_arr.dtype)
            self.shared[0] = json.dumps(DEFAULT_GENERATION_SETTINGS)
        else:
            self.shared = sa.attach(f"shm://{SHARED_SETTINGS_MEM_NAME}")

    def get(self, prop, default=None):
        settings_dict = json.loads(self.shared[0])
        return settings_dict.get(prop, default)

    def set(self, prop, value):
        settings_dict = json.loads(self.shared[0])
        settings_dict[prop] = value
        self.shared[0] = json.dumps(settings_dict)

    def __getitem__(self, prop):
        return self.get(prop)

    def __setitem__(self, prop, value):
        self.set(prop, value)

    def __contains__(self, prop):
        return prop in self.get(prop)

    def __del__(self):
        if not self.is_client:
            sa.delete(f"shm://{SHARED_SETTINGS_MEM_NAME}")

    def __repr__(self):
        return f"SharedSettingsManager({json.loads(self.shared[0])})"


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