from app.db import SessionLocal

from app.services.reservation_service import ReservationService

from app.utils.database_reset import DatabaseReset


db = SessionLocal()

DatabaseReset().reset_inventory(
    db=db,
    products=[
        (
            1,
            "iPhone 17",
            10,
        ),
    ],
)

ReservationService().reserve(
    db=db,
    product_id=1,
    user_id=101,
    quantity=1,
    expire_after_seconds=10,
)

print()

print("Reservation Created")

db.close()