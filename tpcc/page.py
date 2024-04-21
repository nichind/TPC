import asyncio
from tkinter import simpledialog, Tk
import tkinter as tk
from tkinter import ttk
from .db import SettingsManagement, UserManagement
import sv_ttk
from threading import Thread
from aiogram import Bot
import os
import getpass
from pathlib import Path


def ask(current_value: str = '', title: str = ' TPCC', prompt: str = '') -> str:
    token = simpledialog.askstring(title, prompt, initialvalue=current_value)
    return token


class Ask:
    def __init__(self, current_value: str = '', title: str = ' TPCC', prompt: str = ''):
        self.current_value = current_value
        self.title = title
        self.prompt = prompt
        self.result = None

    def fancy(self, show: bool = True):
        def _return():
            self.result = entry.get()
            return root.destroy()

        root = tk.Tk(className=self.title)
        root.geometry('350x130')
        title = ttk.Label(root, text=self.prompt)
        title.pack(side='top', pady=12)
        entry = ttk.Entry(root, width=280)
        if show:
            entry.insert(0, string=self.current_value)
        else:
            entry.insert(0, string=f'''{"*" * (len(self.current_value) - 2)}{self.current_value[-3:-1]}''')
        entry.pack(pady=0)
        send = ttk.Button(text='Ok', command=_return)
        send.pack(pady=12)

        sv_ttk.set_theme("dark")
        root.mainloop()

        if self.result == f'''{"*" * (len(self.current_value) - 2)}{self.current_value[-3:-1]}''':
            self.result = self.current_value
        return self.result if self.result != '' else self.fancy(show)


class App:
    def __init__(self, *args):
        self.title = ' TPCC'
        self.geometry = '350x230'
        self.current_page = 'main'
        self.root = tk.Tk(className=self.title)
        self.root.geometry(self.geometry)
        Thread(target=self.main).start()
        self.mainloop()

    def mainloop(self):
        self.root.mainloop()

    def clear(self):
        for ele in self.root.winfo_children():
            ele.destroy()
        sv_ttk.set_theme("dark")

    def settings(self):
        self.clear()

        def change_token():
            SettingsManagement.update(1, bot_token=token_entry.get())
            self.settings()

        username = getpass.getuser()

        def change_password():
            SettingsManagement.update(1, password=password_entry.get())
            for user in asyncio.run(UserManagement.get_all()):
                asyncio.run(UserManagement.update(user.user_id, access=False))

        def add_to_boot():
            file_path = os.getcwd()
            bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % username
            with open(bat_path + '\\' + "tpcc.bat", "w+") as bat_file:
                bat_file.write(r'start /MIN "" %s' % f'{file_path}/run_build.bat')
            self.settings()

        def remove_from_boot():
            os.remove(r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\tpcc.bat' % username)
            self.settings()

        settings = SettingsManagement.get(1)

        bot_title = ttk.Label(self.root, text="Bot token")
        bot_title.grid(row=0, column=0, sticky="W", padx=8, pady=8)
        token_entry = ttk.Entry(self.root)
        token_entry.insert(0, string=f'''{"*" * (len(settings.bot_token) - 2)}{settings.bot_token[-3:-1]}''')
        token_entry.grid(row=1, column=0, padx=8)

        apply_token = ttk.Button(text='Apply', command=change_token)
        apply_token.grid(row=1, column=1)

        bot = Bot(settings.bot_token)
        logged_as = ttk.Label(self.root, text=f"Connected as @{asyncio.run(bot.get_me())['username']}", font=(None, 8))
        logged_as.grid(row=2, column=0, sticky="W", padx=8, pady=2)
        asyncio.run((asyncio.run(bot.get_session())).close())

        password_title = ttk.Label(self.root, text="Bot password")
        password_title.grid(row=3, column=0, sticky="W", padx=8, pady=8)
        password_entry = ttk.Entry(self.root)
        password_entry.insert(0, string=f'''{"*" * (len(settings.password) - 2)}{settings.password[-3:-1]}''')
        password_entry.grid(row=4, column=0, padx=8)

        apply_password = ttk.Button(text='Apply', command=change_password)
        apply_password.grid(row=4, column=1)

        if Path(r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\tpcc.bat' % username).is_file():
            boot_button = ttk.Button(text='remove from Windows boot', command=remove_from_boot)
        else:
            boot_button = ttk.Button(text='add to Windows boot', command=add_to_boot)
        boot_button.grid(row=5, column=0, padx=8, pady=8)

        back = ttk.Button(text='Back', command=self.main)
        back.place(anchor='center', relx=.9, rely=.1)

    def links(self):
        self.clear()

        text = ttk.Label(self.root, text='discord.gg/nichind\nt.me/nichindpf', font=('', 12))
        text.pack(anchor='center', pady=0)

        back = ttk.Button(text='Back', command=self.main)
        back.place(anchor='center', relx=.9, rely=.1)

    def main(self):
        self.clear()
        title = ttk.Label(self.root, text='TPCC', font=('', 24))
        title.pack(side='top', pady=12)
        desc = ttk.Label(self.root, text='discord.gg/nichind\n    t.me/nichindpf', font=('', 12))
        desc.pack(side='top', pady=0)
        settings = ttk.Button(text='Settings', command=self.settings)
        settings.place(anchor='center', relx=.4, rely=.7)
        links = ttk.Button(text='Links', command=self.links)
        links.place(anchor='center', relx=.6, rely=.7)
