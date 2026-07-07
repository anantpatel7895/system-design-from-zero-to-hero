## Q1. Does a transaction start when the client opens the TCP connection?

### My Answer

No.

Opening a TCP connection to PostgreSQL does **not** start a database transaction.

A TCP connection is simply a communication channel between the client and the PostgreSQL server.

After the connection is established, PostgreSQL creates a backend session for that client. This session may remain idle for a long time without any active transaction.

A transaction begins only when transaction processing starts (either explicitly with `BEGIN` or implicitly when the first SQL statement is executed, depending on the client and transaction mode).

Therefore, these are three distinct concepts:

```text
TCP Connection
        │
        ▼
Database Session
        │
        ▼
Transaction
```

A single database connection can execute many transactions during its lifetime.

Example:

```text
Connection Open
        │
        ▼
Transaction 1
COMMIT
        │
        ▼
Transaction 2
ROLLBACK
        │
        ▼
Transaction 3
COMMIT
        │
        ▼
Connection Closed
```

### Key Takeaway

A database connection is **not** the same as a transaction.

* **Connection** establishes communication.
* **Session** represents the client's interaction with PostgreSQL.
* **Transaction** is a unit of work executed within a session.

---

## Q2. At what exact moment does PostgreSQL create a transaction?

Suppose you execute:

```python
url = repository.get_by_short_code(db, "google")
```

SQLAlchemy sends:

```sql
SELECT *
FROM urls
WHERE short_code = 'google';
```

### Question

At what exact moment does PostgreSQL create the transaction?

1. Before parsing the SQL?
2. While parsing the SQL?
3. Just before executing the SQL?
4. After the `SELECT` finishes?

### Objective

Understand the exact point in the PostgreSQL execution lifecycle where a transaction begins. This forms the foundation for understanding:

* Implicit transactions
* Explicit transactions
* MVCC
* Row-level locking
* Isolation levels
* Concurrent transaction execution

---

## Q3. What does `db: Session = Depends(get_db)` actually create?

### Question

Every time a FastAPI endpoint executes:

```python
db: Session = Depends(get_db)
```

what exactly is created?

Does it create:

* A PostgreSQL transaction?
* A PostgreSQL session?
* A TCP connection?
* Something else?

---

### My Answer

`SessionLocal()` creates a **SQLAlchemy Session object**.

It does **not** create:

* a PostgreSQL transaction,
* a PostgreSQL backend session,
* or a TCP connection.

A SQLAlchemy Session is an **ORM Unit of Work** that manages the interaction between Python objects and the database.

Its responsibilities include:

* Tracking ORM objects.
* Maintaining the Identity Map.
* Tracking dirty (modified) objects.
* Tracking newly created objects.
* Tracking deleted objects.
* Managing transactions.
* Obtaining a database connection from the connection pool only when it is needed.

Initially, after creating the Session, there may be:

* No SQL executed.
* No active database transaction.
* No database connection acquired yet.

---

### SQLAlchemy Session

```text
             SQLAlchemy Session
          ┌──────────────────────┐
          │ Identity Map          │
          │ Dirty Objects         │
          │ New Objects           │
          │ Deleted Objects       │
          │ Transaction Manager   │
          └──────────────────────┘
```

---

### Request Lifecycle

When an HTTP request arrives:

```text
HTTP Request
      │
      ▼
get_db()
      │
      ▼
SessionLocal()
      │
      ▼
SQLAlchemy Session
```

At this point:

* No SQL has been executed.
* No transaction has started.
* A database connection may not even be acquired yet.

---

### First Database Operation

Suppose the application executes:

```python
repository.get_by_short_code(db, "google")
```

Only now does SQLAlchemy need to communicate with PostgreSQL.

The flow becomes:

```text
SQLAlchemy Session
        │
        ▼
Connection Pool
        │
        ▼
Borrow Database Connection
        │
        ▼
Send SQL to PostgreSQL
```

At this point PostgreSQL begins processing the SQL statement and transaction management starts according to the configured transaction mode.

---

### One Request

```text
HTTP Request
      │
      ▼
SessionLocal()
      │
      ▼
SELECT
      │
      ▼
UPDATE
      │
      ▼
COMMIT
      │
      ▼
db.close()
```

