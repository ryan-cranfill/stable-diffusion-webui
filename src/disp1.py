import random
import time
import slmpy
import numpy as np
from PIL import Image
from pathlib import Path
import tkinter as tk
from screeninfo import get_monitors

THIS_FILE = Path(__file__).resolve().absolute()
ROOT_DIR = THIS_FILE.parent
# IMAGE_OPTIONS = list((ROOT_DIR / 'outputs' / 'img2img-images').glob('*.png'))
IMAGE_OPTIONS = list(Path('/Users/ryan/Downloads/stained-glass-cats/donkey1_upscayled/').glob('*.png'))
TEST_IMAGES = [Image.open(img) for img in IMAGE_OPTIONS[:10]]

monitors = get_monitors()
print('monitors:', monitors)
#####################################
root = tk.Tk()

mon0 = monitors[0]
mon1 = monitors[1]

w0, h0 = mon0.width, mon0.height
w1, h1 = mon1.width, mon1.height

# specify resolutions of both windows
# w0, h0 = 3840, 2160
# w1, h1 = 1920, 1080

# set up window for display on HDMI 0
win0 = tk.Toplevel()
win0.geometry(f"{w0}x{h0}+0+0")
root.overrideredirect(1)
# win0.attributes("-fullscreen", True)
#
# set up window for display on HDMI 1
win1 = tk.Toplevel()
win1.geometry(f"{w1}x{h1}+{w0}+0") # <- the key is shifting right by w0 here
# win1.attributes("-fullscreen", True)

root.withdraw()  # hide the empty root window
root.mainloop()

#####################################
# # Create the main window
# window1 = tk.Tk()
# window2 = tk.Tk()
# # Set the window geometry and fullscreen it
# # screen_width = window1.winfo_screenwidth()
# # screen_height = window1.winfo_screenheight()
#
# mon0 = monitors[0]
# mon1 = monitors[1]
# window1.geometry(f'{mon1.width}x{mon1.height}+{mon1.x}+{mon1.y}')
# window2.geometry(f'{mon0.width}x{mon0.height}+{mon0.x}+{mon0.y}')
# # window.geometry(f"{screen_width}x{screen_height}+0+0")
#
# window1.attributes("-fullscreen", True)
# window2.attributes("-fullscreen", True)
# # window.wm_attributes("-topmost", 1)
# # window.attributes("-screen", 2)
#
# # window.title("Image Viewer")
#
# # Load the image
# image = tk.PhotoImage(file="txt2img_Screenshot.png")
#
# # Create a label and set the image as its background
# label1 = tk.Label(window1, image=image)
# label1.pack()
# label2 = tk.Label(window2, image=image)
# label2.pack()
#
# # Run the Tkinter event loop
# window1.mainloop()
# window2.mainloop()
