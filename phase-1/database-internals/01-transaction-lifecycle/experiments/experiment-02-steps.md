# Experiment 02 — Does `SessionLocal()` Connect to PostgreSQL?

## Goal

Verify whether creating a SQLAlchemy Session immediately acquires a database connection from the connection pool.

We want to answer the following question:

> Does `SessionLocal()` immediately establish a connection to PostgreSQL?

---

## Experiment

Create:

```text
experiments/experiment-02-session.py
```

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg://username:password@localhost:5432/url_shortener"

print("=" * 60)
print("STEP 1 : Creating Engine")
print("=" * 60)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

print("Engine Created")

input("\nPress ENTER to create Session...")

print("=" * 60)
print("STEP 2 : Creating SQLAlchemy Session")
print("=" * 60)

db = SessionLocal()

print("Session Created")

input("\nPress ENTER to exit...")
```

---

## PostgreSQL Terminal

Before running the experiment, execute:

```sql
SELECT
    pid,
    usename,
    application_name,
    state,
    query
FROM pg_stat_activity
ORDER BY pid;
```

---

## Observation 1

Before running the Python program:

```text
Connections:
_________
```

---

## Observation 2

After:

```python
engine = create_engine(...)
```

```text
Connections:
_________
```

---

## Observation 3

After:

```python
db = SessionLocal()
```

```text
Connections:
_________
```

---

## Important

Do **not** execute any SQL.

Do **not** call:

```python
db.execute(...)
```

or

```python
db.query(...)
```

The objective is to isolate the behavior of `SessionLocal()` only.

---

## Hypothesis

Before running the experiment, answer:

**Q8**

After executing:

```python
db = SessionLocal()
```

what do you expect?

* [ ] A new PostgreSQL connection is created.
* [ ] No PostgreSQL connection is created.

Write down your prediction before observing the result.

---

## Observation

```markdown
# Experiment 02

## Before Running Python

Connections:
?

## After create_engine()

Connections:
?

## After SessionLocal()

Connections:
?

## Conclusion

?
```

---

## Objective

By the end of this experiment, we should know whether:

* `SessionLocal()` acquires a database connection immediately.
* SQLAlchemy remains lazy after creating a Session.
* A PostgreSQL backend process is created during Session creation.
