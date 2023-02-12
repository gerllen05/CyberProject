import socket
import threading
import time
import os
import sqlite3
import shutil

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
        db_conn = sqlite3.connect('Server.db')
        db_conn.execute(f'UPDATE Users SET clientId = NULL, openedFilePath = NULL')
        db_conn.commit()
        db_conn.close()
        
        print("\nServer is starting...")
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.bind(self.ADDR)
        self.SERVER.listen()
        print(f"Listening: {self.IP}:{self.PORT}")

        try:
            os.mkdir(f'users')
        except:
            pass

        create_thread(self.new_client_thread)
        create_thread(self.get_input_thread)

        #when the loop finishes, all daemon threads will close
        while not self.FINISH:
            time.sleep(0.1)

    def new_client_thread(self):
        while True:
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
                client = Client(ip, conn, ())
                self.CLIENTS.append(client)
                client_id = self.CLIENTS.index(client)

                print(f"\n{client_id}. New msgs connection: {addr} connected.")
                create_thread(self.handle_msgs_thread, (client_id,))
            # for conn_files
            else:
                client = self.CLIENTS[for_files_client_id]

                upd_client = Client(client.ip, client.conn_msgs, conn)
                self.CLIENTS[for_files_client_id] = upd_client
                print(f"{for_files_client_id}. New files connection: {addr} connected.")
                print("Waiting for new client...")
                       
    def get_input_thread(self):
        while True:
            msg = input()
            if msg == "exit": 
                print("Server is closing...")
                if self.CLIENTS:
                    print("Clients disconnecting:")
                # self.send_all("exit")
                self.FINISH = True
            elif msg[:4] == "kick":
                try:
                    client = self.CLIENTS[int(msg[5:])]            
                    self.send(client.conn_msgs, "exit")
                except:
                    print("You have to enter available [client_id] after 'kick'.")
            elif msg == "close":
                self.FINISH = True
            elif msg == "threads":
                print(f"\nActive threads: {threading.enumerate()}")
            elif msg == "clients":
                print(f"\nActive connections:")
                for client in self.CLIENTS:
                    if not client == []:
                        print(f"id {self.CLIENTS.index(client)}. {client.ip}")
            elif msg[:4] == "info":
                try:
                    client = self.CLIENTS[int(msg[5:])]
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
        exit = False
        while not exit:
            msg = conn.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
            db_conn = sqlite3.connect('Server.db')
            msg_list = msg.split("|")
            for msg in msg_list:
                if msg:
                    if msg == "exit":
                        exit = True
                        break
                    elif msg[:3] == "reg":
                        msg = msg[4:]
                        login = msg.split()[0]
                        password = msg.split()[1]
                        check = db_conn.execute(f'SELECT password FROM Users WHERE login = "{login}"').fetchone() # check if login has already been used
                        if len(login) < 8 or len(password) < 8:
                            self.send(conn, "In login and password must be 8 or more digits.")
                        elif check:
                            self.send(conn, "This login has already been used.")
                        else:
                            db_conn.execute(f'INSERT INTO Users (login, password, clientId) VALUES("{login}", "{password}", "{client_id}")')
                            db_conn.commit()
                            client = self.CLIENTS[client_id]
                            client.online = True
                            self.send(conn, "online")

                            os.mkdir(f'users/{login}')
                            print(conn, f"Successefuly registered: login - {login}, password - {password}.")
                    elif msg[:6] == "log_in":
                        msg = msg[7:]
                        login = msg.split()[0]
                        password = msg.split()[1]
                        print(f"Logging in: login - {login}, password - {password}...")
                        userId = db_conn.execute(f'SELECT userId FROM Users WHERE login = "{login}" AND password = "{password}"').fetchone()
                        if not userId:
                            self.send(conn, "Login or password is wrong.")
                            print("No such user.")
                        else: 
                            previous_client_id = db_conn.execute(f'SELECT clientId FROM Users WHERE userId = {userId[0]}').fetchone()[0]
                            if not previous_client_id == None:
                                if self.CLIENTS[previous_client_id]:
                                    user_not_online = False
                                    self.send(conn, "This user is already online.")
                                    print("This user is already online.")
                                else:
                                    user_not_online = True
                            else:
                                user_not_online = True
                            if user_not_online:
                                db_conn.execute(f'UPDATE Users SET clientId = {client_id} WHERE userId = {userId[0]}')
                                db_conn.commit()
                                client = self.CLIENTS[client_id]
                                client.online = True

                                self.send(conn, "online")
                                print('Logged in.')
                    if client.online:
                        if msg == "log_out":
                            client.online = False
                            login = db_conn.execute(f'SELECT login FROM Users WHERE clientId = {client_id}').fetchone()[0]
                            print(f'Logged out: login - {login}')
                            db_conn.execute(f'UPDATE Users SET clientId = NULL, openedFilePath = NULL WHERE clientId = {client_id}')
                            db_conn.commit()
                        elif msg[:4] == "file":
                            path = db_conn.execute(f'SELECT openedFilePath FROM Users WHERE clientId = {client_id}').fetchone()[0]
                            self.file_recv(client_id, path)
                            self.files_send_when_accessed(path, client_id, db_conn)
                        elif msg[:3] == "dir":
                            path = msg[4:]
                            user_id = db_conn.execute(f'SELECT userId FROM Users WHERE clientId = {client_id}').fetchone()[0]
                            login = db_conn.execute(f'SELECT login FROM Users WHERE userId = {user_id}').fetchone()[0]
                            dir_list = []
                            if not path:
                                dir_list.append(login)
                                print(path)
                            elif path.split('/')[0] == login:
                                dir_list = os.listdir(f'users/{path}')

                            # adds accessed dirs
                            accessed_files = db_conn.execute(f'SELECT path FROM Accesses WHERE guestId = {user_id}').fetchall()
                            for file_path in accessed_files:
                                if os.path.exists(f'users/{file_path[0]}'):
                                    if file_path[0].startswith(path):
                                        file_path = file_path[0][len(path):]
                                        dir_list.append(file_path.split('/')[0])

                            dir_string = "dir"
                            for dir in dir_list:
                                dir_string += " " + dir
                            self.send(client.conn_msgs, dir_string)
                        elif msg[:4] == "open":
                            path = msg[5:]
                            try:
                                file = open(f'users/{path}', "rb")
                                data = file.read()
                                client.conn_files.sendall(data)
                                client.conn_files.send(b"<END>")
                                file.close()
                                print(path)
                                db_conn.execute(f'UPDATE Users SET openedFilePath = "{path}" WHERE clientId = {client_id}')
                                db_conn.commit()
                            except Exception as e:
                                print('ERROR WITH OPENER')
                                client.conn_files.send(b"<FAIL>")
                        elif msg[:6] == "create":
                            msg = msg[7:]
                            if msg[:6] == "folder":
                                path = msg[7:]
                                try:
                                    os.mkdir(f'users/{path}')
                                except Exception as e:
                                    print(e)
                            elif msg[:4] == "file":
                                path = msg[5:]
                                with open(f'users/{path}', 'w') as file:
                                    pass 
                        elif msg[:6] == "delete":
                            path = msg[7:]
                            self.opened_file_deleted_stop(path, client_id, db_conn)
                            path = f'users/{path}'
                            if path.endswith(".txt"):
                                try:
                                    os.remove(path)
                                except Exception as e:
                                    print(e)
                            else:
                                shutil.rmtree(path, ignore_errors=True)
                        elif msg == "stop":
                            client.conn_files.send(b"<STOP>")
                        elif msg[:6] == "access":
                            msg = msg[7:]
                            if msg[:4] == "give":
                                msg = msg[5:]
                                guest_and_path = msg.split('>')
                                user_id = db_conn.execute(f'SELECT userId FROM Users WHERE login = "{guest_and_path[0]}"').fetchone()
                                if not user_id:
                                    self.send(client.conn_msgs, 'There is no user with such login.')
                                else: 
                                    duplicates = db_conn.execute(f'SELECT guestId FROM Accesses WHERE path = "{guest_and_path[1]}" AND guestId = {user_id[0]}').fetchone()
                                    if duplicates:
                                        self.send(client.conn_msgs, 'This user already has access to this file.')
                                    else:
                                        db_conn.execute(f'INSERT INTO Accesses (path, guestId) VALUES("{guest_and_path[1]}", {user_id[0]})')
                                        db_conn.commit()
                                        self.send(client.conn_msgs, 'Success')
                            elif msg[:6] == "browse":
                                path = msg[7:]
                                guests = db_conn.execute(f'SELECT guestId FROM Accesses WHERE path = "{path}"').fetchall()

                                guests_string = 'guests'
                                for guestId in guests:
                                    guest_login = db_conn.execute(f'SELECT login FROM Users WHERE userId = {guestId[0]}').fetchone()
                                    if guest_login:
                                        guests_string += " " + guest_login[0]

                                self.send(client.conn_msgs, guests_string)
                            elif msg[:6] == "remove":
                                msg = msg[7:]
                                guest_and_path = msg.split('>')
                                user_id = db_conn.execute(f'SELECT userId FROM Users WHERE login = "{guest_and_path[0]}"').fetchone()
                                if not user_id:
                                    self.send(client.conn_msgs, 'There is no user with such login.')
                                else:
                                    db_conn.execute(f'DELETE FROM Accesses WHERE path = "{guest_and_path[1]}" AND guestId = {user_id[0]}')
                                    db_conn.commit()
                                    self.send(client.conn_msgs, 'Success')
            db_conn.close()

        print(f"{client_id}. {client.ip} disconnecting...")
        self.CLIENTS[client_id] = []
        db_conn.close()
        try:
            client.conn_msgs.close()
            client.conn_files.close()
        except:
            pass
        print("handle_msgs_thread stopped.")

    def file_send(self, client_id, path):
        client = self.CLIENTS[client_id]
        if client:
            try:
                file = open(f'users/{path}', "rb")
                data = file.read()
                client.conn_files.sendall(data)
                client.conn_files.send(b"<END>")
                file.close()
            except Exception as e:
                print(e)

    def file_recv(self, client_id, path):
        client = self.CLIENTS[client_id]
        if client:
            file = open(f"users/{path}", "wb")
            fbytes = b""
            while True:
                data = client.conn_files.recv(self.SIZE)
                fbytes += data
                if fbytes[-5:] == b"<END>":
                    fbytes = fbytes[:-5]
                    file.write(fbytes)
                    file.close()
                    break

    def files_send_when_accessed(self, path, who_updated_client_id, db_conn):
        guests_client_ids = db_conn.execute(f'SELECT clientId FROM Users WHERE openedFilePath = "{path}"').fetchall()

        for client_id in guests_client_ids:
            client_id = client_id[0]
            if (not client_id == who_updated_client_id) and (not client_id == None): 
                self.file_send(client_id, path)
            
    def opened_file_deleted_stop(self, path, who_deleted_client_id, db_conn):
        guests_client_ids = db_conn.execute(f'SELECT clientId FROM Users WHERE openedFilePath = "{path}"').fetchall()

        for client_id in guests_client_ids:
            client_id = client_id[0]
            print (client_id)
            if (not client_id == who_deleted_client_id):
                client = self.CLIENTS[client_id] 
                print(f"SENT STOP to id - {client_id}")
                client.conn_files.send(b"<STOP>")

    def send(self, conn, msg):
        conn.send(msg.encode(self.FORMAT, errors= 'ignore'))

    def send_all(self, msg):
        for client in self.CLIENTS:
            if client:
                self.send(client.conn_msgs, msg)

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
    def __init__(self, ip, conn_msgs, conn_files, online=False, files_send_queue=[], files_recv_queue=[]):
        self.ip = ip
        self.conn_msgs = conn_msgs
        self.conn_files = conn_files
        self.online = online
        self.files_send_queue = files_send_queue
        self.files_recv_queue = files_recv_queue

    def info(self):
        print(f"ip: {self.ip}")
        print(f"conn_msgs: connected") #{self.conn_msgs}
        if self.conn_files:
            print(f"conn_files: connected") #{self.conn_files}
        print(f"online: {self.online}") 
        print(f"files_send_queue: {self.files_send_queue}")
        print(f"files_recv_queue: {self.files_recv_queue}")

if __name__ == "__main__":
    Server().main()