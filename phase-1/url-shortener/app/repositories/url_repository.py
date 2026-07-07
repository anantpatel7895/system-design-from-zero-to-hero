from sqlalchemy.orm import Session
from app.models.url import URL
import logging

logger = logging.getLogger(__name__)

class URLRepository:

    # def create(
    #     self,
    #     db: Session,
    #     original_url: str
    # ) -> URL:

    #     url = URL(
    #         original_url=original_url
    #     )
    #     logger.info("Creating URL: %s", original_url)

    #     db.add(url) # register the new URL python-object with the SQLAlchemy session
    #     db.commit() # generate the SQL INSERT statement and execute it against the database

    #     db.refresh(url) # reload the object from the database to get the latest state

    #     return url
    
   
    def add(self, db:Session,url:URL) -> None:
        logger.info("Adding URL to session.")
        db.add(url)


    def flush(self, db:Session) -> None:
        logger.info("Flushing session.")
        db.flush()

    def commit(self, db:Session) -> None:
        logger.info("Committing transaction.")
        try:
            db.commit()

        except:
            db.rollback()
            raise

    def rollback(self, db:Session) -> None:
        logger.info("Rolling back transaction.")
        db.rollback()
    
    
    def get_by_id(self,db: Session,url_id: int,) -> URL | None:
        logger.info("Fetching URL with ID: %d", url_id)

        return (
            db.query(URL)
            .filter(URL.id == url_id)
            .first()
        )
    
    def get_by_original_url(self,db: Session,original_url: str,) -> URL | None:

        return (
            db.query(URL) # select statement
            .filter(URL.original_url == original_url) # where condition
            .first() # limit
        )
    
    def get_by_short_code(self, db:Session, short_code:str) -> URL:
        logger.debug("getting url for short code")

        return (
            db.query(URL)
            .filter(URL.short_code == short_code)
            .first()
        )