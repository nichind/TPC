import time
import pystray
from PIL import Image


def cycle(tray: pystray.Icon, gif_path: str, delay: float = 0.2):
    while True:
        with Image.open(gif_path) as im:
            for i in range(im.n_frames):
                im.seek(i)
                tray.icon = im
                time.sleep(delay)
