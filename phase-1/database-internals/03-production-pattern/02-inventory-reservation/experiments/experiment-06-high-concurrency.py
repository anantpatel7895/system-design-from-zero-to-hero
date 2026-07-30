import threading
import time

from app.db import SessionLocal

from app.repositories.product_repository import ProductRepository
from app.repositories.reservation_repository import ReservationRepository

from app.services.reservation_service import ReservationService

from app.utils.database_reset import DatabaseReset

# ============================================================
# Configuration
# ============================================================

INITIAL_STOCK = 10
THREADS = 100

# ============================================================
# Shared Counters
# ============================================================

success_count = 0
failure_count = 0

counter_lock = threading.Lock()

# ============================================================
# Worker
# ============================================================


def worker(user_id: int):

    global success_count
    global failure_count

    db = SessionLocal()

    try:

        success = ReservationService().reserve(
            db=db,
            product_id=1,
            user_id=user_id,
            quantity=1,
            expire_after_seconds=900,
        )

        with counter_lock: # to prevent race condition in memory, not in database

            if success:
                success_count += 1
            else:
                failure_count += 1

    finally:

        db.close()


# ============================================================
# Reset Database
# ============================================================

db = SessionLocal()

DatabaseReset().reset_inventory(
    db=db,
    products=[
        (
            1,
            "iPhone 17",
            INITIAL_STOCK,
        ),
    ],
)

db.close()

# ============================================================
# Create Threads
# ============================================================

workers = []

for i in range(THREADS):

    thread = threading.Thread(
        target=worker,
        args=(i + 1,),
    )

    workers.append(thread)

# ============================================================
# Benchmark
# ============================================================

start = time.perf_counter()

for thread in workers:
    thread.start()

for thread in workers:
    thread.join()

elapsed = time.perf_counter() - start

# ============================================================
# Verify Database
# ============================================================

db = SessionLocal()

product_repository = ProductRepository()

reservation_repository = ReservationRepository()

product = product_repository.get_by_id(
    db=db,
    product_id=1,
)

reservations = reservation_repository.get_all(db)

db.close()

# ============================================================
# Report
# ============================================================

print()
print("=" * 60)
print("High Concurrency Reservation Test")
print("=" * 60)

print(f"Threads                 : {THREADS}")
print(f"Initial Stock           : {INITIAL_STOCK}")

print()

print(f"Successful Reservations : {success_count}")
print(f"Failed Reservations     : {failure_count}")

print()

print(f"Remaining Stock         : {product.stock}")
print(f"Reservation Rows        : {len(reservations)}")

print()

print(f"Elapsed                 : {elapsed:.3f} sec")
print(f"TPS                     : {THREADS / elapsed:.2f}")

print("=" * 60)