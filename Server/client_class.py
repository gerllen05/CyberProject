from cryptography.fernet import Fernet

class Client:
    SIZE = 2048
    FORMAT = "utf-8"

    # conn_msgs - socket for text messages, conn_files - socket for files
    def __init__(self, ip, conn_msgs, conn_files, key, online=False):
        self.ip = ip
        self.conn_msgs = conn_msgs
        self.conn_files = conn_files
        self.encrypter = Fernet(key)
        self.online = online

    def info(self):
        print(f"ip: {self.ip}")
        print(f"conn_msgs: {self.conn_msgs}") 
        print(f"conn_files: {self.conn_msgs}") 
        print(f"online: {self.online}")
        

    def send_msg(self, msg: str):
        try:
            msg_bytes = msg.encode(self.FORMAT, errors= 'ignore')
            msg_encrypted = self.encrypter.encrypt(msg_bytes)
            self.conn_msgs.send(msg_encrypted)
        except:
            print('send_msg stopped')

    def recv_msg(self):
        try:
            msg_encrypted = self.conn_msgs.recv(self.SIZE)
            msg_bytes = self.encrypter.decrypt(msg_encrypted)
            msg = msg_bytes.decode(self.FORMAT, errors= 'ignore')
            return msg
        except:
            print('recv_msg stopped')
    
    def send_file(self, data_bytes: str):
        try:
            data_encrypted = self.encrypter.encrypt(data_bytes)
            size = len(data_encrypted)
            self.send_msg(f"file {size}")
            self.conn_files.send(data_encrypted)
        except:
            print('send_file stopped')

    def recv_file(self, size: int):
        try:
            data_encrypted = self.conn_files.recv(size)
            if not data_encrypted:
                data_bytes = data_encrypted
            else:
                data_bytes = self.encrypter.decrypt(data_encrypted)
            return data_bytes
        except:
            print('recv_file stopped')
   