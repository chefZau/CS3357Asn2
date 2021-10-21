# CS3357 Assignment 2 - Implementing a Python Çhat Room

## by Luca(MingCong) Zhou

Implement in Python a simple client-server chat program. The general purpose of this assignment is to gain network programming experience in:

1. Writing networked applications.
2. Using the socket API in Python.
3. Writing software supporting a simple protocol.


## Hardware Required

As mentioned by the professor in the email: "Please note that under Windows, at least some versions of Python on some versions of Windows don't like using sys.stdin with selectors. It does work fine under Linux and Mac, however, so you should be able to use the same environment used for Assignment #1 if you run into troubles with this under Windows.", therefore, I recommend using either Mac or Linux to test the program.

## How It Works

Detailed instructions have been illustrated on OWL. For your convenience, here is a quick explanation. There are two files in this assignment: **client.py** and **server.py**. As their name suggests, **server.py** is for starting the server and handling incoming requests, whereas **client.py** is responsible for taking client input at the console and communicating with the server.

When the server is up, it constantly runs in the background. Users will then run **client.py** to register connections. When users are successfully registered, they can send and receive messages back and forth using the terminal(console).

Notice that the program allows multiple clients to run concurrently. This is done by using the built-in [selectors](https://docs.python.org/3/library/selectors.html) module. 

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

When the server starts, it will output a port number in the console. Record this number; we will use it to register a client.

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

## Inspiration

When completing this assignment, I noted that there weren't many examples for using the [selectors](https://docs.python.org/3/library/selectors.html) module. On the contrary, there were many implementations related to [threading](https://www.techwithtim.net/tutorials/socket-programming/). Yet, those examples were irrelevant to the assignment. Therefore, I started by reading the [Socket Programming in Python (Guide)](https://realpython.com/python-sockets/) to familiarize myself with the networking fundamentals. Furthermore, I also watched a [Python Socket Programming Tutorial](https://youtu.be/3QiPPX-KeSc) on YouTube. Up to this point, I was able to implement the majority of the program.

Since the server needs to support communicating with multiple clients simultaneously, I started by learning the basics of the selectors module. Here are some inspirational links I encountered:

* [Python 3 Standard Library: selectors I/O Multiplex Abstraction](https://programming.vip/docs/python-3-standard-library-selectors-i-o-multiplex-abstraction.html)
* [Python selectors模块用法：实现非阻塞式编程](https://naoketang.com/p/nozql01vqg01)
* [使用Python实现一个简单的聊天室](https://blog.csdn.net/u011960402/article/details/107503730)

The last bit was the user input. One of the requirements was the following:

* To send a message, a user will type it at a prompt provided by their chat client.

I tried using the built-in `input()` method. However, the way blocks the incoming message from the server, and the incoming message only displays when I press the enter key on the keyboard. This is not ideal. Fortunately, the professor sent a follow-up email regarding this issue. Here is the email:

```text
Several of you have had issues with input() blocking in your client, making it unable to retrieve server messages until input of some kind is provided. That's not ideal and not the way you should be doing things.  You don't need to use threads to solve this problem, but instead should be using the selectors package there similar to how you do so in the server.  The difference is that in the client, in addition to waiting for input from the server, you can also wait for input from sys.stdin. That way, you only go to retrieve input from the terminal when input is there waiting for you.  (And there's a few ways to retrieve things nicely from sys.stdin ...)  If you do things this way, we can readily avoid issues in blocking while still only using the selectors package.
...
```

Here is a helpful link related to [Taking input from sys.stdin, non-clocking](https://stackoverflow.com/questions/53045592/python-non-blocking-sockets-using-selectors).