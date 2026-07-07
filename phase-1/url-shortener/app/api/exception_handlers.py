from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions.url_exceptions import AliasAlreadyExistsError
from app.exceptions.url_exceptions import URLNotFoundError


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(AliasAlreadyExistsError)
    async def alias_already_exists_handler(
        request: Request,
        exc: AliasAlreadyExistsError,
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": str(exc),
            },
        )
    
    @app.exception_handler(URLNotFoundError)
    async def url_not_found_handler(
        request: Request,
        exc: URLNotFoundError,
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": str(exc),
            },
        )
    