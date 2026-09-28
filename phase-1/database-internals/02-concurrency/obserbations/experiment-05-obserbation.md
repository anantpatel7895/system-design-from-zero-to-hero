# Experiment 05 — `SELECT ... FOR UPDATE`

## Goal

Understand how `SELECT ... FOR UPDATE` behaves compared to a normal `SELECT`.

Unlike a normal `SELECT`, `SELECT ... FOR UPDATE` explicitly requests a row-level lock from PostgreSQL.

This experiment demonstrates how PostgreSQL serializes transactions that attempt to lock the same row.

---

# Initial State

The row already existed.

```text
id = 1
click_count = 2
```

---

# Transaction A

Executed:

```sql
SELECT *
FROM urls
WHERE id = 1
FOR UPDATE;
```

### SQLAlchemy Log

```text
BEGIN (implicit)

SELECT *
FROM urls
WHERE id = 1
FOR UPDATE
```

### Observation

* SQLAlchemy started a transaction.
* PostgreSQL successfully returned the row.
* PostgreSQL acquired a **row-level lock**.
* Transaction A remained open while waiting for COMMIT.

Application output:

```text
Row Locked
```

---

# Transaction B

Executed the same statement.

```sql
SELECT *
FROM urls
WHERE id = 1
FOR UPDATE;
```

### Observation

The SQL statement did **not** return immediately.

Transaction B waited until Transaction A committed.

Only after Transaction A released the lock did Transaction B receive the row.

This demonstrates that `SELECT ... FOR UPDATE` participates in PostgreSQL's row-locking mechanism.

---

# Transaction A

Executed:

```sql
COMMIT;
```

### Observation

Immediately after Transaction A committed:

* The row-level lock was released.
* Transaction B resumed execution.
* Transaction B successfully acquired the lock and returned the row.

---

# PostgreSQL Observation

While Transaction B was waiting, `pg_stat_activity` showed:

```text
Transaction A

State:
idle in transaction
```

Meaning:

* Transaction A had finished executing the SQL statement.
* The transaction remained open.
* The row lock was still being held.

---

Transaction B showed:

```text
State:
active

wait_event_type:
Lock

wait_event:
transactionid
```

### Observation

Transaction B was blocked while waiting for a lock held by Transaction A.

PostgreSQL suspended execution until the conflicting transaction completed.

---

# pg_locks Observation

Important lock information:

```text
Transaction A

transactionid

ExclusiveLock

Granted = true
```

Transaction B

```text
transactionid

ShareLock

Granted = false
```

### Observation

Transaction B requested a lock but PostgreSQL did not grant it immediately.

Instead, Transaction B waited until Transaction A released its lock.

---

# Timeline

```text
Time
────────────────────────────────────────────────────────────>

Transaction A

SELECT ... FOR UPDATE

↓

Row Locked

↓

Waiting

↓

COMMIT

────────────────────────────────────────────────────────────

Transaction B

SELECT ... FOR UPDATE

↓

Waiting for Lock

↓

Lock Granted

↓

Row Returned

↓

COMMIT
```

---

# Comparison with Normal SELECT

## Normal SELECT

```sql
SELECT *
FROM urls
WHERE id = 1;
```

Behavior:

* Does not acquire a row lock.
* Does not wait.
* Reads the latest committed row version using MVCC.

---

## SELECT ... FOR UPDATE

```sql
SELECT *
FROM urls
WHERE id = 1
FOR UPDATE;
```

Behavior:

* Requests a row-level lock.
* Waits if another transaction already holds a conflicting lock.
* Guarantees exclusive access to the selected row until the transaction completes.

---

# Key Learnings

* `SELECT ... FOR UPDATE` is fundamentally different from a normal `SELECT`.
* A normal `SELECT` uses MVCC and does not block on row locks.
* `SELECT ... FOR UPDATE` **explicitly acquires a row-level lock**.
* If another transaction already holds the lock, PostgreSQL suspends the second transaction until the first transaction commits or rolls back.
* Lock waits are visible in `pg_stat_activity` through:

  * `wait_event_type = Lock`
  * `wait_event = transactionid`
* `pg_locks` provides detailed information about granted and waiting locks.

---

# Production Relevance

`SELECT ... FOR UPDATE` is commonly used when an application must ensure that only one transaction can modify a row at a time.

Typical use cases include:

* Bank account balance updates
* Inventory reservation
* Seat booking systems
* Order processing
* Wallet transactions
* Job queues

It allows the application to safely perform:

```text
Read

↓

Business Logic

↓

Update

↓

Commit
```

without another transaction modifying the same row concurrently.

---

# Biggest Takeaway

This experiment demonstrates the fundamental difference between reading data and locking data.

A normal `SELECT` asks PostgreSQL:

> "Show me the latest committed version."

`SELECT ... FOR UPDATE` asks PostgreSQL:

> "Show me the row **and prevent other transactions from acquiring a conflicting lock on it until I finish**."

This distinction is one of the most important concepts in relational database concurrency control.
