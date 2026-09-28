# 03 — Money Transfer

## Problem Statement

Build a **bank-like money transfer system** where money can be transferred from one account to another.

The system must guarantee that a transfer remains **correct even when failures or concurrent transfers occur**.

---

## Basic Scenario

Initial state:

```text
Account A = ₹1,000
Account B = ₹500
```

Transfer:

```text
A → B : ₹100
```

Expected result:

```text
Account A = ₹900
Account B = ₹600
```

The total amount of money must remain unchanged:

```text
Total money before = ₹1,500
Total money after  = ₹1,500
```

---

## The Core Problem

A money transfer consists of two database operations:

```text
1. Debit money from Account A
2. Credit money to Account B
```

These two operations must behave as **one atomic operation**.

### Failure Scenario

Consider:

```text
Debit A
   ↓
₹100 removed
   ↓
Application crashes
   ↓
Credit B never happens
```

Without a database transaction:

```text
Account A = ₹900
Account B = ₹500

₹100 disappeared ❌
```

This must never happen.

---

## Transaction-Based Solution

The transfer should execute inside a database transaction:

```text
BEGIN

    Debit A
       ↓
    Credit B

COMMIT
```

If both operations succeed:

```text
COMMIT
```

Both changes become permanent.

If any operation fails:

```text
BEGIN

    Debit A
       ↓
    Failure

ROLLBACK
```

The database should restore the original state:

```text
Account A = ₹1,000
Account B = ₹500
```

---

## Concurrency Problem

The system must also handle multiple transfers executing concurrently.

Example:

```text
Transaction T1:
A → B ₹100

Transaction T2:
A → C ₹200

Transaction T3:
B → A ₹50
```

These transactions may execute at the same time.

The system must prevent problems such as:

* Lost updates
* Incorrect balances
* Double spending
* Partial transfers
* Negative balances
* Inconsistent account state
* Deadlocks

---

## Important Invariant

The most important invariant is:

```text
Total money before transfers
        =
Total money after successful transfers
```

For example:

```text
Before:

A = ₹1,000
B = ₹500
C = ₹500

Total = ₹2,000
```

After:

```text
A = ₹700
B = ₹600
C = ₹700

Total = ₹2,000
```

Money must not be accidentally created or destroyed.

---

## Project Objective

By completing this project, we should be able to understand and demonstrate:

* Database transactions
* `BEGIN`
* `COMMIT`
* `ROLLBACK`
* Atomicity
* Row-level locking
* Concurrent transfers
* Transaction isolation
* Deadlocks
* Lock ordering
* Insufficient balance handling
* Database consistency
* Failure recovery

---

## Final Question

The core question we are trying to answer is:

> **How can a database guarantee that money is never partially transferred, even when multiple transfers execute concurrently or a transaction fails halfway through?**
