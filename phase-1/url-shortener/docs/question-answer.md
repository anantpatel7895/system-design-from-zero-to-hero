# Project 1 — URL Shortener (TinyURL)

## Stage 1 — Questions & Answers

---

## Q1. Why let PostgreSQL generate IDs instead of generating them in Python?

### Answer

Instead of generating IDs in Python, we let PostgreSQL generate them because it guarantees that each ID is unique, even when many requests arrive at the same time.

### Example

Suppose the last ID in the database is:

```text
100
```

Two users send requests simultaneously.

#### Python-generated ID

```text
User A reads last_id = 100
User B reads last_id = 100

User A generates ID = 101
User B generates ID = 101

Both try to insert ID = 101
```

Result:

```text
❌ Duplicate Primary Key Error
```

This problem is called a **Race Condition**.

### PostgreSQL Solution

PostgreSQL uses an internal **Sequence**.

```text
Sequence

100
 ↓
101
 ↓
102
 ↓
103
```

If multiple requests arrive simultaneously:

```text
Request A → 101

Request B → 102

Request C → 103

Request D → 104
```

Every request gets a unique ID automatically.

### Key Takeaway

- Prevents race conditions
- Guarantees unique IDs
- Thread-safe
- Database handles concurrency efficiently

---

## Q2. If the database contains one million rows, how does it efficiently find `id = 999999`?

### Answer

The database does **not** scan every row.

Instead, it uses an **Index** (typically a B-Tree) on the primary key.

### Without Index

```text
1
2
3
4
...
999999
```

The database checks every row until it finds the correct one.

Time Complexity:

```text
O(n)
```

This is called a **Full Table Scan**.

### With Index

Think of a book.

Instead of reading every page, you use the index.

```text
Hash Tables ........ Page 842
Networking ......... Page 102
Operating Systems .. Page 512
```

The database works similarly using a **B-Tree**.

```text
                500000
               /      \
         250000      750000
         /    \      /    \
     ...      ...  ...   999999
```

It follows the tree until it reaches the desired value.

Time Complexity:

```text
O(log n)
```

### Key Takeaway

- Primary keys are automatically indexed.
- Indexed lookups are much faster than scanning the entire table.
- This is why querying by primary key is highly efficient.

---

## Q3. Why don't we store the shortened URL itself in the database yet?

### Answer

The shortened URL is **derived data**, not **canonical data**.

Instead of storing:

| id | short_url |
|----|-----------|
|15|https://tiny.io/15|

We store only:

| id | original_url |
|----|--------------|
|15|https://google.com|

Whenever the API responds, it generates the short URL dynamically.

Example:

```python
short_url = f"http://localhost:8000/{id}"
```

Later, when we introduce Base62 encoding:

```python
short_url = f"https://tiny.io/{base62(id)}"
```

### Why is this better?

Suppose the domain changes.

Old domain:

```text
tiny.io
```

New domain:

```text
tinyurl.com
```

If we stored the complete short URL, we would need to update millions of rows.

If we generate it dynamically, we only change one configuration value.

### Key Takeaway

Store only the **canonical data**.

Generate presentation data when needed.

This avoids:

- Data duplication
- Inconsistent data
- Expensive database updates

---

# Summary

| Question | Answer |
|----------|--------|
| Why does PostgreSQL generate IDs? | Prevents race conditions and guarantees unique IDs. |
| How does PostgreSQL quickly find `id = 999999`? | Uses a B-Tree index on the primary key, resulting in O(log n) lookup time. |
| Why don't we store the shortened URL? | Because it is derived data and can be generated dynamically from the ID and domain. |

---

# Important Concepts Learned

- Race Condition
- Primary Key
- Sequence
- Auto Increment
- Database Index
- B-Tree
- Full Table Scan
- Time Complexity: O(n)
- Time Complexity: O(log n)
- Canonical Data
- Derived Data

## Q4. Why do we use a `.env` file instead of hardcoding configuration values?

### My Answer

A `.env` file allows us to manage different configurations for different environments without changing the application code.

For example:

- Development
- Testing
- Staging
- Production

Each environment can have its own database URL, API keys, and other configuration values.

Example:

Development

```text
DATABASE_URL=postgresql://localhost:5432/url_shortener
```

Production

```text
DATABASE_URL=postgresql://prod-server:5432/url_shortener
```

The application code remains the same; only the configuration changes.

### Benefits

- No hardcoded credentials
- Easy to switch between environments
- More secure
- Easier deployment
- Better maintainability

### Key Takeaway

> Keep configuration separate from application code.

## Q5. Why do we centralize configuration in `config.py` instead of calling `os.getenv()` throughout the project?

### My Answer

Centralizing configuration makes the application easier to maintain and scale.

Instead of calling:

```python
os.getenv("DATABASE_URL")
```

in multiple files, we load the configuration once in `config.py` and import it wherever needed.

Example:

```python
from app.config import settings

settings.database_url
```

### Why is this better?

If we use `os.getenv()` in many files:

- Every file must read environment variables.
- If a configuration name changes, we must update many files.
- It becomes difficult to track configuration usage.

With a centralized configuration:

- Configuration is managed in one place.
- Changes are made only once.
- Type validation is available using Pydantic.
- The code becomes cleaner and easier to test.

### Key Takeaway

> Centralize configuration so the entire application has a single source of truth.

## Q7. What is the SQLAlchemy Engine?

### My Answer

The SQLAlchemy Engine is responsible for managing the connection to the database.

It knows:

- Database host
- Port
- Username
- Password
- Database name
- Database driver

The Engine itself is **not the database** and does not store data. It acts as a connection manager between the application and the database.

```text
Application
      │
      ▼
SQLAlchemy Engine
      │
      ▼
PostgreSQL
```

### Key Takeaway

The Engine knows **how to connect** to the database but does not represent a database session.

## Q8. Why do we need a Session instead of using the Engine directly?

### My Answer

The Engine is shared across the entire application, while a Session represents a single conversation (or transaction) with the database.

Every incoming HTTP request should have its own Session.

```text
Request A
    │
 Session A
    │
PostgreSQL

Request B
    │
 Session B
    │
PostgreSQL
```

If multiple requests shared the same Session, transactions could interfere with each other, causing data inconsistencies.

FastAPI creates a new Session for each request and closes it when the request is complete.

### Key Takeaway

- Engine → Shared connection manager
- Session → Per-request unit of work

## Q9. What is the purpose of `Base`?

### My Answer

`Base` is the parent class for all SQLAlchemy ORM models.

When a model inherits from `Base`, SQLAlchemy knows that the class should be mapped to a database table.

Example:

```python
class URL(Base):
    __tablename__ = "urls"
```

Without inheriting from `Base`, SQLAlchemy will treat it as a normal Python class and will not create or map a database table.

### Key Takeaway

`Base` tells SQLAlchemy:

> "This class represents a database table."

## Q10. Why does FastAPI use `Depends(get_db)`?

### My Answer

`Depends()` is FastAPI's Dependency Injection mechanism.

Instead of manually creating and closing a database Session in every endpoint, FastAPI automatically injects a Session by calling `get_db()`.

```python
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    ...
```

The request lifecycle becomes:

```text
HTTP Request
      │
      ▼
Create Session
      │
      ▼
Execute Endpoint
      │
      ▼
Close Session
```

