from sqlalchemy.orm import Session
import logging

from app.models.url import URL
from app.repositories.url_repository import URLRepository
from app.utils.base62 import decode, encode
from app.schemas.url import URLCreate
from app.exceptions.url_exceptions import AliasAlreadyExistsError, URLNotFoundError



logger = logging.getLogger(__name__)

class URLService:

    def __init__(self):
        self.repository = URLRepository()

    def create_short_url(
        self,
        db: Session,
        request: URLCreate,
    ) -> URL:
        
        if request.custom_alias and self.repository.get_by_short_code(db, request.custom_alias):
            raise AliasAlreadyExistsError(request.custom_alias)

        url = URL(original_url=str(request.original_url))

        self.repository.add(db, url)
        self.repository.flush(db)

        url.short_code = request.custom_alias or encode(url.id)

        self.repository.commit(db)

        return url
        
    def get_original_url(self, db: Session, short_code: str,) -> URL | None:

        url = self.repository.get_by_short_code(db, short_code)

        if not url:
            raise URLNotFoundError(short_code)
        
        url.click_count += 1

        self.repository.commit(db)

        return url
    
    def get_url_stats(self, db: Session, short_code: str) -> URL:

        url = self.repository.get_by_short_code(db, short_code)

        if not url:
            raise URLNotFoundError(short_code)

        return url