Each HTTP request typically receives its own SQLAlchemy Session.

---

### What Happens During `db.close()`?

Calling:

```python
db.close()
```

does **not** usually close the TCP connection to PostgreSQL.

Instead, SQLAlchemy returns the database connection to the **connection pool**, allowing future requests to reuse it.

Example:

```text
Request A
    │
    ▼
Connection #5
    │
    ▼
db.close()
    │
    ▼
Returned to Connection Pool

────────────────────────────────

Request B
    │
    ▼
Reuses Connection #5
```

The SQLAlchemy Session is destroyed, but the underlying database connection may continue to exist.

---

### The Four Layers

Understanding these four layers is fundamental to database internals:

```text
FastAPI Request
        │
        ▼
SQLAlchemy Session
        │
        ▼
PostgreSQL Connection
        │
        ▼
PostgreSQL Transaction
```

Each layer has its own lifecycle and responsibility.

### Key Takeaway

Do not confuse these concepts:

* **FastAPI Request** — Represents a single incoming HTTP request.
* **SQLAlchemy Session** — Manages ORM objects, tracks changes, and coordinates database work.
* **PostgreSQL Connection** — A communication channel between the application and the database, typically managed by a connection pool.
* **PostgreSQL Transaction** — A unit of work executed on the database that provides atomicity and consistency.

These are four distinct layers, and understanding the lifecycle of each is essential before studying transactions, MVCC, row-level locking, isolation levels, and concurrent transaction execution.

---

## Q4. What happens if the connection pool size is 10 but the application receives 100 simultaneous requests?

### Question

Suppose the SQLAlchemy Engine is configured as:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
)
```

and the application receives:

```text
100 simultaneous HTTP requests
```

What happens?

* Will SQLAlchemy immediately create 100 database connections?
* Will it create only 10 connections?
* What happens to the remaining 90 requests?

---

### My Answer

The SQLAlchemy Engine will **not** immediately create 100 database connections.

The connection pool is **lazy**. It creates connections only when they are needed.

With `pool_size=10`, the pool can have up to **10 active database connections** (ignoring overflow configuration).

When 100 requests arrive simultaneously:

* The first 10 requests acquire the available database connections.
* The remaining 90 requests cannot obtain a connection immediately.
* Those requests wait until one of the existing connections is returned to the pool.

SQLAlchemy does **not** create unlimited connections because doing so could overwhelm the database server.

---

### Connection Pool Lifecycle

Initially:

```text
Application Starts
        │
        ▼
Engine Created
        │
        ▼
Connection Pool
Connections = 0
```

No database connections are created.

---

First request:

```text
Request 1
        │
        ▼
Need Database
        │
        ▼
Create Connection #1
```

Second request:

```text
Request 2
        │
        ▼
Need Database
        │
        ▼
Create Connection #2
```

The pool gradually grows as demand increases until it reaches its configured limit.

---

### Pool Full

Eventually:

```text
Connections = 10
```

The pool has reached its maximum configured size.

Now another request arrives:

```text
Request 11
        │
        ▼
Need Database
        │
        ▼
No Free Connection
        │
        ▼
WAIT
```

The request waits until another request finishes and returns its connection to the pool.

---

### Timeline

```text
Time →

Connection 1  ───────────── Busy ───── Free

Connection 2  ───────────── Busy ───── Free

...

Connection10 ───────────── Busy ───── Free

────────────────────────────────────────────

Request11

WAIT WAIT WAIT WAIT

↓

Connection2 becomes free

↓

Request11 acquires Connection2
```

The request is waiting for a **free database connection**, not for PostgreSQL itself.

---

### Why `db.close()` Is Important

At the end of every request:

```python
db.close()
```

does **not** normally close the TCP connection.

Instead, it returns the connection back to the connection pool.

```text
Request Finished
        │
        ▼
db.close()
        │
        ▼
Connection Returned to Pool
        │
        ▼
