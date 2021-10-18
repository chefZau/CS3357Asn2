#!/usr/bin/env python3

import socket
import argparse
import signal
from urllib.parse import urlparse
import sys

FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

BUFFER_SIZE = 2048

active = True


def signalHandler(sig, frame):
    active = False
    print('Interrupt received, shutting down ...')
    sys.exit(0)


def main():

    # Register our signal handler for shutting down.
    signal.signal(signal.SIGINT, signalHandler)

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Host name of server")
    parser.add_argument("address", help="Port number of server")

    args = parser.parse_args()
    name = args.name
    address = args.address

    parsedURL = urlparse(address)
    ADDR = (parsedURL.hostname, parsedURL.port)

    print('Connecting to server ...')

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    client.sendall(f'USERNAME:{name}'.encode(FORMAT))

    msg = 'Connection to server established. Sending intro message...\nRegistration successful.  Ready for messageing!\n'
    print(msg)

    while active:

        line = input('>')

        client.send(line.rstrip().encode(FORMAT))

        msg = client.recv(BUFFER_SIZE).decode(FORMAT)
        if msg:
            print(msg)

    client.close()


if __name__ == '__main__':
    main()
