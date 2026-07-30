from sqlalchemy import text


class DatabaseReset:

    def reset_inventory(
        self,
        db,
        products: list[tuple[int, str, int]],
    ):

        # ----------------------------------------
        # Clear Reservations
        # ----------------------------------------

        db.execute(
            text("""
                DELETE
                FROM inventory_reservations
            """)
        )

        # ----------------------------------------
        # Clear Products
        # ----------------------------------------

        db.execute(
            text("""
                DELETE
                FROM products
            """)
        )

        # ----------------------------------------
        # Insert Products
        # ----------------------------------------

        for product_id, name, stock in products:

            db.execute(
                text("""
                    INSERT INTO products
                    (
                        id,
                        name,
                        stock
                    )
                    VALUES
                    (
                        :id,
                        :name,
                        :stock
                    )
                """),
                {
                    "id": product_id,
                    "name": name,
                    "stock": stock,
                },
            )

        db.commit()

        print("=" * 60)
        print("Database Reset")
        print("=" * 60)