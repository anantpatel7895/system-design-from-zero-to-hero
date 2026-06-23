# Interview Question: Arrival Rate vs Processing Rate

## Scenario

Consider a server with the following configuration:

```python
server.listen(1000)
```

The server can process:

```text
10 requests/second
```

Incoming traffic arrives at:

```text
100 requests/second
```

Question:

Even with a backlog of 1000, what will eventually happen and why?

---

# Understanding the Numbers

### Arrival Rate

```text
100 requests/second
```

Every second, 100 new requests arrive.

### Processing Rate

```text
10 requests/second
```

Every second, the server can complete only 10 requests.

---

# Queue Growth Calculation

Each second:

```text
100 arrive
10 processed
```

Remaining requests:

```text
100 - 10
=
90 requests
```

Therefore, the queue grows by:

```text
90 requests/second
```

---

# Queue Size Over Time

Initial state:

```text
Queue Size = 0
```

After 1 second:

```text
90 waiting
```

After 2 seconds:

```text
180 waiting
```

After 5 seconds:

```text
450 waiting
```

After 10 seconds:

```text
900 waiting
```

After 11 seconds:

```text
990 waiting
```

After approximately 12 seconds:

```text
1080 waiting
```

But the backlog size is:

```text
1000
```

The queue can no longer hold new requests.

---

# What Happens When the Queue Is Full?

Once the backlog reaches its limit:

```text
1000 pending connections
```

new incoming requests cannot be stored.

The Linux kernel starts:

* Dropping connections
* Rejecting connections
* Timing out connections

Clients may experience:

```text
Connection timed out
```

or

```text
Connection refused
```

---

# Why Increasing Backlog Does Not Solve the Problem

Suppose we increase:

```python
server.listen(1000)
```

to

```python
server.listen(10000)
```

Will the problem disappear?

### No.

The queue simply takes longer to fill.

The server still processes:

```text
10 requests/second
```

while traffic still arrives at:

```text
100 requests/second
```

The imbalance remains:

```text
Arrival Rate
      >
Processing Rate
```

The backlog only acts as a temporary buffer.

---

# Restaurant Analogy

Imagine:

```text
100 customers arrive every minute
```

but

```text
10 customers can be served every minute
```

A larger waiting room allows more people to wait.

However:

```text
Customers are not being served any faster.
```

Eventually the waiting room fills.

New customers must be turned away.

---

# The Real Problem

The actual issue is not:

```text
Small Queue
```

The actual issue is:

```text
Low Processing Capacity
```

---

# Real Solutions

## Option 1: Increase Processing Capacity

Example:

```text
10 req/sec
      →
100 req/sec
```

Methods:

* Faster code
* Better algorithms
* Database optimization
* Caching

---

## Option 2: Scale Horizontally

```text
Load Balancer
      |
      +---- Server A
      +---- Server B
      +---- Server C
```

Multiple servers share the load.

---

## Option 3: Use Concurrency

Examples:

* Thread Pool
* Async I/O
* Event Loops

Used by:

* FastAPI
* Uvicorn
* Nginx
* NodeJS

---

# Senior Engineer Takeaway

The most important scalability equation is:

```text
Arrival Rate
       -
Processing Rate
       =
Queue Growth Rate
```

If:

```text
Arrival Rate > Processing Rate
```

then:

```text
Queue grows
      ↓
Queue fills
      ↓
Requests wait longer
      ↓
Timeouts occur
      ↓
System failure
```

This exact pattern appears in:

* Web Servers
* Kafka
* RabbitMQ
* Database Connection Pools
* Load Balancers
* Kubernetes Work Queues

Understanding this principle is fundamental to system design.
