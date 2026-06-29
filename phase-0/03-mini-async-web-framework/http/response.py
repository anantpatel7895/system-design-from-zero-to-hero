"""
response.py

Converts Python objects into HTTP responses.
"""

import json

from config import DEFAULT_CONTENT_TYPE
from config import SERVER_NAME

from core.constants import (
    CRLF,
    HTTP_VERSION,
)

from core.status_codes import HTTP_STATUS


class Response:

    def __init__(
        self,
        body="",
        status=200,
        headers=None,
    ):

        self.status = status

        self.body = body

        self.headers = headers or {}

    def to_bytes(self):

        if isinstance(self.body, (dict, list)):

            body = json.dumps(
                self.body,
                indent=4,
            )

            content_type = "application/json"

        elif isinstance(self.body, str):

            body = self.body

            content_type = "text/plain"

        else:

            body = str(self.body)

            content_type = DEFAULT_CONTENT_TYPE

        body_bytes = body.encode()

        self.headers["Content-Type"] = (
            content_type
        )

        self.headers["Content-Length"] = str(
            len(body_bytes)
        )

        self.headers["Server"] = SERVER_NAME

        self.headers.setdefault(
            "Connection",
            "keep-alive",
        )

        status_line = (
            f"{HTTP_VERSION} "
            f"{self.status} "
            f"{HTTP_STATUS[self.status]}"
        )

        header_lines = []

        for key, value in self.headers.items():

            header_lines.append(
                f"{key}: {value}"
            )

        response = (
            status_line
            + CRLF
            + CRLF.join(header_lines)
            + CRLF
            + CRLF
        )

        return response.encode() + body_bytes