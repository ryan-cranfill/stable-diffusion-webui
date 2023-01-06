from webui import *
from modules.api.models import StableDiffusionImg2ImgProcessingAPI


def img2imgapi(api, img2imgreq: StableDiffusionImg2ImgProcessingAPI):
    init_images = img2imgreq.init_images
    if init_images is None:
        raise HTTPException(status_code=404, detail="Init image not found")

    mask = img2imgreq.mask
    if mask:
        mask = decode_base64_to_image(mask)

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

    with api.queue_lock:
        p = StableDiffusionProcessingImg2Img(sd_model=shared.sd_model, **args)
        p.init_images = [decode_base64_to_image(x) for x in init_images]

        shared.state.begin()
        processed = process_images(p)
        shared.state.end()

    b64images = list(map(encode_pil_to_base64, processed.images))

    if not img2imgreq.include_init_images:
        img2imgreq.init_images = None
        img2imgreq.mask = None

    return ImageToImageResponse(images=b64images, parameters=vars(img2imgreq), info=processed.js())


def api_only_with_monkeypatch():
    initialize()

    app = FastAPI()
    setup_cors(app)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    api = create_api(app)
    # TODO: monkeypatch
    api.add_api_route()

    modules.script_callbacks.app_started_callback(None, app)

    api.launch(server_name="0.0.0.0" if cmd_opts.listen else "127.0.0.1", port=cmd_opts.port if cmd_opts.port else 7861)
