from app.repository import CounterRepository


class CounterService:

    def __init__(self):
        self.repository = CounterRepository()

    def increment(
        self,
        db,
        url_id: int,
    ):

        count = self.repository.get_count(
            db,
            url_id,
        )

        count += 1

        self.repository.update_count(
            db,
            url_id,
            count,
        )

    def atomic_increment(
        self,
        db,
        url_id: int,
    ):

        self.repository.atomic_increment(
            db=db,
            url_id=url_id,
        )
