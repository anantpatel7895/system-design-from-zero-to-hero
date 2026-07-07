# Experiment 07 — Can Another Transaction See My Uncommitted Changes?

## Goal

Determine whether one transaction can see another transaction's uncommitted changes.

This experiment uses two independent database sessions executing concurrently.

---

# Initial Database State

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

# Transaction A

Executed:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

### SQLAlchemy Log

```text
BEGIN (implicit)

UPDATE urls
SET click_count = click_count + 1
WHERE id = 1
```

### Observation

* SQLAlchemy started an implicit transaction.
* PostgreSQL executed the UPDATE.
* The transaction remained uncommitted while waiting for user input.

---

# Transaction B (Before Commit)

Executed while Transaction A was still waiting.

```sql
SELECT click_count
FROM urls
WHERE id = 1;
```

Result:

```text
Click Count = 0
```

### Observation

Transaction B could **not** see the UPDATE performed by Transaction A.

Although Transaction A had already modified the row, the modification was still uncommitted.

---

# Transaction A

Executed:

```python
db.commit()
```

### SQLAlchemy Log

```text
COMMIT
```

### Observation

The transaction completed successfully.

The UPDATE became permanent.

---

# Transaction B (After Commit)

Executed again after Transaction A committed.

```sql
SELECT click_count
FROM urls
WHERE id = 1;
```

Result:

```text
Click Count = 1
```

### Observation

After the COMMIT, Transaction B immediately observed the updated value.

---

# Timeline

```text
                Transaction A                     Transaction B

BEGIN
    │
UPDATE click_count = 1
    │
    │----------------------------------------► SELECT
    │                                         Result = 0
    │
COMMIT
    │
    │----------------------------------------► SELECT
                                              Result = 1
```

---

# Conclusions

This experiment demonstrates PostgreSQL's transaction isolation.

While Transaction A had modified the row, the modification remained private until the transaction committed.

Other transactions continued to read the previously committed version of the row.

Only after the COMMIT did the new value become visible to other transactions.

---

# Key Learnings

* Every transaction has its own isolated view of the database.
* Uncommitted changes are visible only inside the transaction that made them.
* Other concurrent transactions continue to read the last committed version of the data.
* `COMMIT` makes the changes durable and immediately visible to future transactions.
* PostgreSQL prevents dirty reads under its default isolation level (`READ COMMITTED`).

---

# Production Relevance

This behavior prevents applications from reading incomplete or partially updated data.

For example, if a banking transaction transfers money between two accounts, other users will never observe an intermediate state where money has been deducted from one account but not yet credited to the other.

They either see:

* The old committed state, or
* The fully committed new state.

They never see partially completed work.

---

# Biggest Takeaway

This experiment proved that PostgreSQL does **not** expose uncommitted changes to other transactions.

This is one of the core guarantees that allows multiple users to safely access and modify the same database concurrently without observing inconsistent data.
