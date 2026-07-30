from sqlalchemy import text


class ProductRepository:

    def get_stock(
        self,
        db,
        product_id: int,
    ):

        result = db.execute(
            text("""
                SELECT stock
                FROM products
                WHERE id = :id
            """),
            {"id": product_id},
        )

        return result.scalar()

    def update_stock(
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

    def get_stock_for_update(
        self,
        db,
        product_id: int,
    ):

        result = db.execute(
            text("""
                SELECT stock
                FROM products
                WHERE id = :id
                FOR UPDATE
            """),
            {"id": product_id},
        )

        return result.scalar()