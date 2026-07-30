# Experiment 02 — SELECT ... FOR UPDATE

## Goal

Understand how `SELECT ... FOR UPDATE` prevents overselling by locking a row before making a business decision.

---

# Initial Database State

Reset the inventory.

```sql
UPDATE products
SET stock = 1
WHERE id = 1;
```

Verify:

```sql
SELECT *
FROM products
WHERE id = 1;
```

Expected:

| id | name      | stock |
| -- | --------- | ----: |
| 1  | iPhone 17 |     1 |

---

# Step 1 — Start Transaction A

Run:

```bash
python3 -m experiments.experiment-02-transaction-a-select-for-update
```

Transaction A executes:

```sql
SELECT stock
FROM products
WHERE id = 1
FOR UPDATE;
```

Expected output:

```text
Current Stock = 1

Press ENTER to BUY...
```

Do **not** commit yet.

---

# Step 2 — Start Transaction B

Open another terminal.

Run:

```bash
python3 -m experiments.experiment-02-transaction-b-select-for-update
```

Transaction B also executes:

```sql
SELECT stock
FROM products
WHERE id = 1
FOR UPDATE;
```

Expected behavior:

Transaction B does **not** continue immediately.

It waits because Transaction A already owns the row lock.

---

# Step 3 — Observe PostgreSQL

While Transaction B is waiting, execute:

```sql
SELECT
    pid,
    state,
    wait_event_type,
    wait_event,
    query
FROM pg_stat_activity
WHERE datname = 'url_shortener';
```

Also inspect:

```sql
SELECT *
FROM pg_locks;
```

Observe:

* Which backend owns the row lock.
* Which backend is waiting.
* The lock types held by each transaction.

---

# Step 4 — Commit Transaction A

Press ENTER in Terminal A.

Transaction A performs:

```sql
UPDATE products
SET stock = 0
WHERE id = 1;

COMMIT;
```

The row lock is released.

---

# Step 5 — Observe Transaction B

Immediately after Transaction A commits:

Transaction B wakes up automatically.

It now executes:

```sql
SELECT stock
FROM products
WHERE id = 1
FOR UPDATE;
```

The result is:

```text
Current Stock = 0
```

Business logic:

```python
if stock <= 0:
    print("Out Of Stock")
    db.rollback()
```

Expected output:

```text
Out Of Stock
```

---

# Step 6 — Verify Database

Execute:

```sql
SELECT *
FROM products
WHERE id = 1;
```

Expected result:

| id | name      | stock |
| -- | --------- | ----: |
| 1  | iPhone 17 |     0 |

---

# Expected Result

Customer A:

```text
Purchased
```

Customer B:

```text
Out Of Stock
```

Only one purchase succeeds.

No overselling occurs.
