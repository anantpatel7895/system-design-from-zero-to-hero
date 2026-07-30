import time

from app.db import SessionLocal
from app.services.reservation_cleanup_service import (
    ReservationCleanupService,
)

print("=" * 60)
print("Reservation Cleanup Worker Started")
print("=" * 60)

service = ReservationCleanupService()

while True:

    db = SessionLocal()

    try:

        print()
        print("Checking for expired reservations...")

        count = service.cleanup(db)
        print(f"Expired Reservations: {count}")

    except Exception as e:

        db.rollback()

        print(e)

    finally:

        db.close()

    time.sleep(5)