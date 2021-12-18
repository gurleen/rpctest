import socket
import json
from pprint import pprint
from boltons.socketutils import BufferedSocket

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ("localhost", 5000)
sock.connect(server_address)
bufsock = BufferedSocket(sock, maxsize=64 ** 2)

payload = {
    "function": "get_friends",
    "args": [],
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.ZT-ypcqw58gj7i_V4PShR0xUfTFz0DRcxf74xGjk49Q",
}

d = json.dumps(payload).encode("utf-8") + b"\r\n"
bufsock.sendall(d)


pprint(json.loads(bufsock.recv_until(b"\r\n").decode("utf-8")))
