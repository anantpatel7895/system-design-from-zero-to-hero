from fastapi import APIRouter, logger
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
import logging

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.url import URLCreate
from app.schemas.url import URLResponse, URLStatsResponse
from app.services.url_service import URLService
from app.utils.base62 import decode

router = APIRouter()

service = URLService()

logger = logging.getLogger(__name__)
@router.post(
    "/shorten",
    response_model=URLResponse,
)
def shorten_url(
    request: URLCreate,
    db: Session = Depends(get_db), # dependency injection at api-layer
):
    logger.info(f"/shorten payload : {request.model_dump_json()}")
    url = service.create_short_url(
        db=db,
        request=request,
    )

    return URLResponse(
        id=url.id,
        short_url=f"http://localhost:8000/{url.id}",
    )

@router.get("/{short_code}")
def redirect(
    short_code: str,
    db: Session = Depends(get_db),
):
    logger.info(f"testing Redirection : {short_code}")
    url = service.get_original_url(
        db=db,
        short_code=short_code,
    )

    if url is None:
        logger.warning("URL not found for short code: %s", short_code)
        raise HTTPException(
            status_code=404,
            detail="URL not found",
        )
    logger.debug("Redirecting to original URL: %s", url.original_url)
    return RedirectResponse(
        url.original_url,
        status_code=302,
    )

@router.get(
    "/{short_code}/stats",
    response_model=URLStatsResponse,
)
def get_url_stats(
        short_code: str,
        db: Session = Depends(get_db),
    ):

    logger.info("Getting statistics for short code: %s", short_code)

    url = service.get_url_stats(db, short_code)

    return URLStatsResponse(
            id=url.id,
            original_url=url.original_url,
            short_code=url.short_code,
            click_count=url.click_count,
            created_at=url.created_at,
        )

    
    
