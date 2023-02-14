import socket
import threading
import time
import os
import sqlite3
import shutil
from bcrypt import hashpw, checkpw, gensalt
from datetime import datetime

class Server:
    IP = "0.0.0.0"
    PORT = 25565
    ADDR = (IP, PORT)
    SERVER = ()
    SIZE = 4096
    FORMAT = "utf-8"
    
    CLIENTS = []
    FINISH = False

    def main(self):
        db_conn = sqlite3.connect('Server.db')
        self.create_db(db_conn)
        db_conn.execute(f'UPDATE Users SET clientId = NULL, openedFilePath = NULL')
        db_conn.commit()
        db_conn.close()
        
        print("\nStarting server...")

        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print(hostname, ':', ip_address)
        self.IP = ip_address

        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.bind(self.ADDR)
        self.SERVER.listen()

        print(f"Listening: {self.IP}:{self.PORT}")

        try:
            os.mkdir(f'users')
        except:
            pass

        create_thread(self.new_client_thread)
        # create_thread(self.get_input_thread)

        #when the loop finishes, all daemon threads will close
        while not self.FINISH:
            time.sleep(0.1)
        
        print("Server closed.")

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
            if msg == "close":
                print("Closing server...")
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
                    print("You have to enter available [client_id] after 'info'.")
            elif msg == "help":
                print("Here are all available commands:")
                print("- close --> closes only server")
                print("- threads --> shows all threads")
                print("- clients --> shows list of all clients, [client_id] is index of the client")
                print("- info [client_id] --> shows list of all client properties")
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
                    if msg == "exit": # when the app is closed
                        exit = True
                        break
                    elif msg[:3] == "reg": # when client registers a new account
                        msg = msg[4:]
                        login = msg.split()[0]
                        password = msg.split()[1]
                        check = db_conn.execute(f'SELECT password FROM Users WHERE login = "{login}"').fetchone() # check if login has already been used
                        if len(login) < 8 or len(password) < 8:
                            self.send(conn, "In login and password must be 8 or more digits.")
                        elif check:
                            self.send(conn, "This login has already been used.")
                        else:
                            now = datetime.now()
                            time_str = now.strftime("%d/%m/%Y-%H:%M:%S")
                            hashed_password = hashpw(password.encode(self.FORMAT), gensalt(5)).decode(self.FORMAT)

                            db_conn.execute(f'INSERT INTO Users (login, password, regTime) VALUES("{login}", "{hashed_password}", "{time_str}")')
                            db_conn.commit()
                            client = self.CLIENTS[client_id]
                            client.online = True
                            self.send(conn, "online")

                            os.mkdir(f'users/{login}')
                            print(f"{client_id}. Successefuly registered: login - {login}, password - {password}.")
                    elif msg[:6] == "log_in": # when client logs in to an existing account
                        msg = msg[7:]
                        login = msg.split()[0]
                        password = msg.split()[1]
                        print(f"Logging in: login - {login}, password - {password}...")
                        hashed_password = db_conn.execute(f'SELECT password FROM Users WHERE login = "{login}"').fetchone()
                        if not hashed_password:
                            self.send(conn, "There is no user with such login and password.")
                            print(f"{client_id}. There is no user with login - {login}.")
                        elif not checkpw(password.encode(self.FORMAT), hashed_password[0].encode(self.FORMAT)):
                            self.send(conn, "There is no user with such login and password.")
                            print(f"{client_id}. The password - {password} for user with login - {login} is wrong.")
                        else: 
                            user_id = db_conn.execute(f'SELECT userId FROM Users WHERE login = "{login}" AND password = "{hashed_password[0]}"').fetchone()[0]
                            previous_client_id = db_conn.execute(f'SELECT clientId FROM Users WHERE userId = {user_id}').fetchone()[0]
                            if not previous_client_id == None:
                                if self.CLIENTS[previous_client_id]:
                                    user_not_online = False
                                    self.send(conn, "This user is already online.")
                                    print(f"{client_id}. This user is already online.")
                                else:
                                    user_not_online = True
                            else:
                                user_not_online = True
                            if user_not_online:
                                now = datetime.now()
                                time_str = now.strftime("%d/%m/%Y-%H:%M:%S")

                                db_conn.execute(f'UPDATE Users SET clientId = {client_id}, lastLogInTime = "{time_str}" WHERE userId = {user_id}')
                                db_conn.commit()
                                client = self.CLIENTS[client_id]
                                client.online = True

                                self.send(conn, "online")
                                print(f'{client_id}. Logged in.')
                    if client.online:
                        if msg == "log_out": # when client logs out
                            client.online = False
                            login = db_conn.execute(f'SELECT login FROM Users WHERE clientId = {client_id}').fetchone()[0]
                            print(f'{client_id}. Logged out: login - {login}')
                            db_conn.execute(f'UPDATE Users SET clientId = NULL, openedFilePath = NULL WHERE clientId = {client_id}')
                            db_conn.commit()
                        elif msg[:3] == "dir": # when client's directory listbox opens and client wants to browse accessed directories
                            path = msg[4:]
                            user_id = db_conn.execute(f'SELECT userId FROM Users WHERE clientId = {client_id}').fetchone()[0]
                            login = db_conn.execute(f'SELECT login FROM Users WHERE userId = {user_id}').fetchone()[0]
                            login = str(login)
                            dir_list = []
                            if not path:
                                dir_list.append(login)
                            elif path.split('/')[0] == login:
                                try:
                                    dir_list = os.listdir(f'users/{path}')
                                except Exception as e:
                                    print(e)

                            # adds accessed dirs
                            accessed_files = db_conn.execute(f'SELECT path FROM Accesses WHERE guestId = {user_id}').fetchall()
                            for file_path in accessed_files:
                                if os.path.exists(f'users/{file_path[0]}'):
                                    if file_path[0].startswith(path):
                                        file_path = file_path[0][len(path):]
                                        needed_dir = file_path.split('/')[0]
                                        if dir_list.count(needed_dir) == 0:
                                            dir_list.append(needed_dir)

                            dir_string = "dir"
                            for dir in dir_list:
                                dir_string += " " + str(dir)
                            self.send(client.conn_msgs, dir_string)
                        elif msg[:4] == "open": # when client opens choosed file
                            path = msg[5:]
                            try:
                                file = open(f'users/{path}', "rb")
                                data = file.read()
                                client.conn_files.sendall(data)
                                client.conn_files.send(b"<END>")
                                file.close()
                                print(f"{client_id}. Opened {path}")
                                db_conn.execute(f'UPDATE Users SET openedFilePath = "{path}" WHERE clientId = {client_id}')
                                db_conn.commit()
                            except Exception as e:
                                print(f"{client_id}. ERROR WITH OPENER")
                                client.conn_files.send(b"<FAIL>")
                        elif msg[:4] == "file": # when client sends opened changed file 
                            path = db_conn.execute(f'SELECT openedFilePath FROM Users WHERE clientId = {client_id}').fetchone()[0]
                            self.file_recv(client_id, path)
                            self.files_send_when_accessed(path, client_id, db_conn)
                        elif msg == "stop": # when client closes file
                            client.conn_files.send(b"<STOP>")
                            self.send(client.conn_msgs, "!stop")
                            db_conn.execute(f'UPDATE Users SET openedFilePath = NULL WHERE clientId = {client_id}')
                            db_conn.commit()
                        elif msg[:6] == "create": # when client creates new folder or file
                            msg = msg[7:]
                            if msg[:6] == "folder": # folder
                                path = msg[7:]
                                try:
                                    os.mkdir(f'users/{path}')
                                except Exception as e:
                                    print(e)
                            elif msg[:4] == "file": # file
                                path = msg[5:]
                                with open(f'users/{path}', 'w') as file:
                                    pass 
                        elif msg[:6] == "delete": # when client deletes folder or file (works only if it was created by them)
                            msg = msg[7:]
                            if msg[:6] == "folder": # folder
                                path = msg[7:]
                                current_len = len(path.split('/')[-2])
                                new_path = path[:len(path) - current_len - 1]
                                print('new_path = ', new_path)
                                self.opened_folder_deleted_stop(path, new_path, client_id, db_conn)
                                path = f'users/{path}'
                                shutil.rmtree(path, ignore_errors=True)
                            elif msg[:4] == "file": #file
                                path = msg[5:]
                                self.opened_file_deleted_stop(path, '!stop', client_id, db_conn)
                                path = f'users/{path}'
                                try:
                                    os.remove(path)
                                except Exception as e:
                                    print(e)
                            elif msg[:7] == "account":
                                client.online = False
                                login = msg[8:]
                                self.opened_folder_deleted_stop(login+'/', '', client_id, db_conn)
                                shutil.rmtree(f'users/{login}', ignore_errors=True)
                                user_id = db_conn.execute(f'SELECT userId FROM Users WHERE clientId = "{client_id}"').fetchone()[0]
                                db_conn.execute(f'DELETE FROM Accesses WHERE creatorId = {user_id} OR guestId = {user_id}')
                                db_conn.execute(f'DELETE FROM Users WHERE userId = {user_id}')
                                db_conn.commit()
                                print(f'{client_id}. Account deleted: login - {login}')
                        elif msg[:6] == "access": # when client manages access (works only on files)
                            msg = msg[7:]
                            if msg[:4] == "give": # gives access to another user
                                msg = msg[5:]
                                guest_and_path = msg.split('>')
                                guest_login = guest_and_path[0]
                                path = guest_and_path[1]
                                creator_login = path.split('/')[0]
                                creator_id = db_conn.execute(f'SELECT userId FROM Users WHERE login = "{creator_login}"').fetchone()[0]
                                user_id = db_conn.execute(f'SELECT userId FROM Users WHERE login = "{guest_login}"').fetchone()
                                if not user_id:
                                    self.send(client.conn_msgs, 'There is no user with such login.')
                                else: 
                                    duplicates = db_conn.execute(f'SELECT guestId FROM Accesses WHERE guestId = {user_id[0]} AND path = "{path}"').fetchone()
                                    if duplicates:
                                        self.send(client.conn_msgs, 'This user already has access to this file.')
                                    else:
                                        db_conn.execute(f'INSERT INTO Accesses (creatorId, guestId, path) VALUES({creator_id}, {user_id[0]}, "{path}")')
                                        db_conn.commit()
                                        self.send(client.conn_msgs, 'Success')
                            elif msg[:6] == "browse": # browses accesses to another users
                                path = msg[7:]
                                guests = db_conn.execute(f'SELECT guestId FROM Accesses WHERE path = "{path}"').fetchall()

                                guests_string = 'guests'
                                for guestId in guests:
                                    guest_login =  db_conn.execute(f'SELECT login FROM Users WHERE userId = {guestId[0]}').fetchone()
                                    if guest_login:
                                        guests_string += " " + str(guest_login[0])

                                self.send(client.conn_msgs, guests_string)
                            elif msg[:6] == "remove": # removes another user's access
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
        print(f"{client_id}. handle_msgs_thread stopped.")

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

    def opened_folder_deleted_stop(self, path, new_path, who_deleted_client_id, db_conn):
        dir_list = os.listdir(f'users/{path}')
        for item in dir_list:
            path += item
            if not item.endswith('.txt'):
                self.opened_folder_deleted_stop(f'{path}/', new_path, who_deleted_client_id, db_conn)
            else:
                self.opened_file_deleted_stop(path, new_path, who_deleted_client_id, db_conn)
            
    def opened_file_deleted_stop(self, path, new_path, who_deleted_client_id, db_conn):
        db_conn.execute(f'DELETE FROM Accesses WHERE path = "{path}"')
        db_conn.commit()
        guests_client_id = db_conn.execute(f'SELECT clientId FROM Users WHERE openedFilePath = "{path}"').fetchall()

        for client_id in guests_client_id:
            client_id = client_id[0]
            if (not client_id == who_deleted_client_id):
                client = self.CLIENTS[client_id] 
                db_conn.execute(f'UPDATE Users SET openedFilePath = NULL WHERE clientId = {client_id}')
                client.conn_files.send(b"<STOP>")
                self.send(client.conn_msgs, new_path)

    def send(self, conn, msg):
        conn.send(msg.encode(self.FORMAT, errors= 'ignore'))

    def create_db(self, db_conn):
        db_conn.execute('''CREATE TABLE IF NOT EXISTS Users (
            userId INTEGER PRIMARY KEY AUTOINCREMENT ,
            login STRING NOT NULL ,
            password STRING NOT NULL ,
            clientId INTEGER ,
            openedFilePath STRING ,
            regTime STRING NOT NULL ,
            lastLogInTime STRING )''')
        db_conn.execute('''CREATE TABLE IF NOT EXISTS Accesses (
            creatorId INTEGER NOT NULL ,
            guestId INTEGER NOT NULL ,
            path STRING NOT NULL ,
            FOREIGN KEY (creatorId) REFERENCES Users (userId) ,
            FOREIGN KEY (guestId) REFERENCES Users (userId) )''')

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

if __name__ == "__main__":
    Server().main()