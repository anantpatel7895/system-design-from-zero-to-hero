from handlers import (
    hello,
    users,
    health,
    create_user
)

from response import Response


ROUTES = {

    ("GET", "/hello"): hello,

    ("GET", "/users"): users,

    ("GET", "/health"): health,

    ("POST", "/users"): create_user
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