# Experiment 01 — Lost Update

## Goal

Reproduce the Lost Update problem using two concurrent transactions.

---

## Initial State

```text
click_count = 0
```

---

## Transaction A

Executed:

```sql
SELECT click_count
FROM urls
WHERE id = 1;
```

Result:

```text
click_count = 0
```

The application calculated:

```text
new_value = 1
```

Then executed:

```sql
UPDATE urls
SET click_count = 1
WHERE id = 1;
```

Finally:

```text
COMMIT
```

---

## Transaction B

Before Transaction A committed, Transaction B executed:

```sql
SELECT click_count
FROM urls
WHERE id = 1;
```

Result:

```text
click_count = 0
```

> The application independently calculated:

```text
new_value = 1
```

Then executed:

```sql
UPDATE urls
SET click_count = 1
WHERE id = 1;
```

Finally:

```text
COMMIT
```

---

## Final Database State

```sql
SELECT click_count
FROM urls
WHERE id = 1;
```

Result:

```text
click_count = 1
```

Expected:

```text
click_count = 2
```

Actual:

```text
click_count = 1
```

---

## Why This Happened

Both transactions read the same committed value:

```text
0
```

Each transaction independently calculated:

```text
0 + 1 = 1
```

Each transaction wrote:

```text
1
```

The second transaction overwrote the first transaction's update.

One increment was lost.

---

## Timeline

```text
Transaction A                Transaction B

Read 0

                             Read 0

Calculate 1

                             Calculate 1

Write 1

Commit

                             Write 1

                             Commit

Final Database = 1
```

---

## Key Learnings

* The bug occurs because the application performs a read-modify-write sequence.
* Both transactions work with stale application state.
* PostgreSQL executes the SQL statements exactly as requested.
* The database cannot infer that the second update was based on an outdated value.
* This concurrency bug is known as the **Lost Update** problem.

---

## Production Impact

Lost updates are common in applications that implement counters, balances, inventory management, or voting systems using a read-modify-write pattern.

Without proper synchronization or atomic operations, concurrent requests can overwrite each other's work, leading to incorrect results.
