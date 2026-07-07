# Experiment 07 — Can Another Transaction See My Uncommitted Changes?

## Goal

Understand transaction isolation by observing whether one transaction can read another transaction's uncommitted changes.

This is our first experiment involving **two concurrent transactions**.

---

# Scenario

We will run two Python programs simultaneously.

```text
Transaction A

↓

BEGIN

↓

UPDATE click_count

↓

WAIT

────────────────────────────

Transaction B

↓

SELECT click_count

↓

Observe Result
```

---

# Initial Database State

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

# Terminal A

Create:

```text
experiments/experiment-07-transaction-a.py
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

print("STEP 1 : UPDATE")

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

# Terminal B

Create:

```text
experiments/experiment-07-transaction-b.py
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

input("Run AFTER Transaction A executes UPDATE.\nPress ENTER...")

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

# Experiment Steps

## Step 1

Run:

```text
Transaction A
```

Execute the UPDATE.

Do **not** commit.

Wait.

---

## Step 2

Run:

```text
Transaction B
```

Execute the SELECT.

Record the result.

---

## Step 3

Now return to:

```text
Transaction A
```

Commit.

---

## Step 4

Run Transaction B again.

Observe the new value.

---

# Questions

## Q14

Before Transaction A commits:

What value does Transaction B read?

---

## Q15

After Transaction A commits:

What value does Transaction B read?

---

# Observe PostgreSQL

During the experiment, execute:

```sql
SELECT
    pid,
    state,
   xact_start,
   query
FROM pg_stat_activity
WHERE datname='url_shortener';
```

Observe:

* Number of backend processes.
* Number of active transactions.
* Transaction states.

---

# Objective

By the end of this experiment we should answer:

* Can one transaction see another transaction's uncommitted changes?
* What changes after `COMMIT`?
* How does PostgreSQL isolate concurrent transactions?

Do not rely on theory.

Record only what PostgreSQL demonstrates.