Even if an exception occurs, FastAPI ensures the Session is properly closed.

### Benefits

- Automatic resource management
- Cleaner endpoint code
- Prevents database connection leaks
- Easy to test by injecting different dependencies

### Key Takeaway

`Depends(get_db)` uses Dependency Injection to provide a database Session for each request and automatically cleans it up afterwards.

## Q11. What is `__tablename__`?

`__tablename__` specifies the name of the database table that the SQLAlchemy ORM model maps to.

Example:

```python
class URL(Base):
    __tablename__ = "urls"
```

This tells SQLAlchemy that the `URL` Python class corresponds to the `urls` table in PostgreSQL.

### Key Takeaway

`__tablename__` defines the mapping between a Python class and a database table.

## Q12. What is `mapped_column()`?

`mapped_column()` defines a database column and its properties.

It tells SQLAlchemy:

- Column name
- Data type
- Primary key
- Nullable
- Default value
- Index
- Unique constraint
- Foreign key (if applicable)

Example:

```python
name = mapped_column(String, nullable=False)
```

### Key Takeaway

`mapped_column()` maps a Python attribute to a database column and defines how that column should behave.

---

## Q13. Why do we use `server_default=func.now()` instead of `datetime.now()`?

### My Answer

We use `server_default=func.now()` so that the database generates the timestamp instead of the application.

The database is the **source of truth** for persisted data.

If multiple application servers are running in different locations or have slightly different system clocks, using the database ensures that all timestamps are generated consistently.

### Example

**Application-generated timestamp**

```python
created_at = datetime.now()
```

Problems:

- Different application servers may have different clocks.
- Time synchronization issues can occur.
- The application becomes responsible for generating timestamps.

**Database-generated timestamp**

```python
created_at = mapped_column(
    DateTime(timezone=True),
    server_default=func.now()
)
```

The generated SQL is similar to:

```sql
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

Here, PostgreSQL automatically assigns the timestamp when the row is inserted.

### Benefits

- Database is the source of truth.
- Consistent timestamps across all application servers.
- No dependency on application server clocks.
- Simpler application code.

### Key Takeaway

> Let the database generate values that belong to the database, such as creation timestamps.

___

## Q14. Why do we store timestamps with time zones?

We store timestamps with time zones so that the exact moment an event occurred can be understood consistently across different countries and servers.

Without a time zone, the same timestamp can be interpreted differently depending on the server's local time.

Using timezone-aware timestamps prevents ambiguity and makes distributed systems more reliable.

### Example

Without timezone:

```text
2026-06-29 10:00
```

Where?

- India?
- USA?
- Germany?

Impossible to know.

With timezone:

```text
2026-06-29T10:00:00+05:30
```

or

```text
2026-06-29T04:30:00Z
```

Now every system understands the exact same point in time.

### Key Takeaway

Always store timezone-aware timestamps in distributed systems.

---

## Q15. Why do we need to import our models before calling `Base.metadata.create_all()`?

SQLAlchemy can only create tables for models that have been imported into the application.

Importing the models registers them with `Base.metadata`.

If a model is not imported, SQLAlchemy does not know it exists, so no table will be created for it.

### Key Takeaway

Importing a model registers it with SQLAlchemy's metadata so it can participate in table creation.

---

## Q16. What does `Base.metadata.create_all()` do?

`Base.metadata.create_all()` examines all registered ORM models, generates the corresponding SQL `CREATE TABLE` statements, and executes them against the database.

Before creating a table, SQLAlchemy checks whether it already exists.

If the table exists, it skips it.

If the table does not exist, it creates it.

### Key Takeaway

`create_all()` creates only missing tables; it does not modify existing ones.

---

## Q17. Why isn't `create_all()` used in production for schema changes?

`create_all()` can create new tables, but it cannot modify existing database schemas.

For example, it cannot:

- Add new columns
- Remove columns
- Rename columns
- Change data types
- Create migration history

Production systems use migration tools like **Alembic** to safely evolve the database schema over time.

### Key Takeaway

`create_all()` is suitable for development and initial table creation, while production systems use migrations to manage schema changes.

---

## Q18. Why do we use the Repository Pattern?

### My Answer

The Repository Pattern separates database operations from business logic.

Instead of writing SQLAlchemy queries throughout the application, all database operations are centralized in the repository layer.

### Benefits

* Easy to switch databases (e.g., PostgreSQL to MongoDB)
* Keeps business logic independent of database implementation
* Easier to test using mock repositories
* Better code organization and maintainability

### Architecture

```text
API
 │
 ▼
Service
 │
 ▼
Repository
 │
 ▼
Database
```

### Key Takeaway

The Repository Pattern makes the application easier to maintain, test, and evolve by separating persistence logic from business logic.

---

## Q19. What does `db.add()` do?

### My Answer

`db.add()` registers a Python object with the current SQLAlchemy Session.

It does **not** execute an SQL `INSERT` statement.

Instead, it marks the object as **pending**.

```text
Python Object
      │
      ▼
db.add()
      │
      ▼
Session (Pending State)
```

The actual SQL statement is generated when `db.commit()` (or sometimes `db.flush()`) is called.

### Key Takeaway

`db.add()` tells SQLAlchemy to track the object, but it does not save it to the database.

---

## Q20. What does `db.commit()` do?

### My Answer

`db.commit()` commits the current transaction.

When called, SQLAlchemy **generates** the necessary **SQL statements** (such as `INSERT`, `UPDATE`, or `DELETE`) based on the tracked objects in the Session and sends them to the database.

If the database successfully executes the transaction, the changes become permanent.

```text
Python Object
      │
      ▼
Session
      │
      ▼
Generate SQL
      │
      ▼
PostgreSQL
      │
      ▼
Data Saved
```

### Key Takeaway

`db.commit()` persists all pending changes in the Session to the database.

---

## Q21. Why do we call `db.refresh()` after `commit()`?

### My Answer

After `db.commit()`, PostgreSQL may have generated values such as:

* Primary key (`id`)
* Default timestamps (`created_at`)
* Trigger-generated values

The Python object does not automatically know about these database-generated values.

`db.refresh()` reloads the object from the database so it contains the latest values.

Example:

Before commit:

```python
url.id
```

Output:

```text
None
```

After:

```python
db.commit()
db.refresh(url)
```

Output:

```text
15
```

### Key Takeaway

`db.refresh()` synchronizes the Python object with the latest state stored in the database.

---

## Q22. Why do we need a Service Layer?

### My Answer

The Service Layer contains the application's business logic.

It separates business rules from both the API layer and the database layer.

Instead of placing business logic inside API endpoints or repositories, the Service Layer coordinates the application's workflow.

### Responsibilities

* Business rules
* Validation
* Workflow coordination
* Calling repositories
* Calling external services
* Managing transactions (when needed)

### Key Takeaway

The Service Layer is responsible for **how the application behaves**, not **how data is stored** or **how HTTP requests are handled**.

---

## Q23. What is the responsibility of the Repository-layer?

### My Answer

The Repository is responsible for all database interactions.

It contains CRUD operations and SQLAlchemy queries but does **not** contain business logic.

### Responsibilities

* Create records
* Read records
* Update records
* Delete records
* Execute database queries

### Example

```text
Service
    │
    ▼
