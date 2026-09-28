# PostgreSQL Row-Level Locks — When Does Another Transaction Block?

## 1. Core Question

Suppose Transaction A acquires a row-level lock:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Now Transaction B wants to access the same row.

The important question is:

> **Will Transaction B be blocked?**

### Answer

**Not always.**

Transaction B is blocked only when the operation it requests requires a lock that **conflicts with a lock already held by Transaction A**.

An ordinary `SELECT` can generally continue because PostgreSQL uses **MVCC**.

---

# 2. The Most Important Rule

Do not remember:

> "Row lock means everybody waits."

Remember:

> **A transaction waits only when the lock it requests conflicts with a lock already held by another transaction.**

Conceptually:

```text
Transaction A
      │
      ▼
  Row 1 locked
      │
      ▼
Transaction B
      │
      ▼
What operation does B want?
      │
      ├── Compatible lock ──→ Continue
      │
      └── Conflicting lock ─→ WAIT
```

---

# 3. Example Setup

Suppose we have:

```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    balance INTEGER
);

INSERT INTO accounts VALUES (1, 1000);
```

Transaction A:

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Transaction A now holds a row-level lock on:

```text
accounts.id = 1
```

We will call this:

```text
Row 1 🔒
```

Transaction B now tries different operations.

---

# 4. Case 1 — Transaction B Reads Normally

Transaction A:

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Transaction B:

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1;
```

### Does B block?

**Normally, no.**

```text
Transaction A
      │
      ▼
Row 1 🔒
      │
      │
      ├───────────────┐
      │               │
      ▼               ▼
Txn A              Txn B
FOR UPDATE         SELECT
                   │
                   ▼
                Continue
```

Why?

Because PostgreSQL uses **MVCC (Multi-Version Concurrency Control)**.

An ordinary `SELECT` does not normally need to acquire a conflicting row lock.

Therefore:

```text
A → locks row
B → normal SELECT
```

B can generally read the appropriate visible version of the row.

---

# 5. Case 2 — Transaction B Uses `FOR UPDATE`

Transaction A:

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Transaction B:

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

### Does B block?

**Yes.**

Both transactions want a conflicting row lock.

```text
Txn A
  │
  ▼
Row 1 🔒
  │
  │
  │    Txn B requests FOR UPDATE
  │             │
  │             ▼
  │           WAIT
  │
  ▼
COMMIT
  │
  ▼
Txn B obtains lock
```

So:

```text
A → FOR UPDATE → Lock
B → FOR UPDATE → WAIT
```

---

# 6. Case 3 — Transaction B Performs an UPDATE

Transaction A:

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Transaction B:

```sql
BEGIN;

UPDATE accounts
SET balance = 500
WHERE id = 1;
```

### Does B block?

**Yes.**

An `UPDATE` needs a conflicting row lock.

```text
Txn A
  │
  └── Row 1 🔒
          │
          ▼
       Txn B
          │
          └── UPDATE Row 1
                  │
                  ▼
                 WAIT
```

B waits until A releases the conflicting lock by committing or rolling back.

---

# 7. Case 4 — Transaction B Performs `DELETE`

Transaction A:

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Transaction B:

```sql
BEGIN;

DELETE FROM accounts
WHERE id = 1;
```

### Does B block?

**Yes.**

`DELETE` requires a conflicting row lock.

```text
Txn A → Row 1 🔒
              │
              ▼
Txn B → DELETE Row 1
              │
              ▼
             WAIT
```

---

# 8. Case 5 — Transaction B Uses `SELECT FOR NO KEY UPDATE`

Transaction A:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Transaction B:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR NO KEY UPDATE;
```

### Does B block?

**Yes.**

`FOR UPDATE` conflicts with `FOR NO KEY UPDATE`.

Therefore:

```text
A → FOR UPDATE 🔒
B → FOR NO KEY UPDATE
             ↓
            WAIT
```

---

# 9. Case 6 — Transaction B Uses `SELECT FOR SHARE`

Transaction A:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Transaction B:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR SHARE;
```

### Does B block?

**Yes.**

`FOR SHARE` conflicts with the stronger `FOR UPDATE` lock.

```text
A → FOR UPDATE 🔒
B → FOR SHARE
       ↓
      WAIT
```

---

# 10. Case 7 — Transaction B Uses `SELECT FOR KEY SHARE`

Transaction A:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Transaction B:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR KEY SHARE;
```

### Does B block?

**Yes.**

A `FOR UPDATE` lock conflicts with `FOR KEY SHARE`.

