import threading
import time

from app.db import SessionLocal

from app.repositories.product_repository import ProductRepository
from app.repositories.reservation_repository import ReservationRepository

from app.services.reservation_service import ReservationService

from app.utils.database_reset import DatabaseReset
from app.utils.benchmark import Benchmark

# ============================================================
# Configuration
# ============================================================

INITIAL_STOCK = 10
THREADS = 100

# ============================================================
# Worker
# ============================================================


def worker(
    user_id: int,
    results: list,
):

    db = SessionLocal()

    try:

        result = ReservationService().reserve(
            db=db,
            product_id=1,
            user_id=user_id,
            quantity=1,
        )

        results.append(result)

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

results = []

workers = []

for i in range(THREADS):

    t = threading.Thread(
        target=worker,
        args=(
            i + 1,
            results,
        ),
    )

    workers.append(t)


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


successful = sum(
    r.success
    for r in results
)

failed = THREADS - successful

average_latency = sum(
    r.elapsed_ms
    for r in results
) / len(results)

fastest = min(
    r.elapsed_ms
    for r in results
)

slowest = max(
    r.elapsed_ms
    for r in results
)

print("=" * 60)
print("High Concurrency Reservation Test")
print("=" * 60)

print(f"Threads                 : {THREADS}")
print(f"Initial Stock           : {INITIAL_STOCK}")

print()

print(f"Successful Reservations : {successful}")
print(f"Failed Reservations     : {failed}")

print()

print(f"Remaining Stock         : {product.stock}")
print(f"Reservation Rows        : {len(reservations)}")

print()

print(f"Elapsed                 : {elapsed:.3f} sec")
print(f"TPS                     : {THREADS / elapsed:.2f}")

print()

print(f"Average Latency         : {average_latency:.2f} ms")
print(f"Fastest Request         : {fastest:.2f} ms")
print(f"Slowest Request         : {slowest:.2f} ms")

print("=" * 60)

benchmark = Benchmark(results)

print(f"Average Latency : {benchmark.average():.2f} ms")
print(f"Minimum Latency : {benchmark.minimum():.2f} ms")
print(f"Maximum Latency : {benchmark.maximum():.2f} ms")
print(f"P50             : {benchmark.median():.2f} ms")
print(f"P95             : {benchmark.percentile(95):.2f} ms")
print(f"P99             : {benchmark.percentile(99):.2f} ms")
