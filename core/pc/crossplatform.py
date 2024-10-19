from mss import mss
from plyer import notification


class PCHandlers:
    def __init__(self, tpc):
        self.tpc = tpc

    async def screenshot(self) -> bytes:
        with mss() as sct:
            return sct.grab(sct.monitors[0])
        
    async def notify(self, title: str, text: str):
        notification.notify(title=title, message=text, timeout=10, app_name=self.tpc.name, app_icon=self.tpc.icon)
    