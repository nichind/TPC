from asyncio import (
    get_event_loop,
    run_coroutine_threadsafe,
)
from threading import Thread
from PIL import Image
from PIL.ImageQt import ImageQt
import sys
from json import loads, dumps
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QWidget,
)
from PySide6.QtCore import Signal, QObject, QTimer
from AsyncioPySide6 import AsyncioPySide6
from webbrowser import open as webopen
from .ui import ask
from core.util.database import Setting
import core


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
        self.change_token_action = self._bot_menu.addAction(
            self.tpc.tl("TRAY_SETTING_BOT_CHANGETOKEN")
        )
        self.change_token_action.triggered.connect(self.change_token)

        self.add_user_action = self._bot_menu.addAction(
            self.tpc.tl("TRAY_SETTING_BOT_ADDUSER")
        )
        self.add_user_action.triggered.connect(self.add_user)

        self.deauth_all_users_action = self._bot_menu.addAction(
            self.tpc.tl("TRAY_SETTING_BOT_DEAUTHALLUSERS")
        )
        self.deauth_all_users_action.triggered.connect(self.deauth_all_users)

        self._boot_menu_checkbox_action = self.menu.addAction(
            self.tpc.tl("TRAY_SETTING_STARTONBOOT")
        )
        self._boot_menu_checkbox_action.triggered.connect(self.toggle_on_boot)
        self._boot_menu_checkbox_action.setCheckable(True)

        self._restart_bot_action = self._bot_menu.addAction(
            tpc.tl("TRAY_RESTART_BOT"), self.tpc.restart_bot
        )

        menu.addSeparator()

        if (
            "python" in sys.executable.split("\\")[-1]
            or "python" in sys.executable.split("/")[-1]
        ):
            self._restart_action = menu.addAction(
                tpc.tl("TRAY_RESTART"), self.tpc.restart
            )
        self._exit_action = menu.addAction(tpc.tl("TRAY_EXIT"), self.tpc.exit)

        self.setContextMenu(menu)

        self.activated.connect(self.on_icon_click)
        self.show()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(1500)

    def toggle_on_boot(self, checked):
        if checked:
            self.tpc.pc_handlers.add_to_boot()
        else:
            self.tpc.pc_handlers.remove_from_boot()
        self.tpc.loop.run_until_complete(
            Setting.update(key="start_on_boot", value=checked)
        )

    def refresh(self):
        async def _():
            self.bot_info.triggered.disconnect()
            if self.tpc.bot:
                self._restart_bot_action.setEnabled(True)
                self.bot_info.triggered.connect(
                    lambda x: webopen(
                        "https://t.me/{}".format(self.tpc.bot.chached_me["username"])
                    )
                )
                self.bot_info.setText(
                    self.tpc.tl("TRAY_SETTING_BOT_LOGGED").format(
                        **self.tpc.bot.chached_me
                    )
                )
            else:
                self._restart_bot_action.setEnabled(False)
                self.bot_info.triggered.connect(
                    lambda x: webopen("https://t.me/nichindpf")
                )
                self.bot_info.setText(self.tpc.tl("TRAY_SETTING_BOT_NOTLOGGED"))

            on_boot = (await Setting.get(key="start_on_boot")).value
            self._boot_menu_checkbox_action.setChecked(on_boot == "1")

        AsyncioPySide6.runTask(_())

    def change_token(self):
        token = ask(
            title=self.tpc.tl("TRAY_SETTING_BOT_CHANGETOKEN_TITLE"),
            prompt=self.tpc.tl("TRAY_SETTING_BOT_CHANGETOKEN_PROMPT"),
        )
        if not token:
            return

        async def stop():
            loop = get_event_loop()
            loop.stop()

        self.tpc.run_in_loop(Setting.update(key="bot_token", value=token))
        if self.tpc.bot_thread.is_alive():
            run_coroutine_threadsafe(stop(), self.tpc.bot_loop)
            self.tpc.bot_loop = None
        self.tpc.bot_thread = Thread(target=self.tpc.restart_bot)
        self.tpc.bot_thread.start()

    def add_user(self):
        async def _():
            user_id = ask(
                title=self.tpc.tl("TRAY_SETTING_BOT_ADDUSER_TITLE"),
            )
            if not user_id:
                return

            if user_id.isdigit() is False:
                return self.tpc.pc_handlers.notify(
                    "TPC", self.tpc.tl("TRAY_SETTING_BOT_ADDUSER_INVALID")
                )

            users = await Setting.get(key="user_ids")
            if users is None or users.value is None:
                users.value = "[]"
            users = loads(users.value)

            print(user_id)
            user_id = int(user_id)
            if user_id in users:
                users.remove(user_id)
            else:
                users.append(user_id)
            await Setting.update(key="user_ids", value=dumps(users))

        AsyncioPySide6.runTask(_())

    def deauth_all_users(self):
        async def _():
            await Setting.update(key="user_ids", value="[]")

        AsyncioPySide6.runTask(_())

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
            self._icon = SystemTrayIcon(
                QIcon(QPixmap(ImageQt(im))), self.tpc, self._widget
            )
        self.tpc.run_in_loop = self.run_in_loop

        # Add title on hover for tray
        self._icon.setToolTip(
            self.tpc.tl("TRAY_TITLE").format(version=self.tpc.version)
        )

        self.frame_changed.connect(self._icon.setIcon)

        self.frames = []
        with Image.open(self.icon_path) as im:
            for i in range(im.n_frames):
                if i == 0:
                    continue
                im.seek(i)
                self.frames.append(QPixmap(ImageQt(im.copy())))

            im.seek(0)
            im.save(core.resource_path("icon.ico"), format="ICO")
            self.tpc.static_icon = core.resource_path("icon.ico")

            self.frame_delay = im.info["duration"] / im.n_frames
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
        self.tpc.bot_thread = Thread(target=self.tpc.restart_bot)
        self.tpc.bot_thread.start()
        with AsyncioPySide6.use_asyncio():
            self._app.exec()
