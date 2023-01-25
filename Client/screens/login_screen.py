from tkinter import *
from screens.conts import Colours
from PIL import Image, ImageTk
from screens.reg_screen import RegScreen
from screens.dir_screen import DirScreen

class LoginScreen:
    def __init__(self, main_frame, client):
        self.main_frame = main_frame
        self.client = client
        self.conn = client.conn_msgs

        self.login_screen_frame = Frame(main_frame, bg=Colours().black)

        # logo = PhotoImage(file = 'utils/Network Drive.png')
        # logo_label = Label(root, image=logo)
        # logo_label.place(x=500, y=500, relwidth=0.3, relheight=0.3)

        header = Label(self.login_screen_frame, text="Network Drive", bg=Colours().black, fg=Colours().red, font=("Gabriola", 100))
        header.pack()

        frame = Frame(self.login_screen_frame, bg=Colours().gray, highlightbackground=Colours().red, highlightthickness=1)
        frame.pack()

        subheader = Label(frame, text='Log in to your account:', bg=Colours().gray, fg=Colours().white, font=("Calibri", 50))
        subheader.grid(row=0, column=0)

        self.login = StringVar()
        login_input = Entry(frame, textvariable=self.login, bg=Colours().gray, fg=Colours().white, font=("Calibri", 50))
        add_placeholder(login_input, 'Enter login')
        login_input.grid(row=1, column=0, padx=20, pady=10)
        self.password = StringVar()
        password_input = Entry(frame, textvariable=self.password, bg=Colours().gray, fg=Colours().white, font=("Calibri", 50))
        add_placeholder(password_input, 'Enter password')
        password_input.grid(row=2, column=0, padx=20, pady=10)

        submit_button = Button(frame, text='Log In', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.submit_method)
        submit_button.grid(row=3, column=0, pady=10)

        empty = Label(self.login_screen_frame, text="", bg=Colours().black, fg=Colours().red, font=("Calibri", 30))
        empty.pack(pady=40)
        reg_label = Label(self.login_screen_frame, text="You don't have an account?", bg=Colours().black, fg=Colours().red, font=("Calibri", 30))
        reg_label.pack()
        reg_button = Button(self.login_screen_frame, text='Register', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.go_to_reg_screen)
        reg_button.pack()

    def submit_method(self):
        login = self.login.get()
        password = self.password.get()
        send(self.conn, f"log in {login} {password}")
        # go to directory screen
        self.login_screen_frame.pack_forget()
        DirScreen(self.main_frame, self.client, self.login_screen_frame).dir_screen_frame.pack()

    def go_to_reg_screen(self):
        self.login_screen_frame.pack_forget()
        RegScreen(self.main_frame, self.client, self.login_screen_frame).reg_screen_frame.pack()

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
    launch = LoginScreen(root, "")
    root.mainloop()


