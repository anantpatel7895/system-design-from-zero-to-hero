class HTTPException(Exception):
    pass


class BadRequest(HTTPException):
    pass


class RouteNotFound(HTTPException):
    pass