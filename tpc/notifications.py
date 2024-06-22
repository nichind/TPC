from plyer.utils import platform
from plyer import notification


def notify(message: str = 'Message', title: str = 'Notification', app_name: str = 'TPC', app_icon: str = './ico.ico'):
    notification.notify(
        title=title,
        message=message,
        app_name=app_name,
        app_icon=app_icon
    )
