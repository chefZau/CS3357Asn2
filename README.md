# CS3357 Assignment 2 - Implementing a Python Çhat Room

## by Luca(MingCong) Zhou

Implement in Python a simple client-server chat program. The general purpose of this assignment is to gain network programming experience in:

1. writing networked applications.
2. using the socket API in Python.
3. writing software supporting a simple protocol.

## Hardware Required

As mentioned by the professor in the email: "Please note that under Windows, at least some versions of Python on some versions of Windows don't like using sys.stdin with selectors. It does work fine under Linux and Mac, however, so you should be able to use the same environment used for Assignment #1 if you run into troubles with this under Windows.", therefore, I recommend using either Mac or Linux to test the program.

## How It Works

Detailed instructions have been illustrated on OWL. For your convenience, here is a quick explanation. There are two files in this assignment: **client.py** and **server.py**. As their name suggests, **server.py** is for starting the server and handling incoming requests, whereas **client.py** is responsible for taking client input at the console and communicating with the server.

## Set it up

### Step 1: Get Your IP Address

You need to know your local IP address. For simplicity, I recommend using `localhost` instead.

To know your IP address:

- If you are a Mac user: use `ifconfig` at your terminal.
- If you are a Windows user: use `ipconfig` at your Command Prompt.

### Step 2: Start the Server

To start a server, use the following script:

```python
python3 server.py
```

When a the server starts, it will output a port number in the console. Record this number, we will use it to register a client.

```text
Will wait for client messages at port 64700   <---- this one
Waiting for incoming client connections ...
```

### Step 3: Create the Client

To create a client, type in the following command in your console:

```python
python3 client.py <username> chat://<host>:<port>
```

1. Replace `<username>` with your prefer username.
2. Enter an address:
   1. Replace `<host>` with `localhost` or your IP address.
   2. Replace `<port>` with the recorded port: `64700`.

Here is an example of the command:

```python
python3 client.py luca chat://localhost:64700
```

### Step 4: Ready to chat

When you see the '>' sign, you are ready to chat! Type in your message and press enter on your keyboard to send.

```text
$ python3 client.py luca chat://localhost:65102
Connecting to server ...
Connection to server established. Sending intro message...
Registration successful.  Ready for messageing!

>
```
