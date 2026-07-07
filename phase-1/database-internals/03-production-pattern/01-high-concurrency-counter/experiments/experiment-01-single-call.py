from sqlalchemy import text

from app.db import SessionLocal
from app.service import CounterService

db = SessionLocal()

# ---------------------------------------
# Reset Counter
# ---------------------------------------

db.execute(
    text("""
        UPDATE urls
        SET click_count = 0
        WHERE id = 1
    """)
)

db.commit()

print("=" * 60)
print("Counter Reset")
print("=" * 60)

# ---------------------------------------
# Increment
# ---------------------------------------

service = CounterService()

service.increment(
    db=db,
    url_id=1,
)

print("Increment Completed")

# ---------------------------------------
# Verify
# ---------------------------------------

result = db.execute(
    text("""
        SELECT click_count
        FROM urls
        WHERE id = 1
    """)
)

print()

print("Current Counter =", result.scalar())

db.close()

"""
SessionLocal()

↓

(No Connection Yet)

────────────────────────────────────

UPDATE

↓

Acquire Connection

↓

BEGIN

↓

UPDATE

↓

COMMIT

────────────────────────────────────

SELECT

↓

BEGIN

↓

SELECT

↓

UPDATE

↓

COMMIT

────────────────────────────────────

SELECT

↓

BEGIN

↓

SELECT

↓

db.close()

↓

ROLLBACK

↓

Return Connection To Pool
"""