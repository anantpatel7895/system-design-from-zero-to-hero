# Experiment 04 — Observations

## Goal

Determine the exact moment PostgreSQL starts a transaction and understand the lifecycle of the transaction, connection, and backend process.

---

## Observation 1 — Before Running the Python Program

**PostgreSQL Connections**

```text
Connections: 10
```

There were no connections belonging to the experiment.

---

## Observation 2 — After `create_engine()`

```python
engine = create_engine(DATABASE_URL)
```

**PostgreSQL Connections**

```text
Connections: 10
```

### Observation

* No new PostgreSQL connection was created.
* No backend process was created.

### Conclusion

`create_engine()` only creates a SQLAlchemy **Engine** object.

It does not communicate with PostgreSQL.

---

## Observation 3 — After `SessionLocal()`

```python
db = SessionLocal()
```

**PostgreSQL Connections**

```text
Connections: 10
```

### Observation

* No new PostgreSQL connection was created.
* No transaction was started.
* No backend process was created.

### Conclusion

Creating a SQLAlchemy Session does not immediately acquire a database connection.

---

## Observation 4 — After Executing the First SQL Statement

```python
db.execute(text("SELECT 1"))
```

### SQLAlchemy Log in the terminal of python program

```text
select pg_catalog.version()

select current_schema()

show standard_conforming_strings

BEGIN (implicit)

SELECT 1
```

### PostgreSQL

```text
Connections: 11

State:
idle in transaction

Transaction Start Time (xact_start):
2026-07-06 18:06:05.702
```

### Observation

Immediately after executing the first SQL statement:

* A new PostgreSQL connection appeared.
* A new backend process was created.
* SQLAlchemy printed `BEGIN (implicit)`.
* PostgreSQL reported the connection state as `idle in transaction`.
* `xact_start` was populated.

### Conclusion

The first SQL statement causes SQLAlchemy to:

1. Acquire a database connection.
2. Create (or obtain) a PostgreSQL backend process.
3. Start a database transaction.
4. Execute the SQL statement.

This experiment proves that even a simple `SELECT` executes inside a transaction.

---

## Observation 5 — After `db.commit()`

```python
db.commit()
```

### SQLAlchemy Log

```text
COMMIT
```

### PostgreSQL

```text
State:
idle

xact_start:
NULL
```

### Observation

* The transaction ended.
* The backend process remained alive.
* The database connection remained active.
* The connection state changed from `idle in transaction` to `idle`.

### Conclusion

`COMMIT` ends the current transaction but does **not** close the database connection.

---

## Observation 6 — After `db.close()`

```python
db.close()
```

### PostgreSQL

```text
Connections: 10
```

### Observation

The experiment's database connection disappeared from `pg_stat_activity`.

### Conclusion

In this standalone experiment, the SQLAlchemy Session released the database connection. Since the program terminated and no component retained the connection, it was closed and the backend process exited.

In a long-running application (such as FastAPI), `db.close()` typically returns the connection to SQLAlchemy's connection pool for reuse instead of terminating the underlying TCP connection immediately.

---

# Transaction Lifecycle

```text
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
First SQL Statement
        │
        ▼
Acquire Database Connection
        │
        ▼
PostgreSQL Backend Process Created
        │
        ▼
BEGIN (implicit)
        │
        ▼
Transaction Starts
        │
        ▼
Execute SQL
        │
        ▼
idle in transaction
        │
        ▼
COMMIT
        │
        ▼
idle
        │
        ▼
db.close()
        │
        ▼
Connection Released
```

---

# Key Learnings

* `create_engine()` does not connect to PostgreSQL.
* `SessionLocal()` does not connect to PostgreSQL.
* The first SQL statement acquires a database connection.
* The first SQL statement starts an implicit transaction.
* A simple `SELECT` executes inside a transaction.
* `COMMIT` ends the transaction but does not terminate the backend process.
* The lifecycle of a **Session**, **Connection**, and **Transaction** are independent.
* A PostgreSQL connection can outlive multiple transactions.
* A transaction is created only when PostgreSQL begins executing SQL that requires one.
