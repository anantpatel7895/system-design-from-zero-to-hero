# Experiment 02 — Atomic UPDATE

## Goal

Understand how PostgreSQL handles concurrent updates when the increment operation is performed entirely inside the database.

In the previous experiment, we implemented the following sequence:

```text
Read

↓

Modify in Python

↓

Write
```

This resulted in a **Lost Update**.

In this experiment, we remove the read-modify-write logic from the application and let PostgreSQL perform the increment atomically.

---

# Initial Database State

Reset the counter:

```sql
UPDATE urls
SET click_count = 0
WHERE id = 1;
```

Verify:

```sql
SELECT
    id,
    click_count
FROM urls
WHERE id = 1;
```

Expected:

```text
id    click_count
-----------------
1     0
```

---

# Scenario

Two transactions execute exactly the same SQL statement concurrently.

```text
            Transaction A                 Transaction B

                    │                             │
                    ▼                             ▼
       UPDATE click_count + 1        UPDATE click_count + 1
                    │                             │
                    ▼                             ▼
                 COMMIT                        COMMIT
```

Unlike the previous experiment, **Python never reads the current value**.

The database performs the increment itself.

---

# Transaction A

Create:

```text
experiments/experiment-02-transaction-a.py
```

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg://username:password@localhost:5432/url_shortener"

engine = create_engine(
    DATABASE_URL,
    echo=True,
)

Session = sessionmaker(bind=engine)

db = Session()

print("=" * 60)
print("Transaction A")
print("=" * 60)

input("Press ENTER to execute UPDATE...")

db.execute(
    text("""
        UPDATE urls
        SET click_count = click_count + 1
        WHERE id = 1
    """)
)

print("UPDATE Executed")

input("Press ENTER to COMMIT...")

db.commit()

print("Committed")

input("Press ENTER to exit...")
```

---

# Transaction B

Create:

```text
experiments/experiment-02-transaction-b.py
```

Use exactly the same code as Transaction A.

---

# Execution Order

## Step 1

Reset the counter.

```sql
UPDATE urls
SET click_count = 0
WHERE id = 1;
```

---

## Step 2

Start **Transaction A**.

Pause before executing the UPDATE.

---

## Step 3

Start **Transaction B**.

Pause before executing the UPDATE.

---

## Step 4

Execute the UPDATE in **Transaction A**.

Do **not** commit yet.

---

## Step 5

Execute the UPDATE in **Transaction B**.

Observe carefully.

Does it execute immediately?

Or does it wait?

---

## Step 6

Commit **Transaction A**.

Observe what happens in **Transaction B**.

---

## Step 7

Commit **Transaction B**.

---

## Step 8

Verify the final value.

```sql
SELECT
    click_count
FROM urls
WHERE id = 1;
```

---

# Observe PostgreSQL

While the experiment is running, execute:

```sql
SELECT
    pid,
    state,
    wait_event_type,
    wait_event,
    query
FROM pg_stat_activity
WHERE datname = 'url_shortener';
```

Also inspect the locks held by each transaction.

```sql
SELECT
    pid,
    locktype,
    relation::regclass,
    mode,
    granted
FROM pg_locks
WHERE pid IN (
    SELECT pid
    FROM pg_stat_activity
    WHERE datname = 'url_shortener'
);
```

Record your observations.

---

# Questions

## Q1

Did Transaction B execute immediately?

Or did it wait?

---

## Q2

What happened after Transaction A committed?

---

## Q3

What was the final value of `click_count`?

---

## Q4

Why is the result different from Experiment 01?

Explain the behavior based on your observations.

---

# Objective

This experiment demonstrates how PostgreSQL executes an atomic UPDATE.

The goal is to understand:

* Why `UPDATE column = column + 1` behaves differently from a read-modify-write pattern.
* Whether PostgreSQL automatically synchronizes concurrent updates.
* How row-level locking protects data consistency.
* Why atomic SQL statements are preferred over application-side calculations for counters and similar operations.

Do not attempt to explain the mechanism yet.

First observe the behavior.

We will explain **row-level locking** after completing the experiment.
