"""
router.py

Stores application routes.
"""

from typing import Callable

from http.response import Response


class Router:

    def __init__(self):

        self.routes = {}

    def add_route(
        self,
        method: str,
        path: str,
        handler: Callable,
    ):

        self.routes[
            (
                method.upper(),
                path,
            )
        ] = handler

    def get(self, path):

        def decorator(func):

            self.add_route(
                "GET",
                path,
                func,
            )

            return func

        return decorator

    def post(self, path):

        def decorator(func):

            self.add_route(
                "POST",
                path,
                func,
            )

            return func

        return decorator

    def resolve(
        self,
        method,
        path,
    ):

        handler = self.routes.get(
            (
                method.upper(),
                path,
            )
        )

        if handler is None:

            return Response(
                {
                    "error": "Route Not Found"
                },
                status=404,
            )

        return handler