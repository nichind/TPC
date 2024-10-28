import dbus 


class PCHandlers:
    def __init__(self, tpc):
        self.tpc = tpc
    
    async def on_startup(self):
        pass

    async def on_shutdown(self):
        pass

    async def get_playing_media(self):
        bus = dbus.SessionBus()
        for service in bus.list_names():
            if service.startswith('org.mpris.MediaPlayer2.'):
                media_player = bus.get_object(service, '/org/mpris/MediaPlayer2')
                interface = dbus.Interface(media_player, dbus_interface='org.freedesktop.DBus.Properties')
                metadata = interface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
                if metadata:
                    info_dict = {
                        'artist': metadata.get('xesam:artist')[0] if 'xesam:artist' in metadata else None,
                        'title': metadata.get('xesam:title') if 'xesam:title' in metadata else None,
                        'artUrl': metadata.get('mpris:artUrl') if 'mpris:artUrl' in metadata else None
                    }
                    return info_dict

    async def lock(self):
        # Lock the desktop using the dbus interface
        bus = dbus.SessionBus()
        obj = bus.get_object('org.gnome.ScreenSaver', '/org/gnome/ScreenSaver')
        interface = dbus.Interface(obj, dbus_interface='org.gnome.ScreenSaver')
        interface.Lock()
