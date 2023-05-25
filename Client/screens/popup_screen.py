from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog

from screens.utils import Colours


class ManageAccessPopUpWindow:
    def __init__(self, dir_screen_frame, client, file_name, path):
        self.client = client
        self.dir_screen_frame = dir_screen_frame
        self.file_name = file_name
        self.path = path

        self.create_interface()

        self.login_listbox.bind('<Double-Button-1>', self.remove_user)
        self.update()

        self.popup_win.protocol("WM_DELETE_WINDOW", self.popup_win.destroy)
    
    def create_interface(self):
        self.popup_win = Toplevel(self.dir_screen_frame, bg=Colours().black)

        label = Label(self.popup_win, text="Click twice to remove", bg=Colours().black, fg=Colours().white, font=("Calibri", 20), highlightbackground=Colours().red, highlightthickness=1)
        label.pack(side=TOP, fill=X)

        add_button = Button(self.popup_win, text='Add user', bg=Colours().black, fg=Colours().white, font=("Calibri", 20), command=self.add_user)
        add_button.pack(side=TOP, fill=X)

        scrollbar = Scrollbar(self.popup_win, orient= VERTICAL)
        scrollbar.pack(side=RIGHT, fill=BOTH)

        self.login_listbox = Listbox(self.popup_win, selectmode=SINGLE, font=("Calibri", 20), bg=Colours().gray, fg=Colours().white, width=25, height=10, justify=CENTER, selectbackground=Colours().white, selectforeground=Colours().red)
        self.login_listbox.pack()

        self.login_listbox.config(yscrollcommand= scrollbar.set)
        scrollbar.config(command=self.login_listbox.yview)

    def update(self):
        self.client.send_msg(f'access_browse {self.path}')
        answer = self.client.recv_msg()
        answer = answer[7:]
        guest_logins = answer.split()
        # print(guest_logins)
        for login in guest_logins:
            if login:
                self.login_listbox.insert(END, login)

    def add_user(self):
        guest_login = simpledialog.askstring('Give access', "Input guest's login:")
        if len(guest_login) < 8:
            messagebox.showinfo('Error', f"In login must be 8 or more digits.")
        else:
            self.client.send_msg(f'access_give {guest_login}>{self.path}')
            answer = self.client.recv_msg()
            if answer == 'Success':
                messagebox.showinfo('Success', f"You gave {guest_login} access to {self.file_name}")
            else:
                messagebox.showinfo('Error', answer)
            self.popup_win.lift()
            self.login_listbox.delete(0, END)
            self.update()

    def remove_user(self, e):
        choosed_login = self.login_listbox.get(self.login_listbox.curselection())
        question = messagebox.askquestion('Remove access', f'Are you sure you want to remove {choosed_login} access to {self.file_name}')
        if question == 'yes':
            self.client.send_msg(f'access_remove {choosed_login}>{self.path}')
            answer = self.client.recv_msg()
            if answer == 'Success':
                messagebox.showinfo('Success', f"You removed {choosed_login} access to {self.file_name}")
            else:
                messagebox.showinfo('Error', answer)
            self.popup_win.lift()
            self.login_listbox.delete(0, END)
            self.update()