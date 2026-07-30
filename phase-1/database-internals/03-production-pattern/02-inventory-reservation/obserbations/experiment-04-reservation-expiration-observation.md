# Experiment 04 — Reservation Expiration — Observations

## Goal

Automatically release reserved inventory when the customer never completes payment.

---

# What We Improved from Experiment 03

## Experiment 03

Workflow:

```text
Create Reservation

↓

Decrease Stock

↓

Reservation = RESERVED
```

Problem:

If the customer abandoned checkout, the reservation remained forever.

```text
Stock = 9

Reservation = RESERVED

Forever
```

Inventory gradually became unavailable even though nothing had been sold.

---

## Experiment 04

New workflow:

```text
Create Reservation

↓

Wait Until Expiration

↓

Cleanup Service

↓

Increase Stock

↓

Reservation = EXPIRED
```

Reserved inventory is now automatically returned to stock.

---

# Observation 1 — Reservation Expired

The reservation was created with:

```text
expires_at = NOW() + 10 seconds
```

After waiting:

```text
NOW()

>

expires_at
```

The reservation became eligible for cleanup.

---

# Observation 2 — Cleanup Transaction

The cleanup service executed:

```text
BEGIN

↓

Find Expired Reservations

↓

Increase Product Stock

↓

Mark Reservation EXPIRED

↓

COMMIT
```

Again, multiple database operations were grouped into a single transaction.

---

# Observation 3 — Stock Restored

Before cleanup:

```text
Stock = 9
```

After cleanup:

```text
Stock = 10
```

Inventory became available again.

---

# Observation 4 — Reservation History Preserved

Instead of deleting the reservation:

```sql
DELETE FROM inventory_reservations
```

the system updated its status.

```text
RESERVED

↓

EXPIRED
```

This preserves historical information for:

* Auditing
* Customer support
* Reporting
* Analytics
* Fraud investigation

---

# Observation 5 — Independent Transactions

Reservation creation:

```text
BEGIN

↓

Reserve Inventory

↓

COMMIT
```

Several seconds later:

Cleanup:

```text
BEGIN

↓

Release Inventory

↓

COMMIT
```

These are two completely independent database transactions.

---

# Observation 6 — Beginning of Background Processing

The cleanup logic is independent of customer requests.

Conceptually:

```text
Customer Request

↓

Reserve Product

↓

Commit

────────────────────────

Cleanup Process

↓

Release Inventory

↓

Commit
```

The two processes communicate only through the database.

---

# Observation 7 — No Long-Running Transactions

No database transaction remained open during the waiting period.

Instead:

```text
Transaction A

↓

Commit

──────────────

Wait 10 Seconds

──────────────

Transaction B

↓

Commit
```

This is a fundamental principle of scalable production systems.

---

# Architecture Evolution

## Experiment 03

```text
Customer

↓

Reserve Inventory

↓

Reservation Stored
```

---

## Experiment 04

```text
Customer

↓

Reserve Inventory

↓

Reservation Stored

↓

Reservation Expires

↓

Cleanup Service

↓

Inventory Restored
```

The system now supports the complete reservation lifecycle.

---

# Key Learning

This experiment introduced the concept of background processing.

A reservation is created during one request.

Much later, an independent cleanup process restores inventory if payment never arrives.

This architecture is widely used in:

* E-commerce platforms
* Airline reservation systems
* Hotel booking systems
* Ticket booking applications
* Payment processing systems

---

# Preparation for the Next Experiment

In this experiment, the cleanup service was executed manually.

The next experiment will introduce a dedicated background worker that continuously monitors the database and automatically expires reservations without any manual intervention.
