from app.db import SessionLocal

from app.repositories.product_repository import ProductRepository
from app.repositories.reservation_repository import ReservationRepository

from app.services.reservation_service import ReservationService

from app.utils.database_reset import DatabaseReset


db = SessionLocal()

# ============================================================
# Reset Database
# ============================================================

DatabaseReset().reset_inventory(
    db=db,
    products=[
        (
            1,
            "iPhone 17",
            10,
        ),
        (
            2,
            "MacBook Pro",
            5,
        ),
        (
            3,
            "AirPods Pro",
            20,
        ),
    ],
)

# ============================================================
# Create Reservation
# ============================================================

service = ReservationService()

service.reserve(
    db=db,
    product_id=1,
    user_id=101,
    quantity=1,
)

print()
print("Reservation Created")

# ============================================================
# Verify Products
# ============================================================

product_repository = ProductRepository()

print()
print("=" * 60)
print("Products")
print("=" * 60)

products = product_repository.get_all(db)

for product in products:
    print(product)

# ============================================================
# Verify Reservations
# ============================================================

reservation_repository = ReservationRepository()

print()
print("=" * 60)
print("Reservations")
print("=" * 60)

reservations = reservation_repository.get_all(db)

for reservation in reservations:
    print(reservation)

db.close()