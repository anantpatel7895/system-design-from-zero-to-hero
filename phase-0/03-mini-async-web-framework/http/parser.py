"""
http/parser.py

HTTP request parser.

Responsibilities
----------------
- Parse raw HTTP bytes
- Build a Request object

It knows nothing about routing or sockets.
"""

from __future__ import annotations

from http.request import Request


class HttpParser:

    @staticmethod
    def parse(
        raw_request: bytes,
    ) -> Request:

        text = raw_request.decode(
            "utf-8",
            errors="replace",
        )

        header_text, _, body = text.partition(
            "\r\n\r\n"
        )

        lines = header_text.split(
            "\r\n"
        )

        if not lines:
            raise ValueError(
                "Empty request."
            )

        request_line = lines[0]

        try:

            method, path, version = (
                request_line.split()
            )

        except ValueError:

            raise ValueError(
                "Invalid HTTP request line."
            )

        headers = {}

        for line in lines[1:]:

            if ":" not in line:
                continue

            key, value = line.split(
                ":",
                1,
            )

            headers[
                key.strip()
            ] = value.strip()

        return Request(
            method=method,
            path=path,
            version=version,
            headers=headers,
            body=body.encode(),
        )