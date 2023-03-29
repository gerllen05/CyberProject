from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk

from screens.utils import Colours, CustomButton, Utils
from screens.edit_screen import EditScreen

class DirScreen:
    def __init__(self, main_frame, client, login_screen_frame):
        self.main_frame = main_frame
        self.client = client
        self.login_screen_frame = login_screen_frame

        self.dir_screen_frame = Frame(main_frame, bg=Colours().black)

        top_panel = Frame(self.dir_screen_frame, bg=Colours().gray, highlightbackground=Colours().red, highlightthickness=1)
        top_panel.pack(pady=(10, 5))

        update_button = CustomButton(top_panel, text='Update', command=self.update_dirs).button
        update_button.grid(row=0, column=0, padx=10, pady=10)
        previous_dir__button = CustomButton(top_panel, text='Previous directory', command=self.previous_dir).button
        previous_dir__button.grid(row=0, column=1, padx=10, pady=10)
        access_button = CustomButton(top_panel, text='Manage access', command=self.manage_access).button
        access_button.grid(row=0, column=3, padx=10, pady=10)
        logout_button = CustomButton(top_panel, text='Logout', command=self.log_out).button
        logout_button.grid(row=0, column=4, padx=10, pady=10)
        delete_account_button = CustomButton(top_panel, text='Delete account', command=self.delete_account, bg=Colours().red, activebackground=Colours().red).button
        delete_account_button.grid(row=0, column=5, padx=10, pady=10)

        top_panel2 = Frame(self.dir_screen_frame, bg=Colours().gray, highlightbackground=Colours().red, highlightthickness=1)
        top_panel2.pack(pady=(0,10))

        delete_item_button = CustomButton(top_panel2, text='Delete', command=self.delete_item).button
        delete_item_button.grid(row=1, column=0, padx=10, pady=10)
        create_folder_button = CustomButton(top_panel2, text='Create new folder', command=self.create_folder).button
        create_folder_button.grid(row=1, column=1, padx=10, pady=10)
        create_file_button = CustomButton(top_panel2, text='Create new file', command=self.create_file).button
        create_file_button.grid(row=1, column=2, padx=10, pady=10)
        
        dirs_frame = Frame(self.dir_screen_frame, bg=Colours().gray)
        dirs_frame.pack()

        scrollbar = Scrollbar(dirs_frame, orient= VERTICAL)
        scrollbar.pack(side=RIGHT, fill=BOTH)

        self.path = ''
        self.dir_listbox = Listbox(dirs_frame, selectmode=SINGLE, font=("Calibri", 20), bg=Colours().gray, fg=Colours().white, width=50, height=20, justify=CENTER, selectbackground=Colours().white, selectforeground=Colours().red)
        self.dir_listbox.pack()

        self.dir_listbox.config(yscrollcommand= scrollbar.set)
        scrollbar.config(command=self.dir_listbox.yview)

        self.update_dirs()
        self.dir_listbox.bind('<Double-Button-1>', self.dir_chooser)

        self.path_label = Label(self.dir_screen_frame, text='Path: '+self.path, bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), highlightbackground=Colours().white, highlightthickness=1)
        self.path_label.pack(pady=10)

        
    def dir_chooser(self, e):
        self.path += str(self.dir_listbox.get(self.dir_listbox.curselection()))
        if not self.path.endswith('.txt'):
            self.path += '/'
            self.path_label.configure(text='Path: '+self.path)
            self.update_dirs() # when click on folders
        else:
            self.get_file() # when click on files

    def get_file(self):
        self.client.send_msg('open ' + self.path)
        try:
            msg = self.client.recv_msg()
            if msg[:4] == "file":
                size = int(msg[5:])
                file_data = self.client.recv_file(size)
                self.go_to_edit_screen(file_data)
        except Exception as e:
            print(e)
            messagebox.showinfo('Failed', "There is no such file, press UPDATE button and try again.")
            current_len = len(self.path.split('/')[-1])
            self.path = self.path[:len(self.path) - current_len]
            self.path_label.configure(text='Path: '+self.path)
            return
        
    def update_dirs(self):
        self.client.send_msg('dir ' + self.path)
        dir_string = self.client.recv_msg()
        dir_list = dir_string[4:].split()
        self.dir_listbox.delete(0, END)
        for dir in dir_list:
            if dir:
                self.dir_listbox.insert(END, dir)

    def previous_dir(self):
        if not self.path:
            messagebox.showinfo('Error', "You are already in home directory.")
        elif self.path.count('/') == 0:
            self.path = ''
        else:
            current_len = len(self.path.split('/')[-2])
            self.path = self.path[:len(self.path) - current_len - 1]
            self.path_label.configure(text='Path: '+self.path)
            self.update_dirs()

    def manage_access(self):
        file_name = self.dir_listbox.get(self.dir_listbox.curselection())
        path = self.path + file_name
        if not path.endswith('.txt'):
            messagebox.showinfo('Error', "It is not possible manage folder access, only files.")
        elif not self.path.split('/')[0] == self.client.login:
            messagebox.showinfo('Error', "This is not your file. \nYou are not allowed to manage access to it.")
        else:
            ManageAccessPopUpWindow(self.dir_screen_frame, self.client, file_name, path)

    def log_out(self):
        self.client.send_msg(f"log_out")
        self.dir_screen_frame.destroy()
        self.login_screen_frame.pack()

    def delete_account(self):
        answer = messagebox.askquestion('Delete', f'Are you sure you want to delete your account?')
        if answer == 'yes':
            self.client.send_msg(f"delete_account {self.client.login}")
            self.dir_screen_frame.destroy()
            self.login_screen_frame.pack()

    def delete_item(self):
        if not self.path:
            messagebox.showinfo('Error', "You are not allowed to delete other users folder.")
        elif not self.path.split('/')[0] == self.client.login:
            messagebox.showinfo('Error', "This is not your folder or file. \nYou are not allowed to delete it.")
        else:
            item = self.dir_listbox.get(self.dir_listbox.curselection())
            answer = messagebox.askquestion('Delete', f'Are you sure you want to delete "{item}"?')
            if answer == 'yes':
                item_path = f'{self.path}{item}'
                msg = 'delete_'
                if not item_path.endswith('.txt'):
                    msg += f'folder {item_path}/'
                else:
                    msg += f'file {item_path}'
                self.client.send_msg(msg)
                self.update_dirs()

    def create_folder(self):
        if not self.path:
            messagebox.showinfo('Error', "You are not allowed to create anything in this folder.")
        elif not self.path.split('/')[0] == self.client.login:
            messagebox.showinfo('Error', "This is not your folder. \nYou are not allowed to create new folders here.")
        else:
            name = simpledialog.askstring('Create folder', "Input folder name:")
            if any(c in (Utils().special_characters) for c in name):
                messagebox.showinfo('Error', f"You can't use special characters: {Utils().special_characters}")
            elif name.endswith('.txt'):
                messagebox.showinfo('Error', f"Folder name can't end with '.txt'")
            else:
                self.client.send_msg(f'create_folder {self.path}/{name}')
                self.update_dirs()

    def create_file(self):
        if not self.path:
            messagebox.showinfo('Error', "You are not allowed to create anything in this folder.")
        elif not self.path.split('/')[0] == self.client.login:
            messagebox.showinfo('Error', "This is not your folder. \nYou are not allowed to create new files here.")
        else:
            name = simpledialog.askstring('Create file', "Input file name:")
            if any(c in (Utils().special_characters) for c in name):
                messagebox.showinfo('Error', f"You can't use special characters: {Utils().special_characters}")
            elif name.endswith('.txt'):
                messagebox.showinfo('Error', f"You don't have to write extension here, it will be added by itself.")
            else:
                name += ".txt"
                self.client.send_msg(f'create_file {self.path}{name}')
                self.update_dirs()

    def go_to_edit_screen(self, file_data):
        self.dir_screen_frame.pack_forget()
        EditScreen(self.main_frame, self.client, self, file_data).edit_screen_frame.pack()


class ManageAccessPopUpWindow:
    def __init__(self, dir_screen_frame, client, file_name, path):
        self.client = client
        self.dir_screen_frame = dir_screen_frame
        self.file_name = file_name
        self.path = path

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

        self.login_listbox.bind('<Double-Button-1>', self.remove_user)
        self.update()

        self.popup_win.protocol("WM_DELETE_WINDOW", self.popup_win.destroy)

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
