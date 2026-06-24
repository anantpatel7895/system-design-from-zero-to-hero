# Project 0.4 — Event Loop, Selectors, epoll, kqueue, and Kernel Notifications

# Why This Project Exists

In Project 0.3 we built:

```text
Thread Per Connection
```

Architecture:

```text
Client1 -> Thread1

Client2 -> Thread2

Client3 -> Thread3
```

This works well.

But eventually we discovered:

```text
10000 Clients

=
10000 Threads
```

Problems:

```text
High Memory Usage

Context Switching

Scheduler Overhead
```

Most threads spend their lives:

```text
Waiting
Waiting
Waiting
Waiting
```

for network activity.

This leads us to Event Loop architectures.

---

# Core Question

Suppose:

```text
10000 Clients
```

are connected.

How can a server efficiently know:

```text
Which client has data?

Which socket is ready?

Which connection should be processed?
```

without creating:

```text
10000 Threads
```

The answer:

```text
Operating System Kernel
```

---

# Traditional Blocking Model

Example:

```python
data = client_socket.recv(4096)
```

Behavior:

```text
Thread waits.

Nothing else happens.
```

Timeline:

```text
Client
   |
   v
recv()

Thread sleeping...
```

Problem:

```text
One waiting connection
consumes one thread.
```

---

# Event Loop Model

Instead:

```python
selector.select()
```

The server asks:

```text
Kernel,

tell me when any socket
becomes ready.
```

The server sleeps.

The kernel watches all sockets.

---

# Architecture

```text
                Application

                       |

                   Event Loop

                       |

                  selectors

                       |

                epoll / kqueue

                       |

                Kernel Network Stack

                       |

                 TCP Connections
```

---

# Important Principle

The Event Loop does NOT watch sockets.

The Kernel watches sockets.

This is one of the most important system design concepts.

---

# Registration Phase

Suppose a client connects.

We register the socket:

```python
selector.register(
    client_socket,
    selectors.EVENT_READ,
    callback
)
```

Meaning:

```text
Kernel,

please notify me when this
socket has data to read.
```

---

# What Happens Next?

Event Loop:

```python
events = selector.select()
```

Now:

```text
Event Loop Sleeping
```

No CPU usage.

No busy waiting.

---

# Client Sends Data

Client:

```text
GET /hello HTTP/1.1
```

Network Flow:

```text
Client

   |

Network Card

   |

Kernel TCP Stack

   |

Socket Buffer
```

---

# Kernel Marks Socket Ready

The kernel sees:

```text
Socket contains unread data.
```

State becomes:

```text
READY FOR READ
```

---

# Event Loop Wakes Up

Kernel notifies:

```text
epoll
```

or

```text
kqueue
```

or

```text
IOCP
```

depending on OS.

Then:

```python
selector.select()
```

returns.

---

# Python Receives Events

Example:

```python
events = selector.select()
```

Result:

```python
[
    socket7,
    socket99,
    socket120
]
```

Meaning:

```text
These sockets are ready.

Process them.
```

---

# Visual Timeline

```text
Time 0

Event Loop Sleeping

--------------------------------

Time 1

Client7 sends data

--------------------------------

Time 2

Kernel marks socket ready

--------------------------------

Time 3

selector.select() wakes

--------------------------------

Time 4

Application processes request
```

---

# Common Misconception

Many engineers imagine:

```python
while True:

    for socket in sockets:

        check_if_ready()
```

This is called polling.

It wastes CPU.

---

# What Actually Happens

Real architecture:

```text
Event Loop Sleeping

Kernel Monitoring

Kernel Wakes Event Loop
```

This is event-driven architecture.

---

# Why epoll Exists

Suppose:

```text
100000 Sockets
```

Question:

```text
Can we scan them continuously?
```

Technically yes.

Efficiently?

No.

---

# epoll

Linux provides:

```text
epoll
```

Features:

```text
O(1) notification

Very low overhead

Massive scalability
```

