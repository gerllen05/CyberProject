import socket
import os
import threading
import time
import tqdm

class Client:
    def __init__(self):
        self.IP = "127.0.0.1"
        self.PORT = 8000
        self.SIZE = 4096
        self.FORMAT = "utf-8"
        self.ICON = 'icons/Network Drive.ico'

        self.finished = False
        self.create_online_threads = False
        self.login = ''
        self.opened_file_path = "popopopa/path.txt"
        self.files_recv_queue = []

        self.conn_msgs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_files = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Waiting for a connection...")
         
        while True:
            try:
                self.conn_msgs.connect((self.IP, self.PORT))
                print(f"Client connected to server at {self.IP}:{self.PORT}.")

                self.conn_files.connect((self.IP, self.PORT))
                print("File connection established.")

                # create_thread(self.get_response_thread)
                break
            except:
                pass
            time.sleep(0.1)
        
    def start(self):   
        while not self.finished:      
            time.sleep(0.1)

        print(f"Client disconnected.")
            
    def send(self, conn, msg):
        msg = msg + "|"
        conn.send(msg.encode(self.FORMAT, errors= 'ignore'))

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

if __name__ == "__main__":
    Client().main()