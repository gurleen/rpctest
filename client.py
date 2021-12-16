import socket
import json
from pprint import pprint
from boltons.socketutils import BufferedSocket

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 5000)
sock.connect(server_address)
bufsock = BufferedSocket(sock, maxsize=64 ** 2)

payload = {
    "function": "login",
    "args": ["gurleen", "fdsnkl"]
}

d = json.dumps(payload).encode("utf-8") + b"\r\n"
bufsock.sendall(d)


pprint(json.loads(bufsock.recv_until(b"\r\n").decode("utf-8")))