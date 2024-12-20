import ctypes
import locale
from ..util.database import Setting
from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaManager,
)
from getpass import getuser
from os import remove, system, path
import sys


class PCHandlers:
    def __init__(self, tpc):
        self.tpc = tpc

    async def on_startup(self):
        self.tpc.logger.info("Hello Windows!")
        if (await Setting.get(key="language")).value is None:
            windll = ctypes.windll.kernel32
            language = locale.windows_locale[windll.GetUserDefaultUILanguage()]
            await Setting.update(key="language", value=language[:2].upper())

    async def on_shutdown(self):
        pass

    def add_to_boot(self):
        try:
            bat_path = (
                r"C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
                % getuser()
            )
            with open(bat_path + "\\" + "tpc.bat", "w+") as bat_file:
                bat_file.write(f"start {sys.executable} {sys.argv[0]}")
            self.tpc.logger.info("Added TPC to boot.")
        except Exception as exc:
            self.tpc.logger.exception(exc)

    def remove_from_boot(self):
        try:
            remove(
                r"C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\tpc.bat"
                % getuser()
            )
            self.tpc.logger.info("Removed TPC from boot.")
        except Exception as exc:
            self.tpc.logger.exception(exc)

    def check_autostart(self) -> bool:
        return path.exists(
            r"C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\tpc.bat"
            % getuser()
        )

    async def get_playing_media(self) -> dict | None:
        """
        Get the currently playing media.

        This function will use the Windows Media Session Manager to get the currently playing media.
        It will then parse the media properties and return a dictionary containing the following
        items:

        - title: The title of the media
        - artist: The artist of the media
        - album_artist: The album artist of the media
        - album_title: The album title of the media
        - genres: A list of genres of the media
        - track_number: The track number of the media

        If no media is currently playing, this function will return None.
        """
        sessions = await MediaManager.request_async()
        current_session = sessions.get_current_session()
        info = await current_session.try_get_media_properties_async()
        if info:
            if info.thumbnail:
                pass
            info_dict = {
                song_attr: info.__getattribute__(song_attr)
                for song_attr in dir(info)
                if song_attr[0] != "_"
            }
            info_dict["genres"] = list(info_dict["genres"])
            return info_dict
        return None

    async def lock(self) -> None:
        self.tpc.logger.info("Locking PC...")
        system("rundll32.exe user32.dll,LockWorkStation")
