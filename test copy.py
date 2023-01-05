import socket
import threading
import time
import os
import tqdm
import sqlite3

IP = "0.0.0.0"
PORT = 8000
ADDR = (IP, PORT)
SERVER = ()
SIZE = 1024
FORMAT = "utf-8"
CLIENTS = []
FINISH = False

def main(self):
        print("\nServer is starting...")
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.bind(self.ADDR)
        self.SERVER.listen()
        print(f"Listening: {self.IP}:{self.PORT}")

        create_thread(self.new_client)
        create_thread(self.get_input)

        #when the loop finishes, all daemon threads will close
        while not self.FINISH:
            time.sleep(0.1)

def new_client(self):
    while True:
        conn_msgs, addr_msgs = self.SERVER.accept()

        # recieving client's username
        answer = conn_msgs.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
        if answer[:8] == 'Username':
            username = answer.replace("Username: ", "")
        else:
            username = 'unknown'
        print(f"\n. New connection: {username} connected.")

def create_thread(thread_function, args=(), daemon_state='True', name_extra='', start='True'):
    new_thread = threading.Thread(target=thread_function, args=args)
    new_thread.daemon = daemon_state
    new_thread.name = thread_function.__name__ + " " + name_extra
    if start:
        new_thread.start()
    return new_thread



