from mss import mss
from plyer import notification
from PIL import Image
from io import BytesIO
from datetime import datetime
from os import listdir, getcwd, mkdir
from pynput.keyboard import KeyCode, Controller


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
        """
        Show a notification with the given title and text.

        Args:
            title (str): The title of the notification.
            text (str): The text of the notification.
        """
        self.tpc.logger.info(f'''Sending notification ("{title}","{text}")''')
        notification.notify(title=title, message=text, timeout=10, app_name=self.tpc.name, app_icon=self.tpc.static_icon)
    
    def press(self, key: str):
        """
        Press a given key on the keyboard.

        Args:
            key (str): The key to press. If the key is a combination of keys (e.g. "ctrl&alt&del"), split them by "&" and provide the VK codes as strings (e.g. "17&18&46")
        """
        keyboard = Controller()
        if '&' in key:
            for key in key.split('&'):
                keyboard.press(KeyCode.from_vk(int(key, 0)))
        else:
            keyboard.press(KeyCode.from_vk(int(key, 0)))
    