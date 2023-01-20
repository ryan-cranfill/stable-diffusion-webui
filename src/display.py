import sys
import cv2
import time
import signal
import functools
import numpy as np
from PIL import Image
from PyQt6 import QtCore
from scipy import ndimage
from screeninfo import get_monitors
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QMainWindow

from src.upscale import upscale_img
from src.utils import connect_to_shared
from src.settings import IMAGE_OPTIONS, TARGET_SIZE, NUM_SCREENS, SCREEN_MAP, DEFAULT_IMG_PATH, IMG_SHM_NAMES

UPSCALE = True

shared_settings, shared_mem_manager = connect_to_shared()

signal.signal(signal.SIGINT, signal.SIG_DFL)

monitors = get_monitors()
monitors = [m for m in monitors if m.name != 'DP-0']
monitors = monitors[:NUM_SCREENS]
print('monitors:', monitors)
current_images = {name: np.zeros((*TARGET_SIZE, 3)) for name in IMG_SHM_NAMES}
display_images = {name: np.zeros((*TARGET_SIZE, 3)) for name in IMG_SHM_NAMES}
full_display_images = {name: np.zeros((*TARGET_SIZE, 3)) for name in IMG_SHM_NAMES}


def zoom_at(img, zoom, coord=None):
    """
    Simple image zooming without boundary checking.
    Centered at "coord", if given, else the image center.

    img: numpy.ndarray of shape (h,w,:)
    zoom: float
    coord: (float, float)
    """
    # Translate to zoomed coordinates
    h, w, _ = [zoom * i for i in img.shape]

    if coord is None:
        cx, cy = w / 2, h / 2
    else:
        cx, cy = [zoom * c for c in coord]

    img = cv2.resize(img, (0, 0), fx=zoom, fy=zoom)
    img = img[int(round(cy - h / zoom * .5)): int(round(cy + h / zoom * .5)),
              int(round(cx - w / zoom * .5)): int(round(cx + w / zoom * .5)),
              :]

    return img


def padded_zoom(img, zoom_factor=0.8):
    """
       Zoom in/out an image while keeping the input image shape.
       i.e., zero pad when factor<1, clip out when factor>1.
    """
    if zoom_factor < 1:  # zero padded
        out = np.zeros_like(img)
        zoomed = cv2.resize(img, None, fx=zoom_factor, fy=zoom_factor)

        h, w, c = img.shape
        zh, zw, zc = zoomed.shape

        out[(h - zh) // 2:-(h - zh) // 2, (w - zw) // 2:-(w - zw) // 2] = zoomed
        return out
    else:
        return zoom_at(img, zoom_factor)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.windows = []
        for i in range(len(monitors)):
            print(f'making window {i}')
            ex = App(screen=i, fullscreen=True)
            ex.show()
            self.windows.append(ex)


class App(QWidget):
    def __init__(self, screen=0, fullscreen=True, w=TARGET_SIZE[0], h=TARGET_SIZE[1]):
        super().__init__()
        self.screen = screen
        self.mon = monitors[screen]
        self.w, self.h = w, h
        self.fullscreen = fullscreen
        self.imagenumber = 0
        self.name = IMG_SHM_NAMES[screen]
        self.label = QLabel(self)
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_image_changes)
        self.timer.start(100)
        # reconnect_func = functools.partial(self.reconnect_to_shm, silent=True)
        # self.reconnect_timer.timeout.connect(reconnect_func)
        # self.reconnect_timer.start(1000 * 5)
        pass

    def update(self, blend_steps=75):
        #        resized_new = self.transform_to_screen([display_images[self.name], shared_mem_manager[f'qr_code_{self.screen}']])
        resized_new = self.transform_to_screen(display_images[self.name])
        if blend_steps and resized_new.shape == full_display_images[self.name].shape:
            # print(resized_new.shape, full_display_images[self.name].shape)
            for i in range(blend_steps):
                new_img = cv2.addWeighted(resized_new, i / blend_steps, full_display_images[self.name],
                                          1 - i / blend_steps, 0)
                self.label.setPixmap(self.array_to_pixmap(new_img))
                self.label.adjustSize()
                self.repaint()
                time.sleep(0.01)

        full_display_images[self.name] = resized_new.copy()
        pixmap = self.array_to_pixmap(resized_new)
        self.label.setPixmap(pixmap)
        self.label.adjustSize()
        self.repaint()

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
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setCursor(Qt.CursorShape.BlankCursor)
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
        img_arr = cv2.imread(str(IMAGE_OPTIONS[imagenumber]))
        img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
        img_arr = self.transform_to_screen(img_arr)
        full_display_images[self.name] = img_arr.copy()
        pixmap = self.array_to_pixmap(img_arr)
        label.setPixmap(pixmap)
        self.show()

    def reconnect_to_shm(self, silent=True):
        global shared_settings, shared_mem_manager
        shared_settings, shared_mem_manager = connect_to_shared(silent=silent)

    def transform_to_screen(self, image, resize_to=None, rotate=True) -> np.array:
        already_resized = False
        if isinstance(image, list):
            # If the images aren't all the same size, resize to the largest
            if resize_to is None:
                resize_to = (max([img.shape[1] for img in image] + [self.mon.x]),
                             max([img.shape[0] for img in image] + [self.mon.y]))
            for i, img in enumerate(image):
                # If the width isn't the same, resize while keeping the same aspect ratio
                if img.shape[1] != resize_to[0]:
                    image[i] = cv2.resize(img, (resize_to[0], int(img.shape[0] * resize_to[0] / img.shape[1])))
                    already_resized = True

            image = cv2.vconcat(image)

        if rotate:
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        rotation_adjustment = shared_settings.get('other_settings', {}).get(f'rotation_screen_{self.screen}')
        if rotation_adjustment:
            image = ndimage.rotate(image, rotation_adjustment, reshape=False, )

        zoom_adjustment = shared_settings.get('other_settings', {}).get(f'zoom_screen_{self.screen}')
        if zoom_adjustment and zoom_adjustment != 1:
            # image = zoom_at(image, zoom_adjustment)
            image = padded_zoom(image, zoom_adjustment)

        if resize_to is not None and not already_resized:
            image = cv2.resize(image, resize_to)
        elif self.fullscreen:
            image = cv2.resize(image, (self.mon.width, self.mon.height), interpolation=cv2.INTER_AREA)

        return image

    def array_to_pixmap(self, image, resize_to=None, rotate=True) -> QPixmap:
        h, w, ch = image.shape
        bytes_per_line = ch * w
        qimage = QImage(image, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap

    def check_for_image_changes(self):
        new_image = shared_mem_manager[self.name][:]
        if not np.array_equal(new_image, current_images[self.name]):
            print('changing', self.screen)
            current_images[self.name] = new_image.copy()
            start = time.time()
            print(f'upscaled screen {self.screen} in', time.time() - start)
            if UPSCALE:
                upscaled = upscale_img(new_image)
                display_images[self.name] = upscaled
            else:
                display_images[self.name] = new_image.copy()
            self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.hide()
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print('got keyboard interrupt')
        app.quit()
