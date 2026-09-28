# Why Throughput (TPS) First Increases and Then Decreases

## Benchmark Result

| Threads | Expected |  Actual | Time (sec) |       TPS |
| ------: | -------: | ------: | ---------: | --------: |
|      10 |    1,000 |   1,000 |      0.134 |     7,441 |
|      50 |    5,000 |   5,000 |      0.586 |     8,527 |
|     100 |   10,000 |  10,000 |      1.163 |     8,599 |
|     200 |   20,000 |  20,000 |      2.314 | **8,644** |
|     500 |   50,000 |  50,000 |      5.890 |     8,489 |
|    1000 |  100,000 | 100,000 |     12.017 |     8,322 |

Throughout the benchmark:

```text
Lost Updates = 0
```

This confirms that the atomic SQL implementation is **100% correct**.

However, the throughput (TPS) does not increase forever.

Instead, it follows this pattern:

```text
Low Threads
        │
        ▼
TPS Increases
        │
        ▼
System Saturates
        │
        ▼
TPS Plateaus
        │
        ▼
TPS Begins to Decrease
```

This behavior is observed in almost every high-performance system.

---

# Understanding TPS

TPS means **Transactions Per Second**.

Each increment performs one transaction:

```sql
BEGIN;

UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;

COMMIT;
```

Therefore:

```text
1 Increment

=

1 Database Transaction
```

For example:

```text
1000 Threads

×

100 Increments

=

100,000 Transactions
```

If those transactions complete in:

```text
12.017 seconds
```

Then:

```text
TPS

=

100000 / 12.017

=

8321 Transactions/Second
```

---

# Phase 1 — Low Concurrency

Example:

```text
10 Threads

↓

7441 TPS
```

At this stage the database is **underutilized**.

There are moments when PostgreSQL has no work to perform.

Conceptually:

```text
Database

Transaction

↓

Idle

↓

Transaction

↓

Idle

↓

Transaction
```

The CPU spends part of its time waiting for new requests.

Increasing the number of threads provides more work for PostgreSQL.

Therefore throughput increases.

---

# Factory Analogy

Imagine a factory with one machine.

Only two workers supply parts.

```text
Worker

↓

Machine

↓

Worker
```

The machine occasionally waits because there are not enough workers.

Adding more workers keeps the machine busy.

Productivity increases.

---

# Phase 2 — Better Utilization

Increasing to:

```text
50 Threads

↓

8527 TPS
```

Now PostgreSQL rarely waits.

Whenever one transaction finishes, another is already waiting.

Conceptually:

```text
Transaction

↓

Transaction

↓

Transaction

↓

Transaction
```

The CPU is almost continuously executing useful work.

This is why throughput increases.

---

# Phase 3 — Saturation

Around:

```text
200 Threads

↓

8644 TPS
```

the throughput reaches its maximum.

At this point PostgreSQL is fully utilized.

The limiting factor is no longer Python.

The limiting factor becomes the database itself.

---

# Why?

Every transaction executes:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

Every transaction modifies the **same row**.

PostgreSQL protects that row using a row-level lock.

Conceptually:

```text
Transaction A

Acquire Row Lock

↓

UPDATE

↓

COMMIT

↓

Release Lock
```

Only one transaction may hold the lock.

Every other transaction waits.

---

# Row Lock Queue

Suppose ten transactions arrive simultaneously.

```text
Transaction 1

↓

Acquire Lock

↓

Running

────────────────────────────

Transaction 2

↓

Waiting

────────────────────────────

Transaction 3

↓

Waiting

────────────────────────────

Transaction 4

↓

Waiting

────────────────────────────

...

────────────────────────────

Transaction 10

↓

Waiting
```

Although there are ten concurrent transactions, only one is updating the row.

The remaining transactions are blocked.

---

# Phase 4 — Too Much Concurrency

Now increase to:

```text
500 Threads
```

TPS becomes:

```text
8489
```

Increasing further:

```text
1000 Threads

↓

8322 TPS
```

Notice that throughput actually decreases.

---

# Why Does TPS Decrease?

At this point the database is already operating at maximum capacity.

Adding more threads does **not** increase useful work.

Instead it increases overhead.

---

# Operating System Scheduling

With:

```text
10 Threads
```

the scheduler has little work.

With:

```text
1000 Threads
```

the scheduler repeatedly performs:

```text
Thread 1

↓

Thread 217

↓

Thread 504

↓

Thread 89

↓

Thread 741

↓

Thread 32

↓

...
```

Every switch requires saving and restoring CPU state.

This is called **context switching**.

Context switching consumes CPU time but performs no useful work.

---

# PostgreSQL Backend Scheduling

Each database connection has its own backend process.

With hundreds of concurrent connections PostgreSQL must also schedule many backend processes.

Some are:

```text
Running
```

Others are:

```text
Waiting for Row Lock
```

Others are:

```text
Waiting for Client
```

The operating system continuously switches between these backend processes.

Again, this creates overhead.

---

# Longer Lock Queues

With more concurrent requests:

```text
Thread 1

↓

Acquire Lock

↓

Running

────────────────────────────

Threads 2-1000

↓

Waiting
```

The queue becomes much longer.

Transactions spend more time waiting than performing useful work.

---

# The Factory Analogy Revisited

Imagine a machine capable of producing:

```text
8000 bottles/second
```

### Two Workers

```text
Machine

↓

Occasionally Waiting

↓

6000 bottles/sec
```

---

### Ten Workers

```text
Machine

Always Busy

↓

8000 bottles/sec
```

Perfect utilization.

---

### One Thousand Workers

```text
Machine

Still Produces

8000 bottles/sec

↓

999 Workers Waiting
```

Hiring more workers does not increase production.

It simply increases the number of people standing in line.

---

# The Scalability Curve

```text
Threads

↓

More Parallel Requests

↓

Higher Utilization

↓

Maximum Throughput

↓

Lock Contention

↓

Scheduling Overhead

↓

Lower TPS
```

Every high-performance system follows this pattern.

---

# Important Insight

More concurrency does **not** always mean more throughput.

Initially:

```text
More Threads

↓

Better Resource Utilization

↓

Higher TPS
```

Eventually:

```text
More Threads

↓

More Waiting

↓

More Context Switching

↓

Longer Lock Queues

↓

Lower TPS
```

This point is called **system saturation**.

---

# Why Large Systems Rarely Update One Row

Your benchmark demonstrates why large-scale systems such as:

* YouTube
* Instagram
* Facebook
* X (Twitter)

do not execute:

```sql
UPDATE posts
SET likes = likes + 1
WHERE id = 123;
```

for every incoming request.

Although the operation is perfectly correct, the row eventually becomes a hotspot.

---

# Production Solutions

To eliminate the bottleneck, production systems often use:

```text
Client Requests

↓

Redis Counter

↓

Periodic Batch Update

↓

PostgreSQL
```

or

```text
Client Requests

↓

Kafka

↓

Background Consumer

↓

Batch UPDATE

↓

PostgreSQL
```

or

```text
Client Requests

↓

Sharded Counters

↓

Aggregate

↓

Final Database Update
```

These architectures reduce lock contention while maintaining high throughput.

---

# Biggest Takeaway

This benchmark demonstrates one of the fundamental principles of systems engineering:

> **Adding concurrency improves throughput only until the bottleneck is fully utilized. Beyond that point, additional concurrency increases contention and scheduling overhead instead of increasing useful work.**

This principle applies to databases, CPUs, disks, web servers, caches, distributed systems, and virtually every scalable architecture.

Understanding where a system saturates is one of the most important skills of a senior systems engineer.
