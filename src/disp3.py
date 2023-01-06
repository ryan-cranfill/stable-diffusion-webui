import random
import time
import slmpy
import numpy as np
from PIL import Image, ImageTk
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
mon0 = monitors[0]
mon1 = monitors[1]


import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QPixmap, QScreen, QImage
# Import QScreen

# Create the application and the first window
app = QApplication(sys.argv)
window1 = QWidget()
window1.setWindowTitle("Window 1")
# Move to first monitor
window1.move(0, 0)
window1.showFullScreen()
# # Set the window geometry and fullscreen it
# screen_width = window1.screen().size().width()
# screen_height = window1.screen().size().height()
# window1.resize(screen_width, screen_height)

def image_to_pixmap(image: Image.Image) -> QPixmap:
    qimage = QImage(np.array(image), image.width, image.height, QImage.Format.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)
    return pixmap


# pixmap1 = QPixmap(str(IMAGE_OPTIONS[0]))
# qimage1 = QImage(np.array(TEST_IMAGES[0]), TEST_IMAGES[0].width, TEST_IMAGES[0].height, QImage.Format.Format_RGB888)
# pixmap1 = QPixmap.fromImage(qimage1
pixmap1 = image_to_pixmap(TEST_IMAGES[0])
pixmap2 = image_to_pixmap(TEST_IMAGES[1])
# pixmap1 = QPixmap(str(IMAGE_OPTIONS[0]))
# pixmap2 = QPixmap(str(IMAGE_OPTIONS[1]))

# Create a QLabel to display the image
label1 = QLabel(window1)
label1.setPixmap(pixmap1)
label1.show()

# Create the second window
window2 = QWidget()
window2.setWindowTitle("Window 2")
# Move to second monitor

window2.showFullScreen()

# Create a QLabel to display the image
label2 = QLabel(window2)
label2.setPixmap(pixmap2)
label2.show()

# Show the windows
window1.show()
window2.show()

# app.exit()
while True:
    print('looping')
    # Set labels to random images
    img = random.choice(TEST_IMAGES)
    label1.setPixmap(image_to_pixmap(img))
    label2.setPixmap(image_to_pixmap(img))
    # Show
    # label1.show()
    # label2.show()
    # window1.show()
    # window2.show()

    # Wait a second
    time.sleep(1)



# Run the Qt event loop
# sys.exit(app.exec())

