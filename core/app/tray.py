from asyncio import sleep, new_event_loop, create_task, gather, get_event_loop, run_coroutine_threadsafe
from threading import Thread
from io import BytesIO
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
from json import loads
from .ui import ask
from ..util import *

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, tpc, parent=None):
        super().__init__(icon, parent)
        self.tpc = tpc
        self.is_actived = True

        menu = QMenu(parent)
        self.menu = menu

        self._bot_menu = menu.addMenu(tpc.tl("TRAY_BOT"))
    
        self.bot_info = self._bot_menu.addAction("Loading...")
        self._bot_menu.addSeparator()
        self.change_token_action = self._bot_menu.addAction(self.tpc.tl("TRAY_SETTING_BOT_CHANGETOKEN"))
        self.change_token_action.triggered.connect(self.change_token)
    
        self._boot_menu_checkbox_action = self.menu.addAction(self.tpc.tl("TRAY_SETTING_STARTONBOOT"))
        self._boot_menu_checkbox_action.triggered.connect(self.toggle_on_boot)
        self._boot_menu_checkbox_action.setCheckable(True)
        
        self._restart_bot_action = self._bot_menu.addAction(tpc.tl("TRAY_RESTART_BOT"), self.tpc.restart_bot)
    
        menu.addSeparator()

        if 'python' in sys.executable.split('\\')[-1] or 'python' in sys.executable.split('/')[-1]:
            self._restart_action = menu.addAction(tpc.tl("TRAY_RESTART"), self.tpc.restart)
        self._exit_action = menu.addAction(tpc.tl("TRAY_EXIT"), self.tpc.exit)

        self.setContextMenu(menu)

        self.activated.connect(self.on_icon_click)
        self.show()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(900)

    def toggle_on_boot(self, checked):
        if checked:
            self.tpc.pc_handlers.add_to_boot()
        else:
            self.tpc.pc_handlers.remove_from_boot()
        self.tpc.loop.run_until_complete(Setting.update(key='start_on_boot', value=checked))

    def refresh(self):
        self.bot_info.triggered.disconnect()
        if self.tpc.bot:
            self._restart_bot_action.setEnabled(True)
            self.bot_info.triggered.connect(lambda x: webopen("https://t.me/{}".format(self.tpc.bot.chached_me['username'])))
            self.bot_info.setText(self.tpc.tl("TRAY_SETTING_BOT_LOGGED").format(**self.tpc.bot.chached_me))
        else:
            self._restart_bot_action.setEnabled(False)
            self.bot_info.triggered.connect(lambda x: webopen("https://t.me/nichindpf"))
            self.bot_info.setText(self.tpc.tl("TRAY_SETTING_BOT_NOTLOGGED"))
        
        on_boot = (self.tpc.loop.run_until_complete(Setting.get(key='start_on_boot'))).value
        self._boot_menu_checkbox_action.setChecked(on_boot == '1')


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

class Tray(QObject):
    frame_changed = Signal(QPixmap)

    def __init__(self, tpc):
        super().__init__()
        self.icon_path = tpc.icon_path
        self.tpc = tpc    
        self.tpc.run_in_loop = self.run_in_loop    

        self._app = QApplication(sys.argv)
        self._widget = QWidget()
        
        # self._widget.setStyleSheet("""
        #     background-color: #000000 
        # """)
        
        with Image.open(self.icon_path) as im:
            im.seek(0 if im.n_frames == 1 else 1)
            self._icon = SystemTrayIcon(QIcon(QPixmap(ImageQt(im))), self.tpc, self._widget)        
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

            im.seek(0)
            im.save(resource_path('icon.ico'), format="ICO")
            self.tpc.static_icon = resource_path('icon.ico')

            self.frame_delay = im.info['duration'] / im.n_frames
            self.frame_delay = self.frame_delay * 10
            
        self.current_frame = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(int(self.frame_delay))

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
        self.tpc.restart_bot()
        # self.tpc.bot_thread = Thread(target=self.tpc.restart_bot)
        # self.tpc.bot_thread.start()
        self._app.exec()



