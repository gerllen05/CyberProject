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
            # if self.create_online_threads:
            #     create_thread(self.files_send_thread)
            #     create_thread(self.files_recv_thread)
            #     self.create_online_threads = False         
            time.sleep(0.1)

        print(f"Client disconnected.")

    def get_response_thread(self):
        while True:
            msg = self.conn_msgs.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
            msg_list = msg.split("|")
            for msg in msg_list:
                if msg[:6] == "exit":
                    try:
                        self.finished = True
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
                    path = msg[5:]
                    if self.files_recv_queue.count(path) == 0:
                        self.files_recv_queue.append(path)
                elif msg[:3] == "dir":
                    dir_string = msg[4:]
                    self.DIR_LIST = dir_string.split(" ")
                elif msg == '':
                    pass
                else:
                    print(f"Server: {msg}")

    def files_send_thread(self):
        previous_data = b""
        previous_file_path = self.opened_file_path
        while True:
            if self.opened_file_path:
                try:
                    file = open(self.opened_file_path, "rb")
                    data = file.read()
                    # print(previous_data)
                    if (not data == previous_data) and previous_file_path == self.opened_file_path:
                        print(f"File '{self.opened_file_path}' started sending...")
                        self.send(self.conn_msgs, "path " + self.opened_file_path)
                        self.conn_files.sendall(data)
                        self.conn_files.send(b"<END>")
                        previous_data = data
                        previous_file_path = self.opened_file_path
                    file.close()
                except Exception as e:
                    pass
            time.sleep(0.3)

    def files_recv_thread(self):
        while True:
            try:
                path = self.files_recv_queue[0]
                name = path.split('/')[-1]
                path += "Network Drive Files/"
                dirs = ""
                for dir in path.replace(name, "").split('/'):
                    if dir:
                        dirs += dir + "/"
                        try:
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
                self.files_recv_queue.remove(path)
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