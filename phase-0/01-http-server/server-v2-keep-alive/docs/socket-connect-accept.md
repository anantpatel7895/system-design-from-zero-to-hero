# TCP `connect()` and Server `accept()`

## Client Code

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
print("CLIENT1 CONNECTED")
```

### What it does

#### Create a TCP socket

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```

- `AF_INET` → IPv4 addressing.
- `SOCK_STREAM` → TCP protocol.
- Creates a client socket object.

#### Connect to the server

```python
sock.connect((HOST, PORT))
```

- Attempts to establish a TCP connection to the server.
- Blocks until:
  - the connection succeeds, or
  - an error occurs.

#### Print confirmation

```python
print("CLIENT1 CONNECTED")
```

- Executes only after a successful connection.

---

# Will the server reach `accept()`?

Yes, if the server is listening.

## Server Code

```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

conn, addr = server.accept()
print("Connection accepted")
```

---

## Connection Flow

### Case 1: Server is already waiting in `accept()`

```text
Server: listen()
Server: accept()   <-- blocked

Client: connect()

TCP handshake occurs

Server: accept() returns
Client: connect() returns
```

Result:

```python
conn, addr = server.accept()
```

returns a new connected socket and the client's address.

---

### Case 2: Server called `listen()` but has not yet called `accept()`

```text
Server: listen()

Client: connect()
Client: connect() returns successfully

Server: accept()
Server: accept() returns queued connection
```

Explanation:
- it may be busy with other clients
- The operating system keeps incoming connections in a backlog queue.
- The client's `connect()` can succeed before the server executes `accept()`.
- When the server later calls `accept()`, it receives the pending connection.

#### Busy with other clients

```text 

Server                           Client
------                           ------

listen()

busy with client A

                                 connect()
                                 returns

(connection queued)

                                 send(GET /hello)
                                 returns

busy with client A

                                 recv()
                                 blocks

accept()
read request
send response

                                 recv() returns
```

---

### Case 3: Server is not listening

Client:

```python
sock.connect((HOST, PORT))
```

Raises:

```text
ConnectionRefusedError: [Errno 111] Connection refused
```

Result:

```python
print("CLIENT1 CONNECTED")
```

is never executed.

---

# Timeline Summary

```text
Server                         Client
------                         ------

listen()

accept()  <----------------- waiting

                               connect()

<----- TCP Handshake -------->

accept() returns
                               connect() returns

Data can now be exchanged.
```

---

# Key Point

A successful:

```python
sock.connect((HOST, PORT))
```

will cause a corresponding server:

```python
conn, addr = server.accept()
```

to return, either:

1. Immediately (if already waiting in `accept()`), or
2. Later (if the connection is queued after `listen()`).