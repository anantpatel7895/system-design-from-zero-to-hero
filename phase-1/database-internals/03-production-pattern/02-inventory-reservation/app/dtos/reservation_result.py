from dataclasses import dataclass


@dataclass
class ReservationResult:

    user_id: int

    success: bool

    message: str

    elapsed_ms: float