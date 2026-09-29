from datetime import datetime, timedelta

from app.repositories.product_repository import ProductRepository
from app.repositories.reservation_repository import ReservationRepository
from time import perf_counter

from app.dtos.reservation_result import ReservationResult

from app.events.events import ReservationCreated
from app.events.event_publisher import EventPublisher

class ReservationService:

    def __init__(self):

        self.product_repository = ProductRepository()

        self.reservation_repository = ReservationRepository()
        self.event_publisher = EventPublisher()

    def reserve(
        self,
        db,
        product_id: int,
        user_id: int,
        quantity: int,
        expire_after_seconds: int = 900
    ):
        
        start = perf_counter()

        product = self.product_repository.lock_product(
            db,
            product_id,
        )

        if product.stock < quantity:

            db.rollback()

            # print("Out Of Stock")
            elapsed = (perf_counter() - start) * 1000

            return ReservationResult(
            user_id=user_id,
            success=False,
            message="Out Of Stock",
            elapsed_ms=elapsed,
        )

        self.product_repository.decrease_stock(
            db,
            product_id,
            quantity,
        )

        expires_at = datetime.utcnow() + + timedelta(seconds=expire_after_seconds,)

        reservation_id = self.reservation_repository.create(
            db=db,
            product_id=product_id,
            user_id=user_id,
            quantity=quantity,
            expires_at=expires_at,
        )

        db.commit()

        # ====================================================
        # Event Creation
        # ====================================================

        event = ReservationCreated(
            reservation_id=reservation_id,
            product_id=product_id,
            user_id=user_id,
            quantity=quantity,
            occurred_at=datetime.utcnow(),
        )

        # ====================================================
        # Event Publishing
        # ====================================================

        self.event_publisher.publish(event)

        elapsed = (perf_counter() - start) * 1000

        return ReservationResult(
            user_id=user_id,
            success=True,
            message="Reserved",
            elapsed_ms=elapsed,
        )
