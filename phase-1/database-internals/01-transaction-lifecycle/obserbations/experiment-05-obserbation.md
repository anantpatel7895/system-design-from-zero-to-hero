# Experiment 05 — Transaction Atomicity (No `commit()`)

## Goal

Understand what happens when a transaction is **not committed** and the SQLAlchemy Session is closed.

This experiment answers the following questions:

* What happens if `commit()` is never called?
* Does `db.close()` automatically call `COMMIT`?
* Does `db.close()` automatically call `ROLLBACK`? 
* Are uncommitted changes visible to other database sessions?

---

# Initial Database State

Before running the experiment:

```sql
SELECT
    id,
    click_count
FROM urls
WHERE id = 1;
```

Result:

```text
id    click_count
-----------------
1     0
```

---

# Observation 1 — First SQL Statement

Executed:

```python
result = db.execute(
    text("""
        SELECT click_count
        FROM urls
        WHERE id = 1
    """)
)
```

### SQLAlchemy Log

```text
BEGIN (implicit)

SELECT click_count
FROM urls
WHERE id = 1
```

### Observation

* SQLAlchemy automatically started an implicit transaction.
* PostgreSQL began a transaction before executing the first SQL statement.

### Conclusion

> SQLAlchemy automatically begins a transaction when the first SQL operation requires one.

```text
STEP 1 : Read Current Value
============================================================
2026-09-27 16:20:07,159 INFO sqlalchemy.engine.Engine select pg_catalog.version()
2026-09-27 16:20:07,159 INFO sqlalchemy.engine.Engine [raw sql] {}
2026-09-27 16:20:07,160 INFO sqlalchemy.engine.Engine select current_schema()
2026-09-27 16:20:07,160 INFO sqlalchemy.engine.Engine [raw sql] {}
2026-09-27 16:20:07,160 INFO sqlalchemy.engine.Engine show standard_conforming_strings
2026-09-27 16:20:07,160 INFO sqlalchemy.engine.Engine [raw sql] {}
2026-09-27 16:20:07,160 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-09-27 16:20:07,160 INFO sqlalchemy.engine.Engine 
        SELECT click_count
        FROM urls
        WHERE id = 1
    
2026-09-27 16:20:07,160 INFO sqlalchemy.engine.Engine [generated in 0.00004s] {}
100000
```

---

# Observation 2 — UPDATE

Executed:

```python
db.execute(
    text("""
        UPDATE urls
        SET click_count = click_count + 1
        WHERE id = 1
    """)
)
```

### SQLAlchemy Log

```text
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1
```

### Observation

The UPDATE executed successfully.

However, no `COMMIT` was issued.

---

# Observation 3 — Verify From Another Session

From another PostgreSQL session:

```sql
SELECT
    id,
    click_count
FROM urls
WHERE id = 1;
```

Result:

```text
id    click_count
-----------------
1     0
```

### Observation

The second session still saw:

```text
click_count = 0
```

instead of:

```text
click_count = 1
```

### Conclusion

The UPDATE existed only inside the current transaction.

Other database sessions could **not** see the uncommitted change.

This demonstrates PostgreSQL's transaction isolation.

---

# Observation 4 — PostgreSQL Transaction State

Before closing the Session:

```sql
SELECT
    pid,
    state,
    xact_start,
    query
FROM pg_stat_activity
WHERE datname = 'url_shortener';
```

Important observation:

```text
State:
idle in transaction
```

Query:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1
```

### Observation

The UPDATE had finished executing.

The transaction was still active.

PostgreSQL was waiting for either:

* COMMIT
* ROLLBACK

---

# Observation 5 — Closing the Session

Executed:

```python
db.close()
```

### SQLAlchemy Log

```text
ROLLBACK
```

### PostgreSQL

The backend process reported:

```text
ROLLBACK
```

### Observation

SQLAlchemy automatically issued a **ROLLBACK** when the Session was closed with an active uncommitted transaction.

No explicit call to:

```python
db.rollback()
```

was required.

---

# Observation 6 — Verify Database Again

Executed:

```sql
SELECT
    id,
    click_count
FROM urls
WHERE id = 1;
```

Result:

```text
id    click_count
-----------------
1     0
```

### Observation

The UPDATE was not persisted.

The row remained unchanged.

---

# Transaction Timeline

```text
Session Created
        │
        ▼
BEGIN (implicit)
        │
        ▼
SELECT
        │
        ▼
UPDATE
        │
        ▼
idle in transaction
        │
        ▼
db.close()
        │
        ▼
ROLLBACK
        │
        ▼
Transaction Ends
        │
        ▼
Database Restored
```

---

# Conclusions

This experiment demonstrates several important PostgreSQL behaviors:

1. The first SQL statement automatically starts a transaction.
2. An UPDATE is **not** permanently stored until `COMMIT` is executed.
3. Uncommitted changes remain private to the current transaction.
4. Other database sessions cannot see uncommitted updates.
5. Calling `db.close()` without first calling `commit()` automatically triggers a `ROLLBACK`.
6. `ROLLBACK` discards all changes made during the current transaction.

---

# Key Learnings
* in one transaction, we can make exedcute multiple SQL statements, but until we call `commit()`, the changes are not persisted to the database.
* in one backend process (connection or session), we can have multiple transactions, but only one transaction can be active at a time.
* SQLAlchemy starts an implicit transaction on the first SQL statement.
* PostgreSQL keeps the transaction open until it receives either `COMMIT` or `ROLLBACK`.
* `db.close()` is a safe operation because it prevents accidental persistence of uncommitted changes.
* PostgreSQL guarantees transaction atomicity by discarding incomplete transactions.
* Transaction isolation ensures that uncommitted changes are invisible to other concurrent transactions.

---

# Production Relevance

This behavior is essential for maintaining data consistency in production systems.

If an application crashes or an exception occurs before `COMMIT`, PostgreSQL ensures that partially completed work is not saved.

This guarantees that the database never remains in a partially updated or inconsistent state.
