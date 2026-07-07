# Experiment 06 — Observations

## Goal

Understand the difference between a **SQLAlchemy transaction** and a **PostgreSQL transaction**, and determine when PostgreSQL actually starts a transaction.

---

# Observation 1 — After `db.begin()`

Executed:

```python
db.begin()
```

### PostgreSQL Observation

```text
No new backend process

No new database connection

No active transaction

No xact_start
```

### SQLAlchemy Log

No SQL statements were executed.

No `BEGIN (implicit)` was printed.

### Conclusion

Calling:

```python
db.begin()
```

does **not** immediately communicate with PostgreSQL.

At this point:

* No TCP connection is established.
* No PostgreSQL backend process exists.
* No PostgreSQL transaction exists.

Only the SQLAlchemy Session is informed that subsequent database operations should belong to a transaction.

---

# Observation 2 — After Executing the First SQL Statement

Executed:

```python
db.execute(text("SELECT 1"))
```

### SQLAlchemy Log

```text
select pg_catalog.version()

select current_schema()

show standard_conforming_strings

BEGIN (implicit)

SELECT 1
```

### PostgreSQL Observation

```text
Backend Process Created

Database Connection Created

State:
idle in transaction

xact_start:
2026-07-07 11:06:13.754

Query:
SELECT 1
```

### Conclusion

The first SQL statement triggered:

* Acquisition of a database connection.
* Creation of a PostgreSQL backend process.
* Start of a PostgreSQL transaction.
* Execution of the SQL statement.

Although `db.begin()` had already been called, PostgreSQL was unaware of the transaction until SQLAlchemy executed the first SQL statement.

---

# Observation 3 — After `db.commit()`

Executed:

```python
db.commit()
```

### SQLAlchemy Log

```text
COMMIT
```

### PostgreSQL Observation

```text
State:
idle

xact_start:
NULL

Query:
COMMIT
```

### Conclusion

The transaction completed successfully.

However:

* The backend process remained alive.
* The database connection remained open.
* Only the transaction ended.

This demonstrates that a database connection can execute multiple transactions during its lifetime.

---

# Observation 4 — After `db.close()`

Executed:

```python
db.close()
```

### PostgreSQL Observation

```text
Backend Process:
Still Alive

State:
idle
```

### Conclusion

Calling:

```python
db.close()
```

did **not** terminate the PostgreSQL backend process.

Instead, SQLAlchemy returned the database connection to the connection pool.

The connection remained available for future reuse.

---

# Observation 5 — After the Python Program Exited

After terminating the Python process:

```text
Backend Process:
No Longer Present
```

### Conclusion

Once the Python application exited:

* The SQLAlchemy Engine was destroyed.
* The connection pool was destroyed.
* The database connection was closed.
* PostgreSQL terminated the associated backend process.

---

# Execution Timeline

```text
Python Application
        │
        ▼
Session Created
        │
        ▼
db.begin()
        │
        ▼
SQLAlchemy Transaction Starts
        │
        ▼
(No PostgreSQL Connection)
        │
        ▼
db.execute("SELECT 1")
        │
        ▼
Acquire Database Connection
        │
        ▼
Create PostgreSQL Backend Process
        │
        ▼
BEGIN (implicit)
        │
        ▼
PostgreSQL Transaction Starts
        │
        ▼
Execute SQL
        │
        ▼
COMMIT
        │
        ▼
Transaction Ends
        │
        ▼
Connection Remains Idle
        │
        ▼
db.close()
        │
        ▼
Connection Returned to Pool
        │
        ▼
Python Process Exits
        │
        ▼
Connection Closed
        │
        ▼
Backend Process Terminated
```

---

# Key Learnings

* `db.begin()` starts transaction management within SQLAlchemy but does not immediately communicate with PostgreSQL.
* PostgreSQL does not create a transaction until the first SQL statement is executed.
* The first SQL statement causes SQLAlchemy to:

  * Acquire a database connection.
  * Create a PostgreSQL backend process.
  * Start a PostgreSQL transaction.
* `COMMIT` ends the transaction but does not close the database connection.
* `db.close()` returns the connection to the connection pool rather than terminating it.
* The PostgreSQL backend process remains alive until the underlying database connection is closed.
* The backend process finally terminates when the Python application exits and the connection pool is destroyed.

---

# Important Distinction

This experiment demonstrates that there are two different layers of transaction management:

```text
                Python Application

           SQLAlchemy Transaction
                    │
                    ▼
          PostgreSQL Transaction
```

A SQLAlchemy transaction can begin before PostgreSQL is even aware of it.

PostgreSQL starts the actual database transaction only when SQLAlchemy sends the first SQL statement over a database connection.
