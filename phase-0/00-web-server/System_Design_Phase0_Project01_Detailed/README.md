
# Phase 0 – Project 0.1 – Build a Web Server From Scratch

## Goal

Build a TCP server using raw sockets and understand what happens between a browser and your application.

## Learning Outcomes

- OS fundamentals
- Processes and Threads
- TCP/IP
- Sockets
- bind()
- listen()
- accept()
- Backlog queues
- Linux Kernel responsibilities
- Blocking I/O
- Threaded servers
- Arrival Rate vs Processing Rate

---

# Evolution of the Server

1. simple_server.py
2. continuous_server.py
3. threaded_server.py

---

# Architecture

Internet
    |
Network Card (NIC)
    |
Linux Kernel
    |
Socket
    |
Python Application

---

# Key Insight

The kernel owns:
- TCP stack
- Ports
- Handshakes
- Queues

Python owns:
- Business logic
- Request processing
- Responses

---

# Most Important Concept

Arrival Rate > Processing Rate

=> Queue Growth
=> Queue Full
=> Timeouts

This concept appears later in:
- Kafka
- RabbitMQ
- Databases
- Load Balancers
- Kubernetes

---

# Project Status

Phase 0 Project 0.1: Completed
Phase 0 Project 0.2: Unlocked
