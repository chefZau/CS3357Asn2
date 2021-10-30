import socket
import os
import signal
import sys
import argparse
from urllib.parse import urlparse
import selectors

# Selector for helping us select incoming data from the server and messages typed in by the user.

sel = selectors.DefaultSelector()

# Socket for sending messages.

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# User name for tagging sent messages.

user = ''


def signal_handler(sig, frame):
    """Signal handler for graceful exiting.  
    Let the server know when we're gone.

    Args:
        sig ([type]): [description]
        frame ([type]): [description]
    """
    print('Interrupt received, shutting down ...')
    message = f'DISCONNECT {user} CHAT/1.0\n'
    client_socket.send(message.encode())
    sys.exit(0)


def do_prompt(skip_line=False):
    """Simple function for setting up a prompt for the user.

    Args:
        skip_line (bool, optional): [description]. Defaults to False.
    """
    if (skip_line):
        print("")
    print("> ", end='', flush=True)


def get_line_from_socket(sock):
    """Read a single line (ending with \n) from a socket and return it.
    We will strip out any \r and \n in the process.

    Args:
        sock ([type]): [description]

    Returns:
        [type]: [description]
    """

    done = False
    line = ''
    while (not done):
        char = sock.recv(1).decode()
        if (char == '\r'):
            pass
        elif (char == '\n'):
            done = True
        else:
            line = line + char
    return line


def handle_message_from_server(sock, mask):
    """Handles incoming messages from server.  Also look for 
    disconnect messages to shutdown.

    Args:
        sock ([type]): [description]
        mask ([type]): [description]
    """
    message = get_line_from_socket(sock)
    words = message.split(' ')
    print()
    if words[0] == 'DISCONNECT':
        print('Disconnected from server ... exiting!')
        sys.exit(0)
    else:
        print(message)
        do_prompt()


def handle_keyboard_input(file, mask):
    """Handles incoming messages from user.

    Args:
        file ([type]): [description]
        mask ([type]): [description]
    """
    line = sys.stdin.readline()
    message = f'@{user}: {line}'
    client_socket.send(message.encode())
    do_prompt()


def main():
    """Our main function.

    Raises:
        ValueError: [description]
    """

    global user
    global client_socket

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments to retrieve a URL.

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "user", help="user name for this user on the chat service")
    parser.add_argument(
        "server", help="URL indicating server location in form of chat://host:port")
    args = parser.parse_args()

    # Check the URL passed in and make sure it's valid.  If so, keep track of
    # things for later.

    try:
        server_address = urlparse(args.server)
        if ((server_address.scheme != 'chat') or (server_address.port == None) or (server_address.hostname == None)):
            raise ValueError
        host = server_address.hostname
        port = server_address.port
    except ValueError:
        print('Error:  Invalid server.  Enter a URL of the form:  chat://host:port')
        sys.exit(1)
    user = args.user

    # Now we try to make a connection to the server.

    print('Connecting to server ...')
    try:
        client_socket.connect((host, port))
    except ConnectionRefusedError:
        print('Error:  That host or port is not accepting connections.')
        sys.exit(1)

    # The connection was successful, so we can prep and send a registration message.

    print('Connection to server established. Sending intro message...\n')
    message = f'REGISTER {user} CHAT/1.0\n'
    client_socket.send(message.encode())

    # Receive the response from the server and start taking a look at it

    response_line = get_line_from_socket(client_socket)
    response_list = response_line.split(' ')

    # If an error is returned from the server, we dump everything sent and
    # exit right away.

    if response_list[0] != '200':
        print('Error:  An error response was received from the server.  Details:\n')
        print(response_line)
        print('Exiting now ...')
        sys.exit(1)
    else:
        print('Registration successful.  Ready for messaging!')

    # Set up our selector.

    client_socket.setblocking(False)
    sel.register(client_socket, selectors.EVENT_READ,
                 handle_message_from_server)
    sel.register(sys.stdin, selectors.EVENT_READ, handle_keyboard_input)

    # Prompt the user before beginning.

    do_prompt()

    # Now do the selection.

    while(True):
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)


if __name__ == '__main__':
    main()
