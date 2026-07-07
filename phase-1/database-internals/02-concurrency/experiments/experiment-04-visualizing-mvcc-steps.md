# Experiment 04 — Visualizing MVCC Using System Columns

## Goal

Understand how PostgreSQL implements Multi-Version Concurrency Control (MVCC).

Instead of treating MVCC as a theoretical concept, we will inspect PostgreSQL's hidden system columns to observe how rows change after each UPDATE.

---

# Background

Every row in PostgreSQL contains hidden system columns.

Some of the most useful are:

| Column | Purpose                                                  |
| ------ | -------------------------------------------------------- |
| `xmin` | Transaction ID that created this row version             |
| `xmax` | Transaction ID that deleted or replaced this row version |
| `ctid` | Physical location of the row inside the table            |

These columns are maintained automatically by PostgreSQL.

Applications never need to update them.

---

# Initial State

Reset the row.

```sql
UPDATE urls
SET click_count = 0
WHERE id = 1;
```

---

## Step 1

Execute:

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

Record:

* ctid
* xmin
* xmax
* click_count

---

## Step 2

Execute:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

Commit.

---

## Step 3

Run the same query again.

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

Record everything again.

---

## Step 4

Execute another UPDATE.

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

Commit.

Run the query again.

---

## Step 5

Repeat several times.

Observe:

* Does `ctid` change?
* Does `xmin` change?
* Does `xmax` change?
* Does `click_count` change?

---

# Questions

## Q1

Does `ctid` remain the same after every UPDATE?

---

## Q2

Does `xmin` change?

---

## Q3

Does PostgreSQL appear to overwrite the existing row?

Or does it appear to create a new row version?

---

## Q4

Why do you think PostgreSQL stores multiple row versions instead of modifying rows in place?

Do not search online.

Reason from your observations.

---

# Bonus Experiment

While repeatedly executing:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

keep another DBeaver tab open and continuously run:

```sql
SELECT
    ctid,
    xmin,
    xmax,
    click_count
FROM urls
WHERE id = 1;
```

Watch how the metadata changes after every commit.

---

# Objective

By the end of this experiment, you should be able to answer:

* What is a row version?
* Why does `ctid` change?
* Why does `xmin` change?
* How does PostgreSQL implement MVCC?

Do not read the MVCC documentation yet.

First, let PostgreSQL reveal its behavior through observation.
