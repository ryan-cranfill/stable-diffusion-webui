import sys
import cv2
import time
import numpy as np
from PIL import Image
from PyQt6 import QtCore
from screeninfo import get_monitors
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

from src.utils import connect_to_shared
from src.settings import IMAGE_OPTIONS, TARGET_SIZE, NUM_SCREENS

shared_settings, shared_mem_manager = connect_to_shared()


monitors = get_monitors()[:NUM_SCREENS]
print('monitors:', monitors)


def image_to_pixmap(image: Image.Image | np.ndarray, resize_to=None) -> QPixmap:
    if isinstance(image, Image.Image):
        if resize_to is not None:
            image = image.resize(resize_to)
        image = np.array(image)
    elif isinstance(image, np.ndarray):
        if resize_to is not None and image.shape[:2] != resize_to:
            image = cv2.resize(image, resize_to)
    qimage = QImage(image, image.shape[0], image.shape[1], QImage.Format.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)
    return pixmap


def array_to_pixmap(image: np.array, resize_to=None) -> QPixmap:
    if resize_to is not None:
        image = cv2.resize(image, resize_to)
    qimage = QImage(image, image.shape[0], image.shape[1], QImage.Format.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)
    return pixmap


class App(QWidget):
    def __init__(self, screen=0, fullscreen=True, w=TARGET_SIZE[0], h=TARGET_SIZE[1]):
        super().__init__()
        self.screen = screen
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
        pixmap = array_to_pixmap(shared_mem_manager[f'img_{self.screen}'])
        self.label.setPixmap(pixmap)
        self.show()

    def keyPressEvent(self, event):
        key = event.key()
        print('key:', key)
        if key == Qt.Key.Key_Right:
            self.imagenumber = self.imagenumber + 1
            self.imagenumber %= len(IMAGE_OPTIONS)
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
        # self.show()
        if self.fullscreen:
            # For some reason full screen doesn't work till you show the window/image first
            self.showFullScreen()
            self.showimage(1)

    def showimage(self, imagenumber):
        label = self.label
        print('imagenumber:', imagenumber)
        pixmap = QPixmap(str(IMAGE_OPTIONS[imagenumber]))
        pixmap = pixmap.scaled(self.w, self.h)
        # pixmap = image_to_pixmap(TEST_IMAGES[imagenumber], resize_to=(self.w, self.h))
        label.setPixmap(pixmap)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    for i in range(len(monitors)):
        ex = App(screen=i, fullscreen=False)
    sys.exit(app.exec())
