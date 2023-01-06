import cv2
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

slm1 = slmpy.SLMdisplay()
resX, resY = slm1.getSize()
print('resX, resY:', resX, resY)
# slm2 = slmpy.SLMdisplay(monitor=3)

# cv2.namedWindow('win1', cv2.WINDOW_NORMAL)
# cv2.namedWindow('1', cv2.WND_PROP_FULLSCREEN)
# cv2.moveWindow('win1', 5000, 0)
# cv2.setWindowProperty('win1', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Every second, show a random image
i = 0
while True:
    img = random.choice(TEST_IMAGES)
    slm1.updateArray(np.array(img))
    print('img.shape:', img.shape)
    # time.sleep(1)


    # cv2.imshow('win1', np.array(img))
    # k = cv2.waitKey(1000) & 0xFF
    # if k == 27:  # wait for ESC key to exit
    #     cv2.destroyAllWindows()
    #     break
    # if i == 0:
    #     cv2.setWindowProperty('win1', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # i += 1



