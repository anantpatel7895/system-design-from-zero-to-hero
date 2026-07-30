# Experiment 05 — Background Cleanup Worker — Observations

## Goal

Automate reservation cleanup by introducing a dedicated background worker.

Unlike the previous experiment, cleanup is no longer triggered manually.

---

# What We Improved from Experiment 04

## Experiment 04

Workflow:

```text
Create Reservation

↓

Wait

↓

Manually Execute Cleanup

↓

Inventory Restored
```

### Problem

Cleanup depended on a developer or application manually calling:

```python
ReservationCleanupService().cleanup(db)
```

This is not suitable for production because expired reservations would never be released automatically.

---

## Experiment 05

New workflow:

```text
Background Worker

↓

Wake Up Every 5 Seconds

↓

Check Database

↓

Expire Reservations

↓

Sleep

↓

Repeat Forever
```

Inventory cleanup is now completely automatic.

---

# Observation 1 — Independent Process

The cleanup worker is a completely separate Python application.

```text
cleanup_worker.py
```

It is **not** started by the API.

It runs independently.

---

# Observation 2 — Infinite Loop

The worker continuously executes:

```text
Open Database Session

↓

Cleanup

↓

Close Session

↓

Sleep

↓

Repeat
```

The worker never exits.

It continuously monitors the database.

---

# Observation 3 — Fresh Database Session

Each iteration creates a new database session.

```text
Loop

↓

SessionLocal()

↓

Cleanup

↓

Close Session
```

This prevents problems caused by stale or broken database connections.

Production systems typically avoid holding one database connection forever.

---

# Observation 4 — Automatic Cleanup

When a reservation expires:

```text
Status = RESERVED

↓

expires_at <= NOW()

↓

Cleanup Worker Detects Reservation

↓

Increase Stock

↓

Status = EXPIRED

↓

Commit
```

No manual action is required.

---

# Observation 5 — Communication Through Database

Two completely independent applications communicate only through PostgreSQL.

```text
Reservation API

↓

PostgreSQL

↓

Cleanup Worker
```

Neither process knows the other exists.

The database acts as the communication layer.

---

# Observation 6 — Polling

The worker checks the database every five seconds.

```text
Wake Up

↓

SELECT Expired Reservations

↓

Nothing Found

↓

Sleep
```

This technique is known as **polling**.

Although simple, polling is widely used for periodic maintenance jobs.

---

# Observation 7 — Transaction Per Iteration

Each cleanup iteration executes a new transaction.

```text
BEGIN

↓

Find Expired Reservations

↓

Increase Stock

↓

Mark Reservation EXPIRED

↓

COMMIT
```

The worker never keeps long-running transactions open.

---

# Architecture Evolution

## Experiment 04

```text
Customer

↓

Reserve Product

↓

Manual Cleanup
```

---

## Experiment 05

```text
Customer

↓

Reserve Product

↓

Database

↓

Background Worker

↓

Cleanup
```

The system is now event-driven through shared database state.

---

# Key Learning

This experiment introduced one of the most common production patterns.

Multiple independent applications coordinate by reading and writing shared database state.

Examples include:

* Email sending
* Notification delivery
* Payment reconciliation
* Report generation
* Inventory cleanup
* Video processing

Although the business domains differ, the architectural pattern remains the same.

---

# Preparation for the Next Experiment

The reservation system now supports:

* Safe reservation creation
* Automatic reservation expiration
* Automatic inventory recovery

The next challenge is scalability.

We will simulate hundreds of customers attempting to reserve the same product simultaneously and verify that inventory consistency is maintained under heavy concurrent load.
