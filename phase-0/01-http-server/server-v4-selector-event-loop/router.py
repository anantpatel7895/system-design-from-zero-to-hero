from handlers import (
    hello,
    users,
    health,
    slow
)

from response import Response


ROUTES = {

    ("GET", "/hello"): hello,

    ("GET", "/users"): users,

    ("GET", "/health"): health,

    ("GET", "/slow"): slow,
}


def dispatch(request):

    handler = ROUTES.get(
        (
            request.method,
            request.path
        )
    )

    if not handler:

        return Response(
            "Not Found",
            status=404
        )

    return handler(request)