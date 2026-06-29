"""
http/request_processor.py

Processes one HTTP request.

Responsibilities
----------------
- Parse HTTP request
- Execute route handler
- Build HTTP response
- Configure response headers
"""

"""
http/request_processor.py
"""

from __future__ import annotations

from typing import Any

from core.context import Context
from http.request import Request
from http.response import Response
from http.parser import HttpParser


class RequestProcessor:
    """
    Responsible for processing one HTTP request.

    This class knows nothing about sockets.
    """

    def __init__(self, router):

        self.router = router

    # =====================================================
    # Entry Point
    # =====================================================

    def process(
        self,
        context: Context,
        raw_request: bytes,
    ) -> None:

        context.request = self.parse_request(
            raw_request
        )

        self.dispatch_request(
            context
        )

    # =====================================================
    # Parse Request
    # =====================================================

    def parse_request(
        self,
        raw_request: bytes,
    ) -> Request:

        return HttpParser.parse(
            raw_request
        )

    # =====================================================
    # Dispatch
    # =====================================================

    def dispatch_request(
        self,
        context: Context,
    ) -> None:

        handler = self.router.resolve(
            context.request.method,
            context.request.path,
        )

        if isinstance(
            handler,
            Response,
        ):

            context.response = handler

            return

        result = handler(
            context.request
        )

        context.response = self.create_response(
            result,
            context,
        )

    # =====================================================
    # Response
    # =====================================================

    def create_response(
        self,
        result: Any,
        context: Context,
    ) -> Response:

        if isinstance(
            result,
            Response,
        ):
            response = result

        else:
            response = Response(result)

        self.configure_connection(
            context,
            response,
        )

        return response

    # =====================================================
    # Headers
    # =====================================================

    def configure_connection(
        self,
        context: Context,
        response: Response,
    ) -> None:

        connection = (
            context.request.headers.get(
                "Connection",
                "",
            ).lower()
        )

        if connection == "close":

            context.connection.keep_alive = False

            response.headers[
                "Connection"
            ] = "close"

        else:

            context.connection.keep_alive = True

            response.headers[
                "Connection"
            ] = "keep-alive"