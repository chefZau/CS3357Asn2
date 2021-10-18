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
DISCONNECT_MESSAGE = "!DISCONNECT"

BUFFER_SIZE = 2048

sel = selectors.DefaultSelector()

# clients: { clientName: clientConnection }
clients = dict()


def signalHandler(sig, frame):
    print('Interrupt received, shutting down ...')
    sys.exit(0)


def broadcast(clientName, message):
    for name, conn in clients.items():
        formatedMessage = f'@{clientName}: {message}'
        if name != clientName:
            conn.sendall(formatedMessage.encode(FORMAT))


def acceptWrapper(sock):

    # accept connection
    conn, addr = sock.accept()

    print(f'Accepted connection from client address: {addr}')
    conn.setblocking(False)

    msg = conn.recv(BUFFER_SIZE).decode(FORMAT)
    username = msg.lstrip('USERNAME:')

    print(
        f'Connection to client estatblished, waiting to reveive messages from user "{username}" ... ')
 
    # add client to the dicitonary
    clients[username] = conn

    data = types.SimpleNamespace(
        addr=addr,
        inb=b'',
        outb=b'',
        name=username
    )

    sel.register(conn, selectors.EVENT_READ, data=data)

    print('number of connected client: ', len(clients))


def performService(key):

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

    # Register our signal handler for shutting down.
    signal.signal(signal.SIGINT, signalHandler)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print('Will wait for client messages at port ' +
          str(server.getsockname()[1]))

    server.listen()
    server.setblocking(False)

    sel.register(server, selectors.EVENT_READ)

    print('Waiting for incoming client connections ...')

    while True:

        events = sel.select(timeout=None)
        for key, mask in events:

            if key.data is None:
                acceptWrapper(key.fileobj)
            else:
                performService(key)


if __name__ == '__main__':
    main()
