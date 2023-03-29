class Client:
    SIZE = 4096
    FORMAT = "utf-8"

    # conn_msgs - socket for text messages, conn_files - socket for files
    def __init__(self, ip, conn_msgs, conn_files, online=False):
        self.ip = ip
        self.conn_msgs = conn_msgs
        self.conn_files = conn_files
        self.online = online

    def info(self):
        print(f"ip: {self.ip}")
        print(f"conn_msgs: {self.conn_msgs}") #{self.conn_msgs}
        print(f"conn_files: {self.conn_msgs}") #{self.conn_files}
        print(f"online: {self.online}")

    def send_msg(self, msg: str):
        self.conn_msgs.send(msg.encode(self.FORMAT, errors= 'ignore'))

    def recv_msg(self):
        msg = self.conn_msgs.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
        return msg
    
    def send_file(self, data: str, size):
        self.send_msg(f"file {size}")
        self.conn_files.sendall(data)

    def recv_file(self, size: int):
        data = self.conn_files.recv(size)
        return data 