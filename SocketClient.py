"""Creates a python socket client that will interact with javascript."""
import socket

address = ('localhost', 5050)
#socket_path = '/tmp/node-python-sock'
# connect to the unix local socket with a stream type
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(address)
# send an initial message (as bytes)
client.send(b'python connected')
# start a loop
while True:
    # wait for a response and decode it from bytes
    msg = client.recv(2048).decode('utf-8')
    print(msg)
    if msg == 'hi':
        client.send(b'hello')
    elif msg == 'end':
        # exit the loop
        break

# close the connection
client.close()
