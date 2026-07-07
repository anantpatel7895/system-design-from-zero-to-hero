# Experiment 02 — Does `SessionLocal()` Connect to PostgreSQL?

## Goal

Verify whether creating a SQLAlchemy Session immediately establishes a connection to PostgreSQL.

---

## Observation

### Before Running Python

```text id="gcfm3m"
Connections: 10
```

---

### After `create_engine()`

```text id="qzchhl"
Connections: 10
```

No new PostgreSQL connection was created.

---

### After `SessionLocal()`

```text id="t0j4yw"
Connections: 10
```

No new PostgreSQL connection was created.

---

## Conclusion

Creating a SQLAlchemy Session using:

```python id="q7y89m"
db = SessionLocal()
```

does **not** immediately acquire a database connection.

As verified through `pg_stat_activity`, the number of PostgreSQL connections remained unchanged throughout the experiment.

This demonstrates that SQLAlchemy follows a **lazy connection acquisition** strategy.

Creating a Session only creates a **SQLAlchemy Session object** in Python memory. No database connection is borrowed from the connection pool, no TCP connection is established (if one is not already available), and no PostgreSQL backend process is created at this stage.

A database connection is acquired only when the Session executes its first SQL statement that requires communication with PostgreSQL.

---

## Execution Flow

```text id="vwteca"
Application Starts
        │
        ▼
create_engine()
        │
        ▼
Engine Created
        │
        ▼
SessionLocal()
        │
        ▼
SQLAlchemy Session Created
        │
        ▼
No Database Connection
        │
        ▼
No PostgreSQL Backend Process
        │
        ▼
First SQL Statement
        │
        ▼
Acquire Database Connection
        │
        ▼
Execute SQL
```

---

## How the Observation Was Verified

The PostgreSQL system view `pg_stat_activity` was queried before and after each step.

```sql id="xjbbzs"
SELECT
    pid,
    usename,
    application_name,
    state,
    query
FROM pg_stat_activity
ORDER BY pid;
```

The number of active PostgreSQL connections remained unchanged throughout the experiment, confirming that neither `create_engine()` nor `SessionLocal()` establishes a database connection.

---

## Key Takeaways

* `create_engine()` creates a SQLAlchemy Engine.
* `SessionLocal()` creates a SQLAlchemy Session.
* Neither operation immediately connects to PostgreSQL.
* SQLAlchemy acquires a database connection lazily, only when the first SQL statement is executed.
* The experiment was verified using PostgreSQL's `pg_stat_activity` system view rather than relying on assumptions.
