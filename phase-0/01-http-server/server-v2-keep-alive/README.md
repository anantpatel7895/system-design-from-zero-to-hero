# HTTP Server V2 - From Sockets to Frameworks

## Overview

This project implements a simple HTTP server from scratch using Python sockets.

The goal is not to replace FastAPI, Flask, or Django.

The goal is to understand what happens underneath modern web frameworks.

By building this server manually, we learn:

* TCP Connections
* HTTP Protocol
* Request Parsing
* Response Generation
* Routing
* Middleware
* Keep-Alive Connections
* Server Architecture
* Foundation for Async Programming
* Foundation for FastAPI/Uvicorn Internals

---

# Learning Objectives

After completing this project, you should understand:

## Networking

* What is a TCP connection?
* How does a client connect to a server?
* What does accept() do?
* What does recv() do?
* What does send() do?

## HTTP

* What is an HTTP Request?
* What is an HTTP Response?
* HTTP Methods
* HTTP Headers
* HTTP Body
* Content-Length
* Status Codes
* Keep-Alive

## Backend Architecture

* Request Object
* Response Object
* Router
* Handlers
* Middleware

## System Design

* Single-threaded server limitations
* Why Keep-Alive exists
* Why async programming exists
* Why Uvicorn exists

---

# Project Structure

```text
http-server-v2/
│
├── server.py
├── request.py
├── response.py
├── router.py
├── handlers.py
└── middleware.py
```

---

# Architecture

```text
                Browser

                    |
                    v

           TCP Connection

                    |
                    v

             +------------+
             | server.py  |
             +------------+

                    |
                    v

            +-------------+
            | request.py  |
            +-------------+

                    |
                    v

          +----------------+
          | middleware.py  |
          +----------------+

                    |
                    v

             +-----------+
             | router.py |
             +-----------+

                    |
                    v

           +---------------+
           | handlers.py   |
           +---------------+

                    |
                    v

          +----------------+
          | response.py    |
          +----------------+

                    |
                    v

                Browser
```

---

# Request Lifecycle

Suppose a browser requests:

```http
GET /users HTTP/1.1
Host: localhost:8080
```

The following steps occur.

---

## Step 1

Browser creates TCP connection.

```text
Browser
    |
    v
Server
```

The TCP handshake occurs.

```text
SYN
SYN-ACK
ACK
```

Connection established.

---

## Step 2

Server accepts connection.

```python
client_socket, address = server.accept()
```

A dedicated client socket is created.

---

## Step 3

Browser sends HTTP request.

```python
data = client_socket.recv(4096)
```

Raw bytes arrive.

Example:

```http
GET /users HTTP/1.1
Host: localhost:8080
```

---

## Step 4

Request Parser

request.py converts raw text into a Request object.

```python
request.method
request.path
request.headers
request.body
```

Result:

```python
Request(
    method="GET",
    path="/users"
)
```

---

## Step 5

Middleware

Request logging.

```python
log_request(request)
```

Example output:

```text
GET /users
```

---

## Step 6

Router

The router decides which handler to execute.

```python
("GET", "/users")
```

maps to:

```python
users()
```

---

## Step 7

Handler Execution

Handler generates business response.

```python
return Response(
    body='["anant","john"]'
)
```

---

## Step 8

Response Builder

Response object becomes HTTP text.

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 18

["anant","john"]
```

---

## Step 9

Response Sent

```python
client_socket.sendall(...)
```

Browser receives response.

---

# Understanding Keep-Alive

Without Keep-Alive:

```text
Request
Response
Connection Close

Request
Response
Connection Close
```

Each request requires:

```text
TCP Handshake
```

which is expensive.

---

With Keep-Alive:

```text
TCP Handshake

Request 1
Response 1

Request 2
Response 2

Request 3
Response 3
```

Single connection.

Multiple requests.

Better performance.

---

# Why Content-Length Matters

Suppose:

```http
HTTP/1.1 200 OK

Hello User
```

How does the browser know where the response ends?

It doesn't.

---

Correct response:

```http
HTTP/1.1 200 OK
Content-Length: 10

Hello User
```

Now browser knows:

```text
Read exactly 10 bytes
```

Response complete.

---

# Current Limitation

This server is:

```text
Single Threaded
```

Architecture:

```text
Client 1
    |
    v
Server

Client 2 waits
Client 3 waits
```

Problem:

```python
while True:

    client_socket, addr = server.accept()

    while True:
        recv()
```

The server cannot return to accept() until the current client disconnects.

---

# Why This Is A Problem

Suppose:

```text
Client 1 connects
```

and never disconnects.

```text
Client 2 waits forever
```

Server cannot process Client 2.

---

# Threaded Server Solution

Create a thread per client.

```text
               Server

                   |
              accept()

        --------------------
        |         |        |
        v         v        v

    Thread1   Thread2   Thread3

    Client1   Client2   Client3
```

Now clients execute concurrently.

---

# Why Threads Eventually Fail

Suppose:

```text
50,000 Clients
```

Need:

```text
50,000 Threads
```

Problems:

* Memory Usage
* Context Switching
* Scheduler Overhead

System becomes inefficient.

---

# Async Server Solution

Instead of:

```text
1 Thread Per Client
```

use:

```text
1 Event Loop
Many Connections
```

Architecture:

```text
                Event Loop

                      |

      ----------------------------------

      |               |               |

      v               v               v

   Request A      Request B      Request C
```

One thread.

Thousands of connections.

---

# How Uvicorn Works

Simplified:

```text
Socket

   |

Event Loop

   |

FastAPI Route

   |

await database.query()
```

When waiting:

```python
await db.fetch()
```

The Event Loop executes another request.

No thread wasted.

---

# Future Versions

## V1

Basic HTTP Server

```text
Socket
HTTP
Routing
```

---

## V2

Current Version

```text
Request Object
Response Object
Middleware
Keep-Alive
```

---

## V3

Threaded Server

```text
Thread Per Client
```

---

## V4

Async Server

```text
asyncio
Event Loop
```

---

## V5

Mini Uvicorn

```text
ASGI Style Server
FastAPI Internals
```

---

# End Goal

Understand how this:

```python
@app.get("/users")
async def get_users():
    return {"message": "hello"}
```

eventually becomes:

```python
socket.accept()

recv()

parse_http()

route()

handler()

build_response()

send()
```

Every modern backend framework is built on these same fundamental ideas.
