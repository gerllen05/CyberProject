from encrypter import Encrypter
from time import sleep

class Client:
    SIZE = 2048
    FORMAT = "utf-8"

    # conn_msgs - socket for text messages, conn_files - socket for files
    def __init__(self, ip, conn_msgs, conn_files, key, online=False):
        self.ip = ip
        self.conn_msgs = conn_msgs
        self.conn_files = conn_files
        self.encrypter = Encrypter(key)
        self.online = online

    def info(self):
        print(f"ip: {self.ip}")
        print(f"conn_msgs: {self.conn_msgs}") 
        print(f"conn_files: {self.conn_msgs}") 
        print(f"online: {self.online}")
        

    def send_msg(self, msg: str):
        msg_bytes = msg.encode(self.FORMAT, errors= 'ignore')
        msg_encrypted = self.encrypter.encrypt(msg_bytes)
        self.conn_msgs.send(msg_encrypted)

    def recv_msg(self):
        msg_encrypted = self.conn_msgs.recv(self.SIZE)
        msg_bytes = self.encrypter.decrypt(msg_encrypted)
        msg = msg_bytes.decode(self.FORMAT, errors= 'ignore')
        return msg
    
    def send_file(self, data_bytes: str):
        size = len(data_bytes)
        self.send_msg(f"file {size}")
        for i in range(0, len(data_bytes), self.SIZE):
            chunk = data_bytes[i:i+self.SIZE]
            data_encrypted = self.encrypter.encrypt(chunk)
            self.conn_files.send(data_encrypted)
            sleep(0.1)

    def recv_file(self, size: int):
        data = b""
        while size:
            data_encrypted = self.conn_files.recv(self.SIZE)
            if not data_encrypted:
                data_bytes = data_encrypted
            else:
                data_bytes = self.encrypter.decrypt(data_encrypted)
            size -= len(data_bytes)
            data += data_bytes
        return data
   