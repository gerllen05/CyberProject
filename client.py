import socket
import os
import threading
import time
import tqdm

class Client:
    IP = "127.0.0.1"
    PORT_MSGS = 8000
    PORT_FILES = 8070
    SIZE = 1024
    FORMAT = "utf-8"
    FINISHED = False

    def main(self):
        conn_msgs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        create_thread(self.get_input, (conn_msgs,))

        connected = False
        print("Waiting for a connection...")
        while not self.FINISHED: 
            if not connected:
                try:
                    conn_msgs.connect((self.IP, self.PORT_MSGS))
                    print(f"Connected: Client connected to server at {self.IP}:{self.PORT_MSGS}")

                    # sending client username to a server
                    self.send(conn_msgs, f"Username: {os.getlogin()}") 

                    connected = True
                    create_thread(self.get_response, (conn_msgs,))
                except Exception as e:
                    pass
                    
            time.sleep(0.1)

        print(f"Client disconnected.")

    def get_input(self, conn_msgs):
        while True:
            msg = input()
            if msg == "exit":
                self.CONNECTED = False
                self.FINISHED = True
                try:
                    self.send(conn_msgs, msg)
                    conn_msgs.close()
                except:
                    print("Client didn't connect to a server.")
            elif msg == "threads":
                print(threading.enumerate())
            elif msg == "help":
                print("Here are all available commands:")
                print("- exit --> disconnects client")
                print("- threads --> shows all threads")
                print("- help --> shows all available commands")
            else:
                self.send(conn_msgs, msg)

    def get_response(self, conn_msgs):
        while True:
            msg = conn_msgs.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
            if msg[:6] == "exit":
                try:
                    self.send(conn_msgs, "exit")
                    conn_msgs.close()
                except:
                    pass
                self.CONNECTED = False
                self.FINISHED = True
                break
            elif msg == "online":
                conn_files = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn_files.connect((self.IP, self.PORT_FILES))
                # create thread send files
            elif msg == '':
                print("Empty answer...")
            else:
                print(f"Server: {msg}")

    # *Нужно сделать сенд файлс и гет файлс
    def file_recv(self, conn):
        name = conn.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
        print(f"File '{name}' started downloading...")
        file = open(name, "wb")
        fbytes = b""
        while True:
            data = conn.recv(self.SIZE)
            fbytes += data
            if fbytes[-5:] == b"<END>":
                fbytes = fbytes[:-5]
                file.write(fbytes)
                break
        file.close()

    def file_send(self, path, conn):
        self.send(conn, path)
        try:
            file = open(path, "rb")
            data = file.read()
            conn.sendall(data)
            conn.send(b"<END>")
            file.close()
        except Exception as e:
            print(e)

    def send(self, conn, msg):
        conn.send(msg.encode(self.FORMAT, errors= 'ignore'))

def create_thread(thread_function, args=(), daemon_state='True', name_extra='', start='True'):
    new_thread = threading.Thread(target=thread_function, args=args)
    new_thread.daemon = daemon_state
    new_thread.name = thread_function.__name__ + " " + name_extra
    if start:
        new_thread.start()
    return new_thread

if __name__ == "__main__":
    Client().main()