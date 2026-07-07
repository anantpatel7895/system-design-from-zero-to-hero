# Experiment 01 — Does `create_engine()` Connect to PostgreSQL?

## Goal

Verify whether:

```python
engine = create_engine(...)
```

actually connects to PostgreSQL.

We are not going to assume anything—we are going to prove it.

---

## Folder Structure

```text
01-transaction-lifecycle/

├── experiments/
│   ├── experiment-01-lazy-engine.py
│   └── observations.md
```

---

## Step 1 — Create the Experiment

Create the file:

```text
experiment-01-lazy-engine.py
```

```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg://username:password@localhost:5432/url_shortener"

print("=" * 60)
print("STEP 1 : Creating Engine")
print("=" * 60)

engine = create_engine(DATABASE_URL)

print("Engine Created")

input("\nPress ENTER to exit...")
```

**Do not execute it yet.**

---

## Step 2 — Observe PostgreSQL

Open another terminal and connect to PostgreSQL.

Run:

```sql
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query
FROM pg_stat_activity
ORDER BY pid;
```

Before running the Python program, answer the following question:

> **How many connections belong to your application?**

Record your observation.

---

## Step 3 — Run the Python Program

Execute:

```bash
python experiment-01-lazy-engine.py
```

Expected output:

```text
============================================================
STEP 1 : Creating Engine
============================================================

Engine Created

Press ENTER to exit...
```

Do **not** press **Enter**.

Keep the program running.

---

## Step 4 — Inspect PostgreSQL Again

Return to the PostgreSQL terminal and execute:

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

## Question

Do you see a new connection created by your Python application?

* Yes
* No

Do not guess. Record only what you actually observe.

---

## Why Use `input()`?

Normally the Python program exits immediately after creating the Engine.

Using:

```python
input("\nPress ENTER to exit...")
```

keeps the process alive, giving us enough time to inspect PostgreSQL and verify whether a database connection has been established.

---

# Observations

Create:

```text
observations.md
```

Record your observations.

Example:

```markdown
# Experiment 01

## Observation

Before running Python:

Connections:
0

After create_engine():

Connections:
?

Conclusion:
?
```

Do not fill in the answers based on assumptions. Record only the behavior observed on your machine.

---

# Learning Process

Every experiment in the **Database Internals** module will follow the same workflow:

1. Make a hypothesis.
2. Run the experiment.
3. Observe PostgreSQL.
4. Explain the observed behavior.
5. Document the findings in `question-answer.md`.

The objective is to understand PostgreSQL through observation and experimentation rather than memorization.
