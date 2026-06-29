# Project 0.5 - Step 5: Multi-Client Event Loop

## Goal

Build an event loop that can:

* Accept multiple client connections
* Handle multiple coroutines
* Use a single thread
* Use a single event loop
* Use kernel notifications via `selectors`
* Pause and resume tasks based on socket readiness

This is the first version that starts looking like a simplified implementation of:

* asyncio
* Uvicorn
* Node.js
* Nginx

---

# Why This Project Matters

Previous versions:

## Server V3

```text
Thread Per Connection

Client1 -> Thread1
Client2 -> Thread2
Client3 -> Thread3
```

Problems:

```text
More Clients
    ↓
More Threads
    ↓
More Memory
    ↓
More Context Switching
```

---

## Step 4 Event Loop

```text
One Event Loop
One Client
```

Limitation:

```text
Only one accepted client.
```

---

## Step 5 Event Loop

```text
One Event Loop

Client1
Client2
Client3
Client4
...
```

Multiple clients.

No threads.

---

# Architecture

```text
                    Kernel

                       |

                epoll / kqueue

                       |

                  selectors

                       |

                  Event Loop

                       |

        --------------------------------

        |              |             |

      Task1         Task2        Task3

        |              |             |

     Client1       Client2      Client3
```

---

# Core Components

## Ready Queue

Contains tasks that can run immediately.

Example:

```text
READY

Task1
Task2
Task3
```

---

## Waiting Queue

Contains tasks waiting for socket readiness.

Example:

```text
WAITING

Socket1 -> Task1

Socket2 -> Task2
```

---

## Selector

Responsible for asking the OS:

```text
Tell me when a socket becomes ready.
```

---

## Kernel

Actually monitors sockets.

Not Python.

Not the Event Loop.

Not the Coroutine.

The OS Kernel.

---

# Server Startup

Create listening socket:

```python
server_sock = socket.socket()
```

Bind:

```python
server_sock.bind(
    ("0.0.0.0", 9999)
)
```

Listen:

```python
server_sock.listen()
```

Enable non-blocking mode:

```python
server_sock.setblocking(False)
```

---

# Why Non-Blocking?

Blocking mode:

```python
server_sock.accept()
```

would stop the entire event loop.

Non-blocking mode:

```python
server_sock.accept()
```

raises:

```python
BlockingIOError
```

if no connection exists.

This allows the event loop to continue.

---

# Register Listening Socket

```python
selector.register(
    server_sock,
    selectors.EVENT_READ
)
```

Meaning:

```text
Kernel,

notify me when a new client
is waiting to be accepted.
```

---

# Event Loop

Core loop:

```python
while True:
```

The event loop runs forever.

---

## Phase 1 - Run Ready Tasks

```python
while ready_tasks:
```

Run tasks that are immediately executable.

Example:

```python
task = ready_tasks.pop(0)
```

---

## Phase 2 - Task Yields

Coroutine:

```python
yield WaitForRead(sock)
```

Meaning:

```text
Pause me.

Wake me when data
arrives on this socket.
```

---

Task moves:

```text
READY QUEUE
      ↓
WAITING QUEUE
```

---

# Waiting Queue

Stored as:

```python
waiting_tasks[
    socket
] = task
```

Example:

```text
Client1 Socket -> Task1

Client2 Socket -> Task2
```

---

# Register Client Socket

```python
selector.register(
    socket,
    selectors.EVENT_READ
)
```

Meaning:

```text
Kernel,

notify me when this
client sends data.
```

---

# Kernel Monitoring

The kernel watches:

```text
Socket1

Socket2

Socket3

Socket4
```

No polling.

No busy waiting.

No loops.

---

# Client Sends Data

Example:

```text
Client2

GET /hello
```

Kernel receives packet.

Places bytes into:

```text
Socket Buffer
```

Marks socket:

```text
READY
```

---

# Selector Wakes Up

```python
events = selector.select()
```

returns:

```python
[
    socket2
]
```

Meaning:

```text
Socket2 is ready.
```

---

# Wake Coroutine

Event Loop:

```python
task = waiting_tasks.pop(
    socket2
)
```

Moves task:

```text
WAITING QUEUE
       ↓
READY QUEUE
```

---

# Resume Coroutine

Scheduler executes:

```python
next(task)
```

Coroutine continues exactly where it paused.

---

# Example Timeline

## Client1 Connects

```text
CONNECTED
```

Task1 created.

---

## Task1

```python
yield WaitForRead(sock)
```

Task1 pauses.

---

## Client2 Connects

```text
CONNECTED
```

Task2 created.

---

## Client2 Sends Data

Kernel marks:

```text
Socket Ready
```

---

## Event Loop

Wakes Task2.

Runs Task2.

---

## Important Observation

Task1 was still waiting.

Yet:

```text
Task2 continued running.
```

This is the foundation of asynchronous I/O.

---

# Comparison With Threads

## Thread Model

```text
Client1 -> Thread1

Client2 -> Thread2

Client3 -> Thread3
```

OS scheduler switches threads.

---

## Event Loop Model

```text
Client1 -> Coroutine1

Client2 -> Coroutine2

Client3 -> Coroutine3
```

Event loop switches coroutines.

---

# Real Asyncio Mapping

Our implementation:

```python
yield WaitForRead(sock)
```

Equivalent asyncio:

```python
await reader.read()
```

---

Our scheduler:

```python
next(task)
```

Equivalent asyncio:

```python
task.send(None)
```

---

Our waiting queue:

```python
waiting_tasks
```

Equivalent asyncio:

```text
Future / Task waiting list
```

---

# Important Limitation

Current implementation:

```python
data = sock.recv(1024)
```

reads only once.

Not production ready.

---

Production servers support:

```text
Partial Reads

Partial Writes

Keep Alive

Multiple Requests

Timeouts

Backpressure

Connection Limits
```

---

# Common Mistakes

## Mistake 1

Thinking selectors monitor sockets.

Wrong.

```text
Kernel monitors sockets.
Selectors receive notifications.
```

---

## Mistake 2

Thinking coroutines run themselves.

Wrong.

```text
Scheduler resumes coroutines.
```

---

## Mistake 3

Thinking async creates threads.

Wrong.

```text
One Thread

Many Coroutines
```

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

What happens after:

yield WaitForRead(sock)

````

Answer:

```text
Task moves from Ready Queue
to Waiting Queue.
````

---

## Q3

What wakes the task later?

Answer:

```text
Kernel notification
through selectors.
```

---

## Q4

Can Client2 continue while Client1 waits?

Answer:

```text
Yes.

Client1 is paused.

The scheduler can run Client2.
```

---

## Q5

Does this architecture require threads?

Answer:

```text
No.

One thread can handle many
waiting clients.
```

---

# Mastery Checklist

Before moving to Step 6:

```text
□ Understand Ready Queue

□ Understand Waiting Queue

□ Understand WaitForRead

□ Understand selector.select()

□ Understand socket readiness

□ Understand task pause/resume

□ Understand coroutine scheduling

□ Understand kernel notifications

□ Understand why Client2 can run while Client1 waits

□ Understand how this relates to asyncio
```

---

# Key Takeaway

The event loop does not execute all clients simultaneously.

Instead:

```text
Run Task
      ↓
Task Waits
      ↓
Pause Task
      ↓
Run Another Task
      ↓
Kernel Event Arrives
      ↓
Wake Original Task
```

This pause-and-resume model is the foundation of modern asynchronous systems including asyncio, Uvicorn, FastAPI, Node.js, and Nginx.
