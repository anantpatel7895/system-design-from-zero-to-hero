"""
http/request.py
"""

from __future__ import annotations

import json


class Request:

    def __init__(
        self,
        method: str,
        path: str,
        version: str,
        headers: dict[str, str],
        body: bytes,
    ) -> None:

        self.method = method

        self.path = path

        self.version = version

        self.headers = headers

        self.body = body

    def json(self):

        if not self.body:
            return None

        return json.loads(
            self.body.decode()
        )

    def __repr__(self):

        return (
            f"<Request "
            f"{self.method} "
            f"{self.path}>"
        )