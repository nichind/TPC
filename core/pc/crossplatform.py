from mss import mss
from plyer import notification
from PIL import Image
from io import BytesIO
from pynput.keyboard import KeyCode, Controller


class PCHandlers:
    def __init__(self, tpc):
        self.tpc = tpc

    async def screenshot(self) -> BytesIO:
        self.tpc.logger.info("Taking screenshot")
        with mss() as sct:
            sct_img = sct.grab(sct.monitors[0])
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            img_io = BytesIO()
            img.save(img_io, "PNG")
            img_io.seek(0)
        self.tpc.logger.info("Screenshot taken")
        return img_io

    def notify(self, title: str, text: str):
        """
        Show a notification with the given title and text.

        Args:
            title (str): The title of the notification.
            text (str): The text of the notification.
        """
        self.tpc.logger.info(f"""Sending notification ("{title}","{text}")""")
        notification.notify(
            title=title,
            message=text,
            timeout=10,
            app_name=self.tpc.name,
            app_icon=self.tpc.static_icon,
        )

    async def press(self, key: str):
        """
        Press a given key on the keyboard.

        Args:
            key (str): The key to press. If the key is a combination of keys (e.g. "ctrl&alt&del"), split them by "&" and provide the VK codes as strings (e.g. "17&18&46")
        """
        self.tpc.logger.info(f'Pressing key "{key}"')
        try:
            keyboard = Controller()
            if "&" in key:
                for key in key.split("&"):
                    keyboard.tap(KeyCode.from_vk(int(key, 0)))
                    # keyboard.press(KeyCode.from_vk(int(key, 0)))
            else:
                keyboard.tap(KeyCode.from_vk(int(key, 0)))
                # keyboard.press(KeyCode.from_vk(int(key, 0)))
            keyboard.release_all()
        except Exception as exc:
            self.tpc.logger.exception(f'Failed to press key "{key}": {exc}')
