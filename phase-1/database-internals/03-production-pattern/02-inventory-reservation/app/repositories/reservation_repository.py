from sqlalchemy import text


class ReservationRepository:

    def create(
        self,
        db,
        product_id: int,
        user_id: int,
        quantity: int,
        expires_at,
    ):

        result = db.execute(
            text("""
                INSERT INTO inventory_reservations
                (
                    product_id,
                    user_id,
                    quantity,
                    status,
                    expires_at
                )
                VALUES
                (
                    :product_id,
                    :user_id,
                    :quantity,
                    'RESERVED',
                    :expires_at
                )
                RETURNING id
            """),
            {
                "product_id": product_id,
                "user_id": user_id,
                "quantity": quantity,
                "expires_at": expires_at,
            },
        )

        reservation_id = result.scalar_one()

        return reservation_id

    def get_all(
        self,
        db,
    ):

        result = db.execute(
            text("""
                SELECT
                    id,
                    product_id,
                    user_id,
                    quantity,
                    status,
                    expires_at,
                    created_at
                FROM inventory_reservations
                ORDER BY id
            """)
        )

        return result.fetchall()
    
    def delete_all(
        self,
        db,
    ):

        db.execute(
            text("""
                DELETE
                FROM inventory_reservations
            """)
        )


    def get_expired(
        self,
        db,
    ):

        result = db.execute(
            text("""
                SELECT
                    id,
                    product_id,
                    user_id,
                    quantity,
                    status,
                    expires_at,
                    created_at
                FROM inventory_reservations
                WHERE
                    status = 'RESERVED'
                    AND expires_at <= NOW()
                ORDER BY id
            """)
        )

        return result.fetchall()
    
    def update_status(
        self,
        db,
        reservation_id: int,
        status: str,
    ):

        db.execute(
            text("""
                UPDATE inventory_reservations
                SET status = :status
                WHERE id = :id
            """),
            {
                "id": reservation_id,
                "status": status,
            },
        )

    def mark_expired(
        self,
        db,
        reservation_id: int,
    ):

        db.execute(
            text("""
                UPDATE inventory_reservations
                SET status = 'EXPIRED'
                WHERE id = :id
            """),
            {
                "id": reservation_id,
            },
        )