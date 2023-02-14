import socket
import time

class Client:
    def __init__(self):
        # self.IP = "104.196.232.237"
        # self.IP = "172.17.3.31"
        self.IP = "127.0.0.1"
        self.PORT = 25565
        self.SIZE = 4096
        self.FORMAT = "utf-8"
        self.ICON = 'icons/Network Drive.ico'

        self.login = ''
        self.opened_file_path = "popopopa/path.txt"

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
            time.sleep(0.1)

if __name__ == "__main__":
    Client().main()