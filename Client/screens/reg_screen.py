from tkinter import *
from tkinter import messagebox

from screens.utils import Colours, CustomButton, Utils

class RegScreen:
    def __init__(self, main_frame, client, login_screen_frame):
        self.main_frame = main_frame
        self.client = client
        self.login_screen_frame = login_screen_frame

        self.reg_screen_frame = Frame(main_frame, bg=Colours().black)
        self.create_interface()

    def create_interface(self):
        header = Label(self.reg_screen_frame, text="Network Drive", bg=Colours().black, fg=Colours().red, font=("Gabriola", 100))
        header.pack()

        frame = Frame(self.reg_screen_frame, bg=Colours().gray, highlightbackground=Colours().red, highlightthickness=1)
        frame.pack()

        subheader = Label(frame, text='Register new account:', bg=Colours().gray, fg=Colours().white, font=("Calibri", 50))
        subheader.grid(row=0, column=0)

        self.login = StringVar()
        login_input = Entry(frame, textvariable=self.login, bg=Colours().gray, fg=Colours().white, font=("Calibri", 50))
        Utils().add_placeholder(login_input, 'Enter login')
        login_input.grid(row=1, column=0, padx=20, pady=10)
        self.password = StringVar()
        password_input = Entry(frame, textvariable=self.password, bg=Colours().gray, fg=Colours().white, font=("Calibri", 50))
        Utils().add_placeholder(password_input, 'Enter password')
        password_input.grid(row=2, column=0, padx=20, pady=10)
        self.password_check = StringVar()
        password_check_input = Entry(frame, textvariable=self.password_check, bg=Colours().gray, fg=Colours().white, font=("Calibri", 50))
        Utils().add_placeholder(password_check_input, 'Enter password again')
        password_check_input.grid(row=3, column=0, padx=20, pady=10)

        submit_button = CustomButton(frame, text='Register', command=self.submit).button
        submit_button.grid(row=4, column=0, pady=10)

        login_label = Label(self.reg_screen_frame, text="You already have an account?", bg=Colours().black, fg=Colours().red, font=("Calibri", 30))
        login_label.pack(pady=(50,0))
        login_button = CustomButton(self.reg_screen_frame, text='Log in', command=self.go_to_login_screen).button
        login_button.pack()

    def submit(self):
        login = self.login.get()
        password = self.password.get()
        password_check = self.password_check.get()
        if not password == password_check:
            messagebox.showinfo('Invalid data', 'The second password is not equal first.')
        elif len(login) < 8 and len(password) < 8 or any(c in (Utils().special_characters) for c in login+password):
            messagebox.showinfo('Invalid data', 'In login and password must be 8 or more digits.')
        else:
            self.client.send_msg(f"reg {login} {password}")
            answer = self.client.recv_msg()
            if not answer == "online":
                messagebox.showinfo('Error', answer)
            else:
                print("Successefuly registered.")
                messagebox.showinfo('Successefuly registered', f'Your login: {login} \nYour password: {password}')
                self.go_to_login_screen()
    
    def go_to_login_screen(self):
        self.reg_screen_frame.pack_forget()
        self.login_screen_frame.pack()
