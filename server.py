import socket
import threading
import time
import os
import tqdm
import sqlite3

class Server:
    IP = "0.0.0.0"
    PORT = 8000
    ADDR = (IP, PORT)
    SERVER = ()
    SIZE = 4096
    FORMAT = "utf-8"
    CLIENTS = []
    FINISH = False

    def main(self):
        print("\nServer is starting...")
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.bind(self.ADDR)
        self.SERVER.listen()
        print(f"Listening: {self.IP}:{self.PORT}")

        create_thread(self.new_client_thread)
        create_thread(self.get_input_thread)
        create_thread(self.files_send_queue_updater_thread)

        #when the loop finishes, all daemon threads will close
        while not self.FINISH:
            time.sleep(0.1)

    def new_client_thread(self):
        while True:
            print("Waiting for new client...")
            conn, addr = self.SERVER.accept()

            ip = addr[0]
            # check is it conn for files or not
            for_msgs = True
            for_files_client_id = 0
            for client in self.CLIENTS:
                if client:
                    if client.ip == ip:
                        if not client.conn_files:
                            for_msgs = False
                            for_files_client_id = self.CLIENTS.index(client)
                        else:
                            pass
            # for conn_msgs
            if for_msgs:
                # recieving client's username
                answer = conn.recv(self.SIZE).decode(self.FORMAT, errors='ignore')
                if answer[:8] == 'Username':
                    username = answer.replace("Username: ", "")
                else:
                    username = 'unknown'

                client = Client(ip, conn, (), username)
                self.CLIENTS.append(client)
                client_id = self.CLIENTS.index(client)

                print(f"\n{client_id}. New msgs connection: {username} - {addr} connected.")
                create_thread(self.handle_msgs_thread, (client_id,), name_extra=username)
            # for conn_files
            else:
                client = self.CLIENTS[for_files_client_id]

                upd_client = Client(client.ip, client.conn_msgs, conn, client.username)
                self.CLIENTS[for_files_client_id] = upd_client
                print(f"\n{for_files_client_id}. New files connection: {username} - {addr} connected.")
                       
    def get_input_thread(self):
        while True:
            msg = input()
            if msg == "exit": 
                print("Server is closing...")
                if self.CLIENTS:
                    print("Clients disconnecting:")
                self.send_all("exit")
                self.FINISH = True
            elif msg[:5] == "kick ":
                try:
                    client = self.CLIENTS[int(msg.replace("kick ", ""))]            
                    self.send(client.conn_msgs, "exit")
                except:
                    print("You have to enter available [client_id] after 'kick'.")
            elif msg == "close":
                self.FINISH = True
            elif msg == "threads":
                print(f"\nActive threads: {threading.enumerate()}")
            elif msg == "clients":
                print(f"\nActive connections:")
                for cl in self.CLIENTS:
                    if not cl == []:
                        print(f"id {self.CLIENTS.index(cl)}. {cl.username} - {cl.ip}")
            elif msg[:5] == "info ":
                try:
                    client = self.CLIENTS[int(msg.replace("info ", ""))]
                    client.info()
                except:
                    print("You have to enter available [client_id] after 'kick'.")
            elif msg == "help":
                print("Here are all available commands:")
                print("- exit --> disconnects all clients and closes server")
                print("- kick [client_id] --> disconnects chosen client")
                print("- close --> closes only server")
                print("- threads --> shows all threads")
                print("- clients --> shows list of all clients, [client_id] is index of the client")
                # print("- clients_info --> shows list of all clients, [client_id] is index of the client")
                print("- help --> shows all available commands")
            else:
                print(f"Incorrect command '{msg}': type 'help' to see all commands")

    def handle_msgs_thread(self, client_id):
        client = self.CLIENTS[client_id]
        conn = client.conn_msgs
        db_conn = sqlite3.connect('Server.db')
        while not self.FINISH:
            msg = conn.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
            if msg == "exit":
                break
            elif msg[:3] == "reg":
                msg = msg.replace("reg ", "")
                login = msg.split()[0]
                password = msg.split()[1]
                check = db_conn.execute(f'SELECT password FROM Users WHERE login = "{login}"').fetchone() # check if login has already been used
                if len(login) < 8 or len(password) < 8:
                    self.send(conn, "In login and password must be 8 or more digits.")
                elif check:
                    self.send(conn, "This login has already been used.")
                else:
                    client.online = True
                    db_conn.execute(f'INSERT INTO Users (login, password, clientId) VALUES("{login}", "{password}", "{client_id}")')
                    db_conn.commit()
                    self.send(conn, "online")

                    create_thread(self.files_send_thread, (client_id,), name_extra=f"{client.username}")
                    create_thread(self.files_recv_thread, (client_id,), name_extra=f"{client.username}")
                    self.send(conn, f"Successefuly registered: login - {login}, password - {password}.")
            elif msg[:6] == "log in":
                msg = msg.replace("log in ", "")
                login = msg.split()[0]
                password = msg.split()[1]
                print(login)
                print(password)
                userId = db_conn.execute(f'SELECT userId FROM Users WHERE login = "{login}" AND password = "{password}"').fetchone()[0]
                previous_client_id = db_conn.execute(f'SELECT clientId FROM Users WHERE userId = {userId}').fetchone()[0]
                print(previous_client_id)
                if not userId:
                    self.send(conn, "Login or password is wrong.")
                else:
                    client.online = True
                    db_conn.execute(f'UPDATE Users SET clientId = {client_id} WHERE userId = {userId}')
                    db_conn.commit()

                    self.send(conn, "online")
                    time.sleep(0.1)
                    self.send(conn, f"Successefuly logged in: login - {login}, password - {password}.")
                    time.sleep(0.1)

                    create_thread(self.files_send_thread, (client_id,), name_extra=f"{client.username}")
                    create_thread(self.files_recv_thread, (client_id,), name_extra=f"{client.username}")


            if client.online:
                if msg[:4] == "path":
                    path = msg.replace("path ", "")
                    if client.files_recv_queue.count(path) == 0:
                        client.files_recv_queue.append(path)
                # recv online commands will be here

            # id = self.CLIENTS.index(client)
            # print(f"{id}.{client.username} - {client.ip}: {msg}")

        
        print(f"{client_id}. {client.username} - {client.ip} disconnecting...")
        self.CLIENTS[client_id] = []
        db_conn.close()
        try:
            client.conn_msgs.close()
            client.conn_files.close()
        except:
            pass
        print("handle_msgs_thread stopped.")


    def send_all(self, msg):
        for client in self.CLIENTS:
            if client:
                self.send(client.conn_msgs, msg)

    def send(self, conn, msg):
        conn.send(msg.encode(self.FORMAT, errors= 'ignore'))

    def files_send_thread(self, client_id):
        while True:
            client = self.CLIENTS[client_id]
            if not client:
                print("files_send_thread stopped.")
                break
            if client:
                if client.files_send_queue:
                    path = client.files_send_queue[0]
                    # print(f"File '{path}' started sending...")
                    self.send(client.conn_msgs, "path " + path)
                    time.sleep(0.1)
                    try:
                        file = open(path, "rb")
                        data = file.read()
                        client.conn_files.sendall(data)
                        client.conn_files.send(b"<END>")
                        file.close()
                    except Exception as e:
                        print(e)
                    try:   
                        client.files_send_queue.remove(path)
                    except:
                        pass
            time.sleep(0.3)

    def files_recv_thread(self, client_id):
        while True:
            client = self.CLIENTS[client_id]
            if not client:
                print("files_recv_thread stopped.")
                break
            try:
                path = client.files_recv_queue[0]
                # print(f"File '{path}' started downloading...")
                file = open(f"new/{path}", "wb")
                fbytes = b""
                while True:
                    data = client.conn_files.recv(self.SIZE)
                    fbytes += data
                    if fbytes[-5:] == b"<END>":
                        fbytes = fbytes[:-5]
                        file.write(fbytes)
                        break
                file.close()
                # print(f"File '{path}' finished downloading...")
                client.files_recv_queue.remove(path)
            except:
                time.sleep(0.1)

    def files_send_queue_updater_thread(self):
        while True:
            db_conn = sqlite3.connect('Server.db')
            accesses = db_conn.execute('SELECT path, guestId FROM Accesses').fetchall()
            for access in accesses:
                path = access[0]
                client_id = db_conn.execute(f'SELECT clientId FROM Users WHERE userId = {access[1]}').fetchone()[0]
                if client_id < len(self.CLIENTS):
                    client = self.CLIENTS[client_id]
                    if client and client.files_send_queue.count(path) == 0:
                        client.files_send_queue.append(path)
            db_conn.close()
            time.sleep(0.1)

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

class Client:
    # conn_msgs - socket for text messages, conn_files - socket for files
    def __init__(self, ip, conn_msgs, conn_files, username, online=False, files_send_queue=[], files_recv_queue=[]):
        self.ip = ip
        self.conn_msgs = conn_msgs
        self.conn_files = conn_files
        self.username = username
        self.online = online
        self.files_send_queue = files_send_queue
        self.files_recv_queue = files_recv_queue

    def info(self):
        print(f"ip: {self.ip}")
        print(f"conn_msgs: connected") #{self.conn_msgs}
        if self.conn_files:
            print(f"conn_files: connected") #{self.conn_files}
        print(f"username: {self.username}")
        print(f"online: {self.online}") 
        print(f"files_send_queue: {self.files_send_queue}")
        print(f"files_recv_queue: {self.files_recv_queue}")

if __name__ == "__main__":
    Server().main()