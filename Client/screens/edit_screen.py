from tkinter import *
from tkinter import messagebox
from time import sleep

from screens.utils import Colours, CustomButton, Utils

class EditScreen:
    def __init__(self, main_frame, client, DirScreen, file_data):
        self.main_frame = main_frame
        self.client = client
        self.dir_screen = DirScreen
        self.last_file_data = file_data
        self.being_changed = False
        self.close = False

        self.edit_screen_frame = Frame(main_frame, bg=Colours().black)

        self.create_interface()
        Utils().create_thread(self.get_file_thread)
        Utils().create_thread(self.send_file_when_changed_thread)

    def create_interface(self):
        top_panel = Frame(self.edit_screen_frame, bg=Colours().gray, highlightbackground=Colours().red, highlightthickness=1)
        top_panel.pack(pady=10)

        update_button = CustomButton(top_panel, text='Save and exit', command=self.save_and_exit).button
        update_button.grid(row=0, column=0, padx=10, pady=10)

        scrollbar = Scrollbar(self.edit_screen_frame, orient= VERTICAL)
        scrollbar.pack(side=RIGHT, fill=BOTH)

        self.data_input = Text(self.edit_screen_frame, bg=Colours().gray, fg=Colours().white, font=("Calibri", 20), width=70, height=25)
        self.data_input.insert( "1.0", self.last_file_data)
        self.data_input.pack()

        self.data_input.config(yscrollcommand= scrollbar.set)
        scrollbar.config(command=self.data_input.yview)

    def save_and_exit(self):
        self.client.send_msg('stop')

    def delete_file(self):
        self.close = True
        self.client.send_msg('stop')
        if not self.dir_screen.path:
            messagebox.showinfo('Error', "You are not allowed to delete other users folder.")
        elif not self.dir_screen.path.split('/')[0] == self.client.login:
            messagebox.showinfo('Error', "This is not your folder or file. \nYou are not allowed to delete it.")
        else:
            answer = messagebox.askquestion('Delete', f'Are you sure you want to delete this file?')
            if answer == 'yes':
                self.client.send_msg('delete ' + self.dir_screen.path)
                messagebox.showinfo('File deleted', "You will be transfered back to directory screen.")
        self.go_to_dir_screen()

    def get_file_thread(self):
        while not self.close:
            msg = self.client.recv_msg()
            if msg[:4] == "stop":
                # print("Stopped using file")
                self.close = True
                if len(msg) > 5:
                    new_path = msg[5:]
                    self.go_to_dir_screen(new_path)
                else:
                    self.go_to_dir_screen()
                return
            elif msg[:4] == "file":
                self.being_changed = True
                size = int(msg[5:])
                file_data = self.client.recv_file(size)

                self.last_file_data = file_data
                self.data_input.delete("1.0","end")
                self.data_input.insert( "1.0", file_data)
                self.being_changed = False
                # print(File finished downloading)

    def send_file_when_changed_thread(self):
        while not self.close:
            if not self.being_changed:
                data = self.data_input.get("1.0",'end')
                if data:
                    data = data[:-1]
                if not data == self.last_file_data:
                    # print("File started sending...")
                    self.last_file_data = data
                    self.client.send_file(data)
            sleep(0.01)

    def go_to_dir_screen(self, new_path=""):
        self.edit_screen_frame.destroy()
        if new_path:
            self.dir_screen.path = new_path
        else:
            current_len = len(self.dir_screen.path.split('/')[-1])
            self.dir_screen.path = self.dir_screen.path[:len(self.dir_screen.path) - current_len]

        self.dir_screen.update_dirs()
        self.dir_screen.path_label.configure(text='Path: '+self.dir_screen.path)
        self.dir_screen.dir_screen_frame.pack()
