# How FastAPI Builds an Application

When we create a FastAPI application:

```python
app = FastAPI()
```

FastAPI creates an application object. Conceptually, it looks like this:

```text
FastAPI Object

Routes = {}

Exception Handlers = {}

Middleware = []

Startup Events = []

Shutdown Events = []
```

Initially, all of these collections are empty.

---

## What Happens During Application Startup?

As the application starts, we register different components with the `app` object.

Example:

```python
app = FastAPI()

register_routes(app)
register_exception_handlers(app)
register_middlewares(app)
register_events(app)
```

Each function adds new components to the application.

After registration, the internal structure becomes conceptually similar to:

```text
FastAPI Object

Routes
-------
POST /shorten      → create_short_url()
GET /{short_code}  → redirect_url()

Exception Handlers
------------------
AliasAlreadyExistsError
        ↓
alias_already_exists_handler()

Middleware
----------
LoggingMiddleware
CORSMiddleware

Startup Events
--------------
Create Database Connection

Shutdown Events
---------------
Close Database Connection
```

---

## How Does FastAPI Know Which Exception Handler to Call?

When we write:

```python
@app.exception_handler(AliasAlreadyExistsError)
async def alias_already_exists_handler(request, exc):
    ...
```

the decorator registers the handler with the FastAPI application.

Conceptually, it is similar to:

```python
app.add_exception_handler(
    AliasAlreadyExistsError,
    alias_already_exists_handler,
)
```

Internally, FastAPI stores something like:

```text
Exception Handlers

{
    AliasAlreadyExistsError:
        alias_already_exists_handler
}
```

---

## Runtime Flow

```text
Request
   │
   ▼
API Layer
   │
   ▼
Service Layer
   │
   ▼
raise AliasAlreadyExistsError
   │
   ▼
FastAPI catches the exception
   │
   ▼
Looks up the registered handler
   │
   ▼
alias_already_exists_handler()
   │
   ▼
Returns JSONResponse
   │
   ▼
Client
```

---

## Key Takeaway

`FastAPI()` creates an application object.

Everything else—routes, exception handlers, middleware, startup events, and shutdown events—is **registered** with that object before the server starts accepting requests.

This registration pattern is common across modern web frameworks such as FastAPI, Flask, Django, Spring Boot, and Express.js.

---

