# Project 02 — Inventory Reservation

## Goal

Build an inventory reservation system that prevents overselling when multiple customers attempt to purchase the same product concurrently.

This project demonstrates how production systems such as Amazon, Flipkart, BookMyShow, airline booking systems, and hotel reservation systems protect inventory under heavy concurrent traffic.

---

# Project Structure

```text
02-inventory-reservation/
│
├── app/
│   ├── config.py
│   ├── db.py
│   ├── repository.py
│   ├── service.py
│   └── models.py
│
├── experiments/
│   ├── experiment-01-naive-purchase.py
│   ├── experiment-02-concurrent-buyers.py
│   ├── experiment-03-select-for-update.py
│   ├── experiment-04-reservation-timeout.py
│   ├── experiment-05-high-concurrency.py
│   └── experiment-06-production-pattern.py
│
├── observations/
│
├── question-answer.md
│
└── README.md
```

---

# Problem Statement

Assume the database contains a single product:

```text
Product

ID = 1

Stock = 1
```

Now two customers attempt to purchase it simultaneously.

```text
Customer A

↓

Buy Now

────────────────────

Customer B

↓

Buy Now
```

Question:

> Who should receive the product?

---

# Experiment 01 — Naive Purchase

## Goal

Demonstrate how overselling occurs.

Database:

```text
products

--------------------
id      = 1
name    = iPhone 17
stock   = 1
--------------------
```

Naive implementation:

```python
stock = SELECT stock

if stock > 0:

    stock -= 1

    UPDATE products
```

At first glance this appears correct.

However, it is not safe under concurrent access.

---

# Expected Timeline

```text
Transaction A

SELECT stock

↓

1

────────────────────────────

Transaction B

SELECT stock

↓

1
```

Both transactions read the same value.

Each transaction concludes that inventory is available.

Next:

```text
Transaction A

UPDATE stock = 0

────────────────────────────

Transaction B

UPDATE stock = 0
```

Both purchases succeed even though only one product existed.

This is known as **overselling**.

---

# What This Experiment Teaches

After completing Experiment 01, you will understand:

* Lost Update
* Race Condition
* Overselling
* Why performing `SELECT` followed by `UPDATE` is unsafe under concurrency

---

# We Will Not Fix It Yet

As in the High Concurrency Counter project, we will first:

1. Reproduce the bug.
2. Observe the behavior.
3. Understand why it occurs.
4. Apply the correct production solution.

This approach develops intuition instead of relying on memorized patterns.

---

# Step 1 — Create the Table

Create a minimal table for the experiments.

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    stock INTEGER NOT NULL
);
```

Insert one sample product:

```sql
INSERT INTO products (name, stock)
VALUES ('iPhone 17', 1);
```

---

# Step 2 — Repository Layer

Implement two simple repository methods.

```python
get_stock(db, product_id)

update_stock(db, product_id, stock)
```

Do not introduce any locking mechanisms.

Specifically, do **not** use:

* `SELECT ... FOR UPDATE`
* Explicit row locking
* Reservation logic

The objective is to allow the race condition to occur naturally.

---

# Why This Project Matters

The High Concurrency Counter project answered:

> "How can we safely increment a shared value under concurrency?"

This project answers:

> "How can we prevent selling the same product twice?"

The techniques learned here form the foundation of production inventory systems used by e-commerce platforms, airline reservation systems, hotel booking platforms, ticketing services, and payment workflows.
