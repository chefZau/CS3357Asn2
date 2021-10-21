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

clients = dict()  # clients: { Client Name: Client Connection }


def broadcast(clientName, message):
    """Broadcasts the message to all clients except for the sender

    Args:
        clientName (string): the registered nickname 
        message (string): the sent message
    """
    for name, conn in clients.items():
        formatedMessage = f'@{clientName}: {message}'
        if clientName == '':
            conn.sendall(message.encode(FORMAT))
        elif name != clientName:
            conn.sendall(formatedMessage.encode(FORMAT))


def acceptWrapper(sock):
    """Sign the user up through:
    1. retrieve registered user name from 

    Args:
        sock (socket object): the socket
    """

    # accept connection
    conn, addr = sock.accept()

    conn.setblocking(False)

    print(f'Accepted connection from client address: {addr}')
    
    # retrieves the username from the client
    msg = conn.recv(BUFFER_SIZE).decode(FORMAT)
    username = msg.lstrip('REGISTER ').rstrip(' CHAT/1.0')

    # checks whether the entered nickname is valid
    # checks whether the entered nickname already exists

    validRegistration = True
    controlMsg = '200 Registration successful'
    if 'REGISTER ' not in msg or ' CHAT/1.0' not in msg:
        controlMsg = '400 Invalid registration'
        validRegistration = False
    elif username in clients:
        controlMsg = '401 Client already registered'
        validRegistration = False

    conn.sendall(controlMsg.encode(FORMAT))

    if validRegistration:

        print(
            f'Connection to client estatblished, waiting to reveive messages from user "{username}" ... ')

        clients[username] = conn    # add client to the dicitonary

        # selectors module allows us store data
        # the following code creates the data and stores it
        # using the register method

        data = types.SimpleNamespace(
            addr=addr,
            name=username
        )

        sel.register(conn, selectors.EVENT_READ, data=data)

        print('Number of connected client: ', len(clients))


def performService(key):
    """Retrieve and broadcast the message from the client

    Args:
        key (events): the event key
    """

    conn = key.fileobj
    data = key.data

    message = conn.recv(BUFFER_SIZE).decode(FORMAT)

    if message and 'DISCONNECT' not in message:

        # retrieves the name from the message

        nickname = message.split(':')[0]
        nickname = nickname.lstrip('@')

        # everthing after the ': ' is the actual message

        line = message[message.index(': ') + 1:]

        print(f'Received message from user {data.name}: {line}')

        # broadcast the message to everyone except self
        broadcast(data.name, line)

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

    # create a closure for signalHandler

    def signalHandler(sig, frame):
        """Executed when a user press control + c"""
        print('Interrupt received, shutting down ...')

        disconnectMsg = 'DISCONNECT CHAT/1.0'
        broadcast('', disconnectMsg)

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
