# Experiment 06 — High-Concurrency Reservations — Observations

## Goal

Verify that the inventory reservation system maintains data consistency under heavy concurrent access.

This experiment simulated multiple customers attempting to reserve the same product simultaneously.

---

# What We Improved from Experiment 05

## Experiment 05

The reservation system was functionally complete.

Features implemented:

* Inventory reservation
* Reservation expiration
* Background cleanup worker

However, only a few users interacted with the system.

The system had not yet been tested under heavy concurrent load.

---

## Experiment 06

We introduced a concurrency benchmark.

```text
100 Concurrent Customers

↓

Reservation Service

↓

PostgreSQL

↓

Inventory Reservation
```

The objective was to verify that the business rules remain correct regardless of how many requests arrive at the same time.

---

# Test Configuration

```text
Initial Stock     : 10

Concurrent Threads: 100

Reservation Qty   : 1
```

Every thread attempted to purchase the same product.

---

# Reservation Flow

Each thread executed exactly the same business logic.

```text
Open Database Session

↓

BEGIN

↓

SELECT ... FOR UPDATE

↓

Read Stock

↓

Enough Stock?

↓

YES

↓

Decrease Stock

↓

Create Reservation

↓

COMMIT

↓

Close Session
```

If stock was unavailable:

```text
BEGIN

↓

SELECT ... FOR UPDATE

↓

Read Stock

↓

Out Of Stock

↓

ROLLBACK

↓

Close Session
```

Every thread owned its own:

* Database session
* Database connection
* Database transaction

This closely resembles how production web servers process concurrent HTTP requests.

---

# Observation 1 — No Overselling

Initial inventory:

```text
Stock = 10
```

Successful reservations:

```text
10
```

Remaining stock:

```text
0
```

At no point did the inventory become negative.

The reservation system successfully prevented overselling.

---

# Observation 2 — Business Invariant

One important business rule must always remain true.

```text
Initial Stock

=

Remaining Stock

+

Successful Reservations
```

Experiment values:

```text
10

=

0

+

10
```

The invariant remained valid throughout the benchmark.

This demonstrates that PostgreSQL row-level locking preserved business correctness under concurrent access.

---

# Observation 3 — Reservation Consistency

Application results:

```text
Successful Reservations = 10
```

Database state:

```text
Reservation Rows = 10
```

Both values matched exactly.

This confirms that every successful reservation resulted in exactly one database record.

There were:

* No duplicate reservations
* No missing reservations
* No partially committed transactions

---

# Observation 4 — PostgreSQL Serialized Access

Although 100 threads executed simultaneously, PostgreSQL allowed only one transaction at a time to modify the locked product row.

Conceptually:

```text
100 Threads

↓

100 Transactions

↓

Row Lock Queue

↓

Transaction 1

↓

Transaction 2

↓

Transaction 3

↓

...
```

Instead of corrupting the inventory, PostgreSQL serialized access to the protected row.

---

# Observation 5 — Lock Contention

The benchmark measured request latency.

Results:

```text
Average Latency : 18.87 ms

Minimum Latency : 0.29 ms

Maximum Latency : 72.23 ms
```

The first requests completed almost immediately because they acquired the row lock without waiting.

Later requests waited for previous transactions to commit before obtaining the lock.

This waiting time is called **lock contention**.

The increased latency is expected and indicates that PostgreSQL is correctly synchronizing concurrent updates.

---

# Observation 6 — Throughput

Benchmark result:

```text
Elapsed Time : 0.075 sec

TPS          : 1335.84
```

This throughput includes the complete reservation workflow:

* Lock acquisition
* Stock validation
* Stock update
* Reservation creation
* Transaction commit

The benchmark measures the performance of the complete business operation rather than a single SQL statement.

---

# Observation 7 — Latency Distribution

Latency metrics:

```text
Average : 18.87 ms

P50     : 11.69 ms

P95     : 69.31 ms

P99     : 72.23 ms
```

Interpretation:

* 50% of requests completed within approximately **11.69 ms**.
* 95% completed within **69.31 ms**.
* Only 1% required approximately **72.23 ms**.

Most requests completed quickly.

Only a small number waited significantly longer because of row-lock contention.

This distribution is more informative than using average latency alone.

---

# Observation 8 — Improved Benchmark Design

Earlier experiments maintained shared counters protected by a threading lock.

```text
Shared Counter

↓

threading.Lock()

↓

Increment
```

This experiment improved the design.

Each worker returned its own `ReservationResult`.

```text
Worker

↓

ReservationResult

↓

Main Thread

↓

Aggregate Results
```

Advantages:

* No shared mutable counters
* Cleaner thread implementation
* Easier to extend
* Richer performance metrics
* Closer to production load-testing frameworks

---

# Final Architecture

```text
                   100 Customers
                         │
                         ▼
                Reservation Service
                         │
                         ▼
                  PostgreSQL
                         │
               SELECT ... FOR UPDATE
                         │
                         ▼
                Row-Level Lock Queue
                         │
                         ▼
         Validate → Update → Reserve → Commit
```

PostgreSQL guaranteed that only one transaction modified the inventory row at a time.

---

# Key Learnings

This experiment demonstrated that:

* Row-level locking prevents overselling.
* Transactions preserve business consistency under concurrent load.
* Every successful reservation is committed exactly once.
* Failed reservations leave the database unchanged.
* Measuring latency distributions (P50, P95, P99) provides significantly more insight than average latency alone.
* Production-quality benchmarks collect per-request metrics rather than relying on shared counters.

---

# Preparation for the Next Phase

The inventory reservation system now supports:

* Safe concurrent reservations
* Automatic reservation expiration
* Background cleanup worker
* High-concurrency validation
* Performance benchmarking

At this point, the project has evolved from learning individual database concepts to implementing a production-style inventory reservation system that preserves correctness, scalability, and observability under concurrent workloads.
