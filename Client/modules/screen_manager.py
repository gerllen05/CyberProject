from tkinter import *
from threading import enumerate
from time import sleep

from screens.login_screen import LoginScreen
from screens.utils import Colours
from screens.utils import Utils

class ScreenManager:
    def __init__(self, client):
        self.conn_msgs = client.conn_msgs
        self.conn_files = client.conn_files
        self.client = client
        self.finished = False

        Utils().create_thread(self.get_input_thread)

        try:
            self.root = Tk()
            self.root.title("Network Drive by Leonid Gerlovin")
            width = self.root.winfo_screenwidth()
            height = self.root.winfo_screenheight()
            self.root.geometry(f'{width}x{height}+0+0')
            self.root.resizable(width=True, height=True)
            self.root.iconbitmap('D:/usr/documents/Desktop/Школа/י1/Cyber/CyberProject/Client/icons/Network Drive.ico')
            self.root.configure(bg=Colours().black)
            

            self.main_frame = Frame(self.root, width=width, height=height, bg=Colours().black)
            self.main_frame.pack()
            self.login_frame = LoginScreen(self.main_frame, client).login_screen_frame
            self.login_frame.pack()

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
            self.send(self.conn_msgs, "log_out")
            self.send(self.conn_msgs, "exit")
            self.conn_msgs.close()
            self.conn_files.close()
        except:
            print("Server is closed.")

    def get_input_thread(self):
        while True:
            msg = input()
            if msg == "exit": 
                self.on_closing()
            elif msg == "threads":
                print(f"\nActive threads: {enumerate()}")
            elif msg == "help":
                print("Here are all available commands:")
                print("- exit --> disconnects all clients and closes server")
                print("- threads --> shows all threads")
                print("- help --> shows all available commands")
            else:
                print(f"Incorrect command '{msg}': type 'help' to see all commands")

    def send(self, conn, msg):
        msg = msg + "|"
        conn.send(msg.encode(self.client.FORMAT, errors= 'ignore'))

if __name__ == "__main__":
    ScreenManager()


    
