import socket
from time import sleep
from modules.encrypter import Encrypter

class Client:
    def __init__(self):
        self.IP = "127.0.0.1"
        self.PORT = 8000
        self.SIZE = 2048
        self.FORMAT = "utf-8"

        self.login = ''

        self.conn_msgs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_files = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Waiting for a connection...")
         
        while True:
            try:
                self.conn_msgs.connect((self.IP, self.PORT))
                print(f"Client connected to server at {self.IP}:{self.PORT}.")

                key = self.conn_msgs.recv(32)
                self.encrypter = Encrypter(key)

                self.conn_files.connect((self.IP, self.PORT))
                print("File connection established.")

                break
            except Exception as e:
                pass
            sleep(0.1)

    def send_msg(self, msg: str):
        msg = msg + "|"
        msg_bytes = msg.encode(self.FORMAT, errors= 'ignore')
        msg_encrypted = self.encrypter.encrypt(msg_bytes)
        self.conn_msgs.send(msg_encrypted)

    def recv_msg(self):
        msg_encrypted = self.conn_msgs.recv(self.SIZE)
        print(msg_encrypted)
        msg_bytes = self.encrypter.decrypt(msg_encrypted)
        msg = msg_bytes.decode(self.FORMAT, errors= 'ignore')
        print(msg)
        return msg
    
    def send_file(self, data: str):
        data_bytes = data.encode(self.FORMAT, errors= 'ignore')
        size = len(data_bytes)
        self.send_msg(f"file {size}")
        for i in range(0, len(data_bytes), self.SIZE):
            chunk = data_bytes[i:i+self.SIZE]
            data_encrypted = self.encrypter.encrypt(chunk)
            self.conn_files.send(data_encrypted)
            sleep(0.1)

    def recv_file(self, size: int):
        data = ""
        while size:
            data_encrypted = self.conn_files.recv(self.SIZE)
            if not data_encrypted:
                data_bytes = data_encrypted
            else:
                data_bytes = self.encrypter.decrypt(data_encrypted)
            chunk = data_bytes.decode(self.FORMAT, errors= 'ignore')
            size -= len(chunk)
            data += chunk
        return data


