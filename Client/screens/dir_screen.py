from tkinter import *
from tkinter import messagebox
from screens.conts import Colours
# from conts import Colours
from PIL import Image, ImageTk
import time

class DirScreen:
    def __init__(self, main_frame, client, login_screen_frame):
        self.main_frame = main_frame
        self.client = client
        self.conn = client.conn_msgs
        self.login_screen_frame = login_screen_frame

        self.dir_screen_frame = Frame(main_frame, bg=Colours().black)

        top_panel = Frame(self.dir_screen_frame, bg=Colours().gray, highlightbackground=Colours().red, highlightthickness=1)
        top_panel.pack(pady=10)
        header = Label(top_panel, text="Your directories:", bg=Colours().gray, fg=Colours().red, font=("Calibri", 30))
        header.grid(row=0, column=0)
        update_button = Button(top_panel, text='Update', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.update_dirs)
        update_button.grid(row=0, column=1, padx=10, pady=10)
        create_button = Button(top_panel, text='Create new folder', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.create_folder)
        create_button.grid(row=0, column=2, padx=10, pady=10)
        logout_button = Button(top_panel, text='Logout', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.go_to_login_screen)
        logout_button.grid(row=0, column=3, padx=10, pady=10)
        # delete_button = Button(top_panel, text='Delete folder', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.delete_folder)
        # delete_button.grid(row=0, column=1, padx=10)

        dirs_frame = Frame(self.dir_screen_frame, bg=Colours().gray, highlightbackground=Colours().red, highlightthickness=1)
        dirs_frame.pack()
        # dirs_frame.propagate(False)
        # dirs_frame.columnconfigure(0, weight=10)

        self.dir_listbox = Listbox(dirs_frame, selectmode=SINGLE, bg=Colours().gray, width=150)
        self.dir_listbox.pack()
        self.path = ''
        self.update_dirs()
        self.dir_listbox.bind('<ButtonRelease-1>', self.dir_chooser)
        

    def dir_chooser(self, e):
        self.path += self.dir_listbox.get(self.dir_listbox.curselection())
        self.update_dirs()

    def update_dirs(self):
        send(self.conn, 'dir ' + self.path)
        time.sleep(0.1)
        for dir in self.client.DIR_LIST:
            self.dir_listbox.insert('end', dir)

    def create_folder(self):
        pass
    
    def go_to_login_screen(self):
        self.dir_screen_frame.pack_forget()
        self.login_screen_frame.pack()

def add_placeholder(entry, placeholder):
    def click(event):
        entry.delete(0, END)

    entry.insert(0, placeholder)
    entry.bind("<Button-1>", click)

def send(conn, msg):
    msg = msg + "|"
    conn.send(msg.encode('utf-8', errors= 'ignore'))

if __name__ == "__main__":
    root = Tk()
    root.title("Network Drive by Leonid Gerlovin")
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f'{width}x{height}+0+0')
    root.resizable(width=True, height=True)
    # root.iconbitmap('icons/Network Drive.ico')
    root.configure(bg=Colours().black)

    main_frame = Frame(root, width=width, height=height, bg=Colours().black)
    main_frame.pack()
    dir_frame = DirScreen(main_frame, '', '').dir_screen_frame
    dir_frame.pack()

    root.mainloop()