#!/usr/bin/env python3

import selectors
import socket
import signal
import types
import sys

PORT = 0
SERVER = socket.gethostbyname(socket.gethostname())  # get the IP by name
ADDR = (SERVER, PORT)

FORMAT = 'utf-8'
BUFFER_SIZE = 2048

sel = selectors.DefaultSelector()

# clients: { client Name: client Connection }
clients = dict()

def broadcast(clientName, message):
    """Broadcasts the message to all clients except for the sender

    Args:
        clientName (string): the registered nickname 
        message (string): the sent message
    """
    for name, conn in clients.items():
        formatedMessage = f'@{clientName}: {message}'
        if name != clientName:
            conn.sendall(formatedMessage.encode(FORMAT))


def acceptWrapper(sock):
    """Sign the user up through:
    1. retrieve registered user name from 

    Args:
        sock (socket object): the socket
    """

    # accept connection
    conn, addr = sock.accept()

    print(f'Accepted connection from client address: {addr}')

    conn.setblocking(False)

    # retrieves the username from the client
    msg = conn.recv(BUFFER_SIZE).decode(FORMAT)
    username = msg.lstrip('USERNAME:')

    print(
        f'Connection to client estatblished, waiting to reveive messages from user "{username}" ... ')

    # add client to the dicitonary
    clients[username] = conn

    data = types.SimpleNamespace(
        addr=addr,
        name=username
    )

    sel.register(conn, selectors.EVENT_READ, data=data)

    print('number of connected client: ', len(clients))


def performService(key):
    """Retrieve and broadcast the message from the client

    Args:
        key (events): the event key
    """

    conn = key.fileobj
    data = key.data

    message = conn.recv(BUFFER_SIZE).decode(FORMAT)

    if message:
        print(f'Received message from user {data.name}: {message}')
        broadcast(data.name, message)

    else:
        print(
            f'Received message from user {data.name}: DISCONNECT {data.name} CHAT/1.0')
        print('Disconnecting user', data.name)
        clients.pop(data.name, None)
        print(f'new connected client size: {len(clients)}')
        sel.unregister(conn)
        conn.close()


def main():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print('Will wait for client messages at port ' +
          str(server.getsockname()[1]))

    server.listen()
    server.setblocking(False)

    sel.register(server, selectors.EVENT_READ)
    
    def signalHandler(sig, frame):
        """Executed when a user press control + c"""
        print('Interrupt received, shutting down ...')
        server.close()
        sys.exit(0)

    # Register our signal handler for shutting down.
    signal.signal(signal.SIGINT, signalHandler)

    print('Waiting for incoming client connections ...')

    while True:

        events = sel.select(timeout=None)
        for key, _ in events:

            if key.data is None:
                acceptWrapper(key.fileobj)
            else:
                performService(key)


if __name__ == '__main__':
    main()
