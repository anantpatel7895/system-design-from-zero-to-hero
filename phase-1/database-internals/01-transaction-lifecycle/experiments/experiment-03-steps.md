# Experiment 03 — Which Line Acquires the Database Connection?

## Goal

Determine the exact line of Python code that causes SQLAlchemy to:

* Borrow a database connection from the connection pool.
* Establish a TCP connection (if one does not already exist).
* Create a PostgreSQL backend process.

This experiment will identify the precise moment SQLAlchemy transitions from in-memory objects to communicating with PostgreSQL.

---

# Hypothesis

Based on the previous experiments:

* `create_engine()` does **not** connect.
* `SessionLocal()` does **not** connect.

Therefore, the connection should be acquired only when the first SQL statement is executed.

---

# Experiment

Create:

```text
experiments/experiment-03-first-sql.py
```

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg://username:password@localhost:5432/url_shortener"

print("=" * 60)
print("STEP 1 : Creating Engine")
print("=" * 60)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

input("\nSTEP 1 Complete. Press ENTER...")

print("=" * 60)
print("STEP 2 : Creating Session")
print("=" * 60)

db = SessionLocal()

input("\nSTEP 2 Complete. Press ENTER...")

print("=" * 60)
print("STEP 3 : Executing First SQL")
print("=" * 60)

db.execute(text("SELECT 1"))

input("\nSTEP 3 Complete. Press ENTER...")

print("=" * 60)
print("STEP 4 : Closing Session")
print("=" * 60)

db.close()

input("\nSTEP 4 Complete. Press ENTER to exit...")
```

---

# PostgreSQL Terminal

Keep this query ready:

```sql
SELECT
    pid,
    usename,
    application_name,
    state,
    backend_start,
    xact_start,
    query_start,
    state_change,
    query
FROM pg_stat_activity
ORDER BY pid;
```

Run it after every step.

---

# Observation 1

Before running Python

```text
Connections:
__________
10
```

---

# Observation 2

After:

```python
engine = create_engine(...)
```

```text
Connections:
__________
10
```

---

# Observation 3

After:

```python
db = SessionLocal()
```

```text
Connections:
__________
10
```

---

# Observation 4

After:

```python
db.execute(text("SELECT 1"))
```

```text
Connections:
__________
11
```

Also observe:

* Did a new backend process appear?
* What is the value of `state`?
* What is shown in the `query` column?

---

# Observation 5

After:

```python
db.close()
```

Observe again:

* Did the connection disappear?
* Did the backend process terminate?
* Did the connection become `idle`?
* Is it still visible in `pg_stat_activity`?

Record everything you observe.

---

# Questions to Answer

After completing the experiment, answer the following:

### Q9

Which exact line acquired the database connection?

```python
engine = create_engine(...)

SessionLocal()

db.execute(text("SELECT 1"))

db.close()
```

---

### Q10

After calling:

```python
db.close()
```

Did the PostgreSQL backend process:

* Terminate?
* Remain alive?
* Become idle?
* Disappear from `pg_stat_activity`?

---

# Objective

By the end of this experiment, we should know:

* The exact line that acquires a database connection.
* The lifecycle of a PostgreSQL backend process.
* What happens when a SQLAlchemy Session is closed.
* Whether `db.close()` closes the TCP connection or simply returns it to the connection pool.

Do not rely on documentation.

Let PostgreSQL answer these questions through observation.
