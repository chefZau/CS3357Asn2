import socket
import os
import signal
import sys
import selectors

# Selector for helping us select incoming data and connections from multiple sources.

sel = selectors.DefaultSelector()

# Client list for mapping connected clients to their connections.
# It is a list of tuples; Each tuple has a format of (client name, client connection)

client_list = []


def signal_handler(sig, frame):
    """Signal handler for graceful exiting.
    Let clients know in the process so they can disconnect too.

    Args:
        sig ([type]): [description]
        frame ([type]): [description]
    """
    
    print('Interrupt received, shutting down ...')
    message = 'DISCONNECT CHAT/1.0\n'
    for reg in client_list:
        reg[1].send(message.encode())
    sys.exit(0)


def get_line_from_socket(sock):
    """Reads a single line (ending with \n) from a socket and return it.
    We will strip out the \r and the \n in the process.

    Args:
        sock (socket): the client socket

    Returns:
        (string) : the cleaned line
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


def client_search(user):
    """Search the client list for a particular user.

    Args:
        user (string): the user name of a user

    Returns:
        [socket]: if name exists, return socket otherwise None
    """
    
    for reg in client_list:
        if reg[0] == user:
            return reg[1]
    return None


def client_search_by_socket(sock):
    """Search the client list for a particular user by their socket.

    Args:
        sock (socket): the socket of a client

    Returns:
        [string]: if socket exists, return name otherwise None
    """
    for reg in client_list:
        if reg[1] == sock:
            return reg[0]
    return None


def client_add(user, conn):
    """Add a user to the client list.
    Creates a tuple in a format of (client name, client socket).
    Stores the tuple in to a list.
    
    Args:
        user (string): the name of a client
        conn (socket): the socket of a user
    """
    registration = (user, conn)
    client_list.append(registration)


def client_remove(user):
    """Remove a client when disconnected.

    Args:
        user (string): the registered username of a client
    """
    for reg in client_list:
        if reg[0] == user:
            client_list.remove(reg)
            break


def read_message(sock, mask):
    """Function to read messages from clients.

    Args:
        sock (socket): the socket of a client
        mask (boolean): selectors.EVENT_READ | selectors.EVENT_WRITE
    """
    
    message = get_line_from_socket(sock)

    # Does this indicate a closed connection?

    if message == '':
        print('Closing connection')
        sel.unregister(sock)
        sock.close()

    # Receive the message.

    else:
        user = client_search_by_socket(sock)
        print(f'Received message from user {user}:  ' + message)
        words = message.split(' ')

        # Check for client disconnections.

        if words[0] == 'DISCONNECT':
            print('Disconnecting user ' + user)
            client_remove(user)
            sel.unregister(sock)
            sock.close()

        # Send message to all users.  Send at most only once, and don't send to yourself.
        # Need to re-add stripped newlines here.

        else:
            for reg in client_list:
                if reg[0] == user:
                    continue
                client_sock = reg[1]
                forwarded_message = f'{message}\n'
                client_sock.send(forwarded_message.encode())


def accept_client(sock, mask):
    """Function to accept and set up clients.

    Args:
        sock (socket): the client socket
        mask (boolean): selectors.EVENT_READ | selectors.EVENT_WRITE
    """

    conn, addr = sock.accept()
    print('Accepted connection from client address:', addr)
    message = get_line_from_socket(conn)
    message_parts = message.split()

    # Check format of request.

    if ((len(message_parts) != 3) or (message_parts[0] != 'REGISTER') or (message_parts[2] != 'CHAT/1.0')):
        print('Error:  Invalid registration message.')
        print('Received: ' + message)
        print('Connection closing ...')
        response = '400 Invalid registration\n'
        conn.send(response.encode())
        conn.close()

    # If request is properly formatted and user not already listed, go ahead with registration.

    else:
        user = message_parts[1]

        if (client_search(user) == None):
            client_add(user, conn)
            print(
                f'Connection to client established, waiting to receive messages from user \'{user}\'...')
            response = '200 Registration succesful\n'
            conn.send(response.encode())
            conn.setblocking(False)
            sel.register(conn, selectors.EVENT_READ, read_message)

        # If user already in list, return a registration error.

        else:
            print('Error:  Client already registered.')
            print('Connection closing ...')
            response = '401 Client already registered\n'
            conn.send(response.encode())
            conn.close()


def main():
    """Our main function.
    """

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Create the socket.  We will ask this to work on any interface and to pick
    # a free port at random.  We'll print this out for clients to use.

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 0))
    print('Will wait for client connections at port ' +
          str(server_socket.getsockname()[1]))
    server_socket.listen(100)
    server_socket.setblocking(False)
    sel.register(server_socket, selectors.EVENT_READ, accept_client)
    print('Waiting for incoming client connections ...')

    # Keep the server running forever, waiting for connections or messages.

    while(True):
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)


if __name__ == '__main__':
    main()
