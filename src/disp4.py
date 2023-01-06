import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer
from PyQt6 import QtCore
import os
import random
import time
import numpy as np
from PIL import Image
from pathlib import Path
import SharedArray as sa
from screeninfo import get_monitors


THIS_FILE = Path(__file__).resolve().absolute()
ROOT_DIR = THIS_FILE.parent
# IMAGE_OPTIONS = list((ROOT_DIR / 'outputs' / 'img2img-images').glob('*.png'))
IMAGE_OPTIONS = list(Path('/Users/ryan/Downloads/stained-glass-cats/donkey1_upscayled/').glob('*.png'))
TEST_IMAGES = [Image.open(img) for img in IMAGE_OPTIONS[:10]]

monitors = get_monitors()
print('monitors:', monitors)
mon0 = monitors[0]
# mon1 = monitors[1]

# shared_mems = [sa.attach(f'shared_mem_{i}') for i in range(2)]

shared_mems = []
for i in range(len(monitors)):
    shared_mems.append(sa.attach(f"shm://img_{i}"))

changes_shared_mem = sa.attach(f"shm://changes")

def image_to_pixmap(image: Image.Image, resize_to=None) -> QPixmap:
    if resize_to is not None:
        image = image.resize(resize_to)
    qimage = QImage(np.array(image), image.width, image.height, QImage.Format.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)
    return pixmap


def array_to_pixmap(image: np.array) -> QPixmap:
    qimage = QImage(image, image.shape[0], image.shape[1], QImage.Format.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)
    return pixmap


class App(QWidget):
    def __init__(self, screen=0, fullscreen=True, w=512, h=512):
        super().__init__()
        self.mon = monitors[screen]
        self.w, self.h = w, h
        self.fullscreen = fullscreen
        self.imagenumber = 0
        self.label = QLabel(self)
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def update(self):
        if changes_shared_mem[i] == 1:
            pixmap = array_to_pixmap(shared_mems[i][:])
            self.label.setPixmap(pixmap)
            self.show()
            changes_shared_mem[i] = 0

    def keyPressEvent(self, event):
        key = event.key()
        print('key:', key)
        if key == Qt.Key.Key_Right:
            self.imagenumber = self.imagenumber + 1
            self.imagenumber %= len(TEST_IMAGES)
            self.showimage(self.imagenumber)
            self.show()
        elif key == Qt.Key.Key_Left:
            self.showFullScreen()
        else:
            QtCore.QCoreApplication.quit()

    def initUI(self):
        print(self.mon)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.move(self.mon.x, 0)
        self.setGeometry(self.mon.x, self.mon.y, self.w, self.h)
        self.showimage(5)
        self.show()
        if self.fullscreen:
            # For some reason full screen doesn't work till you show the window/image first
            self.showFullScreen()
            self.showimage(1)

    def showimage(self, imagenumber):
        label = self.label
        # directory = "C:\\Desktop\\Pictures"
        # imagelist = os.listdir(directory)
        # pixmap = QPixmap(directory + '\\' + imagelist[imagenumber])
        print('imagenumber:', imagenumber)
        # pixmap = QPixmap(str(IMAGE_OPTIONS[imagenumber]))
        pixmap = image_to_pixmap(TEST_IMAGES[imagenumber], resize_to=(self.w, self.h))
        # pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
        label.setPixmap(pixmap)
        # self.resize(pixmap.width(), pixmap.height())
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(0, fullscreen=False)
    # ex1 = App(1)
    sys.exit(app.exec())
