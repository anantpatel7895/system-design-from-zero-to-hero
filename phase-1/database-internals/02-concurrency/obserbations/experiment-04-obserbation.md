# Experiment 04 — Visualizing MVCC Using System Columns

## Goal

Understand how PostgreSQL implements **Multi-Version Concurrency Control (MVCC)** by observing the hidden system columns:

* `ctid`
* `xmin`
* `xmax`

The objective is to determine whether PostgreSQL updates a row in place or creates a new row version for every UPDATE.

---

# Initial State

Executed:

```sql
SELECT
    ctid,
    xmin,
    xmax,
    id,
    click_count
FROM urls
WHERE id = 1;
```

Result:

| ctid   | xmin | xmax | id | click_count |
| ------ | ---: | ---: | -: | ----------: |
| (0,25) |  796 |    0 |  1 |           0 |

---

# Observation 1 — Initial Row Version

Current row:

```text
ctid         = (0,25)

xmin         = 796

xmax         = 0

click_count  = 0
```

### Observation

* The row exists at physical location `(0,25)`.
* It was created by transaction `796`.
* `xmax = 0`, indicating that this row version is currently visible and has not yet been replaced or deleted.

---

# Step 2 — First UPDATE

Executed:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;

COMMIT;
```

Executed again:

```sql
SELECT
    ctid,
    xmin,
    xmax,
    id,
    click_count
FROM urls
WHERE id = 1;
```

Result:

| ctid   | xmin | xmax | id | click_count |
| ------ | ---: | ---: | -: | ----------: |
| (0,26) |  797 |    0 |  1 |           1 |

---

# Observation 2 — First New Row Version

Changes observed:

```text
ctid

(0,25)

↓

(0,26)
```

```text
xmin

796

↓

797
```

```text
click_count

0

↓

1
```

### Conclusion

The UPDATE did **not** modify the existing row.

Instead:

* PostgreSQL created a new physical row.
* The new row received a new physical location (`ctid`).
* The new row was created by a new transaction (`xmin = 797`).

---

# Step 3 — Second UPDATE

Executed:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;

COMMIT;
```

Executed again:

```sql
SELECT
    ctid,
    xmin,
    xmax,
    id,
    click_count
FROM urls
WHERE id = 1;
```

Result:

| ctid   | xmin | xmax | id | click_count |
| ------ | ---: | ---: | -: | ----------: |
| (0,27) |  798 |    0 |  1 |           2 |

---

# Observation 3 — Second New Row Version

Changes observed:

```text
ctid

(0,26)

↓

(0,27)
```

```text
xmin

797

↓

798
```

```text
click_count

1

↓

2
```

### Conclusion

Once again:

* PostgreSQL created another physical row.
* The previous row was not modified.
* A completely new row version became the visible version.

---

# Observation 4 — `xmax`

For every visible row:

```text
xmax = 0
```

### Observation

The currently visible row always had:

```text
xmax = 0
```

### Explanation

The query:

```sql
SELECT
    ctid,
    xmin,
    xmax,
    id,
    click_count
FROM urls
WHERE id = 1;
```

returns only the **currently visible row version**.

Older row versions are hidden from normal SQL queries.

Therefore, the visible row has not yet been replaced by another version, so its `xmax` remains `0`.

---

# What This Experiment Demonstrates

Conceptually, PostgreSQL performs the following sequence:

```text
Version 1

ctid = (0,25)

xmin = 796

click_count = 0

↓

UPDATE

↓

Version 2

ctid = (0,26)

xmin = 797

click_count = 1

↓

UPDATE

↓

Version 3

ctid = (0,27)

xmin = 798

click_count = 2
```

Each UPDATE creates a **new row version**.

The previous row version is no longer returned by normal queries but may still exist internally until PostgreSQL determines it can be safely removed.

---

# Key Learnings

* PostgreSQL does **not** update rows in place.
* Every UPDATE creates a new row version.
* `ctid` changes whenever a new row version is created.
* `xmin` identifies the transaction that created the current row version.
* The visible row has `xmax = 0` because it has not yet been replaced.
* Normal SQL queries return only the row version visible to the current transaction.

---

# Understanding MVCC

Before this experiment, it was easy to assume that an UPDATE simply modified an existing row.

This experiment demonstrates a different model.

Instead of:

```text
UPDATE

↓

Modify Existing Row
```

PostgreSQL conceptually performs:

```text
UPDATE

↓

Create New Row Version

↓

Previous Version Becomes Obsolete

↓

Queries Read the Appropriate Visible Version
```

This version-based storage model is the foundation of **Multi-Version Concurrency Control (MVCC)**.

---

# Production Relevance

MVCC enables PostgreSQL to support high concurrency.

Because older row versions remain available while newer versions are being created:

* Readers can continue reading committed data.
* Writers can update rows concurrently.
* Readers are not blocked by ordinary UPDATE statements.
* Applications observe a consistent view of the database without reading partially committed changes.

This architecture is one of the primary reasons PostgreSQL performs well in highly concurrent systems.
