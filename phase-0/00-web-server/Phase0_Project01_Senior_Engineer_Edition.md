
# Phase 0 Project 0.1 — Senior Systems Engineer Edition
## Build a Web Server From Scratch

# Chapter 1: Why Learn This?

Every request to FastAPI, Flask, Django, Nginx, Apache, Kubernetes Ingress, or Load Balancer eventually becomes:

Browser
 -> TCP
 -> Socket
 -> Linux Kernel
 -> Application

Understanding this layer is the foundation of system design.

---

# Chapter 2: The Journey of a Request

User types:

http://example.com

Browser:
1. DNS lookup
2. Gets IP address
3. Opens TCP connection
4. Sends HTTP request
5. Receives HTTP response

---

# Chapter 3: Processes and Threads

Process:
- Own memory
- Own file descriptors
- Own resources

Thread:
- Shares process memory
- Has its own execution stack

Process
 ├─ Thread 1
 ├─ Thread 2
 └─ Thread 3

---

# Chapter 4: What is TCP?

TCP guarantees:

- Reliability
- Ordering
- Error detection

Without TCP:

Packet 3 could arrive before Packet 1.

---

# Chapter 5: TCP Handshake

Client            Server

SYN ----------->

      <--------- SYN ACK

ACK ----------->

Connection Established

Linux Kernel performs the handshake.

Python never performs the handshake.

---

# Chapter 6: What is a Socket?

Socket = Communication Endpoint

Think:

Telephone

A socket allows two machines to communicate.

---

# Chapter 7: socket()

server = socket.socket()

Kernel creates:

- File Descriptor
- Socket Structure
- Buffers

Python receives a handle.

---

# Chapter 8: bind()

bind(("0.0.0.0",8080))

Registers:

Port 8080

Kernel table:

8080 -> Process

---

# Chapter 9: listen()

listen(5)

Meaning:

Ready to accept connections.

Creates backlog queue.

Not:
"Only 5 clients allowed."

---

# Chapter 10: accept()

client_socket, addr = accept()

Returns:

A NEW connected socket.

Important:

accept() does NOT return the listening socket.

---

# Chapter 11: Listening Socket vs Client Socket

Listening Socket:

server_socket

Purpose:
Accept new connections.

Client Socket:

client_socket

Purpose:
Exchange data.

---

# Chapter 12: Simple Server

Accept one client.
Exit.

Educational only.

---

# Chapter 13: Continuous Server

while True:
    accept()
    process()
    close()

Runs forever.

> Still processes one client at a time.

---

# Chapter 14: Threaded Server

accept()
create thread

Thread handles client.

Main thread immediately returns to accept().

---

# Chapter 15: Why Threading Works

Client1 -> Thread1
Client2 -> Thread2
Client3 -> Thread3

Multiple clients active simultaneously.

---

# Chapter 16: GIL Reality

CPU-bound:
Threads don't scale well.

I/O-bound:
Threads work reasonably well.

Web servers are mostly I/O-bound.

---

# Chapter 17: Blocking I/O

Examples:

accept()
recv()
send()
sleep()

Thread waits.

CPU may be idle.

---

# Chapter 18: Arrival Rate vs Processing Rate

Arrival = 100/sec

Processing = 10/sec

Queue Growth = 90/sec

Eventually queue fills.

This is the most important scalability concept.

---

# Chapter 19: Accept Queue

Handshake Complete
       |
       v
Accept Queue
       |
       v
accept()

If application is slow, queue grows.

---

# Chapter 20: What Happens When Queue Is Full?

New connections:

- Timeout
- Dropped
- Rejected

Server process may still be alive.

---

# Chapter 21: Linux Kernel Responsibilities

- TCP
- Routing
- Queues
- Handshakes
- Ports
- Buffers

---

# Chapter 22: Python Responsibilities

- Business Logic
- Parsing Requests
- Generating Responses

---

# Chapter 23: EC2 Deployment

Requirements:

1. bind 0.0.0.0
2. Security Group open
3. Firewall open

Example:

curl http://PUBLIC_IP:8080

---

# Chapter 24: Nginx Architecture

Internet
   |
 Nginx:80
   |
 App:8000

Reverse Proxy Pattern

---

# Chapter 25: Why Async Exists

Thread-per-request:

10000 clients
=
10000 threads

Expensive.

Async:

1 thread
many sockets

Used by:
- FastAPI
- Uvicorn
- NodeJS
- Nginx

---

# Chapter 26: Common Production Failures

1. Queue Full
2. Socket Leak
3. Thread Explosion
4. Slow Database
5. Security Group Misconfiguration

---

# Chapter 27: Interview Questions

1. What is TCP?
2. What is a socket?
3. What does bind() do?
4. What does listen() do?
5. What does accept() return?
6. Difference between process and thread?
7. Who performs handshake?
8. What is blocking I/O?
9. Why async?
10. Why do queues fill?

---

# Chapter 28: Mastery Checklist

[ ] Can explain socket()
[ ] Can explain bind()
[ ] Can explain listen()
[ ] Can explain accept()
[ ] Can explain TCP handshake
[ ] Can explain queues
[ ] Can explain threaded server
[ ] Can explain Linux Kernel responsibilities
[ ] Can explain arrival vs processing rate

Project 0.1 Complete.