Repository
    │
    ▼
PostgreSQL
```

### Key Takeaway

The Repository knows **how to talk to the database**, but it does not decide **when** or **why** an operation should occur.

---

## Q24. What is the responsibility of the Service-layer?

### My Answer

The Service Layer coordinates the application's business workflow.

It communicates with repositories and, when required, other services such as Redis, Kafka, email providers, payment gateways, or external APIs.

The Service decides **what should happen**, while repositories perform the actual database operations.

### Example

```text
Validate URL
      │
      ▼
Check Duplicate
      │
      ▼
Generate Short Code
      │
      ▼
Repository → Save to Database
      │
      ▼
Publish Kafka Event
      │
      ▼
Update Redis Cache
```

### Key Takeaway

The Service Layer orchestrates multiple operations to implement business requirements.

---

## Q25. Why shouldn't business logic be placed in the API layer?

### My Answer

The API Layer should only be responsible for **handling HTTP communication**.

Its responsibilities include:

* Receiving HTTP requests
* Validating request data
* Calling the appropriate Service
* Returning HTTP responses

If business logic is placed in the API layer:

* Endpoints become large and difficult to maintain.
* Business logic gets duplicated across multiple endpoints.
* Testing becomes harder because business logic is tightly coupled to HTTP.

### Architecture

```text
HTTP Request
      │
      ▼
API Layer
      │
      ▼
Service Layer
      │
      ▼
Repository-Layer
      │
      ▼
Database
```

### Key Takeaway

The API Layer handles **communication**, while the Service Layer handles **business logic**.

---

## Q26. Why do we need Pydantic Schemas if we already have SQLAlchemy Models?

### My Answer

Pydantic Schemas and SQLAlchemy Models serve different purposes.

### Pydantic Schema

Works between the **HTTP layer** and the **application**.

Responsibilities:

* Request validation
* Response serialization
* Data type conversion
* API contract

```text
HTTP Request
      │
      ▼
Pydantic Schema
```

### SQLAlchemy Model

Works between the **application** and the **database**.

Responsibilities:

* Table mapping
* ORM
* Database persistence

```text
Python Object
      │
      ▼
SQLAlchemy Model
      │
      ▼
Database
```

### Key Takeaway

Pydantic validates API data, while SQLAlchemy manages database persistence.

---

## Q27. Why shouldn't we expose ORM models directly through APIs?

### My Answer

ORM models represent the database schema, while API responses represent the public contract of the application.

Exposing ORM models directly tightly couples the API to the database.

Problems:

* Database changes can break API clients.
* Internal fields may be exposed accidentally.
* Different clients may require different response formats.
* Security-sensitive fields could leak.

Example:

Database table:

```text
id
original_url
created_at
internal_notes
deleted_at
```

API Response:

```json
{
    "id": 1,
    "short_url": "http://localhost:8000/1"
}
```

The client only receives the fields it needs.

### Key Takeaway

Always expose API Schemas, never database models directly.

---

## Q28. Why do we use `HttpUrl` instead of `str`?

### My Answer

`HttpUrl` automatically validates that the input is a valid HTTP or HTTPS URL.

If the input is invalid, FastAPI returns a validation error before the request reaches the Service Layer.

Example:

Input:

```json
{
    "url": "abc"
}
```

Response:

```http
422 Unprocessable Entity
```

The Service Layer and Repository are never executed.

### Benefits

* Automatic validation
* Prevents invalid data from reaching business logic
* Saves processing time and database resources

### Key Takeaway

Validate input as early as possible.

---

## Q29. Why does the Repository return a Python object instead of JSON?

### My Answer

The Repository is part of the application's persistence layer, not the HTTP layer.

Its responsibility is to interact with the database and return Python objects representing the retrieved or persisted data.

The Repository has no knowledge of:

* HTTP
* JSON
* REST APIs
* Clients

Returning Python objects allows the same Repository to be reused by:

* REST APIs
* Background workers
* Scheduled jobs
* CLI applications
* Unit tests

The API Layer is responsible for converting Python objects into JSON responses.

### Architecture

```text
Repository
      │
      ▼
Python Object
      │
      ▼
Service
      │
      ▼
API Layer
      │
      ▼
JSON Response
```

### Key Takeaway

Repositories work with Python objects; API layers work with HTTP and JSON.

---

## Q30. What is Base62 encoding?

### My Answer

Base62 is an encoding algorithm that converts an integer into a string using **62 different characters**.

The character set consists of:

* 10 digits (`0-9`)
* 26 uppercase letters (`A-Z`)
* 26 lowercase letters (`a-z`)

Total:

```text
10 + 26 + 26 = 62 characters
```

The algorithm repeatedly divides the number by **62**, stores the remainder, and maps each remainder to a character in the Base62 alphabet.

Example:

```text
125

125 ÷ 62 = 2 remainder 1
2 ÷ 62 = 0 remainder 2

Collected remainders:
1, 2

Reverse:
2, 1

Encoded Result:
21
```

### Key Takeaway

Base62 converts numeric IDs into shorter, URL-friendly strings.

---

## Q31. Why do URL shorteners prefer Base62 instead of decimal IDs?

### My Answer

URL shorteners use Base62 because it creates shorter and less predictable URLs than plain decimal IDs.

### Advantages

#### 1. Shorter URLs

Example:

```text
Decimal:
999999999

Base62:
15ftgF
```

Base62 produces much shorter URLs.

#### 2. Reduces Enumeration

Sequential decimal IDs make it easy for users to guess other URLs.

Example:

```text
/100
/101
/102
```

A user can easily enumerate URLs.

Base62 makes the URL less obvious to users, although it is **not** a security mechanism by itself.

### Key Takeaway

Base62 creates compact, URL-friendly identifiers while making sequential IDs less obvious.

---

## Q32. Why do we reverse the characters during Base62 encoding?

### My Answer

When converting a number to Base62, repeated division produces digits from the **least significant digit** to the **most significant digit**.

Example:

```text
125

↓

Remainders:
1
2
```

Humans read numbers from the most significant digit to the least significant digit.

Therefore, we reverse the collected characters before returning the encoded string.

### Key Takeaway

The remainder operation generates digits in reverse order, so we reverse them to obtain the correct Base62 representation.

---

## Q33. Why don't we store the Base62 value in the database?

### My Answer

The Base62 value is **derived data**, while the database ID is the **source of truth**.

Instead of storing both:

| id  | short_code |
| --- | ---------- |
| 125 | 21         |

we store only:

| id  |
| --- |
| 125 |

Whenever needed, we generate the Base62 value from the ID.

### Why is this better?

* Avoids storing duplicate information.
* Keeps the database normalized.
* If the encoding algorithm changes, there is no need to update millions of database rows.
* The short code can always be regenerated from the ID.

### Key Takeaway

Store only the source of truth (`id`) and derive the Base62 short code when needed.

---

## Q34. Why do we store only the source of truth and compute derived values when needed?

The primary reason is to maintain **data consistency**.

If both the original data and its derived value are stored, they can become inconsistent when one is updated but the other is not.

Example:

Instead of storing:

| id  | short_code |
| --- | ---------- |
| 125 | 21         |

we store only:

| id  |
| --- |
| 125 |

Whenever needed, the application computes:

```text
125
   │
   ▼
