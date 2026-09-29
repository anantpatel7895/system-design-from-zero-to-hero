from datetime import datetime

from app.events.events import ReservationCreated


def create_reservation_created_event(
    reservation_id: int,
    product_id: int,
    user_id: int,
    quantity: int,
) -> ReservationCreated:

    return ReservationCreated(
        reservation_id=reservation_id,
        product_id=product_id,
        user_id=user_id,
        quantity=quantity,
        occurred_at=datetime.utcnow(),
    )