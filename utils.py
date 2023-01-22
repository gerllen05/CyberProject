import threading
import socket

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

def file_recv(self, conn):
    path = conn.recv(self.SIZE).decode(self.FORMAT, errors= 'ignore')
    print(f"File '{path}' started downloading...")
    file = open(f'{path}', "wb")
    fbytes = b""
    while True:
        data = conn.recv(self.SIZE)
        fbytes += data
        if fbytes[-5:] == b"<END>":
            fbytes = fbytes[:-5]
            file.write(fbytes)
            break
    file.close()

def send(self, conn, msg):
    conn.send(msg.encode(self.FORMAT, errors= 'ignore'))