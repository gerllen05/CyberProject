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
    SIZE = 1024
    FORMAT = "utf-8"
    CLIENTS = []
    FINISH = False

    def main(self):
        print("\nServer is starting...")
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.bind(self.ADDR)
        self.SERVER.listen()
        print(f"Listening: {self.IP}:{self.PORT}")

        create_thread(self.new_client)
        create_thread(self.get_input)

        #when the loop finishes, all daemon threads will close
        while not self.FINISH:
            time.sleep(0.1)

    def new_client(self):
        while True:
            print("waiting for new client")
            conn, addr = self.SERVER.accept()

            # recieving client's username
            answer = conn.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
            if answer[:8] == 'Username':
                username = answer.replace("Username: ", "")
            else:
                username = 'unknown'

            ip = addr[0]
            # check is it conn for files or not
            for_msgs = True
            for_files_client_id = 0
            for client in self.CLIENTS:
                if client.ip == ip:
                    for_msgs = False
                    for_files_client_id = self.CLIENTS.index(client)
            print(f"sadfaeweawefad")
            # for conn_msgs
            if for_msgs:
                client = Client(ip, conn, addr[1], (), 0, username)
                self.CLIENTS.append(client)
                client_id = self.CLIENTS.index(client)

                print(f"\n{client_id}. New msgs connection: {username} - {addr} connected.")
                create_thread(self.handle_msgs, (client_id,), name_extra=f"{client.ip}")
            # for conn_files
            else:
                client = self.CLIENTS[for_files_client_id]
                port_files = addr[1]

                upd_client = Client(client.ip, client.conn_msgs, client.port_msgs, conn, port_files, client.username)
                self.CLIENTS[client_id] = upd_client
                print(f"\n{client_id}. New files connection: {username} - {addr} connected.")
                       
    def get_input(self):
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
                    conn = self.CLIENTS[int(msg.replace("kick ", ""))].conn_msgs               
                    self.send(conn, "exit")
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

    def handle_msgs(self, client_id):
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
                    db_conn.execute(f'INSERT INTO Users (login, password, clientId, online) VALUES("{login}", "{password}", "{client_id}", "{client.online}")')
                    self.send(conn, "online")

                    create_thread(self.handle_files, (client_id,), name_extra=f"{client.username}")
                    self.send(conn, f"Successefuly registered: login - {login}, password - {password}.")
            elif msg[:5] == "log in":
                msg = msg.replace("log in ", "")
                login = msg.split()[0]
                password = msg.split()[1]
                db_pass = db_conn.execute(f'SELECT password FROM Users WHERE login = {login}').fetchone()[0]
                if not db_pass:
                    self.send(conn, "Login or password is wrong.")
                elif db_pass == password:
                    client.online = True
                    self.send(conn, "online")
                    db_conn.execute(f'SET clientId = {client_id}, online = TRUE FROM Users WHERE login = {login}')
                    
                    create_thread(self.handle_files, (client_id,), name_extra=f"{client.username}")
                    self.send(conn, f"Successefuly logged in: login - {login}, password - {password}.")
            if client.online:
                pass
                # recv online commands will be here

            # id = self.CLIENTS.index(client)
            # print(f"{id}.{client.username} - {client.ip}: {msg}")

        if not client.online:
            print(f"\n{client_id}. {client.username} - {client.ip} disconnecting...")
            self.CLIENTS[client_id] = []
        client.conn_msgs.close()

    # def create_conn_recv_files(self, client_id):
    #     client = self.CLIENTS[client_id]
    #     while True:
    #         conn_files, addr_files = self.SERVER.accept()
    #         if not client.ip == addr_files[0]:
    #             client.conn_msgs.close()
    #             conn_files.close()
    #         else:
    #             port_files = addr_files[1]
    #             break

    #     upd_client = Client(client.ip, client.conn_msgs, client.port_msgs, conn_files, port_files, client.username)
    #     self.CLIENTS[client_id] = upd_client
    #     self.CLIENTS.append(upd_client)

    def handle_files(self, client_id):
        client = self.CLIENTS[client_id]
        while not self.FINISH:
            time.sleep(0.5)
            if client.conn_files:
                try:
                    path = client.conn_files.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
                    self.file_recv(path, client.conn_files)
                    self.file_send_accessed(path)
                    print("File was sent.")
                    time.sleep(0.1)
                except Exception:
                    pass

        print(f"\n{client_id}. {client.username} - {client.ip} disconnecting...")
        self.CLIENTS[client_id] = []
        client.conn_files.close()

    def send_all(self, msg):
        for client in self.CLIENTS:
            if client:
                self.send(client.conn_msgs, msg)

    def send(self, conn, msg):
        conn.send(msg.encode(self.FORMAT, errors= 'ignore'))

    def file_recv(self, path, conn):
        print(f"File '{path}' started downloading...")
        file = open(path, "wb")
        fbytes = b""
        while True:
            data = conn.recv(self.SIZE)
            fbytes += data
            if fbytes[-5:] == b"<END>":
                fbytes = fbytes[:-5]
                file.write(fbytes)
                break
        file.close()

    # fix, it has to create new socket for every file for every client
    def file_send_accessed(self, path):
        db_conn = sqlite3.connect('Server.db')
        accessed = db_conn.execute(f'SELECT guestId FROM Accesses WHERE path = {path}').fetchall()
        accessed.append(path.split('\\')[0])
        for userId in accessed:
            client_id = db_conn.execute(f'SELECT clientId FROM Users WHERE userId = {userId}').fetchone()[0]
            if client_id:
                conn = self.CLIENTS[client_id].conn_files
                # sending file
                try:
                    # name = path.split('\\')[-1]
                    self.send(conn, path)

                    file = open(path, "rb")
                    data = file.read()
                    conn.sendall(data)
                    conn.send(b"<END>")
                    file.close()
                except Exception as e:
                    print(e)

def create_thread(thread_function, args=(), daemon_state='True', name_extra='', start='True'):
    new_thread = threading.Thread(target=thread_function, args=args)
    new_thread.daemon = daemon_state
    new_thread.name = thread_function.__name__ + " " + name_extra
    if start:
        new_thread.start()
    return new_thread

class Client:
    # conn_msgs - socket for text messages, conn_files - socket for files
    def __init__(self, ip, conn_msgs, port_msgs, conn_files, port_files, username, online=False):
        self.ip = ip
        self.conn_msgs = conn_msgs
        self.port_msgs = port_msgs
        self.conn_files = conn_files
        self.port_files = port_files
        self.username = username
        self.online = online

if __name__ == "__main__":
    Server().main()