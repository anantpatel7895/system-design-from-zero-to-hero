import threading
import time

from sqlalchemy import text

from app.db import SessionLocal
from app.service import CounterService

# --------------------------------------------------
# Configuration
# --------------------------------------------------



service = CounterService()


# --------------------------------------------------
# Reset Counter
# --------------------------------------------------

def reset_counter():
    db = SessionLocal()

    try:
        db.execute(
            text("""
                UPDATE urls
                SET click_count = 0
                WHERE id = 1
            """)
        )
        db.commit()

    finally:
        db.close()


# --------------------------------------------------
# Get Counter
# --------------------------------------------------

def get_counter():
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT click_count
                FROM urls
                WHERE id = 1
            """)
        )

        return result.scalar()

    finally:
        db.close()


# --------------------------------------------------
# Worker
# --------------------------------------------------

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


# --------------------------------------------------
# Benchmark
# --------------------------------------------------

def run_test(
    threads: int,
    increments_per_thread: int,
):
    print(f"\nRunning benchmark with {threads} threads...")
    reset_counter()

    workers = []

    for _ in range(threads):
        t = threading.Thread(
            target=worker,
            args=(increments_per_thread,),
        )
        workers.append(t)

    start = time.perf_counter()

    for t in workers:
        t.start()

    for t in workers:
        t.join()

    elapsed = time.perf_counter() - start

    expected = threads * increments_per_thread
    actual = get_counter()

    tps = expected / elapsed

    print("=" * 60)
    print(f"Threads              : {threads}")
    print(f"Increments / Thread  : {increments_per_thread}")
    print(f"Expected             : {expected}")
    print(f"Actual               : {actual}")
    print(f"Lost                 : {expected - actual}")
    print(f"Time                 : {elapsed:.3f} sec")
    print(f"TPS                  : {tps:.2f} sec")
    print("=" * 60)
    print()


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    THREAD_COUNTS = [10, 50, 100, 200, 500, 1000]
    INCREMENTS_PER_THREAD = 100

    for threads in THREAD_COUNTS:
        run_test(
            threads=threads,
            increments_per_thread=INCREMENTS_PER_THREAD,
        )