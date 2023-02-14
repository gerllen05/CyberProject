from tkinter import font
from threading import Thread

class Colours:
    def __init__(self):
        self.black = '#1A1A1D'
        self.gray = '#4E4E50'
        self.white = '#D1D7E0'
        self.red = '#C3073F'

class Utils:
    def __init__(self):
        self.special_characters = "!@#$%^&*() +?=,<>/"

    def create_thread(self, thread_function, args=(), daemon_state='True', name_extra='', start='True'):
        new_thread = Thread(target=thread_function, args=args)
        new_thread.daemon = daemon_state
        if not name_extra:
            new_thread.name = thread_function.__name__
        else:
            new_thread.name = thread_function.__name__ + " " + name_extra
        if start:
            new_thread.start()
        return new_thread
    
    def add_placeholder(self, entry, placeholder):
        def click(event):
            entry.delete(0, 'end')
            entry.unbind("<Button-1>")

        entry.insert(0, placeholder)
        entry.bind("<Button-1>", click)