import sys
import cv2
import time
import signal
import qrcode
import functools
import numpy as np
from PIL import Image, ImageDraw, ImageOps, ImageFont
from PyQt6 import QtCore
from scipy import ndimage
from screeninfo import get_monitors
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

from src.upscale import upscale_img
from src.code_manager import CodeManager
from src.utils import connect_to_shared
from src.settings import IMAGE_OPTIONS, TARGET_SIZE, NUM_SCREENS, SCREEN_MAP, DEFAULT_IMG_PATH, IMG_SHM_NAMES

UPSCALE = True
QR_MONITOR_RES = (1920, 1080)

shared_settings, shared_mem_manager = connect_to_shared()
code_manager = CodeManager()

signal.signal(signal.SIGINT, signal.SIG_DFL)

monitors = get_monitors()
# Filter out QR monitor
display_monitors = [m for m in monitors if m.width != QR_MONITOR_RES[0] and m.height != QR_MONITOR_RES[1]]
# monitors = [m for m in monitors if m.name != 'DP-0']
display_monitors = display_monitors[:NUM_SCREENS]
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


def draw_text_vertically(d: ImageDraw.ImageDraw, text: str, font_size: int = 80,
                         char_padding: int = 10, x=100, start_y=100, fill=(255, 255, 255)):
    # Write text vertically by iterating through characters
    for i, c in enumerate(text):
        d.text(
            (x, font_size * i + char_padding * i + start_y),
            c,
            fill=fill,
            font=ImageFont.truetype('src/robotomono.ttf', font_size)
        )


def draw_text(d: ImageDraw.ImageDraw, text: str, font_size: int = 80,
              x=100, y=100, fill=(255, 255, 255)):
    d.text(
        (x, y),
        text,
        fill=fill,
        font=ImageFont.truetype('src/robotomono.ttf', font_size)
    )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.windows = []
        for i in range(len(display_monitors)):
            print(f'making window {i}')
            ex = App(screen=i, fullscreen=True)
            ex.show()
            self.windows.append(ex)
        self.qr_app = QRCodeApp()


class QRCodeApp(QWidget):
    def __init__(self, screen=None, target_size=(1920, 1080)):
        super().__init__()
        if screen is None:
            # Find the 1080p monitor
            for i, m in enumerate(monitors):
                if m.width == target_size[0] and m.height == target_size[1]:
                    screen = i
                    break
        self.screen = screen
        self.mon = monitors[screen]
        self.w, self.h = self.mon.width, self.mon.height

        self.label = QLabel(self)
        self.initUI()
        self.current_code, self.current_img = self.make_code()

        self.update_image(self.current_img)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_code_changes)
        self.timer.start(250)
        self.show()

    def initUI(self):
        print(self.mon)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setCursor(Qt.CursorShape.BlankCursor)
        self.move(self.mon.x, 0)
        # For some reason full screen doesn't work till you show the window/image first
        self.setGeometry(self.mon.x, self.mon.y, self.mon.width, self.mon.height)

    def make_code(self) -> (str, Image.Image):
        code = code_manager.get_code()
        # Create QR Code image
        # public_url = shared_settings.get('public_url')
        # if public_url is None:
        #     print('No public url set, using default')
        #     public_url = 'http://localhost:5000'
        public_url = 'https://windowsvistas.com'
        full_url = f'{public_url}?code={code}'
        print(f'full url: {full_url}')
        # img = qrcode.make(full_url)
        img = self.make_image(full_url)
        return code, img

    def make_image(self, url):
        img = Image.new('RGB', (self.w, self.h), color=(0, 0, 0))
        d = ImageDraw.Draw(img)

        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=self.h/20)
        qr.add_data(url)
        qr_img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            # fill_color="white", back_color="black"
        )
        qr_img = ImageOps.invert(qr_img)
        # qr_img = qr.make_image(
        #     fill_color="white", back_color="black", module_drawer=RoundedModuleDrawer()
        # )

        # Resize the QR code to fit the banner
        padding = 300
        qr_img.thumbnail((self.h - padding, self.h - padding))
        # Paste the QR code on the right side of the banner
        img.paste(qr_img, (int((self.w - qr_img.width) / 2), padding // 2))

        # draw_text_vertically(d, 'WINDOWS', x=150, start_y=200, font_size=100)
        # draw_text_vertically(d, 'VISTAS', x=450, start_y=200, font_size=100)
        draw_text(d, 'WINDOWS VISTAS', x=300, y=10, font_size=150)
        draw_text(d, 'SCAN TO INTERACT', x=200, y=self.h-220, font_size=150)

        return img

    def check_for_code_changes(self):
        # Check if current code is still unclaimed
        if shared_settings.get('qr_code_needs_change', False):
            # Make a new code
            self.current_code, current_img = self.make_code()
            # And update the image
            self.update_image(current_img)
            # And reset the flag
            shared_settings['qr_code_needs_change'] = False

    def update_image(self, img: Image.Image):
        # Convert to pixmap
        img = img.convert('RGB')
        # img = img.resize((self.w, self.h))
        pixmap = self.array_to_pixmap(np.array(img))
        # Set the pixmap
        self.label.setPixmap(pixmap)
        self.label.adjustSize()
        self.repaint()

    def array_to_pixmap(self, image, resize_to=None, rotate=True) -> QPixmap:
        h, w, ch = image.shape
        bytes_per_line = ch * w
        qimage = QImage(image, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap


class App(QWidget):
    def __init__(self, screen=0, fullscreen=True, w=TARGET_SIZE[0], h=TARGET_SIZE[1]):
        super().__init__()
        self.screen = screen
        self.mon = display_monitors[screen]
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
