import random
import time
import slmpy
import numpy as np
from PIL import Image
from pathlib import Path

THIS_FILE = Path(__file__).resolve().absolute()
ROOT_DIR = THIS_FILE.parent
# IMAGE_OPTIONS = list((ROOT_DIR / 'outputs' / 'img2img-images').glob('*.png'))
IMAGE_OPTIONS = list(Path('/Users/ryan/Downloads/stained-glass-cats/donkey1_upscayled/').glob('*.png'))
TEST_IMAGES = [Image.open(img) for img in IMAGE_OPTIONS[:10]]

import pyglet

# Get a list of all available video displays
# displays = pyglet.canvas.DisplayList()
display = pyglet.canvas.get_display()
displays = display.get_screens()

# Create a window for each display
windows = []
for i, display in enumerate(displays[:2]):
    # Set the window size
    screen_size = (640, 480)

    screen = pyglet.canvas.Screen(display, display._cg_display_id)
    window = pyglet.window.Window(
        # width=screen_size[0],
        # height=screen_size[1],
        screen=screen,
        fullscreen=True,
        vsync=False,
        resizable=True,
        caption='Display {}'.format(i),
    )

    # Create the window
    # window = pyglet.window.Window(fullscreen=True, screen=i, width=screen_size[0], height=screen_size[1])

    # Add the window to the list of windows
    windows.append(window)
    # windows.append(screen)

# Load the images
images = [
    pyglet.image.load(IMAGE_OPTIONS[3]),
    pyglet.image.load(IMAGE_OPTIONS[1])]

# Set the images as the background images
for i, window in enumerate(windows):
    # img = IMAGE_OPTIONS[i]
    # print('img:', img)
    # pil_img = Image.open(img)
    # pyglet_img = pyglet.image.create(pil_img.width, pil_img.height)
    # # pyglet_img.set_data('RGB', pil_img.width * 3, np.array(pil_img.convert('RGB')))
    # pyglet_img.set_data('RGB', pil_img.width * 3, np.array(pil_img.convert('RGB')).dstack())
    # sprite = pyglet.sprite.Sprite(pyglet_img)
    start = time.time()
    img: Image.Image = TEST_IMAGES[i]
    print('img:', img)
    bdata = img.tobytes()
    image_data = pyglet.image.ImageData(img.width, img.height, 'RGB', bdata, pitch=img.width * -3)
    sprite = pyglet.sprite.Sprite(image_data)
    window.sprite = sprite
    print('time to load image:', time.time() - start)

    # image = pyglet.image.load(IMAGE_OPTIONS[i])
    # print('image:', IMAGE_OPTIONS[i])
    # sprite = pyglet.sprite.Sprite(image)
    # print(window)
    # window.sprite = sprite

    @window.event
    def on_draw():
        # window.switch_to()
        # print('drawing', window)
        window.clear()
        window.sprite.draw()
        # images[i].blit(0, 0)


    @window.event
    def on_key_press(symbol, mod):
        global running
        print('key press:', symbol, mod)
        # if symbol == pyglet.window.key.ESCAPE:
        running = False
        pyglet.app.exit()


# class CustomLoop(pyglet.app.EventLoop):
#     def idle(self):
#         print('lol!', pyglet.app.windows)
#         dt = self.clock.update_time()
#         self.clock.call_scheduled_functions(dt)
#
#         # Redraw all windows
#         for window in pyglet.app.windows:
#             window.switch_to()
#             window.dispatch_events()
#             window.dispatch_event('on_draw')
#             window.flip()
#             window._legacy_invalid = False
#
#         # no timout (sleep-time between idle()-calls)
#         return 0
# pyglet.app.event_loop = CustomLoop()
# pyglet.app.run()  # locks the thread


# Run the pyglet loop
running = True
while running:
    try:
        pyglet.clock.tick()

        for index, window in enumerate(pyglet.app.windows):
            window.switch_to()
            window.dispatch_events()
            window.dispatch_event('on_draw')
            window.flip()
    except Exception as e:
        print('error:', e)
        running = False
        pyglet.app.exit()
# pyglet.app.run()
