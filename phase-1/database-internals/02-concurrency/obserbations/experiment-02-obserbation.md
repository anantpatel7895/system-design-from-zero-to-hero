# Experiment 02 — Atomic UPDATE

## Goal

Understand how PostgreSQL handles concurrent updates when the increment operation is performed entirely inside the database.

Unlike the previous experiment, the application does **not** read the current value and perform the increment in Python.

Instead, PostgreSQL performs the increment atomically.

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
* PostgreSQL acquired a row-level lock on the row.
* The UPDATE executed successfully.
* The transaction remained open until COMMIT.

---

# Transaction B

Executed while Transaction A had not yet committed.

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

### Observation

The UPDATE did **not** execute immediately.

Instead, Transaction B waited until Transaction A completed.

The SQL statement remained blocked because Transaction A already held the row lock.

---

# Transaction A — COMMIT

Executed:

```python
db.commit()
```

### Observation

After Transaction A committed:

* The row-level lock was released.
* PostgreSQL allowed Transaction B to continue executing its UPDATE.

---

# Transaction B — UPDATE Resumes

Immediately after Transaction A committed:

* PostgreSQL resumed Transaction B.
* Transaction B executed the UPDATE successfully.
* Transaction B committed successfully.

---

# Final Database State

Executed:

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
1     2
```

---

# Timeline

```text
Time
────────────────────────────────────────────────────────────>

Transaction A

UPDATE click_count = click_count + 1

│

│  (Row Lock Acquired)

│

│────────────── COMMIT ────────────────────────────────►

────────────────────────────────────────────────────────────

Transaction B

UPDATE click_count = click_count + 1

│

│  Waiting for Row Lock...

│

│────────────────────────── UPDATE Executes ───────────►

│

COMMIT

────────────────────────────────────────────────────────────

Final Database

click_count = 2
```

---

# Why This Worked

Unlike the previous experiment, the application never performed:

```python
count = count + 1
```

Instead, PostgreSQL performed the increment itself:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

Because the UPDATE modifies the row directly, PostgreSQL automatically acquires a **row-level lock**.

When another transaction attempts to update the same row:

* It cannot proceed immediately.
* It waits until the first transaction commits or rolls back.
* After the lock is released, PostgreSQL re-reads the latest committed row and applies the increment.

As a result, both increments are preserved.

---

# Comparison with Experiment 01

## Experiment 01

```text
Read

↓

Modify in Python

↓

Write
```

Result:

```text
Final Value = 1
```

Reason:

The second transaction overwrote the first transaction's update.

This is known as the **Lost Update** problem.

---

## Experiment 02

```text
UPDATE click_count = click_count + 1
```

Result:

```text
Final Value = 2
```

Reason:

PostgreSQL performed the increment atomically while protecting the row with a row-level lock.

No update was lost.

---

# Key Learnings

* `UPDATE column = column + 1` is an atomic database operation.
* PostgreSQL automatically acquires a row-level lock during an UPDATE.
* Concurrent UPDATE statements on the same row are serialized.
* The second transaction waits until the first transaction releases the lock.
* PostgreSQL re-evaluates the UPDATE using the latest committed row.
* Atomic SQL statements prevent the Lost Update problem.

---

# Production Relevance

This pattern is commonly used for:

* Page view counters
* URL click counters
* Like counters
* Inventory quantities
* Download counters
* Retry counters

Whenever the operation can be expressed as:

```sql
UPDATE table
SET counter = counter + 1
```

it should be preferred over reading the value into the application, modifying it, and writing it back.

This experiment demonstrates why atomic SQL operations are safer and more scalable than application-side read-modify-write logic.
