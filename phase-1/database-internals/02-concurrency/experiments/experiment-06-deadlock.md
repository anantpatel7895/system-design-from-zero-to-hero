# Experiment 06 — Deadlock

## Goal

Create a real deadlock and observe how PostgreSQL detects and resolves it.

This experiment demonstrates why lock ordering is important in concurrent systems.

---

# Setup

Create two rows.

```sql
UPDATE urls
SET click_count = 0
WHERE id IN (1,2);
```

If row `2` does not exist, insert it first.

Verify:

```sql
SELECT
    id,
    click_count
FROM urls
WHERE id IN (1,2)
ORDER BY id;
```

Expected:

```text
1    0

2    0
```

---

# Transaction A

Create:

```text
experiments/experiment-06-transaction-a.py
```

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener"

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)

db = Session()

print("Transaction A")

db.execute(
    text("""
        UPDATE urls
        SET click_count = click_count + 1
        WHERE id = 1
    """)
)

print("Locked Row 1")

input("Press ENTER to lock Row 2...")

db.execute(
    text("""
        UPDATE urls
        SET click_count = click_count + 1
        WHERE id = 2
    """)
)

print("Updated Row 2")

db.commit()

print("Committed")
```

---

# Transaction B

Create:

```text
experiments/experiment-06-transaction-b.py
```

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener"

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)

db = Session()

print("Transaction B")

db.execute(
    text("""
        UPDATE urls
        SET click_count = click_count + 1
        WHERE id = 2
    """)
)

print("Locked Row 2")

input("Press ENTER to lock Row 1...")

db.execute(
    text("""
        UPDATE urls
        SET click_count = click_count + 1
        WHERE id = 1
    """)
)

print("Updated Row 1")

db.commit()

print("Committed")
```

---

# Execution Order

## Step 1

Run Transaction A.

It locks:

```text
Row 1
```

Stop.

---

## Step 2

Run Transaction B.

It locks:

```text
Row 2
```

Stop.

---

## Step 3

Resume Transaction A.

It tries to update:

```text
Row 2
```

It should wait.

---

## Step 4

Resume Transaction B.

It tries to update:

```text
Row 1
```

Observe carefully.

---

# Expected Result

After a short delay (typically about one second), PostgreSQL should abort one of the transactions.

You should see an error similar to:

```text
ERROR: deadlock detected
```

One transaction will be rolled back.

The other transaction will continue.

---

# Observe PostgreSQL

While both transactions are waiting, execute:

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

Also inspect locks:

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

---

# Questions

## Q1

Which transaction PostgreSQL aborted?

---

## Q2

How long did PostgreSQL wait before detecting the deadlock?

---

## Q3

What error message did PostgreSQL return?

---

## Q4

Why couldn't PostgreSQL allow both transactions to continue?

---

# Objective

By the end of this experiment you should understand:

* What a deadlock is.
* How deadlocks differ from ordinary lock waits.
* How PostgreSQL detects deadlocks automatically.
* Why applications must be prepared to retry aborted transactions.
* Why acquiring locks in a consistent order helps prevent deadlocks.
