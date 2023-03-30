from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

from screens.utils import Colours, Utils
from screens.utils import CustomButton
from screens.reg_screen import RegScreen
from screens.dir_screen import DirScreen

class LoginScreen:
    def __init__(self, main_frame, client):
        self.main_frame = main_frame
        self.client = client

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

        self.login = StringVar() # admin: adminadmin
        login_input = Entry(frame, textvariable=self.login, bg=Colours().gray, fg=Colours().white, font=("Calibri", 50))
        Utils().add_placeholder(login_input, 'Enter login') 
        login_input.grid(row=1, column=0, padx=20, pady=10)

        self.password = StringVar() # admin: a9@sdf8$98
        self.password_input = Entry(frame, textvariable=self.password, bg=Colours().gray, fg=Colours().white, font=("Calibri", 50))
        Utils().add_placeholder(self.password_input, 'Enter password', is_password=True) 
        self.password_input.grid(row=2, column=0, padx=20, pady=10)

        self.checkbutton = CustomButton(frame, text='Show password', command=self.show_password, checkbutton=True).button
        self.checkbutton.grid(row=3, column=0, padx=20, pady=10)

        submit_button = CustomButton(frame, text='Log in', command=self.submit_method).button
        submit_button.grid(row=4, column=0, pady=10)

        reg_label = Label(self.login_screen_frame, text="You don't have an account?", bg=Colours().black, fg=Colours().red, font=("Calibri", 30))
        reg_label.pack(pady=(100,0))
        reg_button = CustomButton(self.login_screen_frame, text='Register', command=self.go_to_reg_screen).button
        reg_button.pack()

    def show_password(self):
        if self.password.get() == "Enter password":
            self.checkbutton.deselect()
        elif self.password_input.cget("show") == '*':
            self.password_input.config(show='')
        else:
            self.password_input.config(show='*')

    def submit_method(self):
        login = self.login.get()
        password = self.password.get()
        if login and password:
            self.client.send_msg(f"log_in {login} {password}")
            answer = self.client.recv_msg()
            if answer == "online":
                print("Successefuly logged in.")
                messagebox.showinfo('Successefuly logged in', f'Your login: {login} \nYour password: {password}')
                self.client.login = login
                self.go_to_dir_screen()
            else:
                messagebox.showinfo('Error', answer)
        else:
            messagebox.showinfo('Invalid data', 'In login and password must be 8 or more digits.')

    def go_to_dir_screen(self):
        self.login_screen_frame.pack_forget()
        DirScreen(self.main_frame, self.client, self.login_screen_frame).dir_screen_frame.pack()

    def go_to_reg_screen(self):
        self.login_screen_frame.pack_forget()
        RegScreen(self.main_frame, self.client, self.login_screen_frame).reg_screen_frame.pack()

if __name__ == "__main__":
    root = Tk()
    launch = LoginScreen(root, "")
    root.mainloop()
