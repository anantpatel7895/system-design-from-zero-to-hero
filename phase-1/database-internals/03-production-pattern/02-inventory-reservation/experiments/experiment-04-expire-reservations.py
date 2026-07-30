import time

from app.db import SessionLocal

from app.repositories.product_repository import ProductRepository
from app.repositories.reservation_repository import ReservationRepository

from app.services.reservation_service import ReservationService
from app.services.reservation_cleanup_service import (
    ReservationCleanupService,
)

from app.utils.database_reset import DatabaseReset


db = SessionLocal()

# ============================================================
# Reset Database
# ============================================================

DatabaseReset().reset_inventory(
    db=db,
    products=[
        (1, "iPhone 17", 10),
    ],
)

# ============================================================
# Create Reservation
# ============================================================

ReservationService().reserve(
    db=db,
    product_id=1,
    user_id=101,
    quantity=1,
    expire_after_seconds=10,
)

print()

print("=" * 60)
print("Reservation Created")
print("=" * 60)

print()

print("Waiting 12 seconds...")

time.sleep(12)

print()

print("=" * 60)
print("Running Cleanup")
print("=" * 60)

ReservationCleanupService().cleanup(db)

print()

print("=" * 60)
print("Products")
print("=" * 60)

products = ProductRepository().get_all(db)

for product in products:
    print(product)

print()

print("=" * 60)
print("Reservations")
print("=" * 60)

reservations = ReservationRepository().get_all(db)

for reservation in reservations:
    print(reservation)

db.close()