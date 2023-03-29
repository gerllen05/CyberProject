import socket
from time import sleep

class Client:
    def __init__(self):
        self.IP = "127.0.0.1"
        # self.IP = "cyberproject-production.up.railway.app"
        self.PORT = 8000
        self.SIZE = 4096
        self.FORMAT = "utf-8"

        self.login = ''
        # self.opened_file_path = "popopopa/path.txt" 123

        self.conn_msgs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_files = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Waiting for a connection...")
         
        while True:
            try:
                self.conn_msgs.connect((self.IP, self.PORT))
                print(f"Client connected to server at {self.IP}:{self.PORT}.")

                self.conn_files.connect((self.IP, self.PORT))
                print("File connection established.")

                break
            except:
                pass
            sleep(0.1)

    def send_msg(self, msg: str):
        msg = msg + "|"
        self.conn_msgs.send(msg.encode(self.FORMAT, errors= 'ignore'))

    def recv_msg(self):
        msg = self.conn_msgs.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
        return msg
    
    def send_file(self, data: str):
        size = len(data)
        self.send_msg(f"file {size}")
        data = data.encode(self.FORMAT, errors= 'ignore')
        self.conn_files.sendall(data)

    def recv_file(self, size: int):
        data = self.conn_files.recv(size)
        file_data = data.decode(self.FORMAT, errors= 'ignore')
        return file_data

if __name__ == "__main__":
    Client().main()
