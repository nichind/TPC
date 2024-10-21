from asyncio import sleep, new_event_loop, create_task, gather
from threading import Thread
from PIL import Image
from PIL.ImageQt import ImageQt
import sys
from datetime import datetime
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QSystemTrayIcon, QApplication, QWidget, QMenu


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, tpc, parent=None):
        self.tpc = tpc
        self.event_play_click = None
        self.event_pause_click = None
        self.event_exit_click = None
        self.is_actived = True

        # QSystemTrayIcon.__init__(self, icon, parent)
        # self.tray = QSystemTrayIcon()
        QSystemTrayIcon.__init__(self)
        self.setIcon(icon)

        menu = QMenu(parent)
        menu.addSeparator()
        self._restart_action = menu.addAction(tpc.tl("TRAY_RESTART"), self.tpc.restart)
        self._exit_action = menu.addAction(tpc.tl("TRAY_EXIT"), self.tpc.exit)

        self.setContextMenu(menu)

        self.activated.connect(self.on_icon_click)
        self.show()

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
            im.seek(0 if im.n_frames == 1 else 1)
            self._icon = SystemTrayIcon(QIcon(QPixmap(ImageQt(im))), self.tpc, self._widget)
        self._icon.event_exit_click = self.on_exit_click        

    def fire_exit_app(self):
        if self.event_exit_app:
            self.event_exit_app(self)

    def on_exit_click(self, sender):
        self.fire_exit_app()
        self.tpc.exit()

    def run_in_loop(self, func):
        """
        Runs the given task in the main loop of the application.

        Args:
            func (typing.Callable): The task to run in the main loop.
        """
        self.tpc.loop.run_until_complete(func)

    async def animate(self):
        """
        Animates the tray icon by setting each frame from the image to the tray icon in sequence, with a delay in between each frame that is calculated based on the duration of the image.

        The duration of the animation is calculated as the total duration of the image divided by the number of frames in the image. The actual delay between frames is then calculated as the duration of the animation divided by the number of frames, minus the time it took to set the previous frame as the tray icon.

        The reason for subtracting the time it took to set the previous frame is to ensure that the animation runs at the correct speed, regardless of how long it takes to set the tray icon.

        The animation runs indefinitely in the background, until the application is closed.
        """
        frames = []
        with Image.open(self.icon_path) as im:
            for i in range(im.n_frames):
                if i == 0:
                    continue
                im.seek(i)
                frames += [im.copy()]
        frame_delay = (im.info['duration'] / im.n_frames)
        while True:
            for i, frame in enumerate(frames):
                self._icon.setIcon(QPixmap(ImageQt(frame)))
                last_frame_at = datetime.now()
                self.tpc.icon = frame
                await sleep(((frame_delay - (datetime.now() - last_frame_at).total_seconds()) * 0.01) - 0.15)

    def run(self):
        """
        Starts the system tray application, sets up necessary components, 
        and begins the event loop. Sends a notification that TPC has started, 
        runs the setup hook and animation tasks in the main thread, and executes 
        the application event loop.
        """
        self.tpc.pc_handlers.notify('TPC', 'TPC started!')
        self.run_in_loop(self.tpc.setup_hook(self.tpc))
        Thread(target=self.run_in_loop, args=(self.animate(),)).start()
        self._app.exec_()
        
