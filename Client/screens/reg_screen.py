from tkinter import *
from tkinter import messagebox
from screens.conts import Colours
from PIL import Image, ImageTk

class RegScreen:
    def __init__(self, main_frame, client, login_screen_frame):
        self.main_frame = main_frame
        self.conn = client.conn_msgs
        self.login_screen_frame = login_screen_frame

        self.reg_screen_frame = Frame(main_frame, bg=Colours().black)

        # logo = PhotoImage(file = 'utils/Network Drive.png')
        # logo_label = Label(root, image=logo)
        # logo_label.place(x=500, y=500, relwidth=0.3, relheight=0.3)

        header = Label(self.reg_screen_frame, text="Network Drive", bg=Colours().black, fg=Colours().red, font=("Gabriola", 100))
        header.pack()

        frame = Frame(self.reg_screen_frame, bg=Colours().gray, highlightbackground=Colours().red, highlightthickness=1)
        frame.pack()

        subheader = Label(frame, text='Register new account:', bg=Colours().gray, fg=Colours().white, font=("Calibri", 50))
        subheader.grid(row=0, column=0)

        self.login = StringVar()
        login_input = Entry(frame, textvariable=self.login, bg=Colours().gray, fg=Colours().white, font=("Calibri", 50))
        add_placeholder(login_input, 'Enter login')
        login_input.grid(row=1, column=0, padx=20, pady=10)
        self.password = StringVar()
        password_input = Entry(frame, textvariable=self.password, bg=Colours().gray, fg=Colours().white, font=("Calibri", 50))
        add_placeholder(password_input, 'Enter password')
        password_input.grid(row=2, column=0, padx=20, pady=10)

        submit_button = Button(frame, text='Register', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.submit)
        submit_button.grid(row=3, column=0, pady=10)

        empty = Label(self.reg_screen_frame, text="", bg=Colours().black, fg=Colours().red, font=("Calibri", 30))
        empty.pack(pady=40)
        login_label = Label(self.reg_screen_frame, text="You already have an account?", bg=Colours().black, fg=Colours().red, font=("Calibri", 30))
        login_label.pack()
        login_button = Button(self.reg_screen_frame, text='Log In', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.go_to_login_screen)
        login_button.pack()

    def submit(self):
        login = self.login.get()
        password = self.password.get()
        if len(login) > 7 and len(password) > 7:
            send(self.conn, f"reg {login} {password}")
            messagebox.showinfo('Successefuly registered', f'Your login: {login} \nYour password: {password}')
            self.go_to_login_screen()
        else:
            messagebox.showinfo('Invalid data', 'In login and password must be 8 or more digits.')
    
    def go_to_login_screen(self):
        self.reg_screen_frame.pack_forget()
        self.login_screen_frame.pack()

def add_placeholder(entry, placeholder):
    def click(event):
        entry.delete(0, END)

    entry.insert(0, placeholder)
    entry.bind("<Button-1>", click)

def send(conn, msg):
    msg = msg + "|"
    conn.send(msg.encode('utf-8', errors= 'ignore'))



