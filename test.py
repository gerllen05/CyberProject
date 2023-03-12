import socket
from time import sleep

class Client:
    def __init__(self):
        # self.IP = "127.0.0.1"
        self.IP = "cyberproject-production.up.railway.app"
        self.PORT = 80
        self.SIZE = 4096
        self.FORMAT = "utf-8"

        self.login = ''
        # self.opened_file_path = "popopopa/path.txt" 123

        self.conn_msgs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_files = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Waiting for a connection...")
         
    def main(self):
        self.conn_msgs.connect((self.IP, self.PORT))
        print(f"Client connected to server at {self.IP}:{self.PORT}.")
        self.conn_msgs.send(b"GET / HTTP/1.1\r\nHost:cyberproject-production.up.railway.app\r\n\r\n")
        msg = self.conn_msgs.recv(self.SIZE).decode()
        print(msg)

        self.conn_files.connect((self.IP, self.PORT))
        print("File connection established.")


if __name__ == "__main__":
    Client().main()
