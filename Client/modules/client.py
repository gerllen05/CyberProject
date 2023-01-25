import socket
import os
import threading
import time
import tqdm

class Client:
    def __init__(self):
        self.IP = "127.0.0.1"
        self.PORT = 8000
        self.SIZE = 1024
        self.FORMAT = "utf-8"
        self.FINISHED = False
        self.OPENED_FILE_PATH = "popopopa/path.txt"
        self.FILES_RECV_QUEUE = []
        self.DIR_LIST = []

        self.conn_msgs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_files = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        create_thread(self.get_input_thread)

        print("Waiting for a connection...")
         
        while True:
            try:
                self.conn_msgs.connect((self.IP, self.PORT))
                print(f"Client connected to server at {self.IP}:{self.PORT}.")

                # sending client username to a server
                self.conn_msgs.send(f"Username: {os.getlogin()}".encode(self.FORMAT, errors= 'ignore'))

                self.conn_files.connect((self.IP, self.PORT))
                print("File connection established.")

                create_thread(self.get_response_thread)
                break
            except:
                pass
            time.sleep(0.1)
        
    def start(self):
        create_thread(self.get_response_thread)
        while not self.FINISHED:         
            time.sleep(0.1)

        print(f"Client disconnected.")

    def get_input_thread(self):
        while True:
            msg = input()
            if msg == "exit":
                try:
                    self.send(self.conn_msgs, msg)
                    self.conn_msgs.close()
                    self.conn_files.close()
                except:
                    print("Client didn't connect to a server.")
                self.FINISHED = True
            elif msg == "threads":
                print(threading.enumerate())
            elif msg == "help":
                print("Here are all available commands:")
                print("- exit --> disconnects client")
                print("- threads --> shows all threads")
                print("- help --> shows all available commands")
            else:
                self.send(self.conn_msgs, msg)

    def get_response_thread(self):
        while True:
            msg = self.conn_msgs.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
            msg_list = msg.split("|")
            for msg in msg_list:
                if msg[:6] == "exit":
                    try:
                        self.FINISHED = True
                        self.send(self.conn_msgs, "exit")
                        self.conn_msgs.close()
                        self.conn_files.close()
                    except:
                        pass
                    break
                elif msg == "online":
                    print("Successefuly logged in.")
                    time.sleep(1)
                    create_thread(self.files_send_thread)
                    create_thread(self.files_recv_thread)
                elif msg[:4] == "path":
                    path = msg.replace("path ", "")
                    if self.FILES_RECV_QUEUE.count(path) == 0:
                        self.FILES_RECV_QUEUE.append(path)
                elif msg[:3] == "dir":
                    dir_string = msg.replace("dir ", "")
                    self.DIR_LIST = dir_string.split(" ")
                elif msg == '':
                    pass
                else:
                    print(f"Server: {msg}")

    def files_send_thread(self):
        previous_data = b""
        previous_file_path = self.OPENED_FILE_PATH
        while True:
            if self.OPENED_FILE_PATH:
                try:
                    file = open(self.OPENED_FILE_PATH, "rb")
                    data = file.read()
                    # print(previous_data)
                    if (not data == previous_data) and previous_file_path == self.OPENED_FILE_PATH:
                        print(f"File '{self.OPENED_FILE_PATH}' started sending...")
                        self.send(self.conn_msgs, "path " + self.OPENED_FILE_PATH)
                        self.conn_files.sendall(data)
                        self.conn_files.send(b"<END>")
                        previous_data = data
                        previous_file_path = self.OPENED_FILE_PATH
                    file.close()
                except Exception as e:
                    pass
            time.sleep(0.3)

    def files_recv_thread(self):
        while True:
            try:
                path = self.FILES_RECV_QUEUE[0]
                name = path.split('/')[-1]
                try:
                    dirs = ""
                    for dir in path.replace(name, "").split('/'):
                        if dir:
                            dirs += dir + "/"
                            print(dirs)
                            os.mkdir(dirs)
                except:
                    pass
                # print(f"File '{path}' started downloading...")
                file = open(f'{path}', "wb")
                fbytes = b""
                while True:
                    data = self.conn_files.recv(self.SIZE)
                    fbytes += data
                    if fbytes[-5:] == b"<END>":
                        fbytes = fbytes[:-5]
                        file.write(fbytes)
                        break
                file.close()
                print(f"File '{path}' finished downloading...")
                self.FILES_RECV_QUEUE.remove(path)
            except:
                time.sleep(0.1)
            
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