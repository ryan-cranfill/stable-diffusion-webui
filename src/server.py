import io
import cv2
import json
import base64
import random
import requests
# import socketio
import uvicorn
import asyncio
from pathlib import Path
from datetime import datetime
from PIL import Image
from typing import Any, List
# from fastapi_socketio import SocketManager
from pydantic import BaseModel
from fastapi_utils.tasks import repeat_every
# from fastapi_frame_stream import FrameStreamer
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form, Response, WebSocket, WebSocketDisconnect

# sio: Any = socketio.AsyncServer(async_mode="asgi")
# socket_app = socketio.ASGIApp(sio)
app = FastAPI()
# fs = FrameStreamer()
# socket_manager = SocketManager(app=app)

AI_ROOT_URL = "http://localhost:7861/sdapi/v1/"

origins = [
    "*",
]


class InputImg(BaseModel):
    img_base64str : str

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_passcode(length=10):
    CHOICES = list(range(10))
    return ''.join([str(x) for x in random.choices(CHOICES, k=length)])


current_passcode = generate_passcode()


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


@app.get('/pass')
async def get_current_passcode():
    return {'status': 'ok', 'passcode': current_passcode}


@app.post('/text2img')
async def text2img(
        prompt: str = Form(...)
):
    data = {
        'prompt': prompt,
        'steps': 20,
        'sampler_name': 'DDIM',
        'width': 256,
        'height': 256,
    }
    response = requests.post(
        AI_ROOT_URL + "txt2img",
        json=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    if response.status_code == 200:
        data = response.json()
        data['success'] = True
        data['images'] = ["data:image/jpeg;base64," + image for image in data['images']]
        return data
    print(response)
    return Response(content={"success": False, "message": "AI server error"}, status_code=response.status_code)


@app.post("/upload")
async def upload(
        file: UploadFile = File(),
        prompt: str = Form(),
        passcode: str = Form(),
        denoising_strength: float = Form(0.6),
        send_to_img2img: bool = True,
        require_passcode: bool = False
):
    try:
        if send_to_img2img:
            if require_passcode:
                if passcode != current_passcode:
                    return {'success': False, 'message': 'bad passcode'}

            if not prompt:
                prompt = 'Garfield'
            print('prompt:', prompt, 'denoising_strength:', denoising_strength)
            img_bytes = io.BytesIO(await file.read()).getvalue()
            img_b64_enc = base64.b64encode(img_bytes)
            img = (bytes("data:image/jpeg;base64,", encoding='utf-8') + img_b64_enc).decode("utf-8")
            data = {
                'init_images': [img],
                'denoising_strength': denoising_strength,
                'steps': 20,
                'prompt': prompt,
                'sd_model': 'ghibliDiffusion_v1',
                'sampler_name': 'DDIM',
            }
            response = requests.post(
                AI_ROOT_URL + "img2img",
                json=data,
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            if response.status_code == 200:
                data = response.json()
                data['success'] = True
                data['images'] = ["data:image/jpeg;base64," + image for image in data['images']]
                return data
            return Response(content={"success": False, "message": "AI server error"}, status_code=response.status_code)
        else:
            im = Image.open(file.file)
            if im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
            buf = io.BytesIO()
            # im.save(buf, 'JPEG')
            im.show('neat!')
            # to get the entire bytes of the buffer use:
            contents = buf.getvalue()
            # or, to read from `buf` (which is a file-like object), call this first:
            buf.seek(0)  # to rewind the cursor to the start of the buffer
    except Exception as e:
        print(e)
    finally:
        file.file.close()
        # buf.close()
        # im.close()


# SOCKETS
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith('{'):
                # This is a json message
                data = json.loads(data)
            print(data)
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


THIS_FILE = Path(__file__).resolve().absolute()
ROOT_DIR = THIS_FILE.parent
# IMAGE_OPTIONS = list((ROOT_DIR / 'outputs' / 'img2img-images').glob('*.png'))
IMAGE_OPTIONS = list(Path('/Users/ryan/Downloads/stained-glass-cats/donkey1_upscayled/').glob('*.png'))
TEST_IMAGES = [Image.open(img) for img in IMAGE_OPTIONS[:10]]

cv2.namedWindow('Raw Image', cv2.WINDOW_NORMAL)

@app.on_event('startup')
@repeat_every(seconds=4)
async def send_random_image_path() -> None:
    if manager.active_connections:
        image_path = random.choice(IMAGE_OPTIONS)
        print('sending image path:', image_path)
        # image = Image.open(image_path)
        # # Convert to base64
        # buffered = io.BytesIO()
        # image.save(buffered, format="PNG")
        # img_str = base64.b64encode(buffered.getvalue())
        # print('loaded vid')
        # # await manager.broadcast(img_str.decode('utf-8'))
        # await fs.send_frame('cool', img_str)
        payload = {'path': str(image_path), 'type': 'image'}
        await manager.broadcast(json.dumps(payload))


# @app.get("/video_feed/{stream_id}")
# async def video_feed(stream_id: str):
#     return fs.get_stream(stream_id)


@app.get(
    "/image",

    # Set what the media type will be in the autogenerated OpenAPI specification.
    # fastapi.tiangolo.com/advanced/additional-responses/#additional-media-types-for-the-main-response
    responses = {
        200: {
            "content": {"image/JPEG": {}}
        }
    },

    # Prevent FastAPI from adding "application/json" as an additional
    # response media type in the autogenerated OpenAPI specification.
    # https://github.com/tiangolo/fastapi/issues/3258
    response_class=Response,
)
def get_image():
    # image_selection: Image = random.choice(IMAGE_OPTIONS)
    image_selection: Image.Image = random.choice(TEST_IMAGES)
    # Convert to bitmap
    # buffered = io.BytesIO()
    # image_selection.save(buffered, format="BMP")
    # Read bytes
    imgio = io.BytesIO()
    image_selection.save(imgio, 'JPEG', quality=95)
    # image_selection.save(imgio, 'BMP')
    imgio.seek(0)
    # image_bytes: bytes = image_selection.tobytes()
    # media_type here sets the media type of the actual response sent to the client.
    return Response(content=imgio.getvalue(), media_type="image/jpeg")
    # return Response(content=buffered.read(), media_type="image/bmp")


if __name__ == '__main__':
    # Broadcast a message every 5 seconds over the websocket
    uvicorn.run('server:app', host="0.0.0.0", port=5000, reload=True)
# app.mount("/", socket_app)
#
#
# @sio.on("connect")
# async def connect(sid, env):
#     print("on connect")

# @app.sio.on('connect')
# @socket_manager.on('connect')
# async def connect(sid, environ):
#     print('connect ', sid)