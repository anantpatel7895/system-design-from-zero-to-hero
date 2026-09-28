from app.repository import CounterRepository


class CounterService:

    def __init__(self):
        self.repository = CounterRepository()

    def increment(
        self,
        db,
        url_id: int,
    ):
        """
        Increment the click count for a given URL ID.

        READ the current count from the database, increment it by 1, and then update the database with the new count.
        This method is not safe for concurrent access and may lead to race conditions if multiple threads or processes attempt to increment the count simultaneously.   
        """

        # READ
        count = self.repository.get_count( # not committing here, will commit it in **update_count**
            db,
            url_id,
        )

        # INCREMENT/MODIFY
        count += 1

        # UPDATE
        self.repository.update_count( # committing the transaction after updating the count in the database. This ensures that the changes are saved and visible to other transactions.
            db,
            url_id,
            count,
        )                           

    def atomic_increment(
        self,
        db,
        url_id: int,
    ):
        """
        Increment the click count for a given URL ID in an atomic manner.
        This method uses a single SQL statement to increment the count, ensuring that the operation is safe for concurrent access and preventing race conditions.
        """

        self.repository.atomic_increment(
            db=db,
            url_id=url_id,
        )