Base62 Encoding
   │
   ▼
21
```

### Benefits

* Single source of truth
* No duplicate data
* Avoids synchronization problems
* Easier maintenance
* Computing simple derived values is usually inexpensive

### Key Takeaway

> Store the minimum required data and derive everything else whenever it is inexpensive and deterministic to compute.

---

## Q34. Why do URL shorteners use HTTP redirects instead of returning JSON?

### My Answer

HTTP already provides a built-in mechanism for redirection using redirect status codes (such as 302 or 301).

When the server returns a redirect response with a `Location` header, browsers and HTTP clients automatically make a new request to the destination URL.

Example:

```http
GET /aBc91K

↓

HTTP/1.1 302 Found
Location: https://google.com
```

The browser automatically navigates to `https://google.com`.

### Why not return JSON?

If the server returned:

```json
{
    "url": "https://google.com"
}
```

every client would have to manually parse the JSON and perform another request.

### Key Takeaway

HTTP redirects provide a standard, automatic, and client-independent way to navigate to another URL.

---

## Q35. What is the purpose of `RedirectResponse`?

### My Answer

`RedirectResponse` is a FastAPI response class that creates an HTTP redirect response.

Instead of returning JSON, it returns:

* An HTTP redirect status code (302, 307, etc.)
* A `Location` header containing the destination URL

Example:

```python
return RedirectResponse(
    url="https://google.com",
    status_code=302
)
```

FastAPI generates a response similar to:

```http
HTTP/1.1 302 Found
Location: https://google.com
```

The browser automatically follows the redirect.

### Key Takeaway

`RedirectResponse` converts a Python return value into a valid HTTP redirect response.

---

## Q36. Why does the Repository return `None` instead of raising an exception when a row is not found?

### My Answer

A missing row is a normal business scenario, not an exceptional database error.

For example, a user may request a short URL that does not exist.

The Repository simply returns `None` to indicate that no matching row was found.

The Service or API Layer then decides how to handle that situation.

For example:

```python
url = repository.get_by_id(...)

if url is None:
    raise HTTPException(status_code=404)
```

### Key Takeaway

The Repository retrieves data. The Service and API decide what the absence of data means.

---

## Q37. Why is the HTTP response created in the API layer instead of the Repository?

### My Answer

The Repository is responsible only for database operations.

It should not know anything about:

* HTTP
* REST
* JSON
* Status codes
* Redirects

The API Layer is responsible for converting application results into HTTP responses.

Example:

```text
Repository
      │
      ▼
Python Object
      │
      ▼
API Layer
      │
      ▼
HTTP Response
```

### Key Takeaway
>Each layer should only be responsible for its own domain.

---

## Q38. What is `db.flush()` in SQLAlchemy?

### My Answer

`db.flush()` sends all pending SQL statements (such as `INSERT`, `UPDATE`, or `DELETE`) to the database without committing the current transaction.

Unlike `db.commit()`, the changes are **not permanently saved** and can still be rolled back.

### Example

```python
url = URL(original_url="https://google.com")

db.add(url)

db.flush()

print(url.id)
```

Output:

```text
125
```

The database has generated the primary key, but the transaction is still open.

### Key Takeaway

`db.flush()` synchronizes the SQLAlchemy Session with the database while keeping the transaction uncommitted.

> flush() makes SQL visible inside the current transaction, while commit() makes it visible to everyone.

---

## Q39. What is the difference between `flush()`, `commit()`, and `refresh()`?

### My Answer

Although all three interact with the database, they serve different purposes.

### `flush()`

* Sends pending SQL statements to the database.
* Does **not** commit the transaction.
* Database-generated values (such as auto-increment IDs) become available.
* Changes can still be rolled back.

### `commit()`

* Commits the current transaction.
* Makes all changes permanent.
* After a successful commit, other database connections can see the changes.

### `refresh()`

* Reloads the object's latest state from the database.
* Useful for retrieving database-generated values or changes made by triggers.

### Summary

| Method      | Sends SQL | Makes Permanent | Reloads Object |
| ----------- | --------- | --------------- | -------------- |
| `flush()`   | ✅         | ❌               | ❌              |
| `commit()`  | ✅         | ✅               | ❌              |
| `refresh()` | ❌         | ❌               | ✅              |

### Key Takeaway

* `flush()` synchronizes the Session with the database.
* `commit()` permanently saves the transaction.
* `refresh()` synchronizes the Python object with the database.

---

## Q40. Why do we use `flush()` when generating `short_code`?

### My Answer

The `short_code` is generated from the database-generated primary key (`id`).

Before calling `flush()`, the `id` is not available because the `INSERT` statement has not yet been executed.

Workflow:

```text
Create URL Object
        │
        ▼
db.add()
        │
        ▼
db.flush()
        │
        ▼
Database generates id
        │
        ▼
Generate short_code = Base62(id)
        │
        ▼
Update URL object
        │
        ▼
db.commit()
```

This allows both the `INSERT` and the `UPDATE` to be committed together in a **single transaction**.

### Why not use two commits?

Using two commits creates the risk of partial updates.

Example:

```text
INSERT
    │
    ▼
COMMIT
    │
    ▼
💥 Application crashes
    │
    ▼
UPDATE never happens
```

The database would contain an incomplete record.

Using `flush()` avoids this problem because the entire operation is committed only once.

### Key Takeaway

`flush()` allows us to obtain the generated ID without committing the transaction, enabling atomic multi-step operations.

---

## Q41. Why does the database not contain the row after `flush()` if the application crashes before `commit()`?

### My Answer

`db.flush()` sends pending SQL statements to the database, but the transaction is still open.

If the application crashes before `db.commit()`, PostgreSQL automatically rolls back the transaction.

As a result, none of the changes become permanent.

### Flow

```text
db.add()
    │
    ▼
db.flush()
    │
    ▼
INSERT executed
    │
    ▼
Transaction still open
    │
    ▼
Application crashes
    │
    ▼
ROLLBACK
    │
    ▼
No row exists in the database
```

### Key Takeaway

Changes made by `flush()` remain part of the current transaction until `commit()` is called. If the transaction is rolled back, all flushed changes are discarded.

---

## Q43. Why don't we call `db.add()` again after modifying the object?

### My Answer

Once an object is added to the SQLAlchemy Session using `db.add()`, it enters the **persistent state**.

SQLAlchemy continues to track the object for any changes.

When an attribute is modified:

```python
url.short_code = encode(url.id)
```

SQLAlchemy automatically marks the object as **dirty**.

During `db.commit()`, SQLAlchemy detects the changes and generates the appropriate `UPDATE` statement.

### Key Takeaway

A persistent object only needs to be added to the Session once. After that, SQLAlchemy automatically tracks modifications.

---

## Q44. How does SQLAlchemy know it needs to execute an `UPDATE` statement?

### My Answer

SQLAlchemy uses a mechanism called **Dirty Checking**.

While an object is attached to the Session, SQLAlchemy monitors its attributes.

If any tracked attribute changes before the transaction is committed, SQLAlchemy automatically generates an `UPDATE` statement.

Example:

```python
url.short_code = "21"
```

Results in SQL similar to:

```sql
UPDATE urls
SET short_code = '21'
WHERE id = 125;
```

