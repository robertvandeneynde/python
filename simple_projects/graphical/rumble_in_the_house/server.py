# Echo server program
import socket

import sys
if sys.vernum < (3,):
    input = raw_input

HOST = input("Host ? (default '')") or ''    # Symbolic name meaning all available interfaces
PORT = input("Port ?") or 50007              # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()

print('Connected by {}'.format(addr))

while True:
    data = conn.recv(1024)
    if not data:
        break
    conn.send(data)
conn.close()