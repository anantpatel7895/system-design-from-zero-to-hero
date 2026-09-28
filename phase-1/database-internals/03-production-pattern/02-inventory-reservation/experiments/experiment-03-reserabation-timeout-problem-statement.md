# Inventory Reservation — From Database Transactions to Production Architecture

## Why the Current Design Is Not Suitable for Production

Our current implementation follows this flow:

```text
BEGIN

↓

SELECT ... FOR UPDATE

↓

User Enters Card Details

↓

User Enters OTP

↓

User Clicks Pay

↓

COMMIT
```

### Question

> How long does a typical customer take to complete payment?

Usually:

```text
30 Seconds

1 Minute

2 Minutes

5 Minutes
```

Can a PostgreSQL transaction remain open for several minutes?

**Absolutely not.**

---

# Problems with This Approach

## Problem 1 — Long-Lived Row Lock

```text
Product

↓

Locked

↓

5 Minutes
```

While the row remains locked, no other customer can purchase the product.

This severely limits concurrency.

---

## Problem 2 — Database Resources

An open transaction consumes valuable database resources.

While the transaction remains open, PostgreSQL must keep:

* A database connection
* A backend process
* Transaction state
* Row locks
* An MVCC snapshot

Holding these resources for minutes does not scale.

With thousands of concurrent users, the database would quickly become exhausted.

---

## Problem 3 — Customer Abandons Checkout

Imagine the customer:

```text
Buy Product

↓

Inventory Reserved

↓

Closes Browser
```

If the transaction remains open, the inventory may stay locked indefinitely.

This is unacceptable for a production system.

---

# Production Solution

The key design principle is:

> **A database transaction is not the same as a business reservation.**

Instead of treating them as the same thing, production systems separate them.

```text
Short Database Transaction

↓

Create Reservation

↓

COMMIT

────────────────────────

Reservation Exists

↓

15 Minutes

↓

Customer Completes Payment

OR

Reservation Expires
```

The transaction lasts only a few milliseconds.

The reservation exists for several minutes.

---

# Database Schema

## Products Table

```sql
CREATE TABLE products (

    id SERIAL PRIMARY KEY,

    name TEXT NOT NULL,

    stock INTEGER NOT NULL

);
```

---

## Inventory Reservations Table

```sql
CREATE TABLE inventory_reservations (

    id SERIAL PRIMARY KEY,

    product_id INTEGER NOT NULL,

    user_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL,

    status TEXT NOT NULL,

    expires_at TIMESTAMP NOT NULL,

    created_at TIMESTAMP DEFAULT now()

);
```

---

# Reservation Status Lifecycle

```text
RESERVED

↓

PAID

or

↓

EXPIRED

or

↓

CANCELLED
```

Each reservation moves through one of these states during its lifetime.

---

# New Purchase Flow

Instead of:

```text
Lock Row

↓

Wait 5 Minutes

↓

COMMIT
```

A production system performs:

```text
BEGIN

↓

SELECT ... FOR UPDATE

↓

Decrease Stock

↓

Insert Reservation

↓

COMMIT
```

Typical duration:

```text
5–20 milliseconds
```

The row lock is released almost immediately.

---

# Customer Payment Flow

After the transaction commits:

```text
Reservation Created

↓

Customer Has 15 Minutes

↓

Complete Payment
```

The customer can take time to complete payment without holding any database locks.

---

# Successful Payment

When payment succeeds:

```text
Reservation

↓

PAID
```

No inventory update is required because the stock was already reserved.

---

# Failed or Abandoned Payment

If payment is never completed:

```text
Reservation

↓

EXPIRED
```

A **background worker** periodically executes:

```text
Increase Stock

↓

Mark Reservation Expired

↓

Inventory Becomes Available Again
```

The product is automatically returned to inventory.

---

# Overall Architecture

```text
Customer

↓

Reserve Product

↓

API Server

↓

PostgreSQL

────────────────────────────

Products

Stock = 9

────────────────────────────

Inventory Reservations

Status = RESERVED

Expires = +15 Minutes

────────────────────────────

Background Worker

↓

Find Expired Reservations

↓

Restore Stock

↓

Mark Reservation Expired
```

This architecture allows customers to complete payment without blocking other database operations.

---

# Roadmap

We will build the system incrementally.

```text
Experiment 03

Create Reservation

↓

Experiment 04

Reservation Timeout

↓

Experiment 05

Background Cleanup

↓

Experiment 06

High-Concurrency Reservations

↓

Experiment 07

Production Architecture
```

Each experiment introduces one additional production concept while keeping the implementation easy to understand.

---

# Why This Project Matters

This project combines nearly everything learned so far:

* Database transactions
* `SELECT ... FOR UPDATE`
* Row-level locking
* Atomic updates
* Concurrent access
* Business logic
* Background processing
* Reservation lifecycle

By the end of this project, you'll understand how modern e-commerce and booking systems safely reserve inventory while serving thousands of concurrent users without keeping long-running database transactions open.
