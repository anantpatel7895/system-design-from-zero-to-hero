
# Transactions and Database Connections

## 1. Multiple SQL Statements in One Transaction

A single transaction can contain multiple SQL statements.

Example:

```python
db.execute(
    text("UPDATE users SET name='Anant' WHERE id=1")
)

db.execute(
    text("UPDATE accounts SET balance=5000 WHERE user_id=1")
)

db.execute(
    text("INSERT INTO audit_log (...) VALUES (...)")
)

db.commit()
```

The transaction lifecycle is:

```text
BEGIN
  │
  ├── UPDATE users
  │
  ├── UPDATE accounts
  │
  └── INSERT audit_log
       │
       ▼
     COMMIT
```

### Before `COMMIT`

The SQL statements have been executed by PostgreSQL, but the transaction has **not yet been committed**.

```text
SQL Statement
      │
      ▼
PostgreSQL
      │
      ▼
Transaction State
      │
      │  COMMIT
      ▼
Committed Data
```

If the transaction is rolled back:

```python
db.rollback()
```

the changes made within that transaction are rolled back.

### Example

```text
BEGIN

UPDATE users
UPDATE accounts
INSERT audit_log

ROLLBACK
```

Result:

```text
All changes from this transaction are rolled back.
```

---

## 2. One Connection Can Have Multiple Transactions

A PostgreSQL connection can execute multiple transactions during its lifetime.

For example:

```text
Connection
    │
    ├── Transaction 1
    │      ├── SQL
    │      ├── SQL
    │      └── COMMIT
    │
    ├── Transaction 2
    │      ├── SQL
    │      └── ROLLBACK
    │
    ├── Transaction 3
    │      ├── SQL
    │      └── COMMIT
    │
    └── Transaction 4
           └── ...
```

The important point is:

> A connection can be reused for many transactions over its lifetime.

However, a connection normally has **only one active transaction at a time**.

---

# 3. Connection vs Transaction

A connection and a transaction are different concepts.

### Connection

A connection represents communication between the application and PostgreSQL.

```text
Application
     │
     │ TCP connection
     ▼
PostgreSQL Backend
```

A connection can remain open for a long time.

### Transaction

A transaction represents a unit of database work.

```text
Connection
    │
    ├── Transaction 1
    │
    ├── Transaction 2
    │
    └── Transaction 3
```

Therefore:

```text
One Connection
      │
      ├── Transaction 1
      ├── Transaction 2
      ├── Transaction 3
      └── Transaction N
```

Transactions happen **sequentially** on a single connection.

---

# 4. SQLAlchemy Connection Pool

SQLAlchemy normally maintains a connection pool.

Conceptually:

```text
Engine
  │
  ▼
Connection Pool
  │
  ├── Connection 1
  ├── Connection 2
  ├── Connection 3
  └── Connection N
```

Each connection can be used for different transactions over time.

For example:

```text
Connection 1
    │
    ├── Request A → Transaction 1 → COMMIT
    │
    ├── Request B → Transaction 2 → COMMIT
    │
    └── Request C → Transaction 3 → ROLLBACK
```

The connection does not need to be recreated for every transaction.

---

# 5. PostgreSQL Backend Process

When a PostgreSQL client connection is established, PostgreSQL creates a backend process/session to handle that connection.

Conceptually:

```text
Application
    │
    ▼
TCP Connection
    │
    ▼
PostgreSQL Backend Process
    │
    ├── Transaction 1
    ├── Transaction 2
    └── Transaction 3
```

You can observe these backend processes using:

```sql
SELECT
    pid,
    usename,
    client_addr,
    state,
    query
FROM pg_stat_activity;
```

The `pid` identifies the PostgreSQL backend process/session.

---

# 6. Important Relationship

The relationship is:

```text
SQLAlchemy Engine
        │
        ▼
Connection Pool
        │
        ├── Connection 1
        │      │
        │      └── PostgreSQL Backend PID 1001
        │              │
        │              ├── Transaction 1
        │              ├── Transaction 2
        │              └── Transaction 3
        │
        ├── Connection 2
        │      │
        │      └── PostgreSQL Backend PID 1002
        │              │
        │              ├── Transaction 1
        │              └── Transaction 2
        │
        └── Connection 3
               │
               └── PostgreSQL Backend PID 1003
```

---

# 7. Kubernetes Example

Suppose we have two application pods.

```text
Pod A
  │
  └── SQLAlchemy Connection Pool
          ├── Connection A1
          ├── Connection A2
          └── Connection A3


Pod B
  │
  └── SQLAlchemy Connection Pool
          ├── Connection B1
          ├── Connection B2
          └── Connection B3
```

These connections communicate with PostgreSQL:

```text
                PostgreSQL
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
     PID 1001      PID 1002      PID 1003
       │             │             │
       ...
```

If each pod can maintain 3 connections:

```text
2 Pods × 3 connections
=
6 possible PostgreSQL connections
```

Therefore:

> **Connection pools are per application process/pod, not shared globally between pods.**

---

# 8. Connection vs Transaction — Quick Comparison

| Concept         | Meaning                                                            |
| --------------- | ------------------------------------------------------------------ |
| Connection      | Communication channel between application and PostgreSQL           |
| Backend process | PostgreSQL process/session handling a connection                   |
| Transaction     | A unit of database work                                            |
| Connection Pool | Collection of reusable database connections                        |
| `COMMIT`        | Permanently commits the current transaction                        |
| `ROLLBACK`      | Rolls back the current transaction                                 |
| `Session`       | SQLAlchemy object used to manage database interaction/transactions |

---

# 9. Key Rules to Remember

### Rule 1

One transaction can contain multiple SQL statements.

```text
Transaction
    ├── SQL 1
    ├── SQL 2
    ├── SQL 3
    └── COMMIT
```

### Rule 2

A transaction ends with:

```text
COMMIT
```

or:

```text
ROLLBACK
```

### Rule 3

One connection can execute many transactions over its lifetime.

```text
Connection
    ├── Transaction 1
    ├── Transaction 2
    ├── Transaction 3
    └── ...
```

### Rule 4

Normally, one connection has only one active transaction at a time.

```text
Connection
    │
    └── Active Transaction
```

After the transaction ends, the connection can start another transaction.

### Rule 5

A connection does not necessarily disappear after a transaction ends.

```text
BEGIN
  ↓
SQL
  ↓
COMMIT
  ↓
Connection still exists
  ↓
Connection can be reused
```

### Rule 6

With SQLAlchemy connection pooling:

```text
db.close()
```

normally releases the connection back to the pool rather than necessarily closing the physical database connection.

---

# 10. Mental Model

The easiest way to remember everything:

```text
                SQLAlchemy
                    │
                    ▼
                  Engine
                    │
                    ▼
             Connection Pool
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
     Connection  Connection  Connection
          │         │         │
          ▼         ▼         ▼
      Backend    Backend    Backend
       PID 1      PID 2      PID 3
          │
          │
    ┌─────┴
    ▼           
Transaction  1
    1          
    │
    ├── SQL 1
    ├── SQL 2
    └── COMMIT
    |__ end of transaction

Transaction  2
    2
    │
    ├── SQL 1
    └── ROLLBACK
    |__ end of transaction
```

## Core Concept

> **Connection is the communication channel. Transaction is the unit of work performed through that channel.**

One connection can execute many transactions over its lifetime, but normally only one transaction is active on that connection at a time.

