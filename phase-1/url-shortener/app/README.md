```text
app/
│
├── api/             # HTTP layer
│
├── core/            # Infrastructure
│   ├── config.py
│   ├── database.py
│   ├── logger.py
│   ├── cache.py          # later
│   └── security.py       # later
│
├── models/          # ORM models
│
├── schemas/         # Pydantic models
│
├── repositories/    # Database operations
│
├── services/        # Business logic
│
├── utils/           # Pure helper functions
│
├── tests/
│
└── main.py
```

```text
Project 1 (Production Version)

Core
──────
✅ Create URL
✅ Redirect
✅ Stats


Production Features
───────────────────
□ Click Counter
□ Expiration Time (TTL)
□ Delete URL
□ Update Alias
□ Pagination
□ Search URLs
□ API Documentation
□ Unit Tests
□ Integration Tests
□ Docker Compose
□ Alembic Migration
```