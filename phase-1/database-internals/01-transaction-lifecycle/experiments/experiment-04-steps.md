# Experiment 04 — When Does a Transaction Actually Start?

## Goal

Determine the exact moment PostgreSQL starts a transaction.

We will observe PostgreSQL directly instead of relying on documentation.

---

## Experiment

Create:

```text id="sud0o6"
experiments/experiment-04-transaction-start.py
```

```python id="sh8g3z"
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg://username:password@localhost:5432/url_shortener"

engine = create_engine(
    DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(bind=engine)

print("=" * 60)
print("STEP 1 : Create Session")
print("=" * 60)

db = SessionLocal()

input("\nSTEP 1 Complete. Press ENTER...")

print("=" * 60)
print("STEP 2 : Execute SELECT")
print("=" * 60)

db.execute(text("SELECT 1"))

input("\nSTEP 2 Complete. Press ENTER...")

print("=" * 60)
print("STEP 3 : Commit")
print("=" * 60)

db.commit()

input("\nSTEP 3 Complete. Press ENTER...")

print("=" * 60)
print("STEP 4 : Close Session")
print("=" * 60)

db.close()

input("\nSTEP 4 Complete. Press ENTER to exit...")
```

---

## PostgreSQL Terminal

Run this query after every step.

```sql id="v8eljt"
SELECT
    pid,
    state,
    xact_start,
    query_start,
    backend_start,
    query
FROM pg_stat_activity
WHERE datname = 'url_shortener'
ORDER BY pid;
```

---

# Observation 1

After:

```python id="te9smq"
db = SessionLocal()
```

Observe:

```text id="it7uad"
state

xact_start

query
```

---

# Observation 2

After:

```python id="s4hjxk"
db.execute(text("SELECT 1"))
```

Observe again:

```text id="wrbhdz"
state

xact_start

query
```

Also observe the SQLAlchemy log.

You should see something similar to:

```text id="j1vy2v"
BEGIN (implicit)

SELECT 1
```

Do not assume what it means.

Simply record it.

---

# Observation 3

After:

```python id="55x1n5"
db.commit()
```

Observe:

```text id="ec02v4"
state

xact_start

query
```

Did the transaction disappear?

Did `xact_start` become NULL?

Record everything.

---

# Questions

## Q11

Exactly when did PostgreSQL start the transaction?

* During `SessionLocal()`?
* During `db.execute()`?
* During `db.commit()`?

Support your answer using your observations.

---

## Q12

SQLAlchemy printed:

```text id="25o0wm"
BEGIN (implicit)
```

What do you think the word **implicit** means?

Do not search online.

Write your own hypothesis based on the experiment.

---

## Expected Deliverables

After completing the experiment, record:

* SQLAlchemy logs
* `pg_stat_activity` output
* Your observations
* Your conclusion
* Your hypothesis about `BEGIN (implicit)`

Do not worry if your hypothesis is wrong.

We will refine it after observing PostgreSQL's behavior.