```text
A → FOR UPDATE 🔒
B → FOR KEY SHARE
       ↓
      WAIT
```

---

# 11. Case 8 — Both Transactions Use `FOR SHARE`

Transaction A:

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1
FOR SHARE;
```

Transaction B:

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1
FOR SHARE;
```

### Does B block?

**No.**

`FOR SHARE` locks are compatible with each other.

```text
Row 1
 │
 ├── Txn A → FOR SHARE 🔒
 │
 └── Txn B → FOR SHARE 🔒
```

Both transactions can hold compatible share locks.

---

# 12. Case 9 — Both Transactions Use `FOR KEY SHARE`

Transaction A:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR KEY SHARE;
```

Transaction B:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR KEY SHARE;
```

### Does B block?

**No.**

These locks are compatible.

```text
Row 1
 │
 ├── Txn A → KEY SHARE
 │
 └── Txn B → KEY SHARE
```

---

# 13. Case 10 — Transaction B Accesses a Different Row

Transaction A:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Transaction B:

```sql
UPDATE accounts
SET balance = 500
WHERE id = 2;
```

### Does B block?

**No.**

A locked:

```text
Row 1
```

B is modifying:

```text
Row 2
```

Therefore:

```text
Row 1 🔒 ← Txn A

Row 2 🔒 ← Txn B
```

No row-level lock conflict.

---

# 14. Case 11 — Transaction B Updates Another Row in the Same Table

The table itself does not determine the conflict.

The important thing is the **row** being accessed.

```text
Txn A:
UPDATE accounts
SET balance = 900
WHERE id = 1;
```

```text
Txn B:
UPDATE accounts
SET balance = 500
WHERE id = 2;
```

No row-level conflict:

```text
Txn A → Row 1 🔒
Txn B → Row 2 🔒
```

Both can proceed concurrently.

---

# 15. Case 12 — Transaction B Reads With Ordinary `SELECT`

A:

```sql
BEGIN;

UPDATE accounts
SET balance = 500
WHERE id = 1;
```

B:

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1;
```

### Does B block?

Normally, **no**.

This is one of the most important PostgreSQL MVCC behaviors.

B can read the appropriate committed version according to its transaction snapshot.

Conceptually:

```text
Database versions:

Old version
balance = 1000

New uncommitted version
balance = 500
```

B's ordinary `SELECT` can see the appropriate visible version rather than simply waiting for A's row lock.

---

# 16. Case 13 — Transaction B Performs `UPDATE` on the Same Row

A:

```sql
BEGIN;

UPDATE accounts
SET balance = 500
WHERE id = 1;
```

B:

```sql
BEGIN;

UPDATE accounts
SET balance = 300
WHERE id = 1;
```

### Does B block?

**Yes.**

B needs to modify the same row.

```text
Txn A
   │
   ▼
Row 1 🔒
   │
   │
   └──────── Txn B → UPDATE Row 1
                         │
                         ▼
                        WAIT
```

When A commits or rolls back, PostgreSQL determines how B proceeds based on the transaction state and isolation semantics.

---

# 17. Case 14 — Transaction B Deletes the Same Row

A:

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

B:

```sql
DELETE FROM accounts
WHERE id = 1;
```

B waits.

```text
Txn A → Row 1 🔒
             │
             ▼
Txn B → DELETE Row 1
             │
             ▼
            WAIT
```

---

# 18. Case 15 — Transaction B Uses `SKIP LOCKED`

A:

```sql
BEGIN;

SELECT *
FROM jobs
WHERE status = 'pending'
FOR UPDATE;
```

B:

```sql
SELECT *
FROM jobs
WHERE status = 'pending'
FOR UPDATE SKIP LOCKED;
```

### Does B block?

**No.**

Instead of waiting for the locked row, PostgreSQL skips it.

Example:

```text
Jobs:

Job 1 🔒 ← Txn A
Job 2    ← available
Job 3    ← available
```

B executes:

```sql
FOR UPDATE SKIP LOCKED
```

and can obtain:

```text
Job 2
```

instead of waiting for Job 1.

This is extremely useful for job queues.

---

# 19. Case 16 — Transaction B Uses `NOWAIT`

A:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

B:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE NOWAIT;
```

### Does B wait?

**No.**

Instead, PostgreSQL immediately returns an error because the required lock is unavailable.

Conceptually:

```text
Txn A → Row 1 🔒

Txn B → FOR UPDATE NOWAIT
             │
             ▼
       Lock unavailable
             │
             ▼
           ERROR
```

Difference:

