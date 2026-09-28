from sqlalchemy import text


class CounterRepository:

    def get_count(self, db, url_id: int) -> int:
        result = db.execute(
            text("""
                SELECT click_count
                FROM urls
                WHERE id = :id
            """),
            {"id": url_id},
        )
        #  Not Committing here, will commit it in **update_count**
        return result.scalar()

    def update_count(
        self,
        db,
        url_id: int,
        value: int,
    ) -> None:

        db.execute(
            text("""
                UPDATE urls
                SET click_count = :value
                WHERE id = :id
            """),
            {
                "id": url_id,
                "value": value,
            },
        )
        # Here we are committing the transaction after updating the count in the database. This ensures that the changes are saved and visible to other transactions.   
        # db transaction are completed when we call db.commit() and the changes are persisted to the database. If we don't call db.commit(), the changes will not be saved and will be lost when the session is closed or rolled back.
        db.commit()

    def atomic_increment(
        self,
        db,
        url_id: int,
    ) -> None:

        db.execute(
            text("""
                UPDATE urls
                SET click_count = click_count + 1
                WHERE id = :id
            """),
            {"id": url_id},
        )

        db.commit()