# OS Scheduling, Python GIL, Threads, Processes, and Edge Cases

# Why This Document Exists

Many engineers learn:

```text
Python has a GIL
```

but cannot explain:

* Who schedules threads?
* What happens on multiple CPU cores?
* Why web servers still use threads?
* Why async exists?
* When threads help?
* When multiprocessing is required?
* What happens during I/O?
* What happens during CPU-heavy work?

This document answers those questions from first principles.

---

# Layered View of Execution

When a Python program runs:

```text
Application Code

       |

Python Runtime

       |

Python Thread

       |

Global Interpreter Lock (GIL)

       |

OS Thread

       |

OS Scheduler

       |

CPU Core
```

Important:

```text
Python does NOT directly schedule threads.

The Operating System schedules threads.
```

---

# CPU Core

Example machine:

```text
16 Core CPU
```

Architecture:

```text
Core1
Core2
Core3
...
Core16
```

Each core can execute instructions.

---

# What Is A Process?

Example:

```bash
python server.py
```

creates:

```text
Process
```

A process contains:

```text
Memory
Code
Heap
Stack
Threads
File Descriptors
Sockets
```

Example:

```text
Python Process
    |
    +--- Thread1
    +--- Thread2
    +--- Thread3
```

---

# What Is A Thread?

A thread is an execution path inside a process.

Example:

```python
thread1.start()
thread2.start()
```

creates:

```text
Process

    |
    +---- Thread1
    |
    +---- Thread2
```

Threads share:

```text
Memory
Variables
Heap
Sockets
```

but have their own:

```text
Stack
Registers
Program Counter
```

---

# Who Schedules Threads?

Answer:

```text
Operating System Scheduler
```

Not Python.

Not Thread1.

Not Thread2.

The OS decides.

---

# Thread States

```text
NEW

READY

RUNNING

WAITING

TERMINATED
```

Example:

```text
Thread Created
      |
      v
READY
      |
      v
RUNNING
      |
      v
WAITING
      |
      v
READY
      |
      v
RUNNING
      |
      v
TERMINATED
```

---

# What Is Context Switching?

Suppose:

```text
Thread1
Thread2
Thread3
```

CPU:

```text
Run Thread1

Save State

Run Thread2

Save State

Run Thread3
```

This is:

```text
Context Switching
```

The OS saves:

```text
Registers
Program Counter
Stack Pointer
```

and restores another thread.

---

# What Is The GIL?

GIL:

```text
Global Interpreter Lock
```

A lock inside CPython.

Rule:

```text
Only one thread can execute Python bytecode at a time.
```

---

# Example

```python
x += 1
```

requires Python bytecode execution.

Before executing:

```text
Acquire GIL
```

After execution:

```text
Release GIL
```

---

# Two Threads On Two Cores

Machine:

```text
Core1
Core2
```

Threads:

```text
Thread1
Thread2
```

OS schedules:

```text
Core1 -> Thread1

Core2 -> Thread2
```

Looks parallel.

But:

```text
Thread1 owns GIL
```

Result:

```text
Thread1 executes Python

Thread2 waits for GIL
```

---

# What Happens To Thread2?

Thread2 is scheduled.

Thread2 gets CPU.

Thread2 tries:

```python
x += 1
```

Needs GIL.

Cannot acquire it.

Thread blocks.

OS sees:

```text
Waiting Thread
```

and schedules something else.

---

# Important Distinction

OS Scheduling:

```text
Can both threads run?
```

Answer:

```text
YES
```

GIL:

```text
Can both execute Python bytecode?
```

Answer:

```text
NO
```

---

# CPU Bound Example

Thread1:

```python
while True:
    calculate_prime()
```

Thread2:

```python
while True:
    calculate_prime()
```

Result:

```text
Thread1 executes

Thread2 waits

Thread2 executes

Thread1 waits
```

Alternating ownership of GIL.

No true parallel Python execution.

---

# I/O Bound Example

Thread1:

```python
data = socket.recv()
```

Thread2:

```python
handle_request()
```

During:

```python
recv()
```