```text
FOR UPDATE
    ↓
WAIT

FOR UPDATE NOWAIT
    ↓
ERROR immediately

FOR UPDATE SKIP LOCKED
    ↓
Skip locked row
```

---

# 20. Case 17 — Transaction B Accesses the Same Row With `FOR NO KEY UPDATE`

Suppose A:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR NO KEY UPDATE;
```

B:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR NO KEY UPDATE;
```

### Does B block?

**Yes.**

Two `FOR NO KEY UPDATE` locks conflict.

```text
A → NO KEY UPDATE 🔒
B → NO KEY UPDATE
        ↓
       WAIT
```

---

# 21. PostgreSQL Row-Level Lock Modes

PostgreSQL provides four main row-level locking clauses:

```text
FOR UPDATE
FOR NO KEY UPDATE
FOR SHARE
FOR KEY SHARE
```

They have different compatibility rules.

A useful simplified compatibility table is:

| Existing lock held by A | B: `FOR UPDATE` | B: `FOR NO KEY UPDATE` | B: `FOR SHARE` | B: `FOR KEY SHARE` |
| ----------------------- | --------------: | ---------------------: | -------------: | -----------------: |
| `FOR UPDATE`            |           Block |                  Block |          Block |              Block |
| `FOR NO KEY UPDATE`     |           Block |                  Block |          Block |           No block |
| `FOR SHARE`             |           Block |                  Block |       No block |           No block |
| `FOR KEY SHARE`         |           Block |               No block |       No block |           No block |

`Block` means B must wait for the conflicting lock to be released.

---

# 22. Simplified Mental Model

Think of the locks as having different strengths:

```text
Strongest

FOR UPDATE
     │
     ▼
FOR NO KEY UPDATE
     │
     ▼
FOR SHARE
     │
     ▼
FOR KEY SHARE

Weakest
```

However, do **not** rely only on this ordering. The compatibility matrix above is the better reference because some locks are compatible despite having different strengths.

---

# 23. Ordinary SELECT Is Different

One of the most important things to remember:

```sql
SELECT *
FROM accounts
WHERE id = 1;
```

is different from:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

### Ordinary SELECT

```text
SELECT
  ↓
MVCC snapshot
  ↓
Read visible version
```

It generally does not wait for another transaction's row lock.

### `SELECT FOR UPDATE`

```text
SELECT FOR UPDATE
       ↓
Request row lock
       ↓
Conflicting lock?
       │
       ├── No → Continue
       │
       └── Yes → Wait
```

---

# 24. Example With Two Kubernetes Pods

This is directly related to the original system-design problem.

Suppose:

```text
Pod A
  │
  ▼
Transaction A
  │
  ▼
SELECT ... FOR UPDATE
  │
  ▼
Account #101 🔒
```

At the same time:

```text
Pod B
  │
  ▼
Transaction B
  │
  ▼
UPDATE account #101
```

B waits.

```text
Pod A                         Pod B
  │                             │
  ▼                             ▼
Txn A                         Txn B
  │                             │
  ▼                             ▼
Account #101 🔒              UPDATE #101
                                │
                                ▼
                               WAIT
                                │
                                │
                         A COMMIT/ROLLBACK
                                │
                                ▼
                           B continues
```

---

# 25. Different Rows — No Conflict

```text
Pod A → Txn A → Account #101 🔒

Pod B → Txn B → Account #102 🔒
```

Both can proceed.

```text
Account #101 🔒 ← A

Account #102 🔒 ← B
```

This is why row-level locking provides better concurrency than locking an entire table.

---

# 26. Same Row — Ordinary Read

```text
Pod A → Txn A → Account #101 🔒

Pod B → Txn B → SELECT Account #101
```

Generally:

```text
A → continues
B → continues
```

because B is performing an ordinary MVCC read.

---

# 27. Same Row — Conflicting Write

```text
Pod A → Txn A → Account #101 🔒

Pod B → Txn B → UPDATE Account #101
```

Result:

```text
A → continues
B → WAIT
```

---

# 28. Same Row — `FOR UPDATE`

```text
Pod A → Txn A → FOR UPDATE Account #101

Pod B → Txn B → FOR UPDATE Account #101
```

Result:

```text
A → continues
B → WAIT
```

---

# 29. What Releases the Lock?

A transaction's row locks are normally released when the transaction ends:

```sql
COMMIT;
```

or:

```sql
ROLLBACK;
```

Conceptually:

