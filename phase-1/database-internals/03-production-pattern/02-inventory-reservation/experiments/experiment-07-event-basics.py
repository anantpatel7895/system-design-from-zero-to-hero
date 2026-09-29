from app.events.reservation_events import (
    create_reservation_created_event,
)


def notification_consumer(event):
    print(
        f"[Notification] "
        f"Reservation {event.reservation_id} created "
        f"for user {event.user_id}"
    )


def analytics_consumer(event):
    print(
        f"[Analytics] "
        f"Product {event.product_id} reserved "
        f"quantity={event.quantity}"
    )


def main():

    # Producer creates an event
    event = create_reservation_created_event(
        reservation_id=101,
        product_id=1,
        user_id=5001,
        quantity=2,
    )

    print("\nEvent created:")
    print(event)

    # Multiple consumers react to the same event
    notification_consumer(event)

    analytics_consumer(event)


if __name__ == "__main__":
    main()