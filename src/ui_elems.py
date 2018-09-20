import tkinter as tk
from tkinter import ttk

class Button(ttk.Button):
    '''TTK Button with simplified constructor'''
    def __init__(self, parent, style, text, command, c_args=None, **kwargs):
        if c_args is None: bind = command
        else: bind = lambda: command(c_args)
        super().__init__(parent, style=style, text=text, command=bind, **kwargs)
