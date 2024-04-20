from tkinter import simpledialog, Tk
import tkinter as tk
from tkinter import ttk
import sv_ttk


def ask(current_value: str = '', title: str = 'TPCC', prompt: str = '') -> str:
    token = simpledialog.askstring(title, prompt, initialvalue=current_value)
    return token


class Ask:
    def __init__(self, current_value: str = '', title: str = 'TPCC', prompt: str = ''):
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
