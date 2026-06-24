from handlers import (
    hello,
    slow,
    users,
    health,
    create_user,
    slow
)

from response import Response


ROUTES = {

    ("GET", "/hello"): hello,

    ("GET", "/users"): users,

    ("GET", "/health"): health,

    ("POST", "/users"): create_user,

    ("GET", "/slow"): slow
}


def dispatch(request):

    handler = ROUTES.get(
        (request.method, request.path)
    )

    if not handler:

        return Response(
            body="Not Found",
            status=404
        )

    return handler(request)