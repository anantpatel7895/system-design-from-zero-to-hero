from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReservationCreated:
    reservation_id: int
    product_id: int
    user_id: int
    quantity: int
    occurred_at: datetime