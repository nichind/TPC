from tkinter import simpledialog, Tk


def ask(current_value: str = "", title: str = " TPC", prompt: str = "") -> str:
    return simpledialog.askstring(title, prompt, initialvalue=current_value)
