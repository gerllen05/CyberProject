from tkinter import *
from threading import enumerate
from time import sleep

from modules.client import Client
from screens.login_screen import LoginScreen
from screens.utils import Colours
from screens.utils import Utils

class ScreenManager:
    def __init__(self):
        self.finished = False
        self.client = Client()

        Utils().create_thread(self.get_input_thread)

        try:
            self.root = Tk()
            self.root.title("Network Drive by Leonid Gerlovin")
            width = self.root.winfo_screenwidth()
            height = self.root.winfo_screenheight()
            self.root.geometry(f'{width}x{height}+0+0')
            self.root.resizable(width=True, height=True)
            self.root.configure(bg=Colours().black)

            LoginScreen(self.root, self.client).login_screen_frame.pack()  

            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()

            while not self.finished:      
                sleep(0.1)

            print(f"Client disconnected.")
        except Exception as e:
            print(e)
            self.on_closing()

    def on_closing(self):
        self.root.destroy()
        self.finished = True
        try:
            self.client.send_msg("log_out")
            self.client.send_msg("exit")
            self.client.conn_msgs.close()
            self.client.conn_files.close()
        except:
            print("Server was closed")

    def get_input_thread(self):
        while True:
            msg = input()
            if msg == "exit": 
                self.on_closing()
            elif msg == "threads":
                print(f"\nActive threads: {enumerate()}")
            elif msg == "close":
                self.on_closing()
            elif msg == "help":
                print("Here are all available commands:")
                print("- exit --> disconnects all clients and closes server")
                print("- threads --> shows all threads")
                print("- close --> closes client with logging out")
                print("- help --> shows all available commands")
            else:
                print(f"Incorrect command '{msg}': type 'help' to see all commands")

if __name__ == "__main__":
    ScreenManager()


    