The developer never writes the SQL manually.

### Key Takeaway

Dirty Checking allows SQLAlchemy to synchronize modified Python objects with the database automatically.

---

## Q45. How many SQL statements are executed during the `flush()` + `commit()` workflow?

### My Answer

In the URL Shortener workflow, SQLAlchemy executes two SQL statements:

1. **INSERT**

```python
db.add(url)
db.flush()
```

This inserts the row into PostgreSQL and retrieves the generated primary key.

2. **UPDATE**

```python
url.short_code = encode(url.id)
db.commit()
```

Since the object was modified after `flush()`, SQLAlchemy detects the change and generates an `UPDATE` statement before committing the transaction.

Finally, PostgreSQL executes:

```sql
COMMIT;
```

to permanently save the transaction.

### Flow

```text
db.add()
    │
    ▼
INSERT
    │
    ▼
db.flush()
    │
    ▼
Generate short_code
    │
    ▼
UPDATE
    │
    ▼
COMMIT
```

### Key Takeaway

`flush()` executes the initial `INSERT`, while `commit()` persists the transaction and any additional SQL statements generated by SQLAlchemy's dirty checking.

## Q46. Why can't a Python `threading.Lock` prevent duplicate requests across multiple application servers?

### My Answer

A `threading.Lock` only synchronizes threads within a single Python process.

In a distributed system, each application server runs in its own process and has its own memory space.

Example:

```text
Load Balancer
      │
 ┌────┴────┐
 ▼         ▼
Server A   Server B
Lock A     Lock B
```

`Lock A` cannot communicate with or block `Lock B`.

Therefore, an in-memory lock cannot prevent duplicate operations across multiple servers.

To coordinate multiple servers, distributed locking mechanisms (such as Redis or ZooKeeper) or database constraints must be used.

### Key Takeaway

A `threading.Lock` protects only a single process. It does not provide synchronization across multiple application servers.

---

## Q47. What is database isolation?

### My Answer

Isolation is one of the ACID properties of a database transaction.

> It defines how much one transaction can see of another transaction's changes before they are committed.

Higher isolation provides stronger consistency but usually reduces concurrency.

Lower isolation improves concurrency but may allow certain anomalies.

### Key Takeaway

Isolation controls the visibility of changes between concurrent transactions.

---

## Q48. What is PostgreSQL's default isolation level?

### My Answer

PostgreSQL's default isolation level is **READ COMMITTED**.

Under this level, every SQL statement can only see data that has already been committed before that statement begins.

Uncommitted changes made by other transactions are never visible.

### Key Takeaway

READ COMMITTED prevents dirty reads while maintaining good concurrency and performance for most applications.

---

## Q49. Why can two transactions/session both read "No Row Found" under PostgreSQL's READ COMMITTED isolation level?

### My Answer

Under the **READ COMMITTED** isolation level, a transaction can only see data that has already been committed.

If Transaction A inserts a row but has not yet committed, Transaction B cannot see that row.

Example:

```text
Transaction A

BEGIN
    │
    ▼
INSERT
    │
    ▼
(No COMMIT yet)

──────────────────────────

Transaction B

BEGIN
    │
    ▼
SELECT
    │
    ▼
No Row Found
```

Both transactions may conclude that the row does not exist and attempt to insert it.

This creates a race condition.

The database `UNIQUE` constraint is the final mechanism that prevents duplicate rows.

### Key Takeaway

READ COMMITTED prevents reading uncommitted data, but it does **not** prevent two concurrent transactions from making the same decision based on the current committed state.

---

## Q50. Why don't we make `original_url` unique in the database?

### My Answer

Whether `original_url` should be unique is a business decision, not a technical one.

If the application should always return the same short URL for a given original URL, then a `UNIQUE` constraint is appropriate.

However, many production URL shorteners allow multiple short codes (or custom aliases) to point to the same original URL.

Example:

```text
https://openai.com

↓

/openai

↓

/chatgpt

↓

/ai
```

In this design, `original_url` must **not** be unique.

Instead, `short_code` is the unique identifier.

### Key Takeaway

Database constraints should reflect business requirements, not implementation convenience.

---

## Q51. Why is `db.refresh()` not required after `db.flush()` in our `create()` method?

### My Answer

`db.flush()` executes the pending `INSERT` statement and retrieves the database-generated primary key (`id`).

After `flush()`, the SQLAlchemy object already contains:

* `id`
* `original_url`
* `short_code` (assigned by the application)

Since no additional database-generated values are required, calling `db.refresh()` is unnecessary.

`db.refresh()` is only needed when we want to reload the latest state of the object from the database.

### Key Takeaway

Use `db.refresh()` only when the application needs values that are generated or modified by the database after the SQL statement executes. In our workflow, `flush()` already provides the generated `id`, so `refresh()` adds no value.

---

## Q52. Why should Base62 encoding be implemented in the Service Layer instead of the Repository Layer?

### My Answer

Base62 encoding is a business rule used to generate a user-facing `short_code`.

The Repository Layer is responsible only for persistence concerns such as database operations, transactions, and CRUD.

If the encoding algorithm changes in the future (for example, from Base62 to NanoID or UUID), only the Service Layer should change.

The Repository should remain unchanged because it should not know how a `short_code` is generated.

### Layer Responsibilities

```text
API Layer
    ↓
HTTP, Validation, Response

Service Layer
    ↓
Business Logic
Workflow
Base62 Encoding

Repository Layer
    ↓
Database
SQL
Transactions
CRUD
```

### Key Takeaway

Business rules belong in the Service Layer. The Repository Layer should focus only on interacting with the database.

---

## Q53. Why should the Service create the `URL` entity instead of the Repository?

### My Answer

Creating a `URL` entity is part of the application's business workflow, so it belongs in the Service Layer.

The Repository's responsibility is only to persist and retrieve entities from the database.

By creating the entity in the Service Layer:

* Business rules remain centralized.
* The Repository stays focused on persistence.
* The same Repository can be reused by different entry points (REST APIs, background jobs, Kafka consumers, CLI tools, etc.).

### Layer Responsibilities

```text
API Layer
    ↓
HTTP, Validation, Response

Service Layer
    ↓
Create Domain Entity
Business Rules
Workflow

Repository Layer
    ↓
Persist Entity
Retrieve Entity
Transactions
```

### Key Takeaway

Repositories should persist domain entities, not construct them. Entity creation belongs in the Service Layer because it is part of the business workflow.

---

## Q54. Why can duplicate URLs still be created even after checking `get_by_original_url()`?

### My Answer

Duplicate URLs can still be created because of **concurrent transactions**.

Consider two requests arriving at nearly the same time:

```text
Request A                     Request B
-------------------------------------------------
BEGIN                         BEGIN

SELECT original_url           SELECT original_url
No row found                  No row found

INSERT                        INSERT

COMMIT                        COMMIT
```

Both transactions execute the `SELECT` query before either transaction commits its `INSERT`.

Under PostgreSQL's default **READ COMMITTED** isolation level, a transaction can only see data that has already been committed. Since neither transaction has committed yet, both transactions believe that the URL does not exist.

As a result, both proceed with the `INSERT`, creating duplicate rows.

### Why does READ COMMITTED allow this?

`READ COMMITTED` only exposes committed data to other transactions.

