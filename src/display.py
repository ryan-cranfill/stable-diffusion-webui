import sys
import cv2
import time
import functools
import numpy as np
from PIL import Image
from PyQt6 import QtCore
from screeninfo import get_monitors
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

from src.utils import connect_to_shared
from src.settings import IMAGE_OPTIONS, TARGET_SIZE, NUM_SCREENS, SCREEN_MAP, DEFAULT_IMG_PATH

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


def array_to_pixmap(image, resize_to=None) -> QPixmap:
    if isinstance(image, list):
        # print(image[0].shape)
        image = np.vstack(image)
        # image = np.concatenate(image, axis=1)
    # print(image.shape)
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
        if screen == 0:
            # self.reconnect_timer = QTimer()
            # reconnect_func = functools.partial(self.reconnect_to_shm, silent=True)
            # self.reconnect_timer.timeout.connect(reconnect_func)
            # self.reconnect_timer.start(1000 * 5)
            pass

    def update(self):
        pixmap = self.array_to_pixmap([shared_mem_manager[f'img_{self.screen}'], shared_mem_manager[f'qr_code_{self.screen}']])
        # pixmap = self.array_to_pixmap(shared_mem_manager[f'qr_code_{self.screen}'], )
        # pixmap = self.array_to_pixmap(shared_mem_manager[f'img_{self.screen}'])
        self.label.setPixmap(pixmap)
        self.label.adjustSize()
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
        # self.setGeometry(self.mon.x, self.mon.y, self.w, self.h)
        self.showimage(0)
        # self.show()
        if self.fullscreen:
            # For some reason full screen doesn't work till you show the window/image first
            self.setGeometry(self.mon.x, self.mon.y, self.mon.width, self.mon.height)
            # self.showFullScreen()
        else:
            self.setGeometry(self.mon.x, self.mon.y, self.w, self.h)
        self.showimage(0)

    def showimage(self, imagenumber):
        label = self.label
        print('imagenumber:', imagenumber)
        pixmap = QPixmap(str(IMAGE_OPTIONS[imagenumber]))
        pixmap = pixmap.scaled(self.w, self.h)
        # pixmap = image_to_pixmap(TEST_IMAGES[imagenumber], resize_to=(self.w, self.h))
        label.setPixmap(pixmap)
        self.show()

    def reconnect_to_shm(self, silent=True):
        global shared_settings, shared_mem_manager
        shared_settings, shared_mem_manager = connect_to_shared(silent=silent)

    def array_to_pixmap(self, image, resize_to=None, rotate=True) -> QPixmap:
        if isinstance(image, list):
            image = cv2.vconcat(image)

        if rotate:
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        if resize_to is not None:
            image = cv2.resize(image, resize_to)
        elif self.fullscreen:
            image = cv2.resize(image, (self.mon.width, self.mon.height), interpolation=cv2.INTER_AREA)

        h, w, ch = image.shape
        bytes_per_line = ch * w
        qimage = QImage(image, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap


if __name__ == '__main__':
    app = QApplication(sys.argv)
    for i in range(len(monitors)):
        ex = App(screen=i, fullscreen=True)
    sys.exit(app.exec())
