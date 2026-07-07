# Experiment 05 — What Happens If We Don't Call `commit()`?

## Goal

Determine what happens when a transaction is left uncommitted and the SQLAlchemy Session is closed.

We want to answer the following questions:

* Does `db.close()` automatically call `COMMIT`?
* Does `db.close()` automatically call `ROLLBACK`?
* What happens to uncommitted changes?
* What does PostgreSQL report?

---

## Experiment

Create:

```text
experiments/experiment-05-no-commit.py
```

```python
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
print("STEP 1 : Read Current Value")
print("=" * 60)

result = db.execute(
    text("""
        SELECT click_count
        FROM urls
        WHERE id = 1
    """)
)

print(result.scalar())

input("\nPress ENTER to UPDATE...")

print("=" * 60)
print("STEP 2 : UPDATE")
print("=" * 60)

db.execute(
    text("""
        UPDATE urls
        SET click_count = click_count + 1
        WHERE id = 1
    """)
)

input("\nPress ENTER to CLOSE SESSION...")

print("=" * 60)
print("STEP 3 : CLOSE SESSION")
print("=" * 60)

db.close()

print("Session Closed")

input("\nPress ENTER to exit...")
```

---

## Before Running

Check the current value.

```sql
SELECT
    id,
    click_count
FROM urls
WHERE id = 1;
```

Write it down.

---

## During the Experiment

Observe SQLAlchemy logs.

Questions:

Did SQLAlchemy print:

```text
BEGIN (implicit)
```

Did SQLAlchemy print:

```text
COMMIT
```

Did SQLAlchemy print:

```text
ROLLBACK
```

---

## After Closing the Session

Run again:

```sql
SELECT
    id,
    click_count
FROM urls
WHERE id = 1;
```

Has the value changed?

---

## Also Observe

Run:

```sql
SELECT
    pid,
    state,
    xact_start,
    query
FROM pg_stat_activity
WHERE datname = 'url_shortener';
```

Observe the backend process before and after `db.close()`.

---

# Questions

## Q13

When `db.close()` is called without `commit()`:

* Does SQLAlchemy automatically commit the transaction?
* Does SQLAlchemy automatically roll back the transaction?
* Does PostgreSQL discard the update?

Support your answer with observations.

---

## Hypothesis

Before running the experiment, write your prediction.

Do **not** search online.

Make a prediction based on everything we have learned so far.
