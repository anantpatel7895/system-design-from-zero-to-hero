# Experiment 03 — Does `SELECT` Wait for a Row Lock?

## Goal

Understand how PostgreSQL handles concurrent reads while another transaction holds a row-level lock.

This experiment demonstrates one of PostgreSQL's most important features:

* A normal `SELECT` does **not** wait for a row lock.
* Instead, it reads the last committed version of the row.

This behavior is made possible by PostgreSQL's **Multi-Version Concurrency Control (MVCC)**.

---

# Initial Database State

Reset the counter.

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

# Transaction A

Create:

```text
experiments/experiment-03-transaction-a.py
```

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg://username:password@localhost:5432/url_shortener"

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

db = Session()

print("=" * 60)
print("Transaction A")
print("=" * 60)

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
experiments/experiment-03-transaction-b.py
```

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg://username:password@localhost:5432/url_shortener"

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

db = Session()

print("=" * 60)
print("Transaction B")
print("=" * 60)

result = db.execute(
    text("""
        SELECT click_count
        FROM urls
        WHERE id = 1
    """)
)

print()

print("Click Count =", result.scalar())

input("Press ENTER to exit...")
```

---

# Execution Steps

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

It executes:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

Do **not** commit.

Leave the transaction waiting.

---

## Step 3

Start **Transaction B**.

It executes:

```sql
SELECT click_count
FROM urls
WHERE id = 1;
```

Observe carefully.

* Does the SELECT wait?
* Or does it return immediately?

---

## Step 4

Now commit Transaction A.

---

## Step 5

Run Transaction B again.

Observe the new result.

---

# Observe PostgreSQL

While Transaction A is waiting, execute:

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

Observe:

* Is Transaction B waiting?
* Is Transaction B blocked?
* Does PostgreSQL report any lock waits?

---

# Questions

## Q1

Did the normal `SELECT` wait for the row lock?

---

## Q2

What value did Transaction B read before Transaction A committed?

---

## Q3

What value did Transaction B read after Transaction A committed?

---

## Q4

Why doesn't a normal `SELECT` block even though another transaction has updated the row?

Do not worry if you don't know the answer yet.

We will explain it after observing the behavior.

---

# Objective

This experiment introduces PostgreSQL's MVCC model.

The goal is to observe that:

* Readers do not block writers.
* Writers do not block readers.
* Readers see the last committed version of the data.

This behavior is one of the major reasons PostgreSQL performs well under concurrent workloads.
