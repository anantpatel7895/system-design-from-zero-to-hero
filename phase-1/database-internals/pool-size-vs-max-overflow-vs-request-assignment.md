# SQLAlchemy Connection Pool Internals

## Goal

Understand how SQLAlchemy manages database connections using a connection pool and what happens when concurrent requests exceed the pool capacity.

---

# Connection Pool Configuration

Example:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
)
```

Meaning:

```text
pool_size = 5

↓

Maximum number of permanent pooled connections.
```

```text
max_overflow = 10

↓

Maximum number of temporary connections that can be created
when all pooled connections are busy.
```

Therefore:

```text
Maximum Simultaneous Connections

=

pool_size + max_overflow

=

5 + 10

=

15
```

---

# Important Concept

The connection pool is **lazy**.

Creating the engine does **not** create any database connections.

```python
engine = create_engine(...)
```

Current state:

```text
Connection Pool Exists

Permanent Connections : 0

Overflow Connections : 0
```

No TCP connection has been established with PostgreSQL.

---

# First Database Request

Application:

```python
db = SessionLocal()

db.execute(...)
```

SQLAlchemy performs:

```text
Acquire Connection

↓

Create TCP Connection

↓

Authenticate

↓

Backend Process Created

↓

Execute SQL
```

Pool status:

```text
Permanent Connections : 1

Overflow Connections : 0
```

---

# Second Request

Another request executes SQL.

Pool status:

```text
Permanent Connections : 2

Overflow Connections : 0
```

---

# Third Request

```text
Permanent Connections : 3

Overflow Connections : 0
```

The pool grows only when additional concurrent requests require more connections.

---

# Pool Growth

Eventually:

```text
Permanent Connections : 5

Overflow Connections : 0
```

The permanent pool is now full.

---

# Sixth Concurrent Request

All five pooled connections are currently busy.

SQLAlchemy creates a temporary overflow connection.

```text
Permanent Connections : 5

Overflow Connections : 1
```

---

# Additional Concurrent Requests

As more requests arrive:

```text
Permanent Connections : 5

Overflow Connections : 2
```

```text
Permanent Connections : 5

Overflow Connections : 3
```

...

Eventually:

```text
Permanent Connections : 5

Overflow Connections : 10
```

Total active connections:

```text
5 + 10 = 15
```

---

# Sixteenth Concurrent Request

Now every available connection is busy.

The application cannot create another connection.

The request waits.

```text
Request 16

↓

Waiting for a Connection
```

Internally:

```text
Thread

↓

Waiting

↓

Connection Returned to Pool

↓

Acquire Connection

↓

Execute SQL
```

No new PostgreSQL backend process is created.

---

# When a Request Finishes

Suppose one request completes:

```python
db.close()
```

SQLAlchemy performs:

```text
Return Connection

↓

Connection Becomes Available

↓

Wake One Waiting Request

↓

Waiting Request Acquires Connection
```

The waiting request continues execution.

---

# What Happens to Overflow Connections?

Overflow connections are temporary.

Example:

```text
Permanent Connections : 5

Overflow Connections : 4
```

Traffic decreases.

Overflow connections are closed.

Eventually:

```text
Permanent Connections : 5

Overflow Connections : 0
```

Only the permanent pooled connections remain.

---

# Complete Lifecycle

```text
Application Starts

↓

Engine Created

↓

Pool Created

↓

Connections = 0

────────────────────────────

First SQL

↓

1 Connection Created

────────────────────────────

More Concurrent Requests

↓

2 Connections

↓

3 Connections

↓

4 Connections

↓

5 Connections

────────────────────────────

Pool Full

↓

Overflow Connections Created

↓

6

↓

7

↓

...

↓

15 Connections

────────────────────────────

16th Concurrent Request

↓

Wait for Free Connection

────────────────────────────

One Request Finishes

↓

Connection Returned

↓

Waiting Request Continues

────────────────────────────

Traffic Drops

↓

Overflow Connections Closed

↓

Permanent Pool Returns to 5 Connections
```

---

# Important Distinction

A **Session** is **not** a database connection.

```text
Session

↓

Requests a Connection

↓

Uses Connection

↓

Returns Connection

↓

Session Continues
```

The connection pool owns the connections.

Sessions borrow connections only while they need them.

---

# Key Takeaways

* `create_engine()` creates a connection pool, **not** database connections.
* Database connections are created **lazily** when the first SQL statement is executed.
* The pool grows only when concurrent demand increases.
* `pool_size` defines the number of permanent pooled connections.
* `max_overflow` defines how many temporary connections may be created beyond the permanent pool.
* The maximum number of simultaneous database connections is `pool_size + max_overflow`.
* When this limit is reached, additional requests wait until a connection is returned.
* Calling `db.close()` does **not** close the database connection. It returns the connection to the pool so another request can reuse it.
* Overflow connections are temporary and are closed when demand decreases.
* Connection pooling avoids the cost of repeatedly creating and destroying TCP connections, making it essential for high-performance production systems.

---

# Next Experiment

We will verify every statement in this document by observing:

* `pg_stat_activity`
* `engine.pool.status()`
* Concurrent threads
* Waiting requests
* Overflow connections

Rather than trusting the documentation, we will watch the connection pool grow, block, reuse connections, and shrink in real time.
