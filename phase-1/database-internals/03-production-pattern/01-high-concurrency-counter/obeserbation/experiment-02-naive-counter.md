# Experiment 02 — Naive Concurrent Counter

## Goal

Evaluate the correctness of the naive **Read → Modify → Write** approach under concurrent execution.

---

# Configuration

* Threads: **10**
* Increments per Thread: **100**

Total expected increments:

```text
10 × 100 = 1000
```

---

# Result

```text
Expected : 1000

Actual   : 249

Lost     : 751
```

---

# Observation

The naive implementation produced a final counter value of **249** instead of the expected **1000**.

A total of **751 increments were lost** due to concurrent execution.

This demonstrates that the implementation is **not safe under concurrency**.

---

# Why Did This Happen?

The service performs the following sequence:

```text
Read Current Value

↓

Increment in Python

↓

Write Updated Value
```

In code:

```python
count = repository.get_count()

count += 1

repository.update_count()
```

This operation is **not atomic** because it consists of two separate SQL statements:

```text
SELECT

↓

UPDATE
```

Between these two statements, another thread can read the same value and overwrite the first thread's update.

---

# Example

Suppose the database contains:

```text
click_count = 100
```

Three threads execute simultaneously.

```text
Thread A

SELECT

↓

100

────────────────────────

Thread B

SELECT

↓

100

────────────────────────

Thread C

SELECT

↓

100
```

Each thread increments the value locally:

```text
Thread A

100 + 1

↓

101

↓

UPDATE

────────────────────────

Thread B

100 + 1

↓

101

↓

UPDATE

────────────────────────

Thread C

100 + 1

↓

101

↓

UPDATE
```

Final database value:

```text
101
```

Although three increments occurred, only one survived.

Two increments were lost because later updates overwrote earlier ones.

---

# Root Cause

The naive implementation follows the **Read → Modify → Write** pattern.

```text
SELECT

↓

Python Modification

↓

UPDATE
```

Since the read and write occur as separate operations, multiple threads can read the same value before any of them writes the updated value back to the database.

This creates a **race condition**, resulting in lost updates.

---

# Key Learning

The naive **Read → Modify → Write** approach is **not safe** for concurrent systems.

When multiple transactions update the same row simultaneously, updates can overwrite each other, leading to incorrect results.

---

# Production Implication

This type of implementation must never be used for shared counters such as:

* Page views
* URL click counts
* Product inventory
* Wallet balances
* Bank account balances
* Seat reservations

Concurrent requests can produce severe data corruption.

---

# Next Step

Replace the naive implementation with an **atomic SQL operation**:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = 1;
```

This allows PostgreSQL to perform the increment as a single atomic operation, preventing lost updates even under heavy concurrency.

---

# Biggest Takeaway

This experiment demonstrates that correctness cannot be achieved by simply reading, modifying, and writing shared data in application code.

For concurrent systems, operations that modify shared state must be performed atomically by the database or another synchronization mechanism.