The kernel maintains readiness information.

Applications only receive changes.

---

# kqueue

macOS and BSD provide:

```text
kqueue
```

Same idea.

Kernel-driven notifications.

---

# IOCP

Windows provides:

```text
IO Completion Ports
```

Same concept.

Different implementation.

---

# selectors Module

Python hides OS differences.

You write:

```python
selectors.DefaultSelector()
```

Python chooses:

Linux:

```text
epoll
```

macOS:

```text
kqueue
```

Windows:

```text
IOCP/select
```

automatically.

---

# Event Loop

Simplified:

```python
while True:

    events = selector.select()

    for event in events:

        process(event)
```

This is the heart of:

```text
Nginx

Node.js

Redis

Uvicorn

Asyncio
```

---

# Important Limitation

Suppose:

```python
def slow():

    time.sleep(20)
```

Request arrives:

```text
GET /slow
```

Event Loop executes:

```python
time.sleep(20)
```

What happens?

---

# Entire Event Loop Stops

State:

```text
Event Loop Sleeping
```

Meaning:

```text
Client1 waiting

Client2 waiting

Client3 waiting

Client1000 waiting
```

Everything stops.

---

# Why Async/Await Was Invented

Instead of:

```python
time.sleep(20)
```

use:

```python
await asyncio.sleep(20)
```

Now:

```text
Coroutine pauses

Event Loop continues
```

This is the next project.

---

# Project 0.3 vs Project 0.4

## Thread Model

```text
Client1 -> Thread1

Client2 -> Thread2

Client3 -> Thread3
```

Advantages:

```text
Simple

Easy To Understand
```

Problems:

```text
Thread Explosion
```

---

## Event Loop Model

```text
One Thread

One Event Loop

Many Connections
```

Advantages:

```text
Low Memory

High Scalability

Few Context Switches
```

Problems:

```text
One Blocking Operation
Can Freeze Everything
```

---

# Senior Engineer Mental Model

Think of:

```text
Threads
```

as:

```text
One Employee Per Customer
```

---

Think of:

```text
Event Loop
```

as:

```text
One Dispatcher

Many Waiting Customers
```

---

Think of:

```text
epoll / kqueue
```

as:

```text
Security Camera System
```

The dispatcher is sleeping.

The cameras watch everything.

When something happens:

```text
Camera alerts dispatcher.
```

Dispatcher wakes up.

Processes the event.

Goes back to sleep.

---

# Interview Questions

## Q1

Who monitors socket readiness?

Answer:

```text
Operating System Kernel
```

---

## Q2

What does selector.select() do?

Answer:

```text
Waits until the kernel reports
ready sockets.
```

---

## Q3

Does the Event Loop continuously scan sockets?

Answer:

```text
No.

The kernel provides notifications.
```

---

## Q4

What is epoll?

Answer:

```text
Linux kernel event notification system.
```

---

## Q5

What is kqueue?

Answer:

```text
macOS/BSD kernel event notification system.
```

---

## Q6

Why is Event Loop architecture scalable?

Answer:

```text
Few threads.

Kernel-driven notifications.

Low memory usage.
```

---

# Mastery Checklist

Before Project 0.5:

```text
□ Understand blocking sockets

□ Understand non-blocking sockets

□ Understand selectors

□ Understand kernel notifications

□ Understand epoll

□ Understand kqueue

□ Understand Event Loop

□ Understand why threads don't scale forever

□ Understand why time.sleep blocks Event Loop

□ Understand why asyncio exists
```

---

# Key Takeaway

The Event Loop does not magically know when a socket becomes ready.

The:

```text
Operating System Kernel
```

tracks every socket.

Technologies like:

```text
epoll
kqueue
IOCP
```

allow the kernel to efficiently notify applications when work is available.

This kernel-notification model is the foundation of:

```text
Nginx

Node.js

Redis

Asyncio

Uvicorn

FastAPI
```

and every modern high-performance backend server.
