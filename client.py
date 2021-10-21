#!/usr/bin/env python3

from urllib.parse import urlparse
import selectors
import argparse
import socket
import signal
import fcntl
import sys
import os

FORMAT = 'utf-8'
BUFFER_SIZE = 2048

# create default selector for handling multiple IO
sel = selectors.DefaultSelector()

# set input non-blocking
origFl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
fcntl.fcntl(sys.stdin, fcntl.F_SETFL, origFl | os.O_NONBLOCK)

# the variable checks whether the client is signed in or not
signIn = False

# sotres their username globally
username = None


def getArgs():
    """Gets and parses user's concole input

    Returns:
        [string]: [the registered name]
        [string]: [the host name]
        [string]: [the port]
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Host name of server")
    parser.add_argument("address", help="Port number of server")

    args = parser.parse_args()
    name = args.name
    address = args.address

    parsedURL = urlparse(address)

    return name, parsedURL.hostname, parsedURL.port


def read(sock):
    """Retrieves server data and print it to console

    Args:
        sock (socket): the current socket/connection
    """
    msg = sock.recv(BUFFER_SIZE).decode(FORMAT)

    if msg:

        # When a client opens the app for the first time, the app will send
        # their entered nickname to the server. The server has three return options:
        # 1. 200 Registration successful
        # 2. 401 Client already registered
        # 3. 400 Invalid registration
        # The following if-else block checks whether the received message
        # contains the above control message. If there isn't a control
        # message, print it out to the console.

        if msg == '200 Registration successful':

            msg = 'Connection to server established. Sending intro message...\nRegistration successful.  Ready for messageing!\n'
            print(msg)

            # the variable checks whether the client is signed in or not
            # (registered successfully), since the nickname is available
            # we turn it to True

            global signIn
            signIn = True

            # asks client for console input
            sel.register(sys.stdin, selectors.EVENT_READ, getStdinInput)

        elif msg in ['401 Client already registered', '400 Invalid registration', 'DISCONNECT CHAT/1.0']:
            print(f'\n{msg} ... Please try again later ')
            sel.unregister(sock)
            sock.close()
            sys.exit(0)

        else:
            print()
            print(msg)

    else:
        print('\nDisconnected from server ... exiting!')
        sel.unregister(sock)
        sock.close()
        sys.exit(0)


def getStdinInput(stdin, conn):
    """Read user input from stdin, and send it to the server

    Args:
        stdin (sys.stdin): standard input object
        conn (the socket): the socket
    """
    line = stdin.read()
    formattedMsg = f'@{username}: {line}'
    conn.send(formattedMsg.rstrip().encode(FORMAT))


def main():

    # retrieves the arguments from the console

    NAME, HOST, PORT = getArgs()
    ADDR = (HOST, PORT)

    global username
    username = NAME

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    client.setblocking(False)

    # Register our signal handler for shutting down.
    def signalHandler(sig, frame):
        """Executed when a user press control + c"""
        formattedMsg = f'DISCONNECT {username} CHAT/1.0'
        client.sendall(formattedMsg.encode(FORMAT))
        print('Interrupt received, shutting down ...')
        sys.exit(0)

    signal.signal(signal.SIGINT, signalHandler)

    registrationMsg = f'REGISTER {NAME} CHAT/1.0'
    client.sendall(registrationMsg.encode(FORMAT))

    print('Connecting to server ...')

    sel.register(client, selectors.EVENT_READ, read)

    while True:

        # prompts (displays '>' sign) client input only if they are registered

        if signIn:
            sys.stdout.write('> ')
            sys.stdout.flush()

        for k, _ in sel.select(timeout=None):

            # notice that k.data here is a function,
            # since in Python, functions are first-class citizens
            # we can assign it to a variable

            callback = k.data

            if callback == getStdinInput:
                callback(k.fileobj, client)
            else:
                callback(k.fileobj)


if __name__ == '__main__':
    main()
