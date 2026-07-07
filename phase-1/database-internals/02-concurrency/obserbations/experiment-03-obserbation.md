# Experiment 03 — Does `SELECT` Wait for a Row Lock?

## Goal

Understand how PostgreSQL behaves when:

* Transaction A updates a row and holds a row-level lock.
* Transaction B executes a normal `SELECT` on the same row.

Determine whether the `SELECT` blocks or immediately returns a result.

---

# Initial Database State

Before starting the experiment:

```sql
SELECT
    id,
    click_count
FROM urls
WHERE id = 1;
```

Result:

```text
id    click_count
-----------------
1     0
```

---

# Transaction A

Executed:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

### SQLAlchemy Log

```text
BEGIN (implicit)

UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

### Observation

* SQLAlchemy started an implicit transaction.
* PostgreSQL acquired a row-level lock on the updated row.
* The transaction remained open while waiting for `COMMIT`.

At this point:

```text
Database (Committed Value)

click_count = 0

--------------------------------

Transaction A (Uncommitted Change)

click_count = 1
```

---

# Transaction B (Before COMMIT)

Executed:

```sql
SELECT
    click_count
FROM urls
WHERE id = 1;
```

Result:

```text
click_count = 0
```

### Observation

The SELECT:

* Did **not** wait.
* Did **not** block.
* Returned immediately.
* Returned the last committed value.

Transaction B could not see Transaction A's uncommitted UPDATE.

---

# Transaction A

Executed:

```sql
COMMIT;
```

### Observation

The transaction completed successfully.

The row-level lock was released.

The updated row became the latest committed version.

---

# Transaction B (After COMMIT)

Executed the same SELECT again.

```sql
SELECT
    click_count
FROM urls
WHERE id = 1;
```

Result:

```text
click_count = 1
```

### Observation

After Transaction A committed:

* Transaction B immediately observed the new value.
* No blocking occurred.

---

# Timeline

```text
Time
────────────────────────────────────────────────────────────>

Transaction A

UPDATE click_count = 1

│

│  (Not Committed)

│

│────────────────────────────── COMMIT ─────────────────────►

────────────────────────────────────────────────────────────

Transaction B

SELECT

↓

Returns 0

────────────────────────────────────────────────────────────

SELECT

↓

Returns 1
```

---

# Why Did the SELECT Not Wait?

A normal `SELECT` does not require a row-level lock.

Instead of waiting for Transaction A to finish, PostgreSQL returned the last committed version of the row.

Conceptually:

```text
Committed Version

click_count = 0

↓

Transaction A Updates

↓

Uncommitted Version

click_count = 1

↓

Transaction B Reads

↓

Returns Committed Version (0)

↓

Transaction A Commits

↓

Committed Version Becomes 1

↓

Future SELECT Returns 1
```

This behavior is implemented using PostgreSQL's **Multi-Version Concurrency Control (MVCC)**.

---

# Key Learnings

* A normal `SELECT` does not block when another transaction holds a row-level lock.
* Readers do not wait for uncommitted writers.
* Readers see the most recent committed version of the row.
* Uncommitted changes remain visible only to the transaction that made them.
* After the transaction commits, subsequent `SELECT` statements observe the new committed value.
* PostgreSQL achieves this behavior using MVCC.

---

# Comparison with Previous Experiments

## Experiment 01 — Lost Update

```text
Read

↓

Modify in Python

↓

Write
```

Result:

```text
Lost Update
```

---

## Experiment 02 — Atomic UPDATE

```text
UPDATE click_count = click_count + 1
```

Result:

```text
Second UPDATE waited for the row lock.

Final value = 2.
```

---

## Experiment 03 — Normal SELECT

```text
UPDATE

↓

SELECT
```

Result:

```text
SELECT did not wait.

Returned the last committed value.
```

---

# Production Relevance

This behavior allows PostgreSQL to support high concurrency.

Applications can continue reading data while other transactions are updating it.

As a result:

* Readers are rarely blocked.
* Read throughput remains high.
* Users observe a consistent, committed view of the database without seeing partially completed work.

This is one of the primary advantages of PostgreSQL's MVCC architecture.
