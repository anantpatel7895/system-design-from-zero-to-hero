from app.db import SessionLocal
from app.service import CounterService
from sqlalchemy import text
import threading

service = CounterService()


def worker(increments: int):

    db = SessionLocal()

    try:

        for _ in range(increments):
            service.atomic_increment(
                db=db,
                url_id=1,
            )

    finally:
        db.close()


db = SessionLocal()

db.execute(
    text("""
        UPDATE urls
        SET click_count = 0
        WHERE id = 1
    """)
)

db.commit()

db.close()


THREADS = 10
INCREMENTS_PER_THREAD = 100

threads = []

for _ in range(THREADS):

    thread = threading.Thread(
        target=worker,
        args=(INCREMENTS_PER_THREAD,),
    )

    threads.append(thread)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

db = SessionLocal()

result = db.execute(
    text("""
        SELECT click_count
        FROM urls
        WHERE id = 1
    """)
)

actual = result.scalar()

db.close()


expected = THREADS * INCREMENTS_PER_THREAD

print("=" * 60)

print(f"Expected : {expected}")

print(f"Actual   : {actual}")

print(f"Lost     : {expected - actual}")