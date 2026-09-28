# Experiment 03 — Which Line Acquires the Database Connection?

## Goal

Determine the exact line of Python code that causes SQLAlchemy to:

* Borrow a database connection from the connection pool.
* Establish a TCP connection if one does not already exist.
* Cause PostgreSQL to create a backend process.

The experiment identifies the point where SQLAlchemy moves from in-memory objects to actual communication with PostgreSQL.

---

# Hypothesis

Based on the previous experiments:

* `create_engine()` does **not** establish a database connection.
* `SessionLocal()` does **not** establish a database connection.
* The database connection should be acquired when the first SQL statement is executed.

---

# Experiment

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

# PostgreSQL Observation Query

The following query was used to observe PostgreSQL:

```sql
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    backend_start,
    xact_start,
    query_start,
    state_change,
    query
FROM pg_stat_activity
ORDER BY pid;
```

---

# Observation 1 — Before Running Python

Before running the Python program, PostgreSQL showed the existing DBeaver connections.

Important existing connections included:

```text
99571  postgres  DBeaver Main <postgres>      idle
99572  postgres  DBeaver Metadata <postgres>  idle
99574  postgres  DBeaver Main <url_shortener> idle
99575  postgres  DBeaver Metadata <url_shortener> idle
```

There was no connection corresponding to the Python application.

### Observation

The Python application had not yet connected to PostgreSQL.

---

# Observation 2 — After `create_engine()`

Python executed:

```python
engine = create_engine(DATABASE_URL)
```

Then `pg_stat_activity` was checked.

### Result

There was **no new PostgreSQL backend process** corresponding to the Python application.

The existing connections remained unchanged.

### Observation

```text
create_engine()
       |
       X
       |
PostgreSQL connection
```

`create_engine()` created the SQLAlchemy `Engine` object and connection-pool configuration in memory.

It did **not** establish the PostgreSQL connection.

### Conclusion

`create_engine()` is **lazy with respect to database connections**.

---

# Observation 3 — After `SessionLocal()`

Python executed:

```python
db = SessionLocal()
```

Again, `pg_stat_activity` was checked.

### Result

There was still **no new PostgreSQL backend process** corresponding to the Python application.

The existing PostgreSQL connections remained unchanged.

### Observation

```text
SessionLocal()
       |
       X
       |
PostgreSQL connection
```

Creating the SQLAlchemy `Session` did not require a database connection.

The `Session` existed as a Python-side object.

### Conclusion

`SessionLocal()` does **not** acquire a database connection.

At this point:

```text
Python process
    |
    +-- Engine
    |
    +-- Session
    |
    X
    |
PostgreSQL
```

Everything is still effectively in memory from the application's perspective.

---

# Observation 4 — After `db.execute(text("SELECT 1"))`

Python executed:

```python
db.execute(text("SELECT 1"))
```

This was the critical observation.

A new PostgreSQL backend appeared:

```text
PID:              16160
User:             postgres
Client address:   ::1
State:            idle in transaction
Backend start:    2026-09-27 15:41:27.634 +0530
Transaction start:2026-09-27 15:41:27.659 +0530
Query start:      2026-09-27 15:41:27.659 +0530
Query:            SELECT 1
```

Before this operation, PID `16160` did not exist in the output.

After the operation, it appeared.

### Most important observation

```text
db.execute(text("SELECT 1"))
              |
              v
      SQLAlchemy needs DB
              |
              v
       Connection acquired
              |
              v
     PostgreSQL connection
              |
              v
   PostgreSQL backend PID 16160
```

Therefore, the experiment confirms that the first SQL operation caused SQLAlchemy to obtain a database connection.

---

# What Happened Internally?

The important lifecycle is approximately:

```text
create_engine()
      |
      |  No DB connection
      v
Engine object
      |
      v
SessionLocal()
      |
      |  No DB connection
      v
Session object
      |
      v
db.execute("SELECT 1")
      |
      |  Session needs a connection
      v
Connection obtained from pool
      |
      |  No existing connection available
      v
New PostgreSQL connection established
      |
      v
PostgreSQL backend process created
      |
      v
SELECT 1 executed
```

---

# Important Observation: `idle in transaction`

The PostgreSQL row showed:

```text
state = idle in transaction
```

and:

```text
query = SELECT 1
```

This is an important result.

The SQL statement had already completed, but the session was still inside a transaction.

Conceptually:

```text
BEGIN
   |
   v
SELECT 1
   |
   v
Query completed
   |
   v
Transaction still open
   |
   v
idle in transaction
```

The SQLAlchemy `Session` had not yet been closed.

---

# Observation 5 — After `db.close()`

Python executed:

```python
db.close()
```

The same PostgreSQL backend process remained:

```text
PID: 16160
```

However, its state changed:

```text
Before db.close():

state = idle in transaction
query = SELECT 1
```

After:

```text
state = idle
query = ROLLBACK
```

The observed row was:

```text
16160  postgres  ::1  idle
```

with:

```text
query = ROLLBACK
```

### Important observation

The PostgreSQL backend process **did not disappear** after:

```python
db.close()
```

Instead:

```text
idle in transaction
        |
        | db.close()
        v
      ROLLBACK
        |
        v
       idle
```

---

# Observation 6 — After Python Process Ended

After the Python process terminated, PID `16160` was no longer present in `pg_stat_activity`.

Therefore:

```text
Python process running
        |
        v
PostgreSQL backend PID 16160
        |
        v
Python process exits
        |
        v
Connection closes
        |
        v
Backend PID 16160 disappears
```

This is consistent with the connection being closed when the Python process terminates.

---

# Q9 — Which Exact Line Acquired the Database Connection?

The answer is:

```python
db.execute(text("SELECT 1"))
```

Not:

```python
engine = create_engine(...)
```

and not:

```python
db = SessionLocal()
```

The PostgreSQL evidence confirms this.

### Evidence

Before `create_engine()`:

```text
PID 16160 → absent
```

After `create_engine()`:

```text
PID 16160 → absent
```

After `SessionLocal()`:

```text
PID 16160 → absent
```

After:

```python
db.execute(text("SELECT 1"))
```

```text
PID 16160 → appeared
```

Therefore:

> **The first SQL operation caused the SQLAlchemy Session to acquire a database connection.**

---

# Q10 — What Happened After `db.close()`?

The PostgreSQL backend did **not** terminate.

Before:

```text
PID = 16160
state = idle in transaction
```

After:

```python
db.close()
```

the same PID remained:

```text
PID = 16160
state = idle
query = ROLLBACK
```

Therefore:

> `db.close()` closed the SQLAlchemy Session's transactional/connection usage, but the PostgreSQL backend process remained alive.

The connection remained available rather than immediately disappearing.

---

# Final Lifecycle Observed

The complete experiment can be summarized as:

```text
                 Python
                   |
                   |
        create_engine()
                   |
                   v
             Engine object
                   |
                   | No connection
                   |
             SessionLocal()
                   |
                   v
             Session object
                   |
                   | No connection
                   |
                   v
       db.execute("SELECT 1")
                   |
                   v
        Connection acquired
                   |
                   v
      PostgreSQL backend created
                   |
                   v
             SELECT 1
                   |
                   v
        idle in transaction
                   |
                   |
              db.close()
                   |
                   v
                ROLLBACK
                   |
                   v
                  idle
                   |
                   |
          Python process exits
                   |
                   v
       PostgreSQL connection closes
                   |
                   v
        Backend disappears
```

---

# Key Findings

| Python operation     |               PostgreSQL connection? | PostgreSQL backend observed? |
| -------------------- | -----------------------------------: | ---------------------------: |
| `create_engine()`    |                                   No |                           No |
| `SessionLocal()`     |                                   No |                           No |
| `db.execute()`       |                              **Yes** |          **Yes — PID 16160** |
| `db.close()`         | Connection no longer used by Session |             **PID remained** |
| Python process exits |                    Connection closes |          **PID disappeared** |

---

# Final Conclusion

This experiment experimentally demonstrated the lazy connection behavior of SQLAlchemy.

### 1. `create_engine()` does not connect

```python
engine = create_engine(DATABASE_URL)
```

creates the Engine and configures the connection pool.

No PostgreSQL backend was created.

### 2. Creating a Session does not connect

```python
db = SessionLocal()
```

creates a Python-side SQLAlchemy Session.

No PostgreSQL backend was created.

### 3. First SQL execution triggers connection acquisition

```python
db.execute(text("SELECT 1"))
```

caused:

```text
Session
   ↓
Connection acquisition
   ↓
PostgreSQL connection
   ↓
PostgreSQL backend PID 16160
   ↓
SELECT 1
```

This was the first point at which PostgreSQL observed the application connection.

### 4. `db.close()` does not necessarily terminate the PostgreSQL backend

The experiment showed:

```text
PID 16160
```

remained after:

```python
db.close()
```

and changed from:

```text
idle in transaction
```

to:

```text
idle
```

The transaction was rolled back/closed and the connection became idle.

### 5. The backend disappeared when the Python process ended

After the Python process terminated, PID `16160` disappeared from `pg_stat_activity`.

---

# Most Important Mental Model

Remember this distinction:

```text
Engine
  |
  | manages
  v
Connection Pool
  |
  | provides
  v
DB Connection
  |
  | communicates with
  v
PostgreSQL Backend Process
```

And:

```text
create_engine()
      ↓
Engine exists

SessionLocal()
      ↓
Session exists

First SQL
      ↓
Connection acquired
      ↓
PostgreSQL backend exists

db.close()
      ↓
Session releases connection
      ↓
Connection can remain in pool

Python process exits
      ↓
Connection closes
      ↓
PostgreSQL backend disappears
```

This distinction will become especially important when we move to **multiple Kubernetes pods + SQLAlchemy connection pools + PostgreSQL**, because every pod can maintain its own pool of PostgreSQL connections.
