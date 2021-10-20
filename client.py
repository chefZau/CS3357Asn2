#!/usr/bin/env python3

import socket
import argparse
import signal
from urllib.parse import urlparse
import sys
import fcntl
import os
import selectors

FORMAT = 'utf-8'
BUFFER_SIZE = 2048

# set input non blocking
sel = selectors.DefaultSelector()
origFl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
fcntl.fcntl(sys.stdin, fcntl.F_SETFL, origFl | os.O_NONBLOCK)


def signalHandler(sig, frame):
    """Executed when a user press control + c"""
    print('Interrupt received, shutting down ...')
    sys.exit(0)


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
    conn.send(line.rstrip().encode(FORMAT))


def main():

    # Register our signal handler for shutting down.
    signal.signal(signal.SIGINT, signalHandler)

    NAME, HOST, PORT = getArgs()
    ADDR = (HOST, PORT)

    print('Connecting to server ...')

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    client.setblocking(False)

    client.sendall(f'USERNAME:{NAME}'.encode(FORMAT))

    msg = 'Connection to server established. Sending intro message...\nRegistration successful.  Ready for messageing!\n'
    print(msg)

    sel.register(client, selectors.EVENT_READ, read)
    sel.register(sys.stdin, selectors.EVENT_READ, getStdinInput)

    try:
        while True:
            sys.stdout.write('> ')
            sys.stdout.flush()
            for k, _ in sel.select(timeout=None):
                callback = k.data
                if callback == getStdinInput:
                    callback(k.fileobj, client)
                else:
                    callback(k.fileobj)
    finally:
        sel.unregister(sys.stdin)
        client.close()
        sel.close()


if __name__ == '__main__':
    main()
