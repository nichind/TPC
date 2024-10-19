from asyncio import sleep, new_event_loop, create_task
from threading import Thread
from PIL import Image
from PIL.ImageQt import ImageQt
import sys
from datetime import datetime
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QSystemTrayIcon, QApplication, QWidget, QMenu


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        self.event_play_click = None
        self.event_pause_click = None
        self.event_exit_click = None
        self.is_actived = True

        # QSystemTrayIcon.__init__(self, icon, parent)
        # self.tray = QSystemTrayIcon()
        QSystemTrayIcon.__init__(self)
        self.setIcon(icon)

        menu = QMenu(parent)
        self._play_action = menu.addAction("Play", self.on_play_click)
        self._pause_action = menu.addAction("Pause", self.on_pause_click)
        menu.addSeparator()
        self._exit_action = menu.addAction("Exit", self.on_exit_click)

        self.setContextMenu(menu)

        self.activated.connect(self.on_icon_click)
        self.show()

    def on_play_click(self):
        self.fire_play_click()
        self.setIcon(QIcon("./t.svg"))  
        print("Play clicked")

    def on_pause_click(self):
        self.fire_pause_click()
        self.setIcon(QIcon("./t.svg"))
        print("Pause clicked")

    def on_exit_click(self):
        self.fire_exit_click()
        print("Exit clicked")
        

    def on_icon_click(self, reason):
        print(reason)

    def fire_play_click(self):
        if self.event_play_click:
            self.event_play_click(self)

    def fire_pause_click(self):
        if self.event_pause_click:
            self.event_pause_click(self)

    def fire_exit_click(self):
        if self.event_exit_click:
            self.event_exit_click(self)
        

class Tray:
    def __init__(self, tpc):
        self.icon_path = "./assets/ico.gif"
        self.tpc = tpc        
        self.event_exit_app = None

        self._app = QApplication(sys.argv)
        self._widget = QWidget()
        with Image.open(self.icon_path) as im:
            im.seek(0)
            self._icon = SystemTrayIcon(QIcon(QPixmap(ImageQt(im))), self._widget)
        self._icon.event_exit_click = self.on_exit_click        

    def fire_exit_app(self):
        if self.event_exit_app:
            self.event_exit_app(self)

    def on_exit_click(self, sender):
        self.fire_exit_app()
        self.tpc.exit()

    async def animate(self):
        frames = []
        with Image.open(self.icon_path) as im:
            for i in range(im.n_frames):
                if i == 0:
                    continue
                im.seek(i)
                frames += [im.copy()]
        frame_delay = (im.info['duration'] / im.n_frames)
        while True:
            print(im.n_frames, im.info['duration'])
            for i, frame in enumerate(frames):
                self._icon.setIcon(QPixmap(ImageQt(frame)))
                last_frame_at = datetime.now()
                self.tpc.icon = frame
                await sleep(((frame_delay - (datetime.now() - last_frame_at).total_seconds()) * 0.01) - 0.15)

    async def run(self):
        self._app.exec()
        