Next Waiting Request Acquires Connection
```

If connections are not returned, the pool eventually becomes exhausted, causing new requests to wait and eventually fail with a pool timeout.

---

### Key Takeaways

* `pool_size` defines the maximum number of database connections that can be active in the pool at the same time.
* SQLAlchemy creates connections **lazily**, not during application startup.
* Extra requests wait for a free connection instead of creating unlimited new connections.
* `db.close()` returns the connection to the pool so it can be reused.
* Proper connection management prevents connection leaks and allows the application to efficiently serve many requests with a limited number of database connections.

---

## Q5. What happens if the connection pool size is 10 but the application receives 100 simultaneous requests?

### Question

Suppose the SQLAlchemy Engine is configured as:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
)
```

The application receives:

```text
100 simultaneous HTTP requests
```

Assume:

* Each request needs a database connection.
* Each database query takes **5 seconds**.
* `pool_timeout = 30` seconds.

What happens?

* Will SQLAlchemy create 100 database connections?
* Will the remaining requests wait?
* What happens if no connection becomes available before the timeout?

---

## My Answer

SQLAlchemy will **not** immediately create 100 database connections.

The connection pool is responsible for limiting the number of active database connections.

With:

```python
pool_size = 10
```

only **10 database connections** can be active simultaneously (ignoring overflow configuration).

When 100 requests arrive:

* The first 10 requests acquire database connections.
* The remaining 90 requests wait for a free connection.
* They do **not** immediately fail.

---

## Timeline

```text
100 HTTP Requests
        │
        ▼

Connection Pool (Size = 10)

        │

First 10 Requests
────────────────────────────────

Request 1  → Connection 1

Request 2  → Connection 2

...

Request10 → Connection10

────────────────────────────────

Remaining Requests

Request11

↓

WAIT

Request12

↓

WAIT

...

Request100

↓

WAIT
```

---

## When a Connection Becomes Available

Suppose Request 3 finishes after 5 seconds.

```text
Request 3
        │
        ▼
db.close()
        │
        ▼
Connection Returned to Pool
        │
        ▼
Request11 Acquires Connection
```

The waiting request continues executing normally.

---

## What if No Connection Becomes Available?

Suppose:

```python
pool_timeout = 30
```

If a request waits longer than 30 seconds for a database connection:

```text
Request90

↓

WAIT

↓

30 Seconds

↓

Timeout
```

SQLAlchemy raises a connection pool timeout exception similar to:

```text
sqlalchemy.exc.TimeoutError:

QueuePool limit of size 10 overflow 0 reached,
connection timed out.
```

The application can catch this exception and return an appropriate HTTP error response.

---

## Connection Pool Timeout vs HTTP Request Timeout

These are different concepts.

### Connection Pool Timeout

The application is waiting for a **database connection**.

```text
Application

↓

Connection Pool

↓

TimeoutError
```

---

### HTTP Request Timeout

The client or web server is waiting for the **entire HTTP request** to complete.

```text
Client

↓

FastAPI

↓

HTTP Timeout
```

A connection pool timeout may eventually lead to an HTTP error response, but they occur at different layers of the system.

---

## Why Doesn't SQLAlchemy Create Unlimited Connections?

Creating unlimited database connections would:

* Overload the PostgreSQL server.
* Consume excessive memory.
* Increase CPU usage.
* Reduce overall throughput.

The connection pool limits the number of active database connections to protect both the application and the database server.

---

## Key Takeaways

* `pool_size` limits the number of active database connections.
* SQLAlchemy creates connections **lazily**.
* Extra requests wait for a free connection instead of creating unlimited connections.
* If a request waits longer than `pool_timeout`, SQLAlchemy raises a `TimeoutError`.
* Connection pool timeouts and HTTP request timeouts are different concepts and occur at different layers of the application.

---

## Q6. How many PostgreSQL backend processes are created?

### Question

Suppose the SQLAlchemy Engine is configured as:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
)
```

How many PostgreSQL backend processes will exist?

Does PostgreSQL create:

* One backend process for the entire application?
* One backend process per SQLAlchemy Session?
* One backend process per database connection?
* Does it depend?

---

## My Answer

The number of PostgreSQL backend processes depends on the number of **active database connections**.

SQLAlchemy acquires database connections lazily. Therefore, PostgreSQL backend processes are also created lazily.

Initially:

```text
Application Started

Connections = 0

Backend Processes = 0
```

When the first SQL statement requires a database connection:

```text
SQLAlchemy

↓

