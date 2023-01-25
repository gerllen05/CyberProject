from tkinter import *
from screens.login_screen import LoginScreen
from screens.conts import Colours

class ScreenManager:
    def __init__(self, client):
        self.conn_msgs = client.conn_msgs
        self.conn_files = client.conn_files
        self.client = client

        self.root = Tk()
        self.root.title("Network Drive by Leonid Gerlovin")
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f'{width}x{height}+0+0')
        self.root.resizable(width=True, height=True)
        # root.iconbitmap('icons/Network Drive.ico')
        self.root.configure(bg=Colours().black)

        self.main_frame = Frame(self.root, width=width, height=height, bg=Colours().black)
        self.main_frame.pack()
        self.login_frame = LoginScreen(self.main_frame, client).login_screen_frame
        self.login_frame.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        send(self.conn_msgs, 'exit')
        self.conn_msgs.close()
        self.conn_files.close()
        self.client.FINISHED = True
        self.root.destroy()

def send(conn, msg):
    msg = msg + "|"
    conn.send(msg.encode('utf-8', errors= 'ignore'))

if __name__ == "__main__":
    ScreenManager()


    
