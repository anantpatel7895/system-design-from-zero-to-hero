from sqlalchemy import text


class ProductRepository:

    def lock_product(
        self,
        db,
        product_id: int,
    ):

        result = db.execute(
            text("""
                SELECT id, stock
                FROM products
                WHERE id = :id
                FOR UPDATE
            """),
            {"id": product_id},
        )

        return result.first()
    
    def decrease_stock(
        self,
        db,
        product_id: int,
        quantity: int,
    ):

        # This is an atomic SQL update.
        db.execute(
            text("""
                UPDATE products
                SET stock = stock - :quantity
                WHERE id = :id
            """),
            {
                "id": product_id,
                "quantity": quantity,
            },
        )

    def get_by_id(
        self,
        db,
        product_id: int,
    ):

        result = db.execute(
            text("""
                SELECT
                    id,
                    name,
                    stock
                FROM products
                WHERE id = :id
            """),
            {"id": product_id},
        )

        return result.first()
    
    def get_all(
        self,
        db,
    ):

        result = db.execute(
            text("""
                SELECT
                    id,
                    name,
                    stock
                FROM products
                ORDER BY id
            """)
        )

        return result.fetchall()
    
    def reset_stock(
        self,
        db,
        product_id: int,
        stock: int,
    ):

        db.execute(
            text("""
                UPDATE products
                SET stock = :stock
                WHERE id = :id
            """),
            {
                "id": product_id,
                "stock": stock,
            },
        )

    def increase_stock(
        self,
        db,
        product_id: int,
        quantity: int,
    ):

        db.execute(
            text("""
                UPDATE products
                SET stock = stock + :quantity
                WHERE id = :id
            """),
            {
                "id": product_id,
                "quantity": quantity,
            },
        )