import asyncio
from tkinter import simpledialog, Tk
import flet as ft
from threading import Thread
from aiogram import Bot
import os
import getpass
from pathlib import Path
from PIL import ImageTk, Image
import io
import webbrowser


class App:
    def __init__(self, *args):
        self.page = None

    def run(self, page: ft.Page):
        self.page = page
        self.settings()

    def refresh(self):
        self.page.clean()
        left = ft.Column(
            spacing=24,
            height=999
        )

        menu = ft.Column(
            width=101,
            spacing=12,
        )

        menu.controls.append(ft.TextButton(text='Settings'))
        menu.controls.append(ft.TextButton(text='Logs'))
        menu.controls.append(ft.TextButton(text='Links'))

        left.controls.append(ft.Text("TPCC", size=22))
        left.controls.append(menu)

        self.page.add(left)

    def settings(self):
        self.refresh()

        title = ft.Text('Settings', )
        self.page: ft.Page


ft.app(App().run)
