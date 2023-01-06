import random
import time
import numpy as np
from PIL import Image
from pathlib import Path
import cv2
from screeninfo import get_monitors

# THIS_FILE = Path(__file__).resolve().absolute()
# ROOT_DIR = THIS_FILE.parent
# IMAGE_OPTIONS = list((ROOT_DIR / 'outputs' / 'img2img-images').glob('*.png'))
IMAGE_OPTIONS = list(Path('/Users/ryan/Downloads/stained-glass-cats/donkey1_upscayled/').glob('*.png'))
TEST_IMAGES = [Image.open(img) for img in IMAGE_OPTIONS[:10]]

monitors = get_monitors()
print('monitors:', monitors)
for i in range(0,1):
    cv2.namedWindow(f'win{i}', cv2.WINDOW_GUI_NORMAL)
    cv2.moveWindow(f'win{i}', monitors[i].x + 100, monitors[i].y + 50)
    cv2.resizeWindow(f'win{i}', monitors[i].width, monitors[i].height)
    cv2.setWindowProperty(f'win{i}', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Every second, show a random image
while True:
    for i in range(0,1):
        img = random.choice(TEST_IMAGES)
        cv2.imshow(f'win{i}', np.array(img))
        # cv2.resizeWindow(f'win{i}', monitors[i].width, monitors[i].height)
        # cv2.setWindowProperty(f'win{i}', ncv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    k = cv2.waitKey(1000) & 0xFF
    if k == 27:  # wait for ESC key to exit
        cv2.destroyAllWindows()
        break


# for m in get_monitors():
#     print(str(m))
#
#
# # Create the main window
# window = tk.Tk()
# # window.title("Image Viewer")
#
# # Load the image
# image = tk.PhotoImage(file="txt2img_Screenshot.png")
#
# # Create a label and set the image as its background
# label = tk.Label(window, image=image)
# label.pack()
#
# # Run the Tkinter event loop
# window.mainloop()