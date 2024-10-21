from asyncio import sleep, new_event_loop, create_task, gather, get_event_loop, run_coroutine_threadsafe
from threading import Thread
from PIL import Image
from PIL.ImageQt import ImageQt
import sys
from datetime import datetime
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QStatusBar,
    QSystemTrayIcon, QMenu, QCheckBox,
    QWidget
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, QSize, Signal, QObject, QTimer
from webbrowser import open as webopen
from time import sleep as tsleep
from .ask import ask
from ..util import *

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, tpc, parent=None):
        super().__init__(icon, parent)
        self.tpc = tpc
        self.event_play_click = None
        self.event_pause_click = None
        self.event_exit_click = None
        self.is_actived = True

        menu = QMenu(parent)

        self._bot_menu = menu.addMenu(tpc.tl("TRAY_BOT"))

        if tpc.bot:
            bot_info = self._bot_menu.addAction(tpc.tl("TRAY_SETTING_BOT_LOGGED").format(**tpc.bot.chached_me))
            bot_info.triggered.connect(lambda x: webopen("https://t.me/" + tpc.bot.chached_me.username))
        else:
            bot_info = self._bot_menu.addAction(tpc.tl("TRAY_SETTING_BOT_NOTLOGGED"))
        self._bot_menu.addSeparator()
        change_token_action = self._bot_menu.addAction(tpc.tl("TRAY_SETTING_BOT_CHANGETOKEN"))
        change_token_action.triggered.connect(self.change_token)

        menu.addSeparator()

        self._restart_action = menu.addAction(tpc.tl("TRAY_RESTART"), self.tpc.restart)
        self._exit_action = menu.addAction(tpc.tl("TRAY_EXIT"), self.tpc.exit)

        self.setContextMenu(menu)

        self.activated.connect(self.on_icon_click)
        self.show()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_bot_info)
        self.refresh_timer.start(2000)

    def refresh_bot_info(self):
        self._bot_menu.clear()
        if self.tpc.bot:
            bot_info = self._bot_menu.addAction(self.tpc.tl("TRAY_SETTING_BOT_LOGGED").format(**self.tpc.bot.chached_me))
            bot_info.triggered.connect(lambda x: webopen("https://t.me/" + self.tpc.bot.chached_me.username))
        else:
            bot_info = self._bot_menu.addAction(self.tpc.tl("TRAY_SETTING_BOT_NOTLOGGED"))
        self._bot_menu.addSeparator()
        change_token_action = self._bot_menu.addAction(self.tpc.tl("TRAY_SETTING_BOT_CHANGETOKEN"))
        change_token_action.triggered.connect(self.change_token)

    def change_token(self):
        token = ask(
            title=self.tpc.tl("TRAY_SETTING_BOT_CHANGETOKEN_TITLE"),
            prompt=self.tpc.tl("TRAY_SETTING_BOT_CHANGETOKEN_PROMPT")
        )
        if not token:
            return
        
        async def stop():
            loop = get_event_loop()
            loop.stop()
        
        self.tpc.run_in_loop(Setting.update(key='bot_token', value=token))
        if self.tpc.bot_thread.is_alive():       
            run_coroutine_threadsafe(stop(), self.tpc.bot_loop)
            self.tpc.bot_loop = None
        self.tpc.bot_thread = Thread(target=self.tpc.restart_bot)
        self.tpc.bot_thread.start()

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

class Tray(QObject):
    frame_changed = Signal(QPixmap)

    def __init__(self, tpc):
        super().__init__()
        self.icon_path = tpc.icon_path
        self.tpc = tpc        
        self.event_exit_app = None

        self._app = QApplication(sys.argv)
        self._widget = QWidget()
        with Image.open(self.icon_path) as im:
            im.seek(0 if im.n_frames == 1 else 1)
            self._icon = SystemTrayIcon(QIcon(QPixmap(ImageQt(im))), self.tpc, self._widget)
        self._icon.event_exit_click = self.on_exit_click        
        self.tpc.run_in_loop = self.run_in_loop

        # Add title on hover for tray
        self._icon.setToolTip(self.tpc.tl('TRAY_TITLE').format(version=self.tpc.version))
        
        self.frame_changed.connect(self._icon.setIcon)

        self.frames = []
        with Image.open(self.icon_path) as im:
            for i in range(im.n_frames):
                if i == 0:
                    continue
                im.seek(i)
                self.frames.append(QPixmap(ImageQt(im.copy())))

        self.current_frame = 0
        self.frame_delay = im.info['duration'] / im.n_frames
        self.frame_delay = self.frame_delay * 10
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(int(self.frame_delay))

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

    def animate(self):
        self.current_frame += 1
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
        self.frame_changed.emit(self.frames[self.current_frame])


    def run(self):
        """
        Starts the system tray application, sets up necessary components, 
        and begins the event loop. Sends a notification that TPC has started, 
        runs the setup hook and animation tasks in the main thread, and executes 
        the application event loop.
        """
        self.run_in_loop(self.tpc.setup_hook(self.tpc))
        self.tpc.bot_thread = Thread(target=self.tpc.restart_bot)
        self.tpc.bot_thread.start()
        self._app.exec()


