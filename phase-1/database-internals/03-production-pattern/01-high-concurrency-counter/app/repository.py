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