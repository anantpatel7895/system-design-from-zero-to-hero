# Experiment 01 — Does `create_engine()` Connect to PostgreSQL?

## Goal

Verify whether calling `create_engine()` immediately establishes a connection to PostgreSQL.

---

## Observation

### Before Running Python

```text
Connections: 10
```

### After Executing `create_engine()`

```text
Connections: 10
```

No new PostgreSQL connection was created.

---

## Conclusion

Calling:

```python
engine = create_engine(DATABASE_URL)
```

does **not** establish a connection to PostgreSQL.

`create_engine()` only creates a SQLAlchemy **Engine** object. The Engine stores the database configuration and knows **how** to create database connections, but it does not create one immediately.

SQLAlchemy follows a **lazy connection** strategy. A database connection is established only when the application executes its first database operation (such as `SELECT`, `INSERT`, `UPDATE`, or `DELETE`) that requires communication with PostgreSQL.

---

## What We Learned

```text
Application Starts
        │
        ▼
create_engine()
        │
        ▼
Engine Object Created
        │
        ▼
No Database Connection
        │
        ▼
No PostgreSQL Backend Process
```

The Engine is simply a factory for creating database connections when they are actually needed.

---

## Key Takeaways

* `create_engine()` does **not** connect to PostgreSQL.
* No TCP connection is established.
* No PostgreSQL backend process is created.
* SQLAlchemy uses **lazy connection acquisition**.
* A database connection is created only when the first SQL statement needs to be executed.
