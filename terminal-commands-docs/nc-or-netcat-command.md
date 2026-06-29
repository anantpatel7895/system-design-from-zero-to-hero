# Netcat (`nc`) Basics

## What is `nc`?

`nc` (Netcat) is a command-line networking tool that can create TCP or UDP connections, send data, and receive data.

It is often called the **"Swiss Army knife of networking"** because it is useful for testing servers, debugging network applications, and transferring data.

---

# Basic Usage

```bash
nc localhost 9999
```

This command creates a TCP connection to port `9999` on the local machine.

---

# Breaking Down the Command

```bash
nc localhost 9999
```

### `nc`

The Netcat program.

### `localhost`

The hostname of the current machine.

Usually resolves to:

```text
127.0.0.1
```

or

```text
::1
```

for IPv6.

### `9999`

The destination TCP port.

---

# What Happens Internally?

Suppose a Python server is running:

```python
server_sock = socket.socket()

server_sock.bind(("localhost", 9999))

server_sock.listen(1)

client_sock, addr = server_sock.accept()
```

The server is waiting for a client connection.

When you run:

```bash
nc localhost 9999
```

Netcat acts as a TCP client and performs the TCP three-way handshake with the server.

```text
Server                             Netcat

listen()
accept()  <-------------------- waiting

                                   nc localhost 9999

<--------- TCP 3-Way Handshake ---------->

accept() returns
```

The server now has a connected client socket.

---

# Sending Data

After connecting, anything typed into the terminal is sent to the server.

Example:

```bash
nc localhost 9999
```

Type:

```text
hello
```

and press Enter.

Netcat sends:

```python
b"hello\n"
```

to the server.

The server can receive it using:

```python
data = client_sock.recv(1024)
```

---

# Example Server Output

Server:

```text
Waiting for client...
Connected: ('127.0.0.1', 54321)

CLIENT TASK STARTED
RECEIVED: hello
CLIENT TASK FINISHED
TASK FINISHED
```

---

# Why Use Netcat?

Netcat is useful because it allows you to test a server without writing a custom client.

Instead of writing:

```python
import socket

sock = socket.socket()

sock.connect(("localhost", 9999))

sock.send(b"hello")
```

you can simply run:

```bash
nc localhost 9999
```

and type messages manually.

---

# Common Commands

### Connect to a TCP Server

```bash
nc localhost 9999
```

### Connect to a Remote Server

```bash
nc example.com 80
```

### Send a Single Message

```bash
echo "hello" | nc localhost 9999
```

### Test if a Port is Open

```bash
nc -zv localhost 9999
```

Example output:

```text
Connection to localhost 9999 port [tcp/*] succeeded!
```

---

# Summary

```bash
nc localhost 9999
```

means:

* Start Netcat.
* Connect to the machine `localhost`.
* Connect to TCP port `9999`.
* Allow the user to send and receive data through that connection.

Netcat is one of the simplest tools for manually testing TCP servers and understanding how socket communication works.