```
Transaction A
--------------
INSERT
(Not Committed)

↓

Transaction B
--------------
SELECT

↓

Cannot see Transaction A's row
```

Therefore, Transaction B incorrectly concludes that the URL does not exist.

### Key Takeaway

Checking for an existing row before inserting is **not sufficient** in a concurrent system.

To prevent duplicates, the application must rely on proper concurrency control mechanisms such as:

* Database `UNIQUE` constraints
* Higher isolation levels (when appropriate)
* Row-level locking
* Optimistic or pessimistic locking
* Other synchronization strategies depending on the system requirements

This problem is a classic example of a **race condition** caused by concurrent transactions.

---

## Q55. Why should the Repository call `db.rollback()` if `db.commit()` fails?

### My Answer

If `db.commit()` fails, the current transaction is aborted and the SQLAlchemy `Session` enters a failed state.

In this state, the `Session` cannot execute any further database operations until `db.rollback()` is called.

Calling `db.rollback()`:

* Aborts the failed transaction.
* Restores the `Session` to a clean and usable state.
* Releases any database resources associated with the failed transaction.
* Allows the exception to be propagated while ensuring the `Session` is not left in an inconsistent state.

After performing the rollback, the Repository should re-raise the exception so that higher layers (such as the Service or API) can decide how to handle or report the error.

### Key Takeaway

A failed transaction leaves the SQLAlchemy `Session` unusable. Calling `db.rollback()` resets the `Session` so it can safely execute future database operations.

---

## Q61. What is the difference between `raise` and `raise e` in Python?

### My Answer

Both `raise` and `raise e` propagate an exception, but they handle the traceback differently.

### `raise`

```python
except Exception:
    db.rollback()
    raise
```

* Re-raises the original exception.
* Preserves the original traceback.
* Makes debugging easier because the traceback points to the actual source of the error.
* This is the recommended approach when you only want to perform cleanup (such as `rollback()`) before propagating the exception.

### `raise e`

```python
except Exception as e:
    db.rollback()
    raise e
```

* Raises the exception object again from the current location.
* Alters the traceback by making it appear as though the exception originated from the `raise e` statement.
* This can make debugging more difficult and is generally not recommended for simple exception propagation.

### Key Takeaway

Use `raise` when you want to propagate the original exception after performing cleanup. It preserves the original traceback and provides more accurate debugging information.

--- 

## Q62. Why does updating `click_count` become a bottleneck for a popular URL?

### My Answer

When a popular URL receives thousands of requests per second, every request executes:

```sql
UPDATE urls
SET click_count = click_count + 1
WHERE id = ?;
```

All of these transactions attempt to update the **same database row**.

PostgreSQL protects data consistency by acquiring a **row-level lock** before updating the row. Since only one transaction can modify the row at a time, all other transactions must wait until the lock is released.

As the request rate increases, more transactions wait for the same row-level lock, causing lock contention and increased latency.

Instead of processing updates in parallel, PostgreSQL serializes them, making the database the bottleneck.

### Key Takeaway

The bottleneck is **not simply the number of concurrent requests**. It is the fact that thousands of concurrent transactions compete for the **same row-level lock**, forcing PostgreSQL to process the updates one after another.

---

## Q63. Why is querying by `short_code` a better long-term design than decoding it to an `id`?

### My Answer

Querying by `short_code` is more flexible and future-proof than decoding it back to an `id`.

Today, the application generates `short_code` using Base62 encoding, so decoding is possible.

However, in the future the application may support:

* Custom aliases (e.g., `chatgpt`)
* Random strings (e.g., NanoID)
* UUID-based short codes
* Other encoding algorithms

These values cannot be decoded into a numeric `id`.

By querying directly using:

```python
repository.get_by_short_code(db, short_code)
```

the redirect logic becomes independent of how the `short_code` was generated.

### Additional Benefit

Removing the decoding step also eliminates a small amount of unnecessary computation, but this performance gain is negligible compared to the database query. The primary benefit is improved flexibility and maintainability.

### Key Takeaway

Design the system around stable interfaces rather than a specific implementation. By treating `short_code` as an opaque identifier instead of assuming it is Base62-encoded, the application can support new short code generation strategies without changing the redirect workflow.

---

## Q64. Which HTTP status code should be returned if a custom alias already exists?

### My Answer

The correct response is **409 Conflict**.

The request itself is valid:

* The JSON is well-formed.
* The URL is valid.
* The custom alias is syntactically valid.

However, the requested alias already exists in the system, creating a conflict with the current state of the resource.

Therefore, the server should reject the request with:

```http
HTTP/1.1 409 Conflict
```

Example response:

```json
{
    "detail": "Custom alias 'chatgpt' already exists."
}
```

### Why not other status codes?

* **400 Bad Request** → The request is malformed or contains invalid data.
* **404 Not Found** → The requested resource does not exist.
* **200 OK** → The operation completed successfully.

None of these accurately describe a duplicate custom alias.

### Key Takeaway

Use **409 Conflict** when a valid request cannot be completed because it conflicts with the current state of the server.

---

## Q65. Should `AliasAlreadyExistsError` contain the alias?

### My Answer

Yes.

The exception should contain the alias because it provides useful context about why the operation failed.

Instead of raising:

```python
raise AliasAlreadyExistsError()
```

it is better to raise:

```python
raise AliasAlreadyExistsError(request.custom_alias)
```

This allows higher layers (such as the API layer) to generate meaningful error messages without performing additional database queries.

Example:

```json
{
    "detail": "Custom alias 'chatgpt' already exists."
}
```

It also improves application logging and debugging because the logs contain the exact alias that caused the conflict.

### Key Takeaway

Exceptions should carry relevant contextual information so that higher layers can handle, log, and report errors more effectively without repeating work.

---

## Q66. Why do we return `JSONResponse` instead of raising `HTTPException` inside an exception handler?

### My Answer

An exception handler is responsible for **handling** an exception, not raising another one.

When an exception reaches the handler, it has already been caught by FastAPI. The framework expects the handler to convert that exception into an HTTP response.

Therefore, the handler should return a `JSONResponse` with the appropriate status code and response body.

```python
return JSONResponse(
    status_code=status.HTTP_409_CONFLICT,
    content={
        "detail": str(exc),
    },
)
```

Raising another `HTTPException` inside the exception handler is unnecessary because the exception has already been handled.

### Request Flow

```text
Service
    │
    ▼
raise AliasAlreadyExistsError()
    │
    ▼
FastAPI Exception Handler
    │
    ▼
Return JSONResponse
    │
    ▼
Client
```

### Key Takeaway

* **Raise an exception** when an error occurs.
* **Handle an exception** by converting it into an appropriate HTTP response.

The exception handler is the final step before the response is sent back to the client.

---

## Q67. In which layer should we log "Created short URL 'google'"?

### My Answer

This log belongs in the **Service Layer**.

Creating a short URL is a **business event**, not an HTTP event or a database event.

The Service Layer coordinates the business workflow:

* Creates the URL entity.
* Generates the short code or uses a custom alias.
* Persists the entity.
* Completes the business operation.

Therefore, the Service Layer has the complete business context and is the correct place to log that a short URL has been created.

### Logging Responsibilities

