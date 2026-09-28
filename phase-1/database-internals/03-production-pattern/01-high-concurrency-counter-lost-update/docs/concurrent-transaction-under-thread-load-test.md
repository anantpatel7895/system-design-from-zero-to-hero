# Understanding Concurrent Transactions During the Thread Load Test

## Question

If:

```python
THREADS = 10
```

Does that mean PostgreSQL executes **10 transactions simultaneously**?

The answer is:

> **Not exactly.**

There are **10 concurrent client threads**, but that does **not** mean all 10 transactions are actively executing SQL at the same instant.

---

# Benchmark Configuration

```python
THREADS = 10

INCREMENTS_PER_THREAD = 100
```

Each thread performs:

```python
db = SessionLocal()

for _ in range(100):
    service.atomic_increment(db, 1)

db.close()
```

Each iteration performs one transaction:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;

COMMIT;
```

Therefore:

```text
10 Threads

×

100 Transactions

=

1000 Total Transactions
```

---

# Does PostgreSQL Execute 1000 Transactions at Once?

No.

The transactions are executed continuously over time.

At any moment, some transactions have:

* Already committed.
* Just started.
* Are executing SQL.
* Are waiting for a row lock.
* Are waiting for the database response.
* Are preparing the next transaction.

The number of actively executing transactions changes continuously.

---

# Thread Lifecycle

Each thread repeatedly performs the following steps:

```text
Python Code

↓

Send SQL Query

↓

Wait for PostgreSQL

↓

Receive Result

↓

Commit

↓

Start Next Transaction
```

When the thread sends the SQL statement, it blocks while waiting for PostgreSQL to complete the request.

During this waiting period, the operating system schedules another runnable thread.

---

# Timeline Example

```text
Time
────────────────────────────────────────────────────────────>

Thread 1

Transaction 1
──────────────┐
              └──────────────

Thread 2

      Transaction 1
      ──────────────┐
                    └──────────────

Thread 3

            Transaction 1
            ──────────────┐
                          └──────────────
```

Although all threads are active, they do not execute at exactly the same CPU cycle.

---

# PostgreSQL Perspective

Assuming the connection pool allows all ten threads to obtain a connection:

```text
10 Threads

↓

10 Database Connections

↓

10 PostgreSQL Backend Processes
```

Each backend process may be in a different state.

Example:

```text
Backend 1

Executing UPDATE

────────────────────────

Backend 2

Waiting for Row Lock

────────────────────────

Backend 3

Executing COMMIT

────────────────────────

Backend 4

Waiting for Next Query

────────────────────────

Backend 5

Idle
```

Not every backend process is actively executing SQL.

---

# Updating the Same Row

Every transaction executes:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

Since all transactions modify the same row, PostgreSQL protects the row using a row-level lock.

Conceptually:

```text
Backend 1

Acquire Row Lock

↓

Execute UPDATE

↓

COMMIT

↓

Release Lock

──────────────────────────────

Backend 2

UPDATE

↓

Waiting for Row Lock

──────────────────────────────

Backend 3

UPDATE

↓

Waiting for Row Lock
```

Only one transaction can modify the row at a time.

All other transactions wait until the lock becomes available.

---

# Important Distinction

There is a significant difference between:

```text
Concurrent Transactions
```

and

```text
Transactions Actively Executing the Critical Section
```

For example:

```text
10 Threads

↓

10 Open Transactions

↓

Only 1 Transaction Updating Row id = 1
```

The remaining transactions are waiting for the row lock.

---

# Summary

With:

```python
THREADS = 10
```

you typically have:

* Up to **10 concurrent client threads**.
* Up to **10 database connections** (assuming the connection pool allows it).
* Up to **10 PostgreSQL backend processes**.
* Up to **10 open transactions**.

However, because every transaction updates the same row:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

only **one transaction at a time** can execute the update.

The remaining transactions wait for the row-level lock before continuing.

---

# Key Takeaway

Concurrency does **not** imply simultaneous execution.

Multiple transactions may exist concurrently, but when they compete for the same database resource, PostgreSQL serializes access using row-level locking.

This guarantees correctness but also introduces lock contention, which eventually becomes the primary scalability bottleneck for a single-row counter under heavy load.
