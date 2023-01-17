import os
import sys
import time
import shlex
import numpy as np
from PIL import Image

# Dumb but makes it so we can use webui-user.sh
commandline_args = os.environ.get('COMMANDLINE_ARGS', "")
sys.argv += shlex.split(commandline_args)

from webui import shared
from modules import sd_models
from modules.api.api import validate_sampler_name
from modules.api.models import StableDiffusionImg2ImgProcessingAPI
from modules.processing import StableDiffusionProcessingImg2Img, process_images

from src.utils import decode_image, connect_to_shared
from src.settings import REMOVE_FROM_REQ_KEYS, NUM_SCREENS

# Connect to shared memory on startup
shared_settings, shared_mem_manager = connect_to_shared()


def img2imgapi(img2imgreq: StableDiffusionImg2ImgProcessingAPI) -> Image.Image:
    init_images = img2imgreq.init_images
    if init_images is None:
        raise ValueError('init_images is None')

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

    # print(args)
    # with api.queue_lock:
    p = StableDiffusionProcessingImg2Img(sd_model=shared.sd_model, **args)
    p.init_images = [decode_image(x) for x in init_images]

    shared.state.begin()
    processed = process_images(p)
    shared.state.end()
    shared.total_tqdm.clear()  # clear the progress bar

    return processed.images[0]


def decay_denoising_strength(num_frames_generated: int, base_strength: float, decay_rate: float = .05, min_val: float = 0.5) -> float:
    return max(base_strength * np.exp(-decay_rate * num_frames_generated), min_val)


def generate_image(i):
    start_time = time.time()

    req = StableDiffusionImg2ImgProcessingAPI()
    for k, v in shared_settings['generation_settings'].items():
        setattr(req, k, v)

    req.denoising_strength = decay_denoising_strength(
        shared_settings[f'{i}_num_frames_generated'],
        shared_settings['generation_settings']['denoising_strength']
    )
    # print(req.denoising_strength)

    req.init_images = [shared_mem_manager[f'src_img_{i}']]
    req.prompt = shared_settings[f'prompt_{i}']

    for k in REMOVE_FROM_REQ_KEYS:
        if k in req.__dict__:
            req.__dict__.pop(k, None)

    out_img = img2imgapi(req)
    shared_mem_manager[f'img_{i}'] = np.array(out_img)

    # shared_settings[f'{i}_last_frame'] = 0
    shared_settings[f'{i}_num_frames_generated'] += 1

    if shared_settings['other_settings'].get('loopback_mode'):
        # Put the generated image back into the source image
        # Check that it hasn't changed in the meantime first though
        if shared_settings[f'{i}_changed'] > start_time:
            # Input image has changed since generation started, don't overwrite it
            return
        shared_mem_manager[f'src_img_{i}'] = np.array(out_img)


if __name__ == '__main__':
    print('Loading model....')
    print(shared.refresh_checkpoints())
    sd_models.load_model()

    # Start generation loop - iterate through each 3 screens and generate an image
    while True:
        for i in range(NUM_SCREENS):
            print(f'Generating image for screen {i}...')
            start = time.time()
            generate_image(i)
            end = time.time()
            duration = end - start
            print(f'Finished generating image for screen {i} in {duration} seconds')

            # Rate limit to not blow up the GPU
            frame_every_n_seconds = shared_settings['other_settings']['frame_every_n_seconds']
            if duration < frame_every_n_seconds:
                time.sleep(frame_every_n_seconds - duration)

            # shared_settings, shared_mem_manager = connect_to_shared(silent=True)