Open Connection #1

↓

PostgreSQL creates Backend Process #1
```

As more concurrent requests require additional database connections, SQLAlchemy opens more connections (up to the configured pool size), and PostgreSQL creates one backend process for each connection.

Example:

```text
Connection 1  → Backend Process 1

Connection 2  → Backend Process 2

Connection 3  → Backend Process 3
```

If the connection pool reaches:

```text
pool_size = 10
```

then, at most, ten active database connections and ten corresponding backend processes will exist for that application (assuming no overflow connections).

---

## PostgreSQL Architecture

```text
FastAPI Request
        │
        ▼
SQLAlchemy Session
        │
        ▼
Connection Pool
        │
        ▼
Database Connection
        │
        ▼
PostgreSQL Backend Process
```

Each database connection is served by exactly one PostgreSQL backend process.

---

## Key Takeaways

* SQLAlchemy creates database connections lazily.
* PostgreSQL creates backend processes lazily as new database connections are established.
* There is a **one-to-one relationship** between an active PostgreSQL connection and a PostgreSQL backend process.
* The number of backend processes depends on the number of active database connections, not on the number of SQLAlchemy Sessions or HTTP requests.

---

## Q7. Where does PostgreSQL store transaction state?

### Question

Suppose a client executes:

```sql
BEGIN;

UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

Where does PostgreSQL store the transaction state?

* Inside the SQLAlchemy Session?
* Inside the PostgreSQL Backend Process?
* Inside shared memory?
* Inside the database files?

---

## My Answer

The **transaction context** is maintained inside the PostgreSQL **Backend Process** that owns the database connection.

Each active database connection has its own backend process, and each backend manages its own transaction independently.

Examples of information stored in the backend process include:

* Current transaction state
* Transaction ID (XID)
* Current SQL command
* Isolation level
* Snapshot information
* Executor state
* Parser state
* Planner state
* Command counter

This information belongs exclusively to that backend process.

---

## Private Transaction State

```text
Backend Process

│

├── Transaction State

├── Current Command

├── Parser

├── Planner

├── Executor

├── Snapshot

└── Local Memory
```

Every backend process maintains its own transaction context.

---

## Shared Transaction Information

Although each backend owns its private transaction state, PostgreSQL also maintains **global transaction information** in shared memory so that backend processes can coordinate with each other.

Shared memory contains structures such as:

* Transaction status
* Lock table
* Shared buffers
* WAL buffers
* Process array (ProcArray)

This allows one backend process to determine whether another transaction is active, committed, or aborted without accessing another process's private memory.

---

## PostgreSQL Architecture

```text
                PostgreSQL Server

Backend A

Private Transaction State

────────────────────────────────

Backend B

Private Transaction State

────────────────────────────────

Shared Memory

• Transaction Status
• Lock Manager
• Shared Buffers
• WAL Buffers
• ProcArray
```

---

## Key Takeaways

* Each PostgreSQL connection has its own backend process.
* Each backend process maintains its own private transaction context.
* Backend processes cannot directly access each other's private memory.
* PostgreSQL uses shared memory structures to coordinate concurrent transactions and maintain global transaction state.
* This separation between private state and shared state is a fundamental part of PostgreSQL's concurrency architecture.

---

# Transaction

A **transaction** is a logical unit of work that groups one or more database operations into a single atomic operation.

A transaction follows the principle:

* Either **all operations succeed** and are permanently saved (`COMMIT`).
* Or **none of the operations are saved**, and all changes are discarded (`ROLLBACK`).

During our experiments, we observed the following transaction lifecycle:

```text
Application
        │
        ▼
Session Created
        │
        ▼
First SQL Statement
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
COMMIT / ROLLBACK
        │
        ▼
Transaction Ends
```

## Key Learnings

* A transaction is **different** from a SQLAlchemy Session.
* A transaction is **different** from a database connection.
* A single database connection can execute **multiple transactions** during its lifetime.
* A transaction begins when PostgreSQL starts processing SQL that requires a transaction.
* A transaction ends with either `COMMIT` or `ROLLBACK`.
* Closing a SQLAlchemy Session with an active uncommitted transaction automatically issues a `ROLLBACK`, ensuring that partial changes are not persisted.
