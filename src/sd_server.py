import time

from src.utils import decode_image
from webui import shared
from modules import sd_models
from modules.api.api import validate_sampler_name, encode_pil_to_base64
from modules.api.models import StableDiffusionImg2ImgProcessingAPI, ImageToImageResponse
from modules.processing import StableDiffusionProcessingImg2Img, process_images

from src.sharing import SharedDict, SharedMemManager
from src.settings import DEFAULT_IMG, REMOVE_FROM_REQ_KEYS


connected_to_shared = False
shared_settings = None
shared_mem_manager = None

# Connect to shared memory on startup
print('connecting to shared memory...')
while not connected_to_shared:
    try:
        shared_settings = SharedDict(is_client=True)
        print('connected to shared settings')
        shared_mem_manager = SharedMemManager(is_client=True)
        print('connected to shared memory manager')
        connected_to_shared = True
    except Exception as e:
        print(e)
        print('Waiting for shared memory to be available and server to start...')
        time.sleep(1)
print('connected to shared memory')


# Configurations
generation_config = {
    1: {
        'prompt': shared_settings['prompt_1'],
        'image': decode_image(shared_settings['source_img_1']),
    },
    2: {
        'prompt': shared_settings['prompt_2'],
        'image': decode_image(shared_settings['source_img_2']),
    },
    3: {
        'prompt': shared_settings['prompt_3'],
        'image': decode_image(shared_settings['source_img_3']),
    },
}

def img2imgapi(img2imgreq: StableDiffusionImg2ImgProcessingAPI):
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

    print(args)
    # with api.queue_lock:
    p = StableDiffusionProcessingImg2Img(sd_model=shared.sd_model, **args)
    p.init_images = [decode_image(x) for x in init_images]

    shared.state.begin()
    processed = process_images(p)
    shared.state.end()
    shared.total_tqdm.clear()  # clear the progress bar

    for i in processed.images:
        i.show()

    b64images = list(map(encode_pil_to_base64, processed.images))

    if not img2imgreq.include_init_images:
        img2imgreq.init_images = None
        img2imgreq.mask = None

    return ImageToImageResponse(images=b64images, parameters=vars(img2imgreq), info=processed.js())


def generate_image(num):
    req = StableDiffusionImg2ImgProcessingAPI()
    for k, v in shared_settings['generation_settings'].items():
        setattr(req, k, v)

    req.init_images = [generation_config[num]['image']]
    req.prompt = generation_config[num]['prompt']

    for k in REMOVE_FROM_REQ_KEYS:
        if k in req.__dict__:
            req.__dict__.pop(k, None)

    return img2imgapi(req)


def check_for_changes():
    for i in range(1, 4):
        if shared_settings[f'{i}_changed']:
            generation_config[i]['image'] = decode_image(shared_settings[f'source_img_{i}'])
            generation_config[i]['prompt'] = shared_settings[f'prompt_{i}']
            shared_settings[f'{i}_changed'] = False
            print(f'inputs for {i} changed')


if __name__ == '__main__':
    print('Loading model....')
    print(shared.refresh_checkpoints())
    sd_models.load_model()

    # Start generation loop - iterate through each 3 screens and generate an image
    while True:
        for i in range(1, 4):
            print(f'Generating image for screen {i}...')
            start = time.time()
            generate_image(i)
            print(f'Finished generating image for screen {i} in {time.time() - start} seconds')

            check_for_changes()