```text
BEGIN
  ↓
FOR UPDATE
  ↓
Row 🔒
  ↓
SQL operations
  ↓
COMMIT
  ↓
Row lock released
```

If the transaction remains open:

```text
BEGIN
  ↓
FOR UPDATE
  ↓
Row 🔒
  ↓
Application waits...
```

the lock can remain held.

This is why long-running transactions can cause serious blocking.

---

# 30. `db.close()` vs Transaction End

In SQLAlchemy, don't confuse:

```python
db.close()
```

with:

```python
db.commit()
```

`commit()` ends the current transaction by committing it.

`rollback()` ends it by rolling it back.

`close()` closes/releases the SQLAlchemy Session and releases its database resources.

For example:

```python
db.execute(...)
db.commit()
db.close()
```

means:

```text
Execute SQL
    ↓
Transaction active
    ↓
COMMIT
    ↓
Transaction ends
    ↓
Session closes
```

---

# 31. How to Observe Blocking in PostgreSQL

You can create two database sessions.

### Session A

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Do not commit yet.

### Session B

```sql
BEGIN;

SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Session B will wait.

You can inspect PostgreSQL using:

```sql
SELECT
    pid,
    usename,
    state,
    wait_event_type,
    wait_event,
    query
FROM pg_stat_activity
WHERE datname = current_database();
```

You may see the waiting session.

---

# 32. Finding Which Transaction Is Blocking Another

PostgreSQL provides useful functions for this.

For example:

```sql
SELECT
    pid,
    pg_blocking_pids(pid) AS blocking_pids,
    state,
    wait_event_type,
    wait_event,
    query
FROM pg_stat_activity
WHERE state <> 'idle';
```

If you see:

```text
pid      blocking_pids
------   -------------
2002     {2001}
```

it means approximately:

```text
PID 2002
   ↓
waiting for
   ↓
PID 2001
```

So:

```text
PID 2001 → blocker
PID 2002 → blocked session
```

---

# 33. Complete Decision Tree

When Transaction A holds a row-level lock, ask:

```text
Transaction A holds Row 1 lock
              │
              ▼
       What does B want?
              │
      ┌───────┼────────┐
      │       │        │
      ▼       ▼        ▼
    Read    Write    Lock
      │       │        │
      ▼       ▼        ▼
 Ordinary   Same     Compatible?
 SELECT     row?        │
      │       │     ┌───┴───┐
      ▼       ▼     ▼       ▼
 Usually   ┌──┴──┐  Yes      No
no block   │     │   │        │
          No     Yes  ▼        ▼
           │      │ Continue   WAIT
           ▼      ▼
        Continue  WAIT
```

---

# 34. The Rules to Memorize

## Rule 1

**Same row does not automatically mean blocking.**

```text
Same row + ordinary SELECT
        ↓
Usually no blocking
```

---

## Rule 2

**Conflicting lock = blocking.**

```text
A → Row lock
B → Conflicting lock
        ↓
      WAIT
```

---

## Rule 3

**Different rows generally don't conflict at the row-lock level.**

```text
A → Row 1
B → Row 2
```

Both can proceed.

---

## Rule 4

**`FOR UPDATE` is a strong row lock.**

Other transactions requesting conflicting locks on that row must wait.

---

## Rule 5

**`NOWAIT` doesn't wait.**

```text
Lock unavailable
      ↓
ERROR immediately
```

---

## Rule 6

**`SKIP LOCKED` doesn't wait.**

```text
Locked row
    ↓
Skip it
    ↓
Process another available row
```

---

## Rule 7

**Transaction duration matters.**

The longer Transaction A holds a conflicting row lock:

```text
BEGIN
  ↓
LOCK
  ↓
...
...
...
  ↓
COMMIT
```

the longer Transaction B may have to wait.

---

# 35. Final Mental Model

The most important concept is:

```text
                  Transaction A
                       │
                       ▼
                   Row 1 🔒
                       │
                       ▼
                  Transaction B
                       │
                 What does B want?
                       │
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
 Ordinary SELECT   Conflicting lock   Different row
       │               │                │
       ▼               ▼                ▼
   Usually no        BLOCK            No block
     block             │
                       ▼
                Wait for A to
                COMMIT/ROLLBACK
```

## One Sentence to Remember

> **A row-level lock does not block everyone; it blocks only transactions requesting incompatible access to the same locked row.**

This distinction—**same row vs different row, read vs write, compatible vs conflicting lock**—is the foundation for understanding PostgreSQL concurrency, deadlocks, inventory systems, banking transactions, job queues, and multiple Kubernetes pods accessing the same database.
