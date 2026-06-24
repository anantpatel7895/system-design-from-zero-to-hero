from handlers import (
    hello_handler,
    users_handler,
    health_handler
)


def route_request(method, path):

    if method == "GET" and path == "/hello":
        return 200, hello_handler()

    elif method == "GET" and path == "/users":
        return 200, users_handler()

    elif method == "GET" and path == "/health":
        return 200, health_handler()

    else:
        return 404, "Not Found"