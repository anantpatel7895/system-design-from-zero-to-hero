"""
network/connection.py

Represents one client connection.

Responsibilities
----------------
- Read HTTP requests
- Parse requests
- Execute route handlers
- Send HTTP responses
- Handle Keep-Alive
- Close connection

The EventLoop decides WHEN read() is called.
Connection decides WHAT to do.
"""

"""
network/connection.py
"""
"""
network/connection.py
"""

from __future__ import annotations

import socket

from core.context import Context
from http.response import Response


class Connection:

    BUFFER_SIZE = 4096

    def __init__(
        self,
        client_socket: socket.socket,
        client_address,
        processor,
        event_loop,
    ):

        self.client_socket = client_socket

        self.client_address = client_address

        self.processor = processor

        self.event_loop = event_loop

        self.keep_alive = True

        self.client_socket.setblocking(False)

    # =====================================================
    # Event Loop Callback
    # =====================================================

    def read(
        self,
        sock,
        mask,
    ) -> None:

        context = Context(self)

        raw_request = self.receive_request()

        if raw_request is None:
            return

        try:

            self.processor.process(
                context,
                raw_request,
            )

        except Exception as exc:

            context.response = Response(
                {
                    "error": str(exc)
                },
                status=500,
            )

        self.send_response(
            context
        )

        if self.should_close():
            self.close()

    # =====================================================
    # Receive
    # =====================================================

    def receive_request(
        self,
    ):

        try:

            data = self.client_socket.recv(
                self.BUFFER_SIZE
            )

        except BlockingIOError:

            return None

        except ConnectionResetError:

            self.close()

            return None

        if not data:

            self.close()

            return None

        return data

    # =====================================================
    # Send
    # =====================================================

    def send_response(
        self,
        context: Context,
    ):

        self.client_socket.sendall(
            context.response.to_bytes()
        )

    # =====================================================
    # Keep Alive
    # =====================================================

    def should_close(
        self,
    ) -> bool:

        return not self.keep_alive

    # =====================================================
    # Close
    # =====================================================

    def close(
        self,
    ):

        print(
            f"Closing {self.client_address}"
        )

        self.event_loop.unregister(
            self.client_socket
        )

        try:

            self.client_socket.close()

        except Exception:
            pass