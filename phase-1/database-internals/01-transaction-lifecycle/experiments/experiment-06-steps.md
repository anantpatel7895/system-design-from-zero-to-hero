# Experiment 06 — Explicit `BEGIN` vs Implicit `BEGIN`

## Goal

Understand the difference between:

* Implicit transactions managed by SQLAlchemy.
* Explicit transactions started by the application.

By the end of this experiment, we should know:

* What `BEGIN (implicit)` means.
* What happens when we explicitly call `db.begin()`.
* Whether PostgreSQL behaves differently.
* Whether SQLAlchemy emits another `BEGIN`.

---

# Hypothesis

In previous experiments, SQLAlchemy automatically printed:

```text id="pcn7ya"
BEGIN (implicit)
```

before executing the first SQL statement.

In this experiment, we will explicitly begin a transaction ourselves.

---

# Experiment

Create:

```text id="g4t8tx"
experiments/experiment-06-explicit-begin.py
```

```python id="ymgimc"
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg://username:password@localhost:5432/url_shortener"

engine = create_engine(
    DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()

print("=" * 60)
print("STEP 1 : Explicit BEGIN")
print("=" * 60)

db.begin()

input("\nSTEP 1 Complete. Press ENTER...")

print("=" * 60)
print("STEP 2 : Execute SELECT")
print("=" * 60)

db.execute(text("SELECT 1"))

input("\nSTEP 2 Complete. Press ENTER...")

print("=" * 60)
print("STEP 3 : COMMIT")
print("=" * 60)

db.commit()

input("\nSTEP 3 Complete. Press ENTER...")

print("=" * 60)
print("STEP 4 : CLOSE SESSION")
print("=" * 60)

db.close()

input("\nSTEP 4 Complete. Press ENTER to exit...")
```

---

# PostgreSQL Observation

After each step execute:

```sql id="crkgcr"
SELECT
    pid,
    state,
    xact_start,
    query
FROM pg_stat_activity
WHERE datname = 'url_shortener';
```

Observe:

* `state`
* `xact_start`
* `query`

---

# Questions

## Observation 1

After:

```python id="jsxbtx"
db.begin()
```

Questions:

* Did SQLAlchemy print anything?
* Was a database connection created?
* Did PostgreSQL show an active transaction?
* Was `xact_start` populated?

---

## Observation 2

After:

```python id="ztyt7d"
db.execute(text("SELECT 1"))
```

Questions:

* Did SQLAlchemy print:

```text id="0uk8mo"
BEGIN (implicit)
```

or not?

* Did PostgreSQL start the transaction now?
* Did `xact_start` change?

---

## Observation 3

After:

```python id="ic0f4k"
db.commit()
```

Observe:

* Transaction ended?
* Connection still alive?
* Backend process still alive?

---

# Objective

By the end of this experiment we should understand:

* The difference between **starting a transaction in SQLAlchemy** and **starting a transaction inside PostgreSQL**.
* Whether `db.begin()` immediately talks to PostgreSQL.
* Whether SQLAlchemy still waits until the first SQL statement before communicating with the database.

Record only what you observe. Do not assume any behavior.
