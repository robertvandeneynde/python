# Echo client program
import socket

import sys
if sys.vernum < (3,):
    input = raw_input

HOST = input("Host ?") or "127.0.0.1"    # The remote host
PORT = input("Port ?") or 50007          # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send('Hello, world')
data = s.recv(1024)
s.close()

print('Received {}'.format(data))