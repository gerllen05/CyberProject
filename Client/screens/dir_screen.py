from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk
import os

from screens.conts import Colours
from screens.conts import SpecialCharacters
from screens.edit_screen import EditScreen

class DirScreen:
    def __init__(self, main_frame, client, login_screen_frame):
        self.main_frame = main_frame
        self.client = client
        self.conn_msgs = client.conn_msgs
        self.conn_files = client.conn_files
        self.login_screen_frame = login_screen_frame

        self.dir_screen_frame = Frame(main_frame, bg=Colours().black)

        top_panel = Frame(self.dir_screen_frame, bg=Colours().gray, highlightbackground=Colours().red, highlightthickness=1)
        top_panel.pack(pady=(10, 5))

        update_button = Button(top_panel, text='Update', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.update_dirs)
        update_button.grid(row=0, column=0, padx=10, pady=10)
        previous_dir__button = Button(top_panel, text='Previous directory', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.previous_dir)
        previous_dir__button.grid(row=0, column=1, padx=10, pady=10)
        logout_button = Button(top_panel, text='Give access', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.give_access)
        logout_button.grid(row=0, column=2, padx=10, pady=10)
        logout_button = Button(top_panel, text='Manage access', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.manage_access)
        logout_button.grid(row=0, column=3, padx=10, pady=10)
        logout_button = Button(top_panel, text='Logout', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.log_out)
        logout_button.grid(row=0, column=4, padx=10, pady=10)

        top_panel2 = Frame(self.dir_screen_frame, bg=Colours().gray, highlightbackground=Colours().red, highlightthickness=1)
        top_panel2.pack(pady=(0,10))

        delete_button = Button(top_panel2, text='Delete', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.delete_item)
        delete_button.grid(row=1, column=0, padx=10, pady=10)
        create_folder_button = Button(top_panel2, text='Create new folder', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.create_folder)
        create_folder_button.grid(row=1, column=1, padx=10, pady=10)
        create_file_button = Button(top_panel2, text='Create new file', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.create_file)
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
        self.path += self.dir_listbox.get(self.dir_listbox.curselection())
        self.path_label.configure(text='Path: '+self.path)
        if not self.path.endswith('.txt'):
            self.path += '/'
            self.update_dirs() # when click on folders
        else:
            self.get_file() # when click on files

    def get_file(self):
        self.send(self.conn_msgs, 'open ' + self.path)
        file_bytes = b""
        while True:
            data = self.conn_files.recv(self.client.SIZE)
            file_bytes += data
            if file_bytes[-5:] == b"<END>":
                file_bytes = file_bytes[:-5]
                break
            elif file_bytes[-6:] == b"<FAIL>":
                messagebox.showinfo('Failed', "There is no such file, press UPDATE button and try again.")
                current_len = len(self.path.split('/')[-1])
                self.path = self.path[:len(self.path) - current_len]
                self.path_label.configure(text='Path: '+self.path)
                return
        print(f"File '{self.path}' finished downloading...")
        file_data = file_bytes.decode(self.client.FORMAT)
        self.go_to_edit_screen(file_data)
        
    def update_dirs(self):
        self.send(self.conn_msgs, 'dir ' + self.path)
        dir_string = self.conn_msgs.recv(self.client.SIZE).decode(self.client.FORMAT, errors= 'ignore')
        dir_list = dir_string[4:].split()
        self.dir_listbox.delete(0, END)
        for dir in dir_list:
            if dir:
                self.dir_listbox.insert(END, dir)

    def previous_dir(self):
        if not self.path:
            messagebox.showinfo('Error', "You are already in home directory.")
        else:
            current_len = len(self.path.split('/')[-2])
            self.path = self.path[:len(self.path) - current_len - 1]
            self.path_label.configure(text='Path: '+self.path)
            self.update_dirs()

    def give_access(self):
        file_name = self.dir_listbox.get(self.dir_listbox.curselection())
        path = self.path + file_name
        if not path.endswith('.txt'):
            messagebox.showinfo('Error', "It is not possible to give access to a folder, only to files.")
        elif not self.path.split('/')[0] == self.client.login:
            messagebox.showinfo('Error', "This is not your file. \nYou are not allowed to give access to it.")
        else:
            guest_login = simpledialog.askstring('Give access', "Input guest's login:")
            if len(guest_login) < 8:
                 messagebox.showinfo('Error', f"In login must be 8 or more digits.")
            else:
                self.send(self.conn_msgs, f'access_give {guest_login}>{path}')
                answer = self.conn_msgs.recv(self.client.SIZE).decode(self.client.FORMAT, errors= 'ignore')
                if answer == 'Success':
                    messagebox.showinfo('Success', f"You gave {guest_login} access to {file_name}")
                else:
                    messagebox.showinfo('Error', answer)

    def manage_access(self):
        file_name = self.dir_listbox.get(self.dir_listbox.curselection())
        path = self.path + file_name
        if not path.endswith('.txt'):
            messagebox.showinfo('Error', "It is not possible manage folder access, only files.")
        elif not self.path.split('/')[0] == self.client.login:
            messagebox.showinfo('Error', "This is not your file. \nYou are not allowed to manage access to it.")
        else:
            popup_win = Toplevel(self.dir_screen_frame, bg=Colours().black)

            label = Label(popup_win, text="Click twice to remove", bg=Colours().gray, fg=Colours().white, font=("Calibri", 20), highlightbackground=Colours().red, highlightthickness=1)
            label.pack(side=TOP, fill=X)

            scrollbar = Scrollbar(popup_win, orient= VERTICAL)
            scrollbar.pack(side=RIGHT, fill=BOTH)

            login_listbox = Listbox(popup_win, selectmode=SINGLE, font=("Calibri", 20), bg=Colours().gray, fg=Colours().white, width=25, height=10, justify=CENTER, selectbackground=Colours().white, selectforeground=Colours().red)
            login_listbox.pack()

            login_listbox.config(yscrollcommand= scrollbar.set)
            scrollbar.config(command=login_listbox.yview)

            def login_chooser(e):
                choosed_login = login_listbox.get(login_listbox.curselection())
                question = messagebox.askquestion('Remove access', f'Are you sure you want to remove {choosed_login} access to {file_name}')
                if question == 'yes':
                    self.send(self.conn_msgs, f'access_remove {choosed_login}>{path}')
                    answer = self.conn_msgs.recv(self.client.SIZE).decode(self.client.FORMAT, errors= 'ignore')
                    if answer == 'Success':
                        messagebox.showinfo('Success', f"You removed {choosed_login} access to {file_name}")
                    else:
                        messagebox.showinfo('Error', answer)
                    popup_win.destroy()

            login_listbox.bind('<Double-Button-1>', login_chooser)

            self.send(self.conn_msgs, f'access_browse {path}')
            answer = self.conn_msgs.recv(self.client.SIZE).decode(self.client.FORMAT, errors= 'ignore')
            answer = answer[7:]
            guest_logins = answer.split()
            print(guest_logins)
            for login in guest_logins:
                if login:
                    login_listbox.insert(END, login)

    def log_out(self):
        self.send(self.conn_msgs, f"log_out")
        self.dir_screen_frame.destroy()
        self.login_screen_frame.pack()

    def delete_item(self):
        if not self.path:
            messagebox.showinfo('Error', "You are not allowed to delete other users folder.")
        elif not self.path.split('/')[0] == self.client.login:
            messagebox.showinfo('Error', "This is not your folder or file. \nYou are not allowed to delete it.")
        else:
            item = self.dir_listbox.get(self.dir_listbox.curselection())
            answer = messagebox.askquestion('Delete', f'Are you sure you want to delete "{item}"')
            if answer == 'yes':
                item_path = f'{self.path}{item}'
                self.send(self.conn_msgs, 'delete ' + item_path)
                messagebox.showinfo('Deleted', "Press UPDATE button to stop seeing it in the list.")

    def create_folder(self):
        if not self.path:
            messagebox.showinfo('Error', "You are not allowed to create anything in this folder.")
        elif not self.path.split('/')[0] == self.client.login:
            messagebox.showinfo('Error', "This is not your folder. \nYou are not allowed to create new folders here.")
        else:
            name = simpledialog.askstring('Create folder', "Input folder name:")
            if any(c in (SpecialCharacters().special_characters) for c in name):
                messagebox.showinfo('Error', f"You can't use special characters: {SpecialCharacters().special_characters}")
            elif name.endswith('.txt'):
                messagebox.showinfo('Error', f"Folder name can't end with '.txt'")
            else:
                self.send(self.conn_msgs, f'create_folder {self.path}/{name}')
                messagebox.showinfo('New folder created', f"Press UPDATE button to see it.")

    def create_file(self):
        if not self.path:
            messagebox.showinfo('Error', "You are not allowed to create anything in this folder.")
        elif not self.path.split('/')[0] == self.client.login:
            messagebox.showinfo('Error', "This is not your folder. \nYou are not allowed to create new files here.")
        else:
            name = simpledialog.askstring('Create file', "Input file name:")
            if any(c in (SpecialCharacters().special_characters) for c in name):
                messagebox.showinfo('Error', f"You can't use special characters: {SpecialCharacters().special_characters}")
            elif name.endswith('.txt'):
                messagebox.showinfo('Error', f"You don't have to write extension here it will be added by itself.")
            else:
                name += ".txt"
                self.send(self.conn_msgs, f'create_file {self.path}/{name}')
                messagebox.showinfo('New file created', f"Press UPDATE button to see it.")

    def go_to_edit_screen(self, file_data):
        self.dir_screen_frame.pack_forget()
        EditScreen(self.main_frame, self.client, self, file_data).edit_screen_frame.pack()

    def send(self, conn, msg):
        msg = msg + "|"
        conn.send(msg.encode(self.client.FORMAT, errors= 'ignore'))

def add_placeholder(entry, placeholder):
    def click(event):
        entry.delete(0, END)
        entry.unbind("<Button-1>")

    entry.insert(0, placeholder)
    entry.bind("<Button-1>", click)