| Layer            | What it should log                                                                |
| ---------------- | --------------------------------------------------------------------------------- |
| API Layer        | HTTP requests, responses, status codes, request duration                          |
| Service Layer    | Business events and workflow                                                      |
| Repository Layer | Database operations such as queries, commits, rollbacks, and transaction failures |

### Key Takeaway

Logs should be placed in the layer that owns the event being logged.

* **API Layer** → HTTP events
* **Service Layer** → Business events
* **Repository Layer** → Database events

---

## Q68. What is the difference between Structural Validation and Business Validation?

### My Answer

Validation in an application can be divided into two categories:

1. **Structural Validation**
2. **Business Validation**

Understanding the difference helps us decide where each validation should be implemented.

---

## 1. Structural Validation

Structural validation verifies that the incoming request has the correct structure, data types, and basic constraints before it enters the business logic.

This validation belongs in the **Pydantic Schema**.

Examples:

* Required fields
* Data types
* Valid URL format
* Minimum and maximum length
* Regular expression (allowed characters)

Example:

```python
class URLCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: str | None = Field(
        default=None,
        min_length=3,
        max_length=20,
    )
```

Examples of structural validation:

* `original_url` must be a valid URL.
* `custom_alias` must be between 3 and 20 characters.
* `custom_alias` may contain only allowed characters.
* Required fields must be present.

Structural validation rejects invalid requests **before they reach the Service Layer**, saving unnecessary business logic and database operations.

---

## 2. Business Validation

Business validation enforces application-specific rules.

This validation belongs in the **Service Layer** because it requires business knowledge and may involve database queries or other services.

Examples:

* Custom alias already exists.
* Reserved aliases (`admin`, `login`, `api`).
* Premium aliases require a paid account.
* User has exceeded the URL creation limit.
* Alias violates company policies.

Example:

```python
if self.repository.get_by_short_code(db, request.custom_alias):
    raise AliasAlreadyExistsError(request.custom_alias)
```

These validations cannot be performed by Pydantic because they depend on business rules or external resources.

---

## Comparison

| Structural Validation   | Business Validation         |
| ----------------------- | --------------------------- |
| Pydantic Schema         | Service Layer               |
| Request structure       | Business rules              |
| No database access      | May query the database      |
| Runs before the Service | Runs inside the Service     |
| Checks data format      | Checks business constraints |

---

## Key Takeaway

Use **Pydantic** to validate the **structure** of incoming requests.

Use the **Service Layer** to validate **business rules** that depend on application logic, the database, or external systems.

Keeping these responsibilities separate results in a clean, maintainable, and scalable architecture.

---

## Q69. If `custom_alias` is shorter than the minimum length, will the request reach the Service Layer?

### My Answer

No.

The request will be rejected by **Pydantic** before it reaches the API route or the Service Layer.

### Request Flow

```text id="ij2g9r"
Client
   │
   ▼
FastAPI
   │
   ▼
Pydantic Validation
   │
   ▼
Validation Failed
   │
   ▼
422 Unprocessable Entity
```

If the request does not satisfy the schema constraints (such as `min_length` or `max_length`), FastAPI automatically returns a **422 Unprocessable Entity** response.

The following layers are **never executed**:

* API Route
* Service Layer
* Repository Layer
* Database

### Key Takeaway

Structural validation is performed by **Pydantic** before the request enters the application's business logic. This prevents invalid requests from consuming unnecessary CPU, memory, and database resources.

---

## Q70. Why is alias format validation implemented in Pydantic instead of the Service Layer?

### My Answer

Alias format validation is a **structural validation**, so it belongs in the **Pydantic schema**.

Pydantic is responsible for validating the structure of incoming requests before they enter the application.

If the request does not satisfy the schema constraints (such as length, allowed characters, or URL format), FastAPI automatically rejects the request and returns a **422 Unprocessable Entity** response.

The request never reaches:

* API Route
* Service Layer
* Repository Layer
* Database

This prevents invalid requests from consuming unnecessary application and database resources.

Alias format validation only checks whether the input matches the expected format. It does **not** require:

* Database access
* Business rules
* External services

Therefore, it belongs in the Pydantic schema rather than the Service Layer.

### Request Flow

```text
Client
   │
   ▼
FastAPI
   │
   ▼
Pydantic Validation
   │
   ▼
Validation Failed
   │
   ▼
422 Unprocessable Entity
```

### Key Takeaway

* **Pydantic** validates the **structure and format** of incoming requests.
* **Service Layer** validates **business rules** that require application logic, database queries, or external services.

---

## Q71. Why do we create `URLStatsResponse` instead of returning the SQLAlchemy `URL` model directly?

### My Answer

We create a dedicated response schema because each layer has its own responsibility.

The SQLAlchemy model represents the **database schema**, while the response schema represents the **API contract**.

Returning the SQLAlchemy model directly tightly couples the API to the database. Any database change could unintentionally affect the API response.

Using a dedicated response schema provides several benefits:

* Maintains a clear separation of responsibilities.
* Exposes only the fields that the client should see.
* Prevents leaking internal database fields.
* Allows the database schema to evolve without breaking the API.
* Keeps the API contract stable and independent of the persistence layer.

### Layer Responsibilities

| Layer                       | Responsibility                       |
| --------------------------- | ------------------------------------ |
| Database Model (SQLAlchemy) | Represents the database schema       |
| Response Schema (Pydantic)  | Represents the API response contract |

### Key Takeaway

Never expose ORM models directly to clients. Always return dedicated response schemas that define the public API contract.

---

## Q72. Why do we use `str` instead of `HttpUrl` in the response schema?

### My Answer

The response schema represents data that already exists in the application's database.

The URL was validated when it entered the system through the request schema, so there is no need to validate it again when returning it to the client.

Therefore, the response schema should use:

```python
original_url: str
```

instead of:

```python
original_url: HttpUrl
```

### Why?

* **Request Schema** validates user input.
* **Response Schema** serializes trusted application data.

Re-validating response data is unnecessary and may even cause response serialization failures if the stored data does not satisfy the validation rules.

### Key Takeaway

* Use **`HttpUrl`** in **request schemas** to validate incoming data.
* Use **`str`** in **response schemas** to serialize data returned from the application.

---

## Q73. Why does the Service return a `URL` object instead of `URLStatsResponse`?

### My Answer

The Service Layer should return **domain objects (Python objects)** rather than HTTP response models.

Creating an HTTP response is the responsibility of the **API Layer**, not the Service Layer.

The Service Layer contains business logic and should remain independent of FastAPI, HTTP, and Pydantic response models.

This separation allows the same Service to be reused by different interfaces, such as:

* REST APIs
* CLI applications
* Background workers
* Scheduled jobs
* gRPC services

The API Layer is responsible for converting the returned domain object into the appropriate response schema.

### Architecture

```text
Client
   │
   ▼
API Layer
   │
   ▼
Service Layer
   │
   ▼
Repository Layer
   │
   ▼
Database
```

### Response Flow

```text
Repository
      │
      ▼
    URL (Domain Object)
      │
      ▼
Service
      │
      ▼
    URL (Domain Object)
      │
      ▼
API
      │
      ▼
URLStatsResponse (Pydantic)
      │
      ▼
HTTP Response
```

### Key Takeaway

