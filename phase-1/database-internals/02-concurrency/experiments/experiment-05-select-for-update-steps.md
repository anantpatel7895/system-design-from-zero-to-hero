# Experiment 05 — `SELECT ... FOR UPDATE`

## Goal

Understand how `SELECT ... FOR UPDATE` differs from a normal `SELECT`.

In the previous experiment we observed:

```sql id="b0vbne"
SELECT ...
```

did **not** wait.

In this experiment we will execute:

```sql id="kpydwt"
SELECT ...
FOR UPDATE
```

and observe how PostgreSQL acquires a row-level lock.

---

# Initial Database State

Reset the counter.

```sql id="q32kik"
UPDATE urls
SET click_count = 0
WHERE id = 1;
```

Verify:

```sql id="vhzd3v"
SELECT
    id,
    click_count
FROM urls
WHERE id = 1;
```

Expected:

```text id="90s2fe"
id    click_count
-----------------
1     0
```

---

# Transaction A

Create:

```text id="ezw0pj"
experiments/experiment-05-transaction-a.py
```

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener"

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)

db = Session()

print("=" * 60)
print("Transaction A")
print("=" * 60)

result = db.execute(
    text("""
        SELECT *
        FROM urls
        WHERE id = 1
        FOR UPDATE
    """)
)

print(result.first())

print("\nRow Locked")

input("Press ENTER to COMMIT...")

db.commit()

print("Committed")

input("Press ENTER to exit...")
```

---

# Transaction B

Create:

```text id="fyijxk"
experiments/experiment-05-transaction-b.py
```

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener"

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)

db = Session()

print("=" * 60)
print("Transaction B")
print("=" * 60)

result = db.execute(
    text("""
        SELECT *
        FROM urls
        WHERE id = 1
        FOR UPDATE
    """)
)

print(result.first())

db.commit()

print("Committed")
```

---

# Execution Steps

## Step 1

Run **Transaction A**.

It executes:

```sql id="9j8zkk"
SELECT *
FROM urls
WHERE id = 1
FOR UPDATE;
```

Do **not** commit.

Leave it waiting.

---

## Step 2

Run **Transaction B**.

It executes the same SQL.

Observe carefully.

Does it return immediately?

Or does it wait?

---

## Step 3

Commit Transaction A.

Observe what immediately happens in Transaction B.

---

## Observe PostgreSQL

While Transaction B is waiting, execute:

```sql id="4y3jlk"
SELECT
    pid,
    state,
    wait_event_type,
    wait_event,
    query
FROM pg_stat_activity
WHERE datname = 'url_shortener';
```

Also inspect locks.

```sql id="cmxw4f"
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
    WHERE datname='url_shortener'
);
```

---

# Questions

## Q1

Did Transaction B wait?

---

## Q2

When did Transaction B continue?

---

## Q3

Why is the behavior different from a normal `SELECT`?

---

## Q4

What kind of lock do you think `SELECT ... FOR UPDATE` acquires?

Do not search online.

Answer using only your observations.

---

# Objective

By the end of this experiment you should understand:

* Why a normal `SELECT` does not block.
* Why `SELECT ... FOR UPDATE` does block.
* How applications intentionally lock rows before modifying them.
* Why `SELECT ... FOR UPDATE` is widely used in banking, inventory, reservation, and order-processing systems.

This experiment introduces explicit row locking, which is one of the most important concurrency control techniques in relational databases.
