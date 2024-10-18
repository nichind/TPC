from pystray import MenuItem, Menu, Icon


class Tray:
    def __init__(self, icon_path, menu_items):
        self.icon = Icon(icon_path)
        self.menu = Menu(*menu_items)

    async def run(self):
        self.icon.run(self.menu)
