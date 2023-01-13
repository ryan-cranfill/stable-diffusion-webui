import io
import os
import sys
import time

import numpy as np
import uvicorn
from PIL import Image
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form, Response, WebSocket, WebSocketDisconnect


from src.utils import decode_image
from src.sharing import SharedDict, SharedMemManager
from src.settings import DEFAULT_IMG, NUM_SCREENS, TARGET_SIZE, SHM_NAMES, SRC_IMG_SHM_NAMES, USE_NGROK

if USE_NGROK:
    # Run this first to ensure no other ngrok processes are running
    os.system("pkill ngrok")

# INITIALIZE SHARED MEMORY
shared_settings = SharedDict(is_client=False)
shared_mem_manager = SharedMemManager(SHM_NAMES, is_client=False)

img_template_arr = np.array(DEFAULT_IMG.resize(TARGET_SIZE))
for name in SRC_IMG_SHM_NAMES:
    shared_mem_manager[name][:] = img_template_arr


app = FastAPI()

origins = [
    "*",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


public_url = None

if USE_NGROK:
    # pyngrok should only ever be installed or initialized in a dev environment when this flag is set
    from pyngrok import ngrok
    from pyngrok.exception import PyngrokNgrokError

    # Get the dev server port (defaults to 8000 for Uvicorn, can be overridden with `--port`
    # when starting the server
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 5000

    # Open a ngrok tunnel to the dev server
    public_url = None

    while not public_url:
        try:
            public_url = ngrok.connect(port).public_url
        except PyngrokNgrokError:
            # kill ngrok process and retry if it's already running
            os.system("pkill ngrok")
            time.sleep(1)
            print('trying to connect to ngrok...')
    print("ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))


class Img2ImgRequest(BaseModel):
    for_screen: int
    image: str | None = None
    prompt: str | None = None


@app.post("/process_img2img")
async def process_img2img_req(
        data: Img2ImgRequest
):
    for_screen = data.for_screen
    image = data.image
    prompt = data.prompt

    try:
        if for_screen >= NUM_SCREENS or for_screen < 0:
            return {'success': False, 'message': 'invalid screen number'}
        changes = {'for_screen': 1}
        if prompt:
            shared_settings[f'prompt_{for_screen}'] = prompt
            changes['prompt'] = 1
        if image:
            if isinstance(image, str):
                img = decode_image(image)
                # img.show()
            else:
                img = Image.open(io.BytesIO(await image.read()))

            if img.size != TARGET_SIZE:
                img = img.resize(TARGET_SIZE)
            shared_mem_manager[SRC_IMG_SHM_NAMES[for_screen]][:] = np.array(img)

            changes['img'] = 1

        return {'success': True, 'changes': changes}
    except Exception as e:
        print(e)
        return Response(content={"success": False, "message": "Server error"}, status_code=500)
    finally:
        if image and not isinstance(image, str):
            image.file.close()


app.mount("/", StaticFiles(directory="src/windows-vistas-client/dist", html=True), name="static")


if __name__ == '__main__':
    uvicorn.run('__main__:app', host="0.0.0.0", port=5000, reload=True, reload_excludes='windows-vistas-client/*')
    # uvicorn.run('__main__:app', host="0.0.0.0", port=5000, reload=not USE_NGROK)
