from app.repositories.product_repository import ProductRepository
from app.repositories.reservation_repository import ReservationRepository


class ReservationCleanupService:

    def __init__(self):

        self.product_repository = ProductRepository()

        self.reservation_repository = ReservationRepository()

    def cleanup(self, db):

        expired = self.reservation_repository.get_expired(db)

        if not expired:
            db.commit()
            return 0

        for reservation in expired:

            self.product_repository.increase_stock(
                db=db,
                product_id=reservation.product_id,
                quantity=reservation.quantity,
            )

            self.reservation_repository.mark_expired(
                db=db,
                reservation_id=reservation.id,
            )

        db.commit()

        return len(expired)

    