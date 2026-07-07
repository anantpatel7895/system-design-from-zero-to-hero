# Experiment 07 — Deadlock Prevention Using Consistent Lock Ordering

## Goal

Understand how acquiring locks in a consistent order prevents deadlocks.

In the previous experiment:

* Transaction A locked **Row 1** then requested **Row 2**.
* Transaction B locked **Row 2** then requested **Row 1**.

This created a circular wait and PostgreSQL detected a deadlock.

In this experiment, both transactions will lock the rows in the **same order**.

---

# Initial Database State

Reset both rows.

```sql
UPDATE urls
SET click_count = 0
WHERE id IN (1, 2);
```

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
id    click_count
-----------------
1     0
2     0
```

---

# Transaction A

Create:

```text
experiments/experiment-07-transaction-a.py
```

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener"

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

db = Session()

print("Transaction A")

db.execute(text("""
    UPDATE urls
    SET click_count = click_count + 1
    WHERE id = 1
"""))

print("Locked Row 1")

input("Press ENTER to lock Row 2...")

db.execute(text("""
    UPDATE urls
    SET click_count = click_count + 1
    WHERE id = 2
"""))

print("Locked Row 2")

input("Press ENTER to COMMIT...")

db.commit()

print("Committed")
```

---

# Transaction B

Create:

```text
experiments/experiment-07-transaction-b.py
```

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener"

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

db = Session()

print("Transaction B")

db.execute(text("""
    UPDATE urls
    SET click_count = click_count + 1
    WHERE id = 1
"""))

print("Locked Row 1")

input("Press ENTER to lock Row 2...")

db.execute(text("""
    UPDATE urls
    SET click_count = click_count + 1
    WHERE id = 2
"""))

print("Locked Row 2")

input("Press ENTER to COMMIT...")

db.commit()

print("Committed")
```

---

# Execution Steps

## Step 1

Start Transaction A.

It locks:

```text
Row 1
```

Do not commit.

---

## Step 2

Start Transaction B.

Observe what happens.

Does it immediately lock Row 1?

Or does it wait?

---

## Step 3

Commit Transaction A.

Observe Transaction B.

---

## Questions

### Q1

Did Transaction B wait?

---

### Q2

Did PostgreSQL report a deadlock?

---

### Q3

Why didn't a deadlock occur this time?

---

### Q4

What is the difference between:

```text
Experiment 06

A : Row1 → Row2

B : Row2 → Row1
```

and

```text
Experiment 07

A : Row1 → Row2

B : Row1 → Row2
```

---

# Expected Timeline

```text
Time
────────────────────────────────────────────────────────────>

Transaction A

Lock Row 1

↓

Lock Row 2

↓

COMMIT

────────────────────────────────────────────────────────────

Transaction B

Wait for Row 1

↓

Lock Row 1

↓

Lock Row 2

↓

COMMIT
```

Notice that Transaction B waits **only once**.

There is never a circular dependency.

---

# Key Concept

A deadlock requires a **cycle**.

```text
Transaction A
     │
Needs Row 2
     ▲
     │
Transaction B

Transaction B
     │
Needs Row 1
     ▲
     │
Transaction A
```

When every transaction acquires locks in the same order:

```text
Row 1

↓

Row 2
```

a cycle cannot form.

One transaction may wait, but eventually it proceeds after the first transaction commits.

---

# Production Rule

One of the most important concurrency rules in database applications is:

> **Always acquire locks in a consistent order.**

Examples include:

* Lock rows by ascending primary key.
* Lock accounts by account ID.
* Lock inventory items by product ID.
* Lock resources alphabetically.

Following a consistent ordering dramatically reduces the likelihood of deadlocks in production systems.