Python releases GIL.

Now:

```text
Thread1 waiting for network

Thread2 executes
```

This is why threads help web servers.

---

# GIL Release Edge Cases

Python releases GIL during:

```text
socket.recv()

socket.send()

time.sleep()

disk I/O

database I/O

network I/O
```

Example:

```python
time.sleep(20)
```

Thread enters:

```text
WAITING
```

GIL released.

Other threads run.

---

# Threaded Web Server

Client1:

```python
time.sleep(20)
```

Thread1:

```text
WAITING
```

Client2:

```python
return "hello"
```

Thread2:

```text
RUNNING
```

Response returns immediately.

---

# Why Threading Works For Web Servers

Most web servers spend time:

```text
Waiting
Waiting
Waiting
Waiting
```

Examples:

```text
Database

Redis

Filesystem

External APIs

Network
```

While waiting:

```text
GIL released
```

Other threads execute.

---

# Why Threading Fails For CPU Work

Example:

```python
Image Processing

Machine Learning

Video Encoding

Prime Number Search

Encryption
```

These are:

```text
CPU Bound
```

Threads compete for GIL.

No real speedup.

---

# Multiprocessing

Solution:

```python
Process1
Process2
```

Each process has:

```text
Own Memory

Own GIL
```

Architecture:

```text
Core1 -> Process1

Core2 -> Process2
```

Now:

```text
True Parallel Execution
```

---

# Thread vs Process

Threads:

```text
Shared Memory

Fast Communication

One GIL
```

Processes:

```text
Separate Memory

Higher Cost

Multiple GILs

True Parallelism
```

---

# Why Async Was Invented

Thread Model:

```text
10000 Clients

10000 Threads
```

Problems:

```text
Memory

Context Switching

Scheduler Overhead
```

Most threads are waiting.

---

# Async Model

Instead:

```text
1 Thread

1 Event Loop

10000 Connections
```

Architecture:

```text
Event Loop

    |
    +---- Client1
    +---- Client2
    +---- Client3
    ...
```

No thread explosion.

---

# Edge Case 1

Two CPU-bound threads.

```python
while True:
    pass
```

Question:

```text
Will they run in parallel?
```

Answer:

```text
No

GIL prevents simultaneous Python execution.
```

---

# Edge Case 2

Two threads doing:

```python
time.sleep(10)
```

Question:

```text
Will they overlap?
```

Answer:

```text
Yes

sleep() releases GIL.
```

---

# Edge Case 3

Thread1 waiting:

```python
socket.recv()
```

Thread2 processing request.

Question:

```text
Can Thread2 execute?
```

Answer:

```text
Yes

recv() releases GIL.
```

---

# Edge Case 4

C Extensions

Example:

```text
NumPy

Pandas

TensorFlow

PyTorch
```

Many release GIL internally.

Result:

```text
Can execute in parallel.
```

Even inside threads.

---

# Edge Case 5

Multiple Processes

```python
multiprocessing.Process
```

Question:

```text
Can two cores execute simultaneously?
```

Answer:

```text
Yes

Each process has its own GIL.
```

---

# Interview Questions

Q1:

Who schedules Python threads?

Answer:

```text
Operating System Scheduler
```

---

Q2:

Does GIL prevent thread scheduling?

Answer:

```text
No

OS still schedules threads.
```

---

Q3:

What does GIL prevent?

Answer:

```text
Multiple threads executing Python bytecode simultaneously.
```

---

Q4:

Why do threads help web servers?

Answer:

```text
Web servers are mostly I/O bound.

I/O releases the GIL.
```

---

Q5:

Why use multiprocessing?

Answer:

```text
True CPU parallelism.
```

---

# Senior Engineer Mental Model

Think of:

```text
OS Scheduler
```

as:

```text
Traffic Police
```

and:

```text
GIL
```

as:

```text
A Single-Key Room
```

Many threads may arrive.

But:

```text
Only one thread can hold the key.
```

and enter the room to execute Python bytecode.

Everyone else waits.

That single idea explains most Python threading behavior.
