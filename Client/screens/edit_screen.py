from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from time import sleep
import os
import threading

from screens.conts import Colours

class EditScreen:
    def __init__(self, main_frame, client, DirScreen, file_data):
        self.main_frame = main_frame
        self.client = client
        self.conn_msgs = client.conn_msgs
        self.conn_files = client.conn_files
        self.dir_screen = DirScreen
        self.last_file_data = file_data
        self.being_changed = False
        self.close = False

        self.edit_screen_frame = Frame(main_frame, bg=Colours().black)

        top_panel = Frame(self.edit_screen_frame, bg=Colours().gray, highlightbackground=Colours().red, highlightthickness=1)
        top_panel.pack(pady=10)

        update_button = Button(top_panel, text='Save and exit', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.save_and_exit)
        update_button.grid(row=0, column=0, padx=10, pady=10)
        # create_button = Button(top_panel, text='Delete file', bg=Colours().gray, fg=Colours().white, font=("Calibri", 30), command=self.delete_file)
        # create_button.grid(row=0, column=1, padx=10, pady=10)

        scrollbar = Scrollbar(self.edit_screen_frame, orient= VERTICAL)
        scrollbar.pack(side=RIGHT, fill=BOTH)

        self.data_input = Text(self.edit_screen_frame, bg=Colours().gray, fg=Colours().white, font=("Calibri", 20), width=70, height=25)
        self.data_input.insert( "1.0", file_data)
        self.data_input.pack()

        self.data_input.config(yscrollcommand= scrollbar.set)
        scrollbar.config(command=self.data_input.yview)

        create_thread(self.get_file)
        create_thread(self.send_file_when_changed)

    def save_and_exit(self):
        self.send(self.conn_msgs, 'stop')

    def delete_file(self):
        self.close = True
        self.send(self.conn_msgs, 'stop')
        if not self.dir_screen.path:
            messagebox.showinfo('Error', "You are not allowed to delete other users folder.")
        elif not self.dir_screen.path.split('/')[0] == self.client.login:
            messagebox.showinfo('Error', "This is not your folder or file. \nYou are not allowed to delete it.")
        else:
            answer = messagebox.askquestion('Delete', f'Are you sure you want to delete this file?')
            if answer == 'yes':
                self.send(self.conn_msgs, 'delete ' + self.dir_screen.path)
                messagebox.showinfo('File deleted', "You will be transfered back to directory screen.")
        self.go_to_dir_screen()

    def get_file(self):
        while not self.close:
            file_bytes = b""
            while True:
                data = self.conn_files.recv(self.client.SIZE)
                file_bytes += data
                if file_bytes[-5:] == b"<END>":
                    file_bytes = file_bytes[:-5]
                    break
                if file_bytes[-6:] == b"<STOP>":
                    print('STOP')
                    self.close = True
                    self.go_to_dir_screen()
                    return
            print(f"File finished downloading...")

            file_data = file_bytes.decode(self.client.FORMAT)

            self.being_changed = True
            self.last_file_data = file_data
            self.data_input.delete("1.0","end")
            self.data_input.insert( "1.0", file_data)
            self.being_changed = False

    def send_file_when_changed(self):
        while not self.close:
            if not self.being_changed:
                data = self.data_input.get("1.0",'end')
                if data:
                    data = data[:-1]
                if not data == self.last_file_data:
                    print(f"File started sending...")
                    self.send(self.conn_msgs, "file")
                    self.last_file_data = data
                    data = data.encode(self.client.FORMAT, errors= 'ignore')
                    self.conn_files.sendall(data)
                    self.conn_files.send(b"<END>") 
            sleep(0.1)

    def go_to_dir_screen(self):
        self.edit_screen_frame.destroy()
        current_len = len(self.dir_screen.path.split('/')[-1])
        self.dir_screen.path = self.dir_screen.path[:len(self.dir_screen.path) - current_len]
        self.dir_screen.path_label.configure(text='Path: '+self.dir_screen.path)
        self.dir_screen.dir_screen_frame.pack()

    def send(self, conn, msg):
        msg = msg + "|"
        conn.send(msg.encode(self.client.FORMAT, errors= 'ignore'))

def add_placeholder(entry, placeholder):
    def click(event):
        entry.delete(0, END)
        entry.unbind("<Button-1>")

    entry.insert(0, placeholder)
    entry.bind("<Button-1>", click)

def create_thread(thread_function, args=(), daemon_state='True', name_extra='', start='True'):
    new_thread = threading.Thread(target=thread_function, args=args)
    new_thread.daemon = daemon_state
    if not name_extra:
        new_thread.name = thread_function.__name__
    else:
        new_thread.name = thread_function.__name__ + " " + name_extra
    if start:
        new_thread.start()
    return new_thread