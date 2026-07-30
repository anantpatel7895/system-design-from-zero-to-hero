# Experiment 03 — Create Reservation — Observations

## Goal

Implement a production-style inventory reservation workflow that separates a short database transaction from the customer payment process.

---

# What We Improved from Experiment 02

## Experiment 02

Our workflow was:

```text
BEGIN

↓

SELECT ... FOR UPDATE

↓

Decrease Stock

↓

Customer Completes Payment

↓

COMMIT
```

### Problems

* Database transaction remained open while the customer was paying.
* Row-level lock was held for a long time.
* Database connection remained occupied.
* Other customers had to wait.
* Poor scalability.

---

## Experiment 03

New workflow:

```text
BEGIN

↓

SELECT ... FOR UPDATE

↓

Validate Stock

↓

Decrease Stock

↓

Create Reservation

↓

COMMIT
```

Customer payment now happens **after** the transaction commits.

This greatly reduces lock duration and database resource usage.

---

# Observation 1 — Short Transaction

The transaction now contains only database operations.

```text
Lock Product

↓

Decrease Stock

↓

Insert Reservation

↓

Commit
```

Typical duration:

```text
5–20 milliseconds
```

The customer can spend several minutes completing payment without holding any database locks.

---

# Observation 2 — Atomic Transaction

Two database modifications occur together.

```text
UPDATE products

↓

INSERT inventory_reservations
```

Both operations execute inside the same transaction.

If either operation fails, PostgreSQL rolls back the entire transaction.

This guarantees database consistency.

---

# Observation 3 — Inventory Reduced Immediately

Initial inventory:

```text
Product

Stock = 10
```

After reservation:

```text
Product

Stock = 9
```

The inventory is reduced immediately after creating the reservation.

This prevents another customer from reserving the same unit.

---

# Observation 4 — Reservation Created

A new record was inserted into:

```text
inventory_reservations
```

Example:

```text
Reservation

Product ID = 1

User ID = 101

Quantity = 1

Status = RESERVED
```

Instead of keeping the database transaction open, the business state is now stored as a reservation.

---

# Observation 5 — Database State

Products

```text
Stock = 9
```

Reservations

```text
Status = RESERVED
```

The database now accurately represents:

* One reserved item
* Remaining available inventory

---

# Observation 6 — Business Transaction vs Database Transaction

This experiment introduced an important architectural concept.

## Database Transaction

```text
BEGIN

↓

Update Database

↓

COMMIT
```

Duration:

```text
Milliseconds
```

---

## Business Reservation

```text
Reservation Created

↓

Customer Pays

↓

15 Minutes
```

Duration:

```text
Minutes
```

These are two completely different concepts.

Production systems keep database transactions short while allowing business workflows to continue for much longer.

---

# Key Learning

Instead of holding a database transaction open during checkout, production systems:

1. Reserve inventory.
2. Commit immediately.
3. Allow the customer to complete payment later.

This design minimizes lock contention while preserving inventory consistency.

---

# Preparation for the Next Experiment

Although inventory is now reserved correctly, another problem still exists.

Suppose the customer never completes payment.

```text
Reservation

↓

Status = RESERVED

↓

Customer Leaves
```

The reserved inventory is never released.

The next experiment introduces reservation expiration and automatic inventory recovery.
