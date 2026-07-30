# Experiment 02 — SELECT ... FOR UPDATE — Observations

## Objective

Observe how PostgreSQL prevents overselling by locking a row before business logic is executed.

---

# Observation 1

Initial stock:

```text
Stock = 1
```

Only one product was available.

---

# Observation 2

Transaction A executed:

```sql
SELECT stock
FROM products
WHERE id = 1
FOR UPDATE;
```

Observation:

* PostgreSQL immediately acquired a row-level lock.
* Transaction A successfully read:

```text
Current Stock = 1
```

The row remained locked until the transaction committed.

---

# Observation 3

Transaction B executed the same query:

```sql
SELECT stock
FROM products
WHERE id = 1
FOR UPDATE;
```

Observation:

Transaction B did **not** immediately receive the result.

Instead, PostgreSQL blocked the transaction because Transaction A already owned the row lock.

Transaction B waited until Transaction A completed.

---

# Observation 4

Transaction A updated the inventory:

```text
Stock

1

↓

0
```

Then committed.

Observation:

The row lock was released only after the transaction committed.

---

# Observation 5

Immediately after Transaction A committed:

Transaction B resumed automatically.

Transaction B then executed:

```sql
SELECT stock
FROM products
WHERE id = 1
FOR UPDATE;
```

Observation:

The returned value was:

```text
Current Stock = 0
```

Unlike the previous experiment, Transaction B did **not** read stale data.

It observed the latest committed value.

---

# Observation 6

Business logic:

```python
if stock <= 0:
    rollback()
```

Observation:

Transaction B detected that inventory was unavailable.

Output:

```text
Out Of Stock
```

The transaction rolled back without updating the database.

---

# Final Database State

```text
Stock = 0
```

Only one successful purchase occurred.

Inventory remained consistent.

---

# Comparison with Experiment 01

## Experiment 01 (Naive Approach)

```text
Transaction A

Read = 1

────────────────────────

Transaction B

Read = 1
```

Both transactions made decisions using the same stale value.

Result:

```text
Two Successful Purchases

↓

Overselling
```

---

## Experiment 02 (SELECT ... FOR UPDATE)

```text
Transaction A

Lock

↓

Read = 1

↓

Update

↓

Commit

↓

Unlock

────────────────────────

Transaction B

Wait

↓

Read = 0

↓

Out Of Stock
```

Transaction B waited until Transaction A completed.

It made its decision using the latest committed data.

Overselling was prevented.

---

# Key Learning

`SELECT ... FOR UPDATE` does **not** protect the `UPDATE` statement.

The `UPDATE` already acquires a row-level lock.

Instead, `SELECT ... FOR UPDATE` protects the **business decision** made after reading the data.

It guarantees that:

* No other transaction can modify the selected row while the current transaction is processing.
* Business logic always executes using the most recent committed data.
* Concurrent transactions are serialized for the locked rows.

---

# Production Use Cases

`SELECT ... FOR UPDATE` is commonly used in:

* Inventory reservation
* Airline seat booking
* Hotel room reservation
* Movie ticket booking
* Banking and payment systems
* Wallet balance updates
* Order processing

Whenever business decisions depend on the current value of shared data, row-level locking is required to preserve consistency under concurrent access.

---

# Conclusion

This experiment demonstrates that correctness is not achieved by locking the `UPDATE` statement alone.

Correctness is achieved by locking the row **before** making the business decision.

This guarantees that only one transaction at a time can inspect, validate, modify, and commit changes to the shared resource.
