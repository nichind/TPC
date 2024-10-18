from mss import mss
from plyer import notification


class PCHandler:
    def __init__(self, icon):
        self.icon = icon

    async def screenshot(self) -> bytes:
        with mss() as sct:
            return sct.grab(0)
        
    async def notify(self, title: str, text: str):
        notification.notify(title=title, message=text, timeout=10, app_name=self.icon.name, app_icon=self.icon.icon)
    