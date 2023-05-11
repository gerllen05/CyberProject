import socket
from time import sleep
from modules.encrypter import Encrypter

class Client:
    def __init__(self):
        self.IP = input("Enter server IP: ")
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
        msg_bytes = self.encrypter.decrypt(msg_encrypted)
        msg = msg_bytes.decode(self.FORMAT, errors= 'ignore')
        return msg
    
    def send_file(self, data: str):
        data_bytes = data.encode(self.FORMAT, errors= 'ignore')
        data_encrypted = self.encrypter.encrypt(data_bytes)
        size = len(data_encrypted)
        self.send_msg(f"file {size}")
        self.conn_files.send(data_encrypted)

    def recv_file(self, size: int):
        data_encrypted = self.conn_files.recv(size)
        if not data_encrypted:
            data_bytes = data_encrypted
        else:
            data_bytes = self.encrypter.decrypt(data_encrypted)
        data = data_bytes.decode(self.FORMAT, errors= 'ignore')
        return data


