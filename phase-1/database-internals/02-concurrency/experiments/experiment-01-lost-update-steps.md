# Experiment 01 — Lost Update

## Goal

Reproduce the **Lost Update** problem.

This experiment demonstrates how two concurrent transactions can overwrite each other's work, resulting in incorrect data.

We will intentionally create the bug before learning how to fix it.

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

Two users access the same row simultaneously.

```text
            Transaction A                Transaction B

                │                            │
                ▼                            ▼
        Read click_count = 0        Read click_count = 0
                │                            │
                ▼                            ▼
        Increment to 1             Increment to 1
                │                            │
                ▼                            ▼
          UPDATE 1                   UPDATE 1
                │                            │
                ▼                            ▼
             COMMIT                       COMMIT
```

Question:

What should the final value be?

---

# Expected Result

If two users each increment the counter once:

```text
0

↓

+1

↓

+1

↓

Final Value = 2
```

---

# Terminal A

Create:

```text
experiments/experiment-01-transaction-a.py
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

result = db.execute(
    text("""
        SELECT click_count
        FROM urls
        WHERE id = 1
    """)
)

count = result.scalar()

print("Current Value:", count)

input("Press ENTER to UPDATE...")

new_value = count + 1

db.execute(
    text("""
        UPDATE urls
        SET click_count = :value
        WHERE id = 1
    """),
    {"value": new_value},
)

print("Updated to:", new_value)

input("Press ENTER to COMMIT...")

db.commit()

print("Committed")

input("Press ENTER to exit...")
```

---

# Terminal B

Create:

```text
experiments/experiment-01-transaction-b.py
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

count = result.scalar()

print("Current Value:", count)

input("Press ENTER to UPDATE...")

new_value = count + 1

db.execute(
    text("""
        UPDATE urls
        SET click_count = :value
        WHERE id = 1
    """),
    {"value": new_value},
)

print("Updated to:", new_value)

input("Press ENTER to COMMIT...")

db.commit()

print("Committed")

input("Press ENTER to exit...")
```

---

# Execution Order

Run the experiment carefully.

### Step 1

Start **Transaction A**.

It should execute:

```text
SELECT click_count
```

Pause before the UPDATE.

---

### Step 2

Start **Transaction B**.

It should also execute:

```text
SELECT click_count
```

Pause before the UPDATE.

Both transactions should have read:

```text
click_count = 0
```

---

### Step 3

Resume Transaction A.

Execute:

```text
UPDATE

↓

COMMIT
```

---

### Step 4

Resume Transaction B.

Execute:

```text
UPDATE

↓

COMMIT
```

---

### Step 5

Verify:

```sql
SELECT click_count
FROM urls
WHERE id = 1;
```

---

# Questions

## Q1

What was the final value?

---

## Q2

What value did Transaction A read?

---

## Q3

What value did Transaction B read?

---

## Q4

Why wasn't the final value equal to **2**?

Do not search online.

Explain the behavior using your own observations.

---

# Objective

This experiment intentionally demonstrates an incorrect result.

Do **not** try to fix it.

The purpose is to understand:

* How concurrent transactions interact.
* Why read-modify-write is dangerous.
* Why databases provide locking and atomic operations.

The solution will be explored in the next experiments.