* **Repository** → Returns database/domain objects.
* **Service** → Returns domain objects after applying business logic.
* **API Layer** → Converts domain objects into HTTP response models.

The Service should never know how the data will be presented to the client.

---

## Q74. Which layer should handle the case when a short code does not exist?

### My Answer

The **Service Layer** should handle this case.

The Repository is only responsible for querying the database. If no matching row exists, it should simply return `None`.

The Service Layer owns the business logic. It interprets the `None` result and decides that the requested short URL does not exist.

Example:

```python
url = self.repository.get_by_short_code(db, short_code)

if not url:
    raise URLNotFoundError(short_code)

return url
```

The exception is then handled by the global exception handler, which converts it into an appropriate HTTP response.

### Flow

```text
Repository
      │
      ▼
Returns None
      │
      ▼
Service
      │
      ▼
Raises URLNotFoundError
      │
      ▼
Exception Handler
      │
      ▼
404 Not Found
```

### Key Takeaway

* **Repository** → Returns data or `None`.
* **Service** → Applies business rules and raises business exceptions.
* **API Layer** → Delegates to the Service and does not contain business logic.
* **Exception Handler** → Converts business exceptions into HTTP responses.

---

## Q75. Why did we change the return type from `URL | None` to `URL`?

### My Answer

We changed the return type to `URL` because the method no longer returns `None`.

If the requested short code does not exist, the Service raises a `URLNotFoundError` instead of returning `None`.

Therefore, the method has only two possible outcomes:

1. Return a valid `URL` object.
2. Raise a `URLNotFoundError`.

This provides a stronger and clearer contract to the caller.

### Before

```python
def get_url_stats(...) -> URL | None
```

The caller had to check:

```python
if url is None:
    ...
```

### After

```python
def get_url_stats(...) -> URL
```

The caller knows that if the method returns successfully, it will always receive a valid `URL` object.

If the URL does not exist, an exception is raised instead.

### Key Takeaway

Returning a concrete type (`URL`) instead of `URL | None` makes the method contract clearer, reduces unnecessary `None` checks, and centralizes error handling through exceptions.

---

## Q76. Why does the API return `URLStatsResponse` instead of the `URL` object?

### My Answer

The API Layer is responsible for communicating with clients over HTTP.

The `URL` object is a domain object used internally by the application, while `URLStatsResponse` is a Pydantic response model that defines the public API contract.

Therefore, the API should convert the domain object into a response model before sending it to the client.

Example:

```python
return URLStatsResponse(
    id=url.id,
    original_url=url.original_url,
    short_code=url.short_code,
    click_count=url.click_count,
    created_at=url.created_at,
)
```

This provides several benefits:

* Hides internal implementation details.
* Exposes only the required fields.
* Keeps the API contract stable.
* Decouples the API from the database model.
* Allows the database schema and API response to evolve independently.

### Layer Responsibilities

| Layer      | Responsibility                                                                   |
| ---------- | -------------------------------------------------------------------------------- |
| Repository | Returns database/domain objects                                                  |
| Service    | Returns domain objects after applying business logic                             |
| API Layer  | Converts domain objects into Pydantic response models and returns HTTP responses |

### Key Takeaway

The API Layer is the boundary between the application and the outside world. It should always communicate using dedicated Pydantic request and response models rather than exposing internal domain or database objects.

---

## Q77. Should we manually map fields or use Pydantic's `model_validate()`?

### My Answer

Both approaches are valid, and the choice depends on the project's requirements.

### Manual Mapping

```python
return URLStatsResponse(
    id=url.id,
    original_url=url.original_url,
    short_code=url.short_code,
    click_count=url.click_count,
    created_at=url.created_at,
)
```

**Advantages**

* Explicit and easy to understand.
* Gives full control over which fields are exposed.
* Reduces the risk of accidentally exposing internal or sensitive fields.

**Disadvantages**

* More boilerplate code.
* Requires updates whenever new response fields are added.

---

### Pydantic `model_validate()`

```python
return URLStatsResponse.model_validate(url)
```

(using `from_attributes=True`)

**Advantages**

* Less boilerplate.
* Easier to maintain as the model grows.
* Cleaner and more concise code.

**Disadvantages**

* Requires careful design of the response model.
* Accidental exposure of fields is easier if the response schema is not reviewed carefully.

---

### My Choice

For this learning roadmap, I prefer **manual mapping** because it clearly demonstrates the separation between:

* Domain objects (Service Layer)
* API response models (API Layer)

For larger production systems with well-defined response schemas, I would consider using `model_validate()` to reduce repetitive code.

### Key Takeaway

Choose the approach based on the trade-off between **explicitness** and **maintainability**, while always preserving the separation between domain models and API contracts.

---

## Q81. After updating `url.click_count`, do we need to call `repository.add(db, url)` again?

### My Answer

No.

We do **not** need to call `repository.add(db, url)` again.

The `URL` Python object is already registered with the current SQLAlchemy session when it is retrieved from the database using:

```python
url = self.repository.get_by_short_code(db, short_code)
```

Since the object is already managed by the session, SQLAlchemy automatically tracks any modifications made to it.

Example:

```python
url.click_count += 1
```

SQLAlchemy marks the object as **dirty**.

When we later execute:

```python
self.repository.commit(db)
```

SQLAlchemy's **dirty checking** mechanism detects the modified fields and automatically generates the appropriate `UPDATE` statement.

There is no need to register the object again with `db.add()`.

### Lifecycle

```text
Database
    │
    ▼
SELECT
    │
    ▼
URL Python Object
    │
    ▼
Registered with SQLAlchemy Session
    │
    ▼
Modify Object

url.click_count += 1
    │
    ▼
Dirty Checking
    │
    ▼
db.commit()
    │
    ▼
UPDATE urls
SET click_count = click_count + 1
```

### Key Takeaway

* `db.add()` is used to register **new** objects with the session.
* Objects loaded from the database are **already managed** by the session.
* SQLAlchemy automatically tracks changes to managed objects and persists them during `commit()` using its dirty checking mechanism.

---

## Q82. What happens if 100 users update `click_count` at the same time?

### My Answer

The application can suffer from **Lost Updates**.

Each request performs the following sequence:

```text
READ
   ↓
MODIFY
   ↓
WRITE
```

Suppose the current value is:

```text
click_count = 10
```

Two concurrent requests may both read the value `10`, increment it to `11`, and then write `11` back to the database.

The expected value is:

```text
12
```

but the actual value becomes:

```text
11
```

One increment is lost.

This problem is known as a **Lost Update**, and it occurs because multiple transactions read and modify the same row concurrently.

### Example

```text
Request A           Request B

Read 10             Read 10
Increment           Increment
Write 11            Write 11
```

Final value:

```text
11
```

instead of:

```text
12
```

### Key Takeaway

The simple statement:

```python
url.click_count += 1
```

is internally a **Read → Modify → Write** operation, making it vulnerable to race conditions under concurrent requests.

This is one of the fundamental concurrency problems that leads to techniques such as row-level locking, atomic database updates, Redis counters, and eventually distributed system designs.

This is one of the fundamental concurrency problems that leads to techniques such as:

Atomic SQL UPDATE
Row-level locking
Database isolation levels
Redis atomic counters
Message queues
Eventual consistency

These techniques are used to prevent lost updates and build scalable, highly concurrent systems.