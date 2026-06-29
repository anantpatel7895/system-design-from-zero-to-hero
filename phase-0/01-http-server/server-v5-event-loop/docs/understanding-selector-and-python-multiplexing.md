# Understanding Python `selectors` and I/O Multiplexing

## 1. The Problem: Blocking I/O

Imagine a server handling multiple clients.

```python
while True:
    client_sock, addr = server_sock.accept()

    data = client_sock.recv(1024)

    process(data)
```

The problem:

```text
accept() blocks
recv() blocks
```

If Client A is slow:

```text
Client A connected
Client A sends nothing
```

The server gets stuck:

```python
data = client_sock.recv(1024)
```

and cannot serve Client B.

---

## 2. One Thread Per Client

A common solution is:

```text
Client A -> Thread A
Client B -> Thread B
Client C -> Thread C
```

Example:

```python
while True:
    client_sock, addr = server_sock.accept()

    threading.Thread(
        target=handle_client,
        args=(client_sock,)
    ).start()
```

This works, but with thousands of clients:

```text
10,000 clients
10,000 threads
```

Problems:

* Huge memory usage
* Context switching overhead
* Scheduler overhead

---

## 3. Observation

Most network servers spend their time waiting.

Example:

```text
Client connects
↓
Client thinks for 5 seconds
↓
Client sends request
↓
Server responds in 5 ms
```

So:

```text
99.9% waiting
0.1% working
```

Why dedicate a whole thread to each waiting socket?

---

## 4. Non-Blocking Sockets

Instead of:

```python
data = sock.recv(1024)
```

blocking forever,

you can do:

```python
sock.setblocking(False)
```

Now:

```python
sock.recv(1024)
```

returns immediately.

If no data exists:

```text
BlockingIOError
```

is raised.

---

## 5. The OS Already Knows

The operating system already knows:

```text
Socket 1 has data
Socket 2 has no data
Socket 3 has data
```

Wouldn't it be nice to ask:

```text
OS, tell me which sockets are ready.
```

That's exactly what I/O multiplexing does.

---

## 6. select()

The oldest solution:

```python
import select

ready, _, _ = select.select(
    [sock1, sock2, sock3],
    [],
    []
)
```

The thread sleeps.

```text
CPU usage ≈ 0%
```

When data arrives:

```text
OS wakes thread
```

and returns:

```python
ready = [sock2]
```

meaning:

```text
Only sock2 is ready to read.
```

---

## 7. poll()

`select()` has limitations.

A newer mechanism is:

```text
poll()
```

which scales better.

---

## 8. epoll() (Linux)

Linux introduced:

```text
epoll
```

Instead of repeatedly checking thousands of sockets, the kernel tracks them internally and reports only the sockets that become ready.

Very efficient for large numbers of connections.

---

## 9. kqueue() (BSD/macOS)

BSD and macOS provide:

```text
kqueue
```

which offers similar functionality to epoll.

---

## 10. Python's selectors Module

Python hides OS-specific details.

```python
import selectors

selector = selectors.DefaultSelector()
```

Python automatically chooses the best implementation:

```text
Linux     -> epoll
macOS     -> kqueue
BSD       -> kqueue
Windows   -> select
```

---

## 11. Registering Interest

Tell the selector what events you care about.

```python
selector.register(
    sock,
    selectors.EVENT_READ
)
```

Meaning:

```text
Wake me when this socket can be read.
```

Or:

```python
selector.register(
    sock,
    selectors.EVENT_WRITE
)
```

Meaning:

```text
Wake me when this socket can be written to.
```

---

## 12. The Event Loop

This is the heart:

```python
while True:

    events = selector.select()

    for key, mask in events:

        handle(key.fileobj)
```

Think of:

```python
selector.select()
```

as:

```text
OS, put me to sleep until something interesting happens.
```

---

## 13. What Happens Internally

Suppose:

```text
Client A connected
Client B connected
Client C connected
```

All sockets are registered.

```text
selector
│
├── A
├── B
└── C
```

The event loop sleeps:

```python
events = selector.select()
```

Client B sends:

```text
hello
```

The kernel marks:

```text
Socket B = readable
```

The selector wakes up and returns:

```python
[(socket_B, EVENT_READ)]
```

Your code handles only B.

---

## 14. Why This Scales

With threads:

```text
10,000 clients
10,000 threads
```

With selectors:

```text
10,000 clients
1 thread
1 selector
```

The OS tells you exactly which sockets need attention.

---

## 15. Connection to asyncio

This code:

```python
yield WaitForRead(sock)
```

is conceptually similar to:

```python
await sock.recv()
```

in asyncio.

Under the hood:

```text
Coroutine pauses
↓
Socket registered with selector
↓
selector.select()
↓
OS reports readiness
↓
Coroutine resumes
```

This is why `asyncio` can handle thousands of connections using a single thread.

---

# Mental Model

Think of a restaurant.

### Thread-per-client

```text
One waiter per table
```

10,000 tables:

```text
10,000 waiters
```

Very expensive.

### Selector/Event Loop

```text
One waiter
```

The waiter says:

```text
Raise your hand when ready.
```

Instead of standing beside every table, the waiter serves only the tables that signal they need attention:

```text
Table 7 raised hand
→ serve Table 7

Table 102 raised hand
→ serve Table 102
```

That's exactly what `selectors` and an event loop do for sockets.
