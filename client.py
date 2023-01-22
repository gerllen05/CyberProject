import socket
import os
import threading
import time
import tqdm

class Client:
    IP = "127.0.0.1"
    PORT = 8000
    SIZE = 1024
    FORMAT = "utf-8"
    FINISHED = False
    OPENED_FILE_PATH = "path.txt"
    FILES_RECV_QUEUE = []
    
    def main(self):
        conn_msgs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_files = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        create_thread(self.get_input_thread, (conn_msgs, conn_files,))

        print("Waiting for a connection...")
         
        while True:
            try:
                conn_msgs.connect((self.IP, self.PORT))
                print(f"Client connected to server at {self.IP}:{self.PORT}.")

                # sending client username to a server
                self.send(conn_msgs, f"Username: {os.getlogin()}") 

                conn_files.connect((self.IP, self.PORT))
                print("File connection established.")

                create_thread(self.get_response_thread, (conn_msgs, conn_files,))
                break
            except:
                pass
            time.sleep(0.1)
        
        while not self.FINISHED:         
            time.sleep(0.1)

        print(f"Client disconnected.")

    def get_input_thread(self, conn_msgs, conn_files):
        while True:
            msg = input()
            if msg == "exit":
                self.FINISHED = True
                try:
                    self.send(conn_msgs, msg)
                    conn_msgs.close()
                    conn_files.close()
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

    def get_response_thread(self, conn_msgs, conn_files):
        while True:
            msg = conn_msgs.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
            if msg[:6] == "exit":
                try:
                    self.FINISHED = True
                    self.send(conn_msgs, "exit")
                    conn_msgs.close()
                    conn_files.close()
                except:
                    pass
                break
            elif msg == "online":
                create_thread(self.files_send_thread, (conn_msgs, conn_files,))
                create_thread(self.files_recv_thread, (conn_files,))
            elif msg[:4] == "path":
                path = msg.replace("path ", "")
                if self.FILES_RECV_QUEUE.count(path) == 0:
                    self.FILES_RECV_QUEUE.append(path)
            elif msg == '':
                print("Empty answer...")
            else:
                print(f"Server: {msg}")

    def files_send_thread(self, conn_msgs, conn_files):
        while True:
            if self.OPENED_FILE_PATH:
                print(f"File '{self.OPENED_FILE_PATH}' started sending...")
                self.send(conn_msgs, "path " + self.OPENED_FILE_PATH)
                time.sleep(0.1)
                try:
                    file = open(self.OPENED_FILE_PATH, "rb")
                    data = file.read()
                    conn_files.sendall(data)
                    conn_files.send(b"<END>")
                    file.close()
                except Exception as e:
                    pass
            time.sleep(0.3)

    def files_recv_thread(self, conn_files):
        try:
            os.mkdir('Network Drive Files')
        except:
            pass
        while True:
            try:
                path = self.FILES_RECV_QUEUE[0]
                # print(f"File '{path}' started downloading...")
                file = open(f'{path}', "wb")
                fbytes = b""
                while True:
                    data = conn_files.recv(self.SIZE)
                    fbytes += data
                    if fbytes[-5:] == b"<END>":
                        fbytes = fbytes[:-5]
                        file.write(fbytes)
                        break
                file.close()
                print(f"File '{path}' finished downloading...")
                self.FILES_RECV_QUEUE.remove(path)
            except:
                time.sleep(0.1)
            
    def send(self, conn, msg):
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