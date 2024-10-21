from mss import mss
from plyer import notification
from PIL import Image
from io import BytesIO
from datetime import datetime
from os import listdir, getcwd, mkdir


class PCHandlers:
    def __init__(self, tpc):
        self.tpc = tpc

    async def screenshot(self):
        with mss() as sct:
            sct_img = sct.grab(sct.monitors[0])
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            with BytesIO() as f:
                img.save(f, format="PNG")
                f.seek(0)
                return f.read()
        
    def notify(self, title: str, text: str):
        self.tpc.logger.info(f'''Sending notification ("{title}","{text}")''')
        notification.notify(title=title, message=text, timeout=10, app_name=self.tpc.name)
    