from app.db import SessionLocal

from app.repositories.product_repository import ProductRepository
from app.repositories.reservation_repository import ReservationRepository

from app.services.reservation_service import ReservationService

from app.utils.database_reset import DatabaseReset


def main():

    db = SessionLocal()

    # ========================================================
    # Reset Database
    # ========================================================

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

    # ========================================================
    # Create Reservation
    # ========================================================

    print()
    print("=" * 60)
    print("Creating Reservation")
    print("=" * 60)

    result = ReservationService().reserve(
        db=db,
        product_id=1,
        user_id=101,
        quantity=1,
    )

    print()
    print("Reservation Result:")
    print(result)

    # ========================================================
    # Verify Product
    # ========================================================

    product = ProductRepository().get_by_id(
        db=db,
        product_id=1,
    )

    print()
    print("Product:")
    print(product)

    # ========================================================
    # Verify Reservation
    # ========================================================

    reservations = ReservationRepository().get_all(db)

    print()
    print("Reservations:")

    for reservation in reservations:
        print(reservation)

    db.close()


if __name__ == "__main__":
    main()