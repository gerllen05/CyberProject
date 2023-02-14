import socket
IP = "0.0.0.0"
PORT = 25565
ADDR = (IP, PORT)

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
for port in range(0, 65535):
    print (f"Port {port} is open")
    result = SERVER.connect_ex(("0.0.0.0", port))
    print(result)
    # if result == 0:
    #     ADDR = (IP, PORT)
    #     print (f"Port {port} is open")
    #     break
    # else:
    #     print('YAUHUSGYDAISYUDI')