# Project 0.3 - Threaded HTTP Server

## Phase 0 - Foundations

### Previous Projects

```text
Project 0.1 - TCP Web Server
Project 0.2 - HTTP Server with Keep-Alive
Project 0.3 - Threaded HTTP Server  ← Current
Project 0.4 - Async HTTP Server
Project 0.5 - Mini Uvicorn
```

---

# Goal

Build a multi-client HTTP server that can process requests concurrently using threads.

In Project 0.2 we discovered:

```text
Keep-Alive
≠
Concurrency
```

A single client could block the entire server.

This project fixes that problem.

---

# Learning Objectives

After completing this project, you should understand:

## Networking

* TCP Connections
* Client Sockets
* Server Sockets
* Connection Lifecycle

## HTTP

* Request Parsing
* Response Building
* Keep-Alive
* Routing

## Concurrency

* Threads
* Main Thread
* Worker Threads
* Concurrent Request Processing

## System Design

* Thread-per-Connection Architecture
* Why Single Threaded Servers Fail
* Why Async Servers Exist

---

# Problem In Project 0.2

> after os done 3-way handshake, server accepts connection and waits for request

Architecture:

```text
Client1
   |
   v

Server

Client2 waiting...
Client3 waiting...
```

Code:

```python
while True:

    client_socket, address = server.accept()

    while True:

        data = client_socket.recv()
```

Problem:

```text
Client1 stays connected

Server never returns to accept()

Client2 waits
Client3 waits
```

---

# Real Experiment

Client1:

```text
Request1
Response1

(waiting 30 seconds)
```

Client2:

```text
Request
```

Observed:

```text
CLIENT2 WAITED 25.12 seconds
```

This proved:

```text
Keep-Alive
does NOT solve concurrency
```

---

# Solution

Create one thread per client.

Instead of:

```text
Client1 blocks everyone
```

Use:

```text
Client1 -> Thread1

Client2 -> Thread2

Client3 -> Thread3
```

---

# Architecture

```text
                     Server

                         |
                     accept()

                         |

      -------------------------------------

      |                 |                |

      v                 v                v

   Thread1          Thread2          Thread3

   Client1          Client2          Client3
```

---

# Request Lifecycle

Suppose:

```http
GET /hello HTTP/1.1
```

arrives.

---

## Step 1

TCP Connection

```text
Client
   |
   v
Server
```

---

## Step 2

Server Accepts Connection

```python
client_socket, addr = server.accept()
```

---

## Step 3

Create Worker Thread

```python
thread = threading.Thread(
    target=handle_client
)
```

---

## Step 4

Thread Starts

```python
thread.start()
```

Now this client has a dedicated worker thread.

---

## Step 5

Request Received

```python
data = client_socket.recv()
```

---

## Step 6

Request Parsed

```python
request = parse_request(data)
```

Result:

```python
Request(
    method="GET",
    path="/hello"
)
```

---

## Step 7

Routing

```python
dispatch(request)
```

Router chooses:

```python
hello()
```

---

## Step 8

Handler Executes

```python
return Response(
    "Hello User"
)
```

---

## Step 9

Response Built

```http
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 10

Hello User
```

---

## Step 10

Response Sent

```python
client_socket.sendall(...)
```

---

# Thread Lifecycle

Connection Created:

```text
Client Connected
```

Thread Created:

```text
Thread Started
```

Requests Processed:

```text
Request1
Response1

Request2
Response2

Request3
Response3
```

Client Disconnects:

```text
Thread Closed
```

---

# Keep-Alive Still Exists

Threaded server still supports:

```http
Connection: keep-alive
```

Example:

```text
Client

Request1
Response1

Request2
Response2

Request3
Response3
```

Same TCP connection reused.

Difference:

```text
Other clients can execute simultaneously
```

---

# Demonstrating Concurrency

## Slow Endpoint

```python
def slow(request):

    time.sleep(20)

    return Response(
        "Done"
    )
```

---

## Terminal 1

```bash
curl http://localhost:8080/slow
```

---

## Terminal 2

```bash
curl http://localhost:8080/hello
```

Result:

```text
Hello User
```

immediately.

---

# Why It Works

Client1:

```text
Thread1

sleep(20)
```

Client2:

```text
Thread2

hello()
```

Different threads.

No blocking.

---

# Thread Memory Model

Each thread has:

```text
Stack
Registers
Execution Context
```

Example:

```text
Thread1

request = /hello
response = Hello
```

Independent from:

```text
Thread2

request = /users
response = [...]
```

---

# Thread Advantages

## Easy To Understand

```text
1 Client
=
1 Thread
```

Simple mental model.

---

## Concurrency

Multiple clients can execute at the same time.

---

## Better User Experience

One slow client no longer blocks everyone.

---

# Thread Problems

Suppose:

```text
50,000 Clients
```

Need:

```text
50,000 Threads
```

Problems:

---

## Memory Explosion

Each thread consumes memory.

Example:

```text
1 MB per thread
```

50,000 threads:

```text
≈ 50 GB RAM
```

Not practical.

---

## Context Switching

CPU constantly switches:

```text
Thread1
Thread2
Thread3
...
```

This has overhead.

---

## Scheduler Cost

Operating System spends time managing threads instead of doing useful work.

---

# Why Async Exists

Threads solve:

```text
Concurrency
```

but not:

```text
Massive Scale
```

At very large scale:

```text
100,000+
Connections
```

servers move to:

```text
Event Loops
epoll
kqueue
IOCP
```

which we build in Project 0.4.

---

# Comparison

## Project 0.2

```text
Single Thread
```

Architecture:

```text
Client1

Server

Client2 waiting
Client3 waiting
```

Concurrency:

```text
1 request
```

---

## Project 0.3

```text
Thread Per Connection
```

Architecture:

```text
Client1 -> Thread1

Client2 -> Thread2

Client3 -> Thread3
```

Concurrency:

```text
Many requests
```

---

# Testing

Start server:

```bash
python3 server.py
```

---

Hello endpoint:

```bash
curl http://localhost:8080/hello
```

---

Users endpoint:

```bash
curl http://localhost:8080/users
```

---

Health endpoint:

```bash
curl http://localhost:8080/health
```

---

Slow endpoint:

```bash
curl http://localhost:8080/slow
```

Expected:

```text
Done
```

after 20 seconds.

---

Concurrency test:

```bash
python3 test/test_concurrency.py
```

Expected:

```text
SLOW REQUEST START

FAST REQUEST START

Hello User
FAST TOOK 0.01s

Done
SLOW TOOK 20.00s
```

---

# Common Mistakes

## Forgetting To Close Socket

Bad:

```python
client_socket.recv()
```

Good:

```python
client_socket.close()
```

---

## Unlimited Threads

Bad:

```python
Thread(...)
```

for every connection forever.

---

## Shared Global Variables

Bad:

```python
users = []
```

Multiple threads modifying same object.

Can cause race conditions.

---

## Assuming Threads Scale Forever

Threads improve concurrency.

They do not solve massive scale.

---

# Interview Questions

## Q1

Why is Project 0.3 better than Project 0.2?

Answer:

```text
Multiple clients can execute simultaneously.
```

---

## Q2

What problem does threading solve?

Answer:

```text
Concurrency.
```

---

## Q3

What problem does threading NOT solve?

Answer:

```text
Massive scale.
```

---

## Q4

What happens if 100,000 clients connect?

Answer:

```text
Too many threads.
Too much memory.
Too much context switching.
```

---

## Q5

What comes after threads?

Answer:

```text
Async Event Loops
```

---

# Mastery Checklist

Before moving to Project 0.4:

```text
□ Explain why V2 blocks

□ Explain why Keep-Alive is not concurrency

□ Explain thread-per-connection architecture

□ Explain how worker threads are created

□ Explain why /slow no longer blocks /hello

□ Explain thread memory overhead

□ Explain context switching

□ Explain why async exists

□ Run concurrency test successfully
```

---

# Key Takeaway

Project 0.2 taught:

```text
Connection Reuse
```

Project 0.3 teaches:

```text
Concurrency
```

The next project will teach:

```text
Scalable Concurrency
```

using event loops and async I/O, which is the foundation of FastAPI, Uvicorn, Node.js, Nginx, and modern high-performance backend systems.